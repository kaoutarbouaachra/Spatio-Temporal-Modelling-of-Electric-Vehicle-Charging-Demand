# ==============================================================================
# PROJECT: SPATIO-TEMPORAL MODELLING OF EV CHARGING DEMAND
# OBJECTIVE: BENCHMARKING INLA VS DISAGGREGATED ML
# ==============================================================================

# ------------------------------------------------------------------------------
# 0. ENVIRONMENT SETUP
# ------------------------------------------------------------------------------
options(timeout = 600)
set.seed(123)

pkgs <- c("dplyr", "ggplot2", "zoo", "tidyr",
          "Metrics", "xgboost", "ranger")

new_pkgs <- pkgs[!(pkgs %in% installed.packages()[,"Package"])]
if(length(new_pkgs)) install.packages(new_pkgs, dependencies = TRUE)

invisible(lapply(pkgs, library, character.only = TRUE))


# ------------------------------------------------------------------------------
# 1. DATA PREPROCESSING
# ------------------------------------------------------------------------------

path_file <- "SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/glasgow datasets/df_final_modeling.csv"
df_final_modeling <- read.csv(path_file, stringsAsFactors = FALSE)

df <- df_final_modeling %>%
  filter(!CPID %in% c("62201","62202","62203","62266","62261","50433","62123"))

df$Date <- as.Date(df$Date)

df <- df %>%
  arrange(CPID, Date) %>%
  group_by(CPID) %>%
  mutate(
    time_index = as.numeric(Date - min(Date)) + 1,
    lag_1  = lag(daily_sessions, 1),
    lag_7  = lag(daily_sessions, 7),
    lag_14 = lag(daily_sessions, 14)
  ) %>%
  ungroup() %>%
  filter(!is.na(lag_14))

df <- df %>%
  mutate(across(c(connector_type, weekday,
                  is_public_access, is_free, CPID),
                as.factor))



df <- df %>%
  arrange(CPID, Date) %>%
  group_by(CPID) %>%
  mutate(
    row_id = row_number(),
    n_obs = n(),
    split_index = floor(0.8 * n_obs)
  ) %>%
  ungroup()


features_ml <- c(
  "connector_type",
  "weekday",
  "is_public_access",
  "is_free",
  "humidity_avg",
  "wind_speed_avg",
  "feels_like_avg",
  "lag_1",
  "lag_7",
  "lag_14"
)

# ------------------------------------------------------------------------------
# 2. DISAGGREGATED ML TRAINING LOOP
# ------------------------------------------------------------------------------

ml_results_list <- list()
unique_cpids <- unique(df$CPID)

for (id in unique_cpids) {
  
  train_sub <- df %>%
    filter(CPID == id, row_id <= split_index)
  
  test_sub <- df %>%
    filter(CPID == id, row_id > split_index)
  
  if(nrow(train_sub) < 30 || nrow(test_sub) == 0) next
  
  # Remove constant features
  features_local <- features_ml[
    sapply(train_sub[features_ml], function(x) length(unique(x)) > 1)
  ]
  
  # Keep only relevant columns + remove NA
  train_sub <- train_sub %>%
    select(daily_sessions, all_of(features_local)) %>%
    drop_na()
  
  test_sub <- test_sub %>%
    select(daily_sessions, all_of(features_local)) %>%
    drop_na()
  
  if(nrow(train_sub) < 30 || nrow(test_sub) == 0) next
  
  # ---------------- GLM POISSON ----------------
  
  formula_glm <- as.formula(
    paste("daily_sessions ~", paste(features_local, collapse = " + "))
  )
  
  pred_glm <- NA
  
  try({
    mod_glm  <- glm(formula_glm, family = poisson, data = train_sub)
    pred_glm <- predict(mod_glm, newdata = test_sub, type = "response")
  }, silent = TRUE)
  
  # ---------------- XGBOOST ----------------
  
  train_matrix <- model.matrix(
    daily_sessions ~ . -1,
    data = train_sub
  )
  
  test_matrix <- model.matrix(
    daily_sessions ~ . -1,
    data = test_sub
  )
  
  dtrain <- xgb.DMatrix(
    data = train_matrix,
    label = train_sub$daily_sessions
  )
  
  dtest <- xgb.DMatrix(
    data = test_matrix,
    label = test_sub$daily_sessions
  )
  
  mod_xgb <- xgb.train(
    params = list(
      objective = "count:poisson",
      eta = 0.05,
      max_depth = 4,
      subsample = 0.8,
      colsample_bytree = 0.8
    ),
    data = dtrain,
    nrounds = 200,
    verbose = 0
  )
  
  pred_xgb <- predict(mod_xgb, dtest)
  
  ml_results_list[[as.character(id)]] <- data.frame(
    CPID = id,
    Actual = test_sub$daily_sessions,
    Pred_GLM = pred_glm,
    Pred_XGB = pred_xgb
  )
}

df_ml_preds <- bind_rows(ml_results_list)

# ------------------------------------------------------------------------------
# 3. Metrics
# ------------------------------------------------------------------------------
metrics_ml <- df_ml_preds %>%
  group_by(CPID) %>%
  summarise(
    obs_mean = mean(Actual),
    MAE_GLM = mean(abs(Actual - Pred_GLM), na.rm = TRUE),
    MAE_XGB = mean(abs(Actual - Pred_XGB), na.rm = TRUE),
    RMSE_GLM = sqrt(mean((Actual - Pred_GLM)^2, na.rm = TRUE)),
    RMSE_XGB = sqrt(mean((Actual - Pred_XGB)^2, na.rm = TRUE)),
    .groups = "drop"
  ) %>%
  pivot_longer(cols = starts_with("MAE") | starts_with("RMSE"), 
               names_to = c(".value", "Model"), names_sep = "_") %>%
  mutate(Model = ifelse(Model == "GLM", "ML (Poisson GLM)", "ML (XGBoost)"),
         MAPE = (MAE / (obs_mean + 1)) * 100)

metrics_inla_all <- comparison_by_cpid %>%
  left_join(df_test_clean %>% group_by(CPID) %>% summarise(obs = mean(daily_sessions)), by="CPID") %>%
  mutate(MAPE = (MAE / (obs + 1)) * 100,
         Model = case_when(Model == "ICAR-RW2" ~ "INLA (ICAR)",
                           Model == "SPDE-RW2" ~ "INLA (SPDE)", 
                           TRUE ~ Model)) %>%
  dplyr::select(CPID, Model, MAE, RMSE, MAPE)

all_comparison_results <- bind_rows(metrics_inla_all, metrics_ml) %>% filter(!is.na(MAE))

# ------------------------------------------------------------------------------
# 4. OUTLIER FILTERING & COLOR SETUP
# ------------------------------------------------------------------------------

is_outlier <- function(x) {
  qnt <- quantile(x, probs=c(.25, .75), na.rm = TRUE)
  H <- 1.5 * IQR(x, na.rm = TRUE)
  return(x < (qnt[1] - H) | x > (qnt[2] + H))
}

all_comparison_filtered <- all_comparison_results %>%
  group_by(Model) %>%
  mutate(outlier_mae = is_outlier(MAE), outlier_rmse = is_outlier(RMSE), outlier_mape = is_outlier(MAPE)) %>%
  ungroup()

model_colors <- c("INLA (ICAR)" = "#31688E", "INLA (SPDE)" = "#35B779", 
                  "ML (XGBoost)" = "#FDE725", "ML (Poisson GLM)" = "#440154")



# ------------------------------------------------------------------------------
# 5. GLOBAL PERFORMANCE VISUALIZATION
# ------------------------------------------------------------------------------

long_plot_data <- all_comparison_filtered %>%
  pivot_longer(cols = c(MAE, RMSE, MAPE), names_to = "Metric", values_to = "Score") %>%
  filter((Metric == "MAE" & !outlier_mae) | (Metric == "RMSE" & !outlier_rmse) | (Metric == "MAPE" & !outlier_mape))

p_global <- ggplot(long_plot_data, aes(x = reorder(Model, Score, FUN = median), y = Score, fill = Model)) +
  geom_boxplot(alpha = 0.7, outlier.shape = NA) +
  geom_jitter(width = 0.15, alpha = 0.2, size = 0.8) +
  facet_wrap(~Metric, scales = "free_y") +
  scale_fill_manual(values = model_colors) +
  theme_minimal(base_family = "serif") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1), legend.position = "none")

print(p_global)


# ------------------------------------------------------------------------------
# 6. PAIRWISE COMPARISON MATRIX
# ------------------------------------------------------------------------------
create_pairwise_plot <- function(df, metric_name, color_hex = "#31688E") {
    scatter_data <- df %>%
    dplyr::select(CPID, Model, !!sym(metric_name)) %>%
    pivot_wider(names_from = Model, values_from = !!sym(metric_name)) %>%
    pivot_longer(cols = starts_with("ML"), 
                 names_to = "ML_Model", values_to = "ML_Value") %>%
    pivot_longer(cols = starts_with("INLA"), 
                 names_to = "INLA_Model", values_to = "INLA_Value")
    p <- ggplot(scatter_data, aes(x = ML_Value, y = INLA_Value)) +
    geom_point(alpha = 0.4, size = 1.2, color = color_hex) +
    geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed", linewidth = 0.8) +
    facet_grid(INLA_Model ~ ML_Model) +
    labs(
      title = paste("Pairwise Comparison:", metric_name),
      subtitle = "Points below the red diagonal indicate higher accuracy for INLA",
      x = paste("ML Benchmark", metric_name),
      y = paste("INLA Spatial Model", metric_name)
    ) +
    theme_bw(base_family = "serif") +
    theme(
      strip.background = element_rect(fill = "grey95"),
      strip.text = element_text(face = "bold"),
      plot.title = element_text(size = 14, face = "bold")
    )
  
  return(p)
}

metrics_to_plot <- list(
  MAE  = "#31688E", # Blue
  RMSE = "#35B779", # Green
  MAPE = "#440154"  # Purple
)

for (metric in names(metrics_to_plot)) {
    p <- create_pairwise_plot(all_comparison_results, metric, metrics_to_plot[[metric]])
    print(p)
    file_name <- paste0("Pairwise_", metric, "_Comparison.png")
  ggsave(file_name, p, width = 11, height = 8, dpi = 300)
  
  cat("Generated and saved:", file_name, "\n")
}

for (metric in names(metrics_to_plot)) {
  
  # 1. Define the PDF file name
  file_name <- paste0("Pairwise_", metric, "_Comparison.pdf")
  
  # 2. Create the plot using your function
  p <- create_pairwise_plot(all_comparison_results, metric, metrics_to_plot[[metric]])
  
  # 3. Open PDF device, Print the plot, and Close device
  pdf(file_name, width = 11, height = 8)
  print(p)
  dev.off()
  
  cat("Successfully generated individual PDF:", file_name, "\n")
}
# ------------------------------------------------------------------------------
# 7. WIN RATE & SUMMARY STATISTICS
# ------------------------------------------------------------------------------
metrics_list <- c("MAE", "RMSE", "MAPE")
model_colors <- c("INLA (ICAR)" = "#31688E", "INLA (SPDE)" = "#35B779")

for (met in metrics_list) {
    win_rate_results <- all_comparison_results %>%
    dplyr::select(CPID, Model, !!sym(met)) %>%
    tidyr::pivot_wider(names_from = Model, values_from = !!sym(met)) %>%
    summarise(
      `ICAR vs XGBoost` = mean(`INLA (ICAR)` < `ML (XGBoost)`, na.rm = TRUE) * 100,
      `ICAR vs GLM`     = mean(`INLA (ICAR)` < `ML (Poisson GLM)`, na.rm = TRUE) * 100,
      `SPDE vs XGBoost` = mean(`INLA (SPDE)` < `ML (XGBoost)`, na.rm = TRUE) * 100,
      `SPDE vs GLM`     = mean(`INLA (SPDE)` < `ML (Poisson GLM)`, na.rm = TRUE) * 100
    )
  
  cat("\n--- WIN RATES (%) FOR", met, "---\n")
  print(t(win_rate_results))
    df_plot_win <- win_rate_results %>%
    tidyr::pivot_longer(cols = everything(), names_to = "Comparison", values_to = "WinRate") %>%
    mutate(
      Spatial_Model = ifelse(grepl("ICAR", Comparison), "INLA (ICAR)", "INLA (SPDE)"),
      Benchmark = ifelse(grepl("XGBoost", Comparison), "vs XGBoost", "vs Poisson GLM")
    )
  
  p <- ggplot(df_plot_win, aes(x = Benchmark, y = WinRate, fill = Spatial_Model)) +
    geom_bar(stat = "identity", position = position_dodge(width = 0.8), alpha = 0.8) +
    geom_text(aes(label = paste0(round(WinRate, 1), "%")), 
              position = position_dodge(width = 0.8), 
              vjust = -0.5, 
              fontface = "bold",
              family = "serif") +
    scale_fill_manual(values = model_colors) +
    ylim(0, 110) + # Increased slightly to fit labels
    labs(
      title = paste("Model Superiority (Win Rate):", met),
      subtitle = paste("Percentage of stations where INLA achieves a lower", met, "than benchmarks"),
      x = "Machine Learning Benchmark",
      y = "Win Rate (%)",
      fill = "Spatial Model"
    ) +
    theme_minimal(base_family = "serif") +
    theme(
      plot.title = element_text(face = "bold", size = 14),
      axis.title = element_text(face = "bold"),
      legend.position = "top"
    )
  
  # 4. Save to PDF
  file_name <- paste0("Win_Rates_", met, ".pdf")
  pdf(file_name, width = 8, height = 6)
  print(p)
  dev.off()
  
  cat("Saved:", file_name, "\n")
}


# WIN RATE DUAL COMPARISON 
metrics_list <- c("MAE", "RMSE", "MAPE")
plot_list <- list()

for (met in metrics_list) {
  
  comparison_data <- all_comparison_results %>%
    dplyr::select(CPID, Model, !!sym(met)) %>%
    tidyr::pivot_wider(names_from = Model, values_from = !!sym(met)) %>%
    summarise(
      ICAR_vs_XGB = mean(`INLA (ICAR)` < `ML (XGBoost)`, na.rm = TRUE) * 100,
      ICAR_vs_GLM = mean(`INLA (ICAR)` < `ML (Poisson GLM)`, na.rm = TRUE) * 100,
      SPDE_vs_XGB = mean(`INLA (SPDE)` < `ML (XGBoost)`, na.rm = TRUE) * 100,
      SPDE_vs_GLM = mean(`INLA (SPDE)` < `ML (Poisson GLM)`, na.rm = TRUE) * 100
    )
  
  df_stacked <- data.frame(
    Comparison = rep(c("ICAR vs XGBoost", "ICAR vs GLM", "SPDE vs XGBoost", "SPDE vs GLM"), each = 2),
    Winner = rep(c("INLA Wins", "ML Wins"), 4),
    Share = c(
      comparison_data$ICAR_vs_XGB, 100 - comparison_data$ICAR_vs_XGB,
      comparison_data$ICAR_vs_GLM, 100 - comparison_data$ICAR_vs_GLM,
      comparison_data$SPDE_vs_XGB, 100 - comparison_data$SPDE_vs_XGB,
      comparison_data$SPDE_vs_GLM, 100 - comparison_data$SPDE_vs_GLM
    )
  )
  
  p <- ggplot(df_stacked, aes(x = Comparison, y = Share, fill = Winner)) +
    geom_bar(stat = "identity", width = 0.7, color = "white") +
    geom_text(aes(label = paste0(round(Share, 1), "%")), 
              position = position_stack(vjust = 0.5), 
              color = "white", fontface = "bold", size = 4) +
    scale_fill_manual(values = c("INLA Wins" = "#31688E", "ML Wins" = "#E67E22")) + 
    labs(
      title = paste("Head-to-Head Model Dominance:", met),
      subtitle = "Spatial INLA Accuracy vs Local Machine Learning Benchmarks",
      x = "", y = "Percentage of Stations (%)",
      fill = "Winner"
    ) +
    theme_minimal(base_family = "serif") +
    theme(
      legend.position = "bottom",
      axis.text.x = element_text(angle = 25, hjust = 1)
    )
  
  plot_list[[met]] <- p
  
  ggsave(paste0("Dominance_Comparison_", met, ".pdf"), p, width = 9, height = 7)
}

print(plot_list$MAE)
print(plot_list$RMSE)
print(plot_list$MAPE)

