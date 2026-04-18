# ==============================================================================
# 03_local_vs_inla.R
# PROJECT: Spatio-Temporal Modelling of EV Charging Demand
# PURPOSE: Benchmarking INLA models vs disaggregated ML (GLM, XGBoost)
# Run after: 02_inla_model.R
# Outputs:  figures/Pairwise_*.pdf
#           figures/Dominance_Comparison_*.pdf
#           figures/Win_Rates_*.pdf
# ==============================================================================

source("config.R")

# ── 0. Setup ──────────────────────────────────────────────────────────────────
options(timeout = 600)
set.seed(RANDOM_SEED)

pkgs <- c("dplyr", "ggplot2", "zoo", "tidyr", "Metrics", "xgboost", "ranger")
new_pkgs <- pkgs[!(pkgs %in% installed.packages()[, "Package"])]
if (length(new_pkgs)) install.packages(new_pkgs, dependencies = TRUE)
invisible(lapply(pkgs, library, character.only = TRUE))

# ── 1. Load data ──────────────────────────────────────────────────────────────
cat("Loading datasets...\n")
df_final_modeling <- read.csv(PATH_MODELING, stringsAsFactors = FALSE)

# ✅ Load INLA results saved by script 02 (were previously expected in memory)
path_comparison <- file.path(RESULTS_DIR, "comparison_by_cpid.csv")
path_test_clean <- file.path(RESULTS_DIR, "df_test_clean.csv")

if (!file.exists(path_comparison) || !file.exists(path_test_clean)) {
  stop("❌ Missing INLA results. Please run 02_inla_model.R first.")
}
comparison_by_cpid <- read.csv(path_comparison, stringsAsFactors = FALSE)
df_test_clean      <- read.csv(path_test_clean,  stringsAsFactors = FALSE)
cat("✓ INLA results loaded.\n")

# ── 2. ML data preparation ────────────────────────────────────────────────────
df <- df_final_modeling %>%
  filter(!CPID %in% EXCLUDED_CPIDS)

df$Date <- as.Date(df$Date)

df <- df %>%
  arrange(CPID, Date) %>%
  group_by(CPID) %>%
  mutate(
    time_index = as.numeric(Date - min(Date)) + 1,
    lag_1      = lag(daily_sessions, 1),
    lag_7      = lag(daily_sessions, 7),
    lag_14     = lag(daily_sessions, 14)
  ) %>%
  ungroup() %>%
  filter(!is.na(lag_14)) %>%
  mutate(across(c(connector_type, weekday, is_public_access, is_free, CPID), as.factor))

df <- df %>%
  arrange(CPID, Date) %>%
  group_by(CPID) %>%
  mutate(row_id = row_number(), n_obs = n(),
         split_index = floor(TRAIN_RATIO * n_obs)) %>%
  ungroup()

features_ml <- c("connector_type", "weekday", "is_public_access", "is_free",
                  "humidity_avg", "wind_speed_avg", "feels_like_avg",
                  "lag_1", "lag_7", "lag_14")

# ── 3. ML training loop ───────────────────────────────────────────────────────
cat("Training ML models per charging station...\n")
ml_results_list <- list()

for (id in unique(df$CPID)) {
  train_sub <- df %>% filter(CPID == id, row_id <= split_index)
  test_sub  <- df %>% filter(CPID == id, row_id >  split_index)

  if (nrow(train_sub) < 30 || nrow(test_sub) == 0) next

  features_local <- features_ml[
    sapply(train_sub[features_ml], function(x) length(unique(x)) > 1)
  ]

  train_sub <- train_sub %>% select(daily_sessions, all_of(features_local)) %>% drop_na()
  test_sub  <- test_sub  %>% select(daily_sessions, all_of(features_local)) %>% drop_na()

  if (nrow(train_sub) < 30 || nrow(test_sub) == 0) next

  # GLM Poisson
  pred_glm <- NA
  try({
    mod_glm  <- glm(as.formula(paste("daily_sessions ~", paste(features_local, collapse = " + "))),
                    family = poisson, data = train_sub)
    pred_glm <- predict(mod_glm, newdata = test_sub, type = "response")
  }, silent = TRUE)

  # XGBoost
  train_mat <- model.matrix(daily_sessions ~ . - 1, data = train_sub)
  test_mat  <- model.matrix(daily_sessions ~ . - 1, data = test_sub)
  dtrain    <- xgb.DMatrix(data = train_mat, label = train_sub$daily_sessions)
  dtest     <- xgb.DMatrix(data = test_mat,  label = test_sub$daily_sessions)

  mod_xgb  <- xgb.train(
    params  = list(objective = "count:poisson", eta = 0.05,
                   max_depth = 4, subsample = 0.8, colsample_bytree = 0.8),
    data    = dtrain, nrounds = 200, verbose = 0
  )
  pred_xgb <- predict(mod_xgb, dtest)

  ml_results_list[[as.character(id)]] <- data.frame(
    CPID     = id,
    Actual   = test_sub$daily_sessions,
    Pred_GLM = pred_glm,
    Pred_XGB = pred_xgb
  )
}

df_ml_preds <- bind_rows(ml_results_list)
cat("✓ ML training complete.\n")

# ── 4. Metrics ────────────────────────────────────────────────────────────────
metrics_ml <- df_ml_preds %>%
  group_by(CPID) %>%
  summarise(
    obs_mean = mean(Actual),
    MAE_GLM  = mean(abs(Actual - Pred_GLM), na.rm = TRUE),
    MAE_XGB  = mean(abs(Actual - Pred_XGB), na.rm = TRUE),
    RMSE_GLM = sqrt(mean((Actual - Pred_GLM)^2, na.rm = TRUE)),
    RMSE_XGB = sqrt(mean((Actual - Pred_XGB)^2, na.rm = TRUE)),
    .groups = "drop"
  ) %>%
  pivot_longer(cols = starts_with("MAE") | starts_with("RMSE"),
               names_to = c(".value", "Model"), names_sep = "_") %>%
  mutate(Model = ifelse(Model == "GLM", "ML (Poisson GLM)", "ML (XGBoost)"),
         MAPE  = (MAE / (obs_mean + 1)) * 100)

metrics_inla_all <- comparison_by_cpid %>%
  left_join(df_test_clean %>% group_by(CPID) %>%
              summarise(obs = mean(daily_sessions), .groups = "drop"),
            by = "CPID") %>%
  mutate(
    MAPE  = (MAE / (obs + 1)) * 100,
    Model = case_when(
      Model == "ICAR-RW2" ~ "INLA (ICAR)",
      Model == "SPDE-RW2" ~ "INLA (SPDE)",
      TRUE ~ Model
    )
  ) %>%
  dplyr::select(CPID, Model, MAE, RMSE, MAPE)

all_comparison_results <- bind_rows(metrics_inla_all, metrics_ml) %>%
  filter(!is.na(MAE))

# ── 5. Outlier filtering ──────────────────────────────────────────────────────
is_outlier <- function(x) {
  qnt <- quantile(x, probs = c(.25, .75), na.rm = TRUE)
  H   <- 1.5 * IQR(x, na.rm = TRUE)
  x < (qnt[1] - H) | x > (qnt[2] + H)
}

all_comparison_filtered <- all_comparison_results %>%
  group_by(Model) %>%
  mutate(outlier_mae  = is_outlier(MAE),
         outlier_rmse = is_outlier(RMSE),
         outlier_mape = is_outlier(MAPE)) %>%
  ungroup()

model_colors <- c("INLA (ICAR)"    = "#31688E",
                  "INLA (SPDE)"    = "#35B779",
                  "ML (XGBoost)"   = "#FDE725",
                  "ML (Poisson GLM)" = "#440154")

# ── 6. Global performance boxplot ─────────────────────────────────────────────
long_plot_data <- all_comparison_filtered %>%
  pivot_longer(cols = c(MAE, RMSE, MAPE), names_to = "Metric", values_to = "Score") %>%
  filter((Metric == "MAE"  & !outlier_mae)  |
         (Metric == "RMSE" & !outlier_rmse) |
         (Metric == "MAPE" & !outlier_mape))

p_global <- ggplot(long_plot_data,
                   aes(x = reorder(Model, Score, FUN = median), y = Score, fill = Model)) +
  geom_boxplot(alpha = 0.7, outlier.shape = NA) +
  geom_jitter(width = 0.15, alpha = 0.2, size = 0.8) +
  facet_wrap(~Metric, scales = "free_y") +
  scale_fill_manual(values = model_colors) +
  theme_minimal(base_family = "serif") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "none")

ggsave(file.path(FIGURES_DIR, "boxplot_inla_vs_ml.pdf"), p_global, width = 11, height = 7)
cat("✓ Saved boxplot_inla_vs_ml.pdf\n")

# ── 7. Pairwise comparison ────────────────────────────────────────────────────
create_pairwise_plot <- function(df, metric_name, color_hex = "#31688E") {
  scatter_data <- df %>%
    dplyr::select(CPID, Model, !!sym(metric_name)) %>%
    pivot_wider(names_from = Model, values_from = !!sym(metric_name)) %>%
    pivot_longer(cols = starts_with("ML"),   names_to = "ML_Model",   values_to = "ML_Value") %>%
    pivot_longer(cols = starts_with("INLA"), names_to = "INLA_Model", values_to = "INLA_Value")

  ggplot(scatter_data, aes(x = ML_Value, y = INLA_Value)) +
    geom_point(alpha = 0.4, size = 1.2, color = color_hex) +
    geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed", linewidth = 0.8) +
    facet_grid(INLA_Model ~ ML_Model) +
    labs(title    = paste("Pairwise Comparison:", metric_name),
         subtitle = "Points below the red diagonal indicate higher accuracy for INLA",
         x = paste("ML Benchmark", metric_name),
         y = paste("INLA Spatial Model", metric_name)) +
    theme_bw(base_family = "serif") +
    theme(strip.background = element_rect(fill = "grey95"),
          strip.text       = element_text(face = "bold"),
          plot.title       = element_text(size = 14, face = "bold"))
}

metrics_palette <- list(MAE = "#31688E", RMSE = "#35B779", MAPE = "#440154")

for (metric in names(metrics_palette)) {
  p <- create_pairwise_plot(all_comparison_results, metric, metrics_palette[[metric]])
  ggsave(file.path(FIGURES_DIR, paste0("Pairwise_", metric, "_Comparison.pdf")),
         p, width = 11, height = 8)
  cat("✓ Saved Pairwise_", metric, "_Comparison.pdf\n", sep = "")
}

# ── 8. Win rate analysis ──────────────────────────────────────────────────────
metrics_list  <- c("MAE", "RMSE", "MAPE")
model_colors2 <- c("INLA (ICAR)" = "#31688E", "INLA (SPDE)" = "#35B779")
plot_list     <- list()

for (met in metrics_list) {
  comp <- all_comparison_results %>%
    dplyr::select(CPID, Model, !!sym(met)) %>%
    tidyr::pivot_wider(names_from = Model, values_from = !!sym(met)) %>%
    summarise(
      ICAR_vs_XGB = mean(`INLA (ICAR)` < `ML (XGBoost)`,     na.rm = TRUE) * 100,
      ICAR_vs_GLM = mean(`INLA (ICAR)` < `ML (Poisson GLM)`, na.rm = TRUE) * 100,
      SPDE_vs_XGB = mean(`INLA (SPDE)` < `ML (XGBoost)`,     na.rm = TRUE) * 100,
      SPDE_vs_GLM = mean(`INLA (SPDE)` < `ML (Poisson GLM)`, na.rm = TRUE) * 100
    )

  df_stacked <- data.frame(
    Comparison = rep(c("ICAR vs XGBoost", "ICAR vs GLM", "SPDE vs XGBoost", "SPDE vs GLM"), each = 2),
    Winner     = rep(c("INLA Wins", "ML Wins"), 4),
    Share      = c(comp$ICAR_vs_XGB, 100 - comp$ICAR_vs_XGB,
                   comp$ICAR_vs_GLM, 100 - comp$ICAR_vs_GLM,
                   comp$SPDE_vs_XGB, 100 - comp$SPDE_vs_XGB,
                   comp$SPDE_vs_GLM, 100 - comp$SPDE_vs_GLM)
  )

  p <- ggplot(df_stacked, aes(x = Comparison, y = Share, fill = Winner)) +
    geom_bar(stat = "identity", width = 0.7, color = "white") +
    geom_text(aes(label = paste0(round(Share, 1), "%")),
              position = position_stack(vjust = 0.5),
              color = "white", fontface = "bold", size = 4) +
    scale_fill_manual(values = c("INLA Wins" = "#31688E", "ML Wins" = "#E67E22")) +
    labs(title    = paste("Head-to-Head Model Dominance:", met),
         subtitle = "Spatial INLA Accuracy vs Local Machine Learning Benchmarks",
         x = "", y = "Percentage of Stations (%)", fill = "Winner") +
    theme_minimal(base_family = "serif") +
    theme(legend.position = "bottom",
          axis.text.x = element_text(angle = 25, hjust = 1))

  plot_list[[met]] <- p
  ggsave(file.path(FIGURES_DIR, paste0("Dominance_Comparison_", met, ".pdf")),
         p, width = 9, height = 7)
  cat("✓ Saved Dominance_Comparison_", met, ".pdf\n", sep = "")
}

cat("\n✅ Script 03 completed.\n")
