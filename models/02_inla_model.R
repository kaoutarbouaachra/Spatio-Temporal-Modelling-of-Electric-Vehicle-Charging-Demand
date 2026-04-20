# ==============================================================================
# 02_inla_model.R 
# PROJECT: Spatio-Temporal Modelling of EV Charging Demand
# PURPOSE: Fit ICAR+RW2 and SPDE+RW2 models via INLA
# Outputs:  data/glasgow_datasets/comparison_by_cpid.csv   ← used by script 03
#           data/glasgow_datasets/df_test_clean.csv         ← used by script 03
#           data/glasgow_datasets/resume_models_test.csv
#           data/glasgow_datasets/resume_par_cpid_test.csv
#           data/glasgow_datasets/df_all_predictions_spde_rw2.csv
#           figures/Figure_Exploratory_Dispersion.pdf
# ==============================================================================

source("config.R")

# ── 0. Environment setup ──────────────────────────────────────────────────────
options(timeout = 600)
set.seed(RANDOM_SEED)

pkgs <- c("dplyr", "ggplot2", "spdep", "igraph", "splines", "fields",
          "reshape2", "viridis", "ggpubr", "sf", "zoo")
new_pkgs <- pkgs[!(pkgs %in% installed.packages()[, "Package"])]
if (length(new_pkgs)) install.packages(new_pkgs, dependencies = TRUE)
if (!require("INLA", quietly = TRUE)) {
  install.packages("INLA",
                   repos = c(getOption("repos"),
                             INLA = "https://inla.r-inla-download.org/R/stable"),
                   dep = TRUE)
}
invisible(lapply(c("INLA", pkgs), library, character.only = TRUE))
viridisBlue <- "#31688E"

# ── 1. Data loading ───────────────────────────────────────────────────────────
cat("Loading modeling dataset...\n")
df_final_modeling <- read.csv(PATH_MODELING, stringsAsFactors = FALSE)

df <- df_final_modeling %>%
  dplyr::filter(!CPID %in% EXCLUDED_CPIDS)

df$Date <- as.Date(df$Date)
df <- df[order(df$Date), ]
df$time_index <- as.numeric(df$Date - min(df$Date)) + 1

df <- df %>%
  mutate(across(c(connector_type, weekday, YearMonth,
                  is_public_access, is_free, Month, CPID), as.factor))
df$id_cpid <- as.numeric(df$CPID)

# ── 2. Dispersion analysis ────────────────────────────────────────────────────
df_dispersion <- df %>%
  group_by(CPID) %>%
  summarise(mu = mean(daily_sessions), sigma2 = var(daily_sessions),
            ratio = sigma2 / mu, .groups = "drop")

cpid_under <- df_dispersion %>% filter(ratio < 1) %>% slice_min(ratio, n = 3) %>% pull(CPID)
cpid_over  <- df_dispersion %>% filter(ratio > 1) %>% slice_max(ratio, n = 3) %>% pull(CPID)

custom_theme <- theme_minimal(base_family = "serif") +
  theme(plot.title = element_text(face = "bold", size = 12),
        strip.text = element_text(face = "italic"))

p1 <- df %>%
  filter(CPID %in% cpid_under) %>%
  ggplot(aes(x = daily_sessions, fill = ..count..)) +
  geom_histogram(binwidth = 1, color = "white", linewidth = 0.2) +
  facet_wrap(~CPID, scales = "free_y") +
  scale_fill_viridis_c(option = "viridis", name = "Frequency") +
  custom_theme +
  labs(title = "A. Observed Under-dispersion",
       subtitle = "Variance < Mean: Indicative of steady-state demand",
       x = "Daily Charging Sessions", y = "Frequency")

p2 <- df %>%
  filter(CPID %in% cpid_over) %>%
  ggplot(aes(x = daily_sessions, fill = ..count..)) +
  geom_histogram(binwidth = 1, color = "white", linewidth = 0.2) +
  facet_wrap(~CPID, scales = "free_y") +
  scale_fill_viridis_c(option = "viridis", name = "Frequency") +
  custom_theme +
  labs(title = "B. Observed Over-dispersion",
       subtitle = "Variance > Mean: Higher volatility in urban charging hotspots",
       x = "Daily Charging Sessions", y = "Frequency")

combined_fig <- ggarrange(p1, p2, ncol = 1, nrow = 2, common.legend = FALSE)
ggsave(file.path(FIGURES_DIR, "Figure_Exploratory_Dispersion.pdf"),
       combined_fig, device = "pdf", width = 5, height = 6, units = "in", dpi = 600)
cat("Saved Figure_Exploratory_Dispersion.pdf\n")

# ── 3. Train / test split ─────────────────────────────────────────────────────
df <- df %>%
  mutate(across(c(connector_type, weekday, YearMonth,
                  is_public_access, is_free, Month, CPID), as.factor))

dates           <- sort(unique(df$Date))
cut_date        <- dates[floor(TRAIN_RATIO * length(dates))]
df_train        <- df %>% filter(Date <= cut_date) %>% mutate(predict = 0)
df_test         <- df %>% filter(Date >  cut_date) %>% mutate(predict = 1)
df_all          <- bind_rows(df_train, df_test)
cat("Training period ends on:", as.character(cut_date), "\n")

# ── 4. ICAR + RW2 ─────────────────────────────────────────────────────────────
df_all$id_cpid <- as.numeric(as.factor(as.character(df_all$CPID)))

coords_cpid <- df_all %>%
  distinct(id_cpid, longitude, latitude) %>%
  arrange(id_cpid)
coords_matrix <- jitter(as.matrix(coords_cpid[, c("longitude", "latitude")]),
                        amount = 0.00001)
knn_nb <- knn2nb(knearneigh(coords_matrix, k = 4), sym = TRUE)
g <- graph_from_adj_list(knn_nb)
comps <- components(g)
if (comps$no > 1) {
  for (i in 2:comps$no) {
    comp1  <- which(comps$membership == 1)
    compi  <- which(comps$membership == i)
    dmat   <- as.matrix(dist(rbind(coords_matrix[comp1, ], coords_matrix[compi, ])))
    dsub   <- dmat[1:length(comp1), (length(comp1) + 1):nrow(dmat)]
    idx    <- which(dsub == min(dsub), arr.ind = TRUE)
    g      <- add_edges(g, c(comp1[idx[1, 1]], compi[idx[1, 2]]))
  }
}
g       <- as_undirected(g, mode = "collapse")
mat_adj <- as_adjacency_matrix(g, sparse = FALSE)
mat_adj <- (mat_adj | t(mat_adj))
lw      <- mat2listw(as.matrix(mat_adj), style = "B")
nb_connexe <- lw$neighbours

graph_file <- file.path(RESULTS_DIR, "cpid_graph.graph")
if (file.exists(graph_file)) file.remove(graph_file)
nb2INLA(graph_file, nb_connexe)

temp_spline_mat <- bs(df_all$temp_avg, df = 3)
df_all <- cbind(df_all,
                temp_spline1 = temp_spline_mat[, 1],
                temp_spline2 = temp_spline_mat[, 2],
                temp_spline3 = temp_spline_mat[, 3])
df_all <- df_all[, !duplicated(names(df_all))]

formula_car_rw2 <- daily_sessions ~
  connector_type + weekday + is_public_access + is_free +
  temp_spline1 + temp_spline2 + temp_spline3 +
  humidity_avg + wind_speed_avg + feels_like_avg +
  f(id_cpid, model = "besag", graph = graph_file) +
  f(time_index, model = "rw2")

result_car_rw2 <- inla(formula_car_rw2, family = "poisson", data = df_all,
                       control.predictor = list(compute = TRUE),
                       control.compute  = list(dic = TRUE, waic = TRUE))
summary(result_car_rw2)

# Evaluation helpers
evaluate_model_test <- function(result, df_all, df_train, model_name) {
  N_train <- nrow(df_train)
  pred    <- result$summary.fitted.values
  df_all$pred_mean  <- pred$mean
  df_all$pred_lower <- pred$`0.025quant`
  df_all$pred_upper <- pred$`0.975quant`
  df_test_pred <- df_all[(N_train + 1):nrow(df_all), ]
  y_true <- df_test_pred$daily_sessions
  y_pred <- df_test_pred$pred_mean
  data.frame(Model = model_name, Set = "test",
             MAE  = mean(abs(y_pred - y_true)),
             RMSE = sqrt(mean((y_pred - y_true)^2)))
}

evaluate_par_cpid_test <- function(result, df_all, df_train, model_name) {
  N_train <- nrow(df_train)
  pred    <- result$summary.fitted.values
  df_all$pred_mean <- pred$mean
  df_all[(N_train + 1):nrow(df_all), ] %>%
    dplyr::group_by(CPID) %>%
    dplyr::summarise(
      MAE  = mean(abs(pred_mean - daily_sessions)),
      RMSE = sqrt(mean((pred_mean - daily_sessions)^2)),
      .groups = "drop"
    ) %>%
    dplyr::mutate(Model = model_name, Set = "test") %>%
    dplyr::select(Model, Set, CPID, MAE, RMSE)
}

results_df       <- evaluate_model_test(result_car_rw2, df_all, df_train, "icar_rw2")
results_cpid_df  <- evaluate_par_cpid_test(result_car_rw2, df_all, df_train, "icar_rw2")
write.csv(results_df,      file.path(RESULTS_DIR, "resume_models_test.csv"),    row.names = FALSE)
write.csv(results_cpid_df, file.path(RESULTS_DIR, "resume_par_cpid_test.csv"),  row.names = FALSE)
cat("Saved resume_models_test.csv and resume_par_cpid_test.csv\n")

# ── 5. SPDE + RW2 ─────────────────────────────────────────────────────────────
df_map      <- st_as_sf(df_all, coords = c("longitude", "latitude"), crs = 4326)
df_map      <- st_transform(df_map, crs = 27700)
coords_m    <- st_coordinates(df_map)
df_all$x_m <- coords_m[, 1]
df_all$y_m <- coords_m[, 2]
coords_matrix_m <- cbind(df_all$x_m, df_all$y_m)
mesh        <- inla.mesh.2d(loc = coords_matrix_m, max.edge = c(200, 2000), cutoff = 100)

spde    <- inla.spde2.matern(mesh = mesh, alpha = 2)
A       <- inla.spde.make.A(mesh, loc = coords_matrix_m)
s.index <- inla.spde.make.index("spatial", n.spde = spde$n.spde)

stack_est <- inla.stack(
  data    = list(y = df_all$daily_sessions),
  A       = list(A, 1),
  effects = list(
    s.index,
    data.frame(
      time_index       = df_all$time_index,
      intercept        = 1,
      connector_type   = df_all$connector_type,
      weekday          = df_all$weekday,
      is_public_access = df_all$is_public_access,
      is_free          = df_all$is_free,
      temp_min         = df_all$temp_min,
      temp_max         = df_all$temp_max,
      temp_avg         = df_all$temp_avg,
      humidity_avg     = df_all$humidity_avg,
      wind_speed_avg   = df_all$wind_speed_avg,
      feels_like_avg   = df_all$feels_like_avg,
      temp_spline1     = df_all$temp_spline1,
      temp_spline2     = df_all$temp_spline2,
      temp_spline3     = df_all$temp_spline3
    )
  ),
  tag = "est"
)

formula_spde <- y ~ connector_type + weekday + is_public_access + is_free +
  temp_spline1 + temp_spline2 + temp_spline3 +
  f(spatial, model = spde) + f(time_index, model = "rw2")

result_spde <- inla(formula_spde, family = "poisson",
                    data              = inla.stack.data(stack_est),
                    control.predictor = list(A = inla.stack.A(stack_est), compute = TRUE),
                    control.compute   = list(dic = TRUE, waic = TRUE))
summary(result_spde)

index_est            <- inla.stack.index(stack_est, "est")$data
df_all$pred_spde_rw2 <- result_spde$summary.fitted.values$mean[index_est]
df_test_results      <- df_all %>% filter(predict == 1)
eval_test <- data.frame(
  RMSE = sqrt(mean((df_test_results$daily_sessions - df_test_results$pred_spde_rw2)^2)),
  MAE  = mean(abs(df_test_results$daily_sessions - df_test_results$pred_spde_rw2))
)
cat("--- TEST SET PERFORMANCE (SPDE) ---\n")
print(eval_test)

write.csv(df_all, file.path(RESULTS_DIR, "df_all_predictions_spde_rw2.csv"), row.names = FALSE)
cat("Saved df_all_predictions_spde_rw2.csv\n")

# ── 6. Compare ICAR vs SPDE & save for script 03 ─────────────────────────────
test_rows_logical <- df_all$predict == 1
df_test_clean     <- df_all %>% filter(predict == 1)
pred_icar         <- result_car_rw2$summary.fitted.values$mean[test_rows_logical]
pred_spde_all     <- result_spde$summary.fitted.values$mean[index_est]
pred_spde_test    <- pred_spde_all[test_rows_logical]

calculate_metrics <- function(y_true, y_pred, model_label, cpid_vector) {
  data.frame(CPID = cpid_vector, True = y_true, Pred = y_pred) %>%
    group_by(CPID) %>%
    summarise(
      MAE  = mean(abs(True - Pred)),
      RMSE = sqrt(mean((True - Pred)^2)),
      MAPE = mean(abs(True - Pred) / (True + 1) * 100),
      .groups = "drop"
    ) %>%
    mutate(Model = model_label)
}

metrics_icar       <- calculate_metrics(df_test_clean$daily_sessions, pred_icar,      "ICAR-RW2", df_test_clean$CPID)
metrics_spde       <- calculate_metrics(df_test_clean$daily_sessions, pred_spde_test, "SPDE-RW2", df_test_clean$CPID)
comparison_by_cpid <- bind_rows(metrics_icar, metrics_spde)

global_summary <- comparison_by_cpid %>%
  group_by(Model) %>%
  summarise(Avg_MAE = mean(MAE), Avg_RMSE = mean(RMSE), Avg_MAPE = mean(MAPE))
print(global_summary)

# Save 
write.csv(comparison_by_cpid, file.path(RESULTS_DIR, "comparison_by_cpid.csv"), row.names = FALSE)
write.csv(df_test_clean,      file.path(RESULTS_DIR, "df_test_clean.csv"),      row.names = FALSE)
cat("Saved comparison_by_cpid.csv and df_test_clean.csv\n")

