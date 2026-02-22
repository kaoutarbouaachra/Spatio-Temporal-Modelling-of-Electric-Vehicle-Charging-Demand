# INLA version 13-02-2026
# ==============================================================================
# PROJECT: SPATIO-TEMPORAL MODELLING OF EV CHARGING DEMAND
# OBJECTIVE: Applying Latent Gaussian Models (INLA)
# ==============================================================================
# ------------------------------------------------------------------------------
# 0. ENVIRONMENT SETUP
# ------------------------------------------------------------------------------
# Configuration for high-performance computing with INLA
options(timeout = 600)
set.seed(123)
pkgs <- c("dplyr", "ggplot2", "spdep", "igraph", "splines", "fields", 
          "reshape2", "viridis", "ggpubr", "sf","zoo")
new_pkgs <- pkgs[!(pkgs %in% installed.packages()[,"Package"])]
if(length(new_pkgs)) install.packages(new_pkgs, dependencies = TRUE)
if (!require("INLA", quietly = TRUE)) {
  install.packages("INLA", repos = c(getOption("repos"), 
                                     INLA = "https://inla.r-inla-download.org/R/stable"), dep = TRUE)
}
invisible(lapply(c("INLA", pkgs), library, character.only = TRUE))
viridisBlue <- "#31688E"
# ------------------------------------------------------------------------------
# 1. DATA PREPROCESSING FOR INLA
# ------------------------------------------------------------------------------
#change this to the path where the folder you got from our git is located
path_file <- "SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/glasgow datasets/df_final_modeling.csv"
df_final_modeling <- read.csv(path_file, stringsAsFactors = FALSE)

df <- df_final_modeling  %>%
  dplyr::filter(!CPID %in% c("62201","62202","62203","62266","62261","50433","62123"))

df$Date <- as.Date(df$Date)
df <- df[order(df$Date), ]
df$time_index <- as.numeric(df$Date - min(df$Date)) + 1

df <- df %>%
  mutate(across(c(connector_type, weekday, YearMonth,is_public_access,
                  is_free, Month, CPID), as.factor))

df$id_cpid <- as.numeric(df$CPID)

# ------------------------------------------------------------------------------
# 2. TIME SERIES VISUALIZATION
# ------------------------------------------------------------------------------


# DISPERSION ANALYSIS: MOTIVATING LIKELIHOOD SELECTION
df_dispersion <- df %>%
  group_by(CPID) %>%
  summarise(
    mu = mean(daily_sessions),
    sigma2 = var(daily_sessions),
    ratio = sigma2 / mu,
    .groups = "drop"
  )
cpid_under <- df_dispersion %>% filter(ratio < 1) %>% slice_min(ratio, n = 3) %>% pull(CPID)
cpid_over  <- df_dispersion %>% filter(ratio > 1) %>% slice_max(ratio, n = 3) %>% pull(CPID)
theme<- theme_minimal(base_family = "serif") +
  theme(plot.title = element_text(face = "bold", size = 12),
        strip.text = element_text(face = "italic"))

# Plot A: Under-dispersed CPIDs
p1 <- df %>% 
  filter(CPID %in% cpid_under) %>%
  ggplot(aes(x = daily_sessions, fill = ..count..)) +
  geom_histogram(binwidth = 1, color = "white", linewidth = 0.2) +
  facet_wrap(~CPID, scales = "free_y") +
  scale_fill_viridis_c(option = "viridis", name = "Frequency") +
  theme +
  labs(title = "A. Observed Under-dispersion", 
       subtitle = "Variance < Mean: Indicative of steady-state demand",
       x = "Daily Charging Sessions", y = "Frequency")

# Plot B: Over-dispersed CPIDs
p2 <- df %>% 
  filter(CPID %in% cpid_over) %>%
  ggplot(aes(x = daily_sessions, fill = ..count..)) +
  geom_histogram(binwidth = 1, color = "white", linewidth = 0.2) +
  facet_wrap(~CPID, scales = "free_y") +
  scale_fill_viridis_c(option = "viridis", name = "Frequency") +
  theme +
  labs(title = "B. Observed Over-dispersion", 
       subtitle = "Variance > Mean: Higher volatility in urban charging hotspots",
       x = "Daily Charging Sessions", y = "Frequency")
combined_fig <- ggarrange(p1, p2, ncol = 1, nrow = 2, common.legend = FALSE)

ggsave(
  filename = "Figure_Exploratory_Dispersion.pdf", 
  plot = combined_fig, 
  device = "pdf",
  width = 5, height = 6, units = "in", dpi = 600
)

cat("EDA completed. Dispersion plots exported as high-resolution PDF.\n")

# ==============================================================================
# 3. SPATIO-TEMPORAL DATA PARTITIONING
# ==============================================================================
df <- df %>%
  mutate(across(c(connector_type, weekday, YearMonth, is_public_access,
                  is_free, Month, CPID), as.factor))

dates <- sort(unique(df$Date))
split_threshold <- dates[floor(0.8 * length(dates))]
cut_date <- dates[floor(0.8*length(dates))]
df_train <- df %>% filter(Date <= cut_date) %>% mutate(predict=0)
df_test  <- df %>% filter(Date >  cut_date) %>% mutate(predict=1)
df_all   <- bind_rows(df_train, df_test)
cat("Training period ends on:", as.character(split_threshold), "\n")

# ==============================================================================
# 4. ICAR + RW2
# ==============================================================================
df_all$id_cpid <- as.numeric(as.factor(as.character(df_all$CPID)))
# Graph construction
coords_cpid <- df_all %>% 
  distinct(id_cpid, longitude, latitude) %>% 
  arrange(id_cpid)
coords_matrix <- jitter(as.matrix(coords_cpid[, c("longitude","latitude")]), amount = 0.00001)
knn_nb <- knn2nb(knearneigh(coords_matrix, k=4), sym=TRUE)
g <- graph_from_adj_list(knn_nb)
comps <- components(g)
if (comps$no > 1) {
  for (i in 2:comps$no) {
    comp1 <- which(comps$membership == 1)
    compi <- which(comps$membership == i)
    coords1 <- coords_matrix[comp1, ]
    coordsi <- coords_matrix[compi, ]
    dmat <- as.matrix(dist(rbind(coords1, coordsi)))
    dsub <- dmat[1:length(comp1), (length(comp1)+1):nrow(dmat)]
    min_index <- which(dsub == min(dsub), arr.ind = TRUE)
    v1 <- comp1[min_index[1,1]]
    v2 <- compi[min_index[1,2]]
    g <- add_edges(g, c(v1, v2))
  }
}
g <- as_undirected(g, mode = "collapse")
mat_adj <- as_adjacency_matrix(g, sparse = FALSE)
mat_adj <- (mat_adj | t(mat_adj)) 
lw <- mat2listw(as.matrix(mat_adj), style = "B")
nb_connexe <- lw$neighbours
graph_file <- "cpid_graph.graph"
if(file.exists(graph_file)) file.remove(graph_file)
nb2INLA(graph_file, nb_connexe)
plot(nb_connexe, coords_matrix, col="black", main="Graphe de voisinage final")
# Model
temp_spline_mat <- bs(df_all$temp_avg, df=3)
df_all <- cbind(df_all,
                temp_spline1=temp_spline_mat[,1],
                temp_spline2=temp_spline_mat[,2],
                temp_spline3=temp_spline_mat[,3])
df_all <- df_all[, !duplicated(names(df_all))]

formula_car_rw2 <- daily_sessions ~ 
  connector_type + 
  weekday + 
  is_public_access + 
  is_free +
  temp_spline1 + 
  temp_spline2 + 
  temp_spline3 +
  humidity_avg +
  wind_speed_avg +
  feels_like_avg +
  f(id_cpid, model="besag", graph="cpid_graph_connexe.graph") +
  f(time_index, model="rw2")

result_car_rw2 <- inla(formula_car_rw2, family="poisson", data=df_all,
                       control.predictor=list(compute=TRUE),
                       control.compute=list(dic=TRUE, waic=TRUE))
summary(result_car_rw2)

# Visualization
spatial_effect <- result_car_rw2$summary.random$id_cpid %>%
  rename(id_cpid = ID) %>%
  left_join(coords_cpid, by = "id_cpid")

ggplot(spatial_effect, aes(x = longitude, y = latitude, color = mean)) +
  geom_point(size = 3.5, alpha = 0.9) +
  scale_color_viridis_c(option = "viridis", name = "Mean Effect") +
  theme_minimal(base_family = "serif") +
  labs(
    title = "Estimated Spatial Effect (ICAR)",
    subtitle = "Posterior mean of the ICAR spatial component",
    x = "Longitude",
    y = "Latitude"
  ) +
  theme(
    plot.title = element_text(face = "bold", size = 14),
    legend.position = "right"
  )

temporal_effect <- result_car_rw2$summary.random$time_index %>%
  mutate(Date = min(df_all$Date) + (ID - 1))

ggplot(temporal_effect, aes(x = Date, y = mean)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50", linewidth = 0.5) +
  geom_ribbon(aes(ymin = `0.025quant`, ymax = `0.975quant`), 
              fill = viridisBlue, alpha = 0.2) +
  geom_line(color = viridisBlue, linewidth = 1) +
  theme_minimal(base_family = "serif") +
  labs(
    title = "Estimated Temporal Effect (RW2)",
    subtitle = "Log-relative change in demand with 95% Credible Interval",
    x = "Date",
    y = "Temporal Effect (Log-scale)"
  ) +
  theme(
    plot.title = element_text(face = "bold", size = 14),
    panel.grid.minor = element_blank()
  )

# Evaluation
mae  <- mean(abs(df_all$daily_sessions - result_car_rw2$summary.fitted.values$mean))
rmse <- sqrt(mean((df_all$daily_sessions - result_car_rw2$summary.fitted.values$mean)^2))
cat("MAE:", mae, " - RMSE:", rmse, "\n")
evaluate_model_test <- function(result, df_all, df_train, df_test, model_name) {
  N_train <- nrow(df_train)
  pred_all <- result$summary.fitted.values
  df_all$pred_mean  <- pred_all$mean
  df_all$pred_lower <- pred_all$`0.025quant`
  df_all$pred_upper <- pred_all$`0.975quant`
  df_test_pred <- df_all[(N_train + 1):nrow(df_all), ]
  get_metrics <- function(df, set_name) {
    y_true <- df$daily_sessions
    y_pred <- df$pred_mean
    mae  <- mean(abs(y_pred - y_true))
    rmse <- sqrt(mean((y_pred - y_true)^2))
    data.frame(
      Model = model_name,
      Set   = set_name,
      MAE   = mae,
      RMSE  = rmse
    )
  }
  get_metrics(df_test_pred, "test")
}

results_list <- list()
results_list[[1]] <- evaluate_model_test(result_car_rw2, df_all, df_train, df_test, "icar_rw2")
results_df <- do.call(rbind, results_list)
print(results_df)
write.csv(results_df, "resume_models_test.csv", row.names = FALSE)

evaluate_par_cpid_test <- function(result, df_all, df_train, df_test, model_name) {
  N_train <- nrow(df_train)
  pred_all <- result$summary.fitted.values
  df_all$pred_mean  <- pred_all$mean
  df_all$pred_lower <- pred_all$`0.025quant`
  df_all$pred_upper <- pred_all$`0.975quant`
  df_test_pred <- df_all[(N_train + 1):nrow(df_all), ]
  df_test_pred %>%
    dplyr::group_by(CPID) %>%
    dplyr::summarise(
      MAE  = mean(abs(pred_mean - daily_sessions)),
      RMSE = sqrt(mean((pred_mean - daily_sessions)^2)),
      .groups = "drop"
    ) %>%
    dplyr::mutate(Model = model_name, Set = "test") %>%
    dplyr::select(Model, Set, CPID, MAE, RMSE)
}

results_cpid_list <- list()
results_cpid_list[[1]] <- evaluate_par_cpid_test(result_car_rw2, df_all, df_train, df_test, "icar_rw2")
results_cpid_df <- do.call(rbind, results_cpid_list)
head(results_cpid_df)
write.csv(results_cpid_df, "resume_par_cpid_test.csv", row.names = FALSE)
# ==============================================================================
# 4. SPDE + RW2
# ==============================================================================
# Mesh construction
df_map <- st_as_sf(df_all, coords = c("longitude", "latitude"), crs = 4326)
df_map <- st_transform(df_map, crs = 27700)
coords_m <- st_coordinates(df_map)
df_all$x_m <- coords_m[,1]
df_all$y_m <- coords_m[,2]
coords_matrix_m <- cbind(df_all$x_m, df_all$y_m)
mesh <- inla.mesh.2d(loc=coords_matrix_m, max.edge=c(200, 2000), cutoff=100)
plot(mesh, 
     main="Spatial Mesh (Glasgow) - Units: Meters", 
     edge.color = "grey70", 
     draw.segments = TRUE)
points(coords_matrix_m, 
       col = viridisBlue, 
       pch = 19, 
       cex = 0.6) 

# Model
spde <- inla.spde2.matern(mesh=mesh, alpha=2)
A <- inla.spde.make.A(mesh, loc=coords_matrix_m)
s.index <- inla.spde.make.index("spatial", n.spde=spde$n.spde)

stack_est <- inla.stack(
  data = list(y = df_all$daily_sessions),
  A = list(A, 1),
  effects = list(
    s.index, 
    data.frame(
      time_index     = df_all$time_index,
      intercept      = 1,
      connector_type   = df_all$connector_type,
      weekday          = df_all$weekday,
      is_public_access = df_all$is_public_access,
      is_free          = df_all$is_free,
      temp_min        = df_all$temp_min,
      temp_max        = df_all$temp_max,
      temp_avg        = df_all$temp_avg,
      humidity_avg    = df_all$humidity_avg,
      wind_speed_avg  = df_all$wind_speed_avg,
      feels_like_avg  = df_all$feels_like_avg,
      temp_spline1    = df_all$temp_spline1,
      temp_spline2    = df_all$temp_spline2,
      temp_spline3    = df_all$temp_spline3
    )
  ),
  tag = "est"
)

formula_spde <- y ~ connector_type + weekday + is_public_access + is_free +
  temp_spline1 + temp_spline2 + temp_spline3 +
  f(spatial, model=spde) + f(time_index, model="rw2")

result_spde <- inla(formula_spde,
                    family = "poisson",
                    data = inla.stack.data(stack_est),
                    control.predictor = list(A = inla.stack.A(stack_est), compute = TRUE),
                    control.compute = list(dic = TRUE, waic = TRUE))
summary(result_spde)

spde_result <- inla.spde2.result(result_spde, "spatial", spde)
cat("\n--- POSTERIOR SPATIAL RANGE RESULTS (METERS) ---\n")
range_m <- inla.zmarginal(spde_result$marginals.range.nominal[[1]])
print(range_m)

# Validation of SPDE Range against Empirical Station Density
coords_unique <- df_all %>% 
  distinct(id_cpid, x_m, y_m) %>% 
  arrange(id_cpid) %>%
  dplyr::select(x_m, y_m)
dist_matrix <- dist(coords_unique)
dist_vector <- as.vector(dist_matrix)
nearest_dist <- apply(as.matrix(dist_matrix), 1, function(x) min(x[x > 0]))
dist_matrix <- as.matrix(dist(coords_unique))
diag(dist_matrix) <- Inf
nearest_dist <- apply(dist_matrix, 1, min)
cat("\n--- NEAREST NEIGHBOR DISTANCE STATISTICS (METERS) ---\n")
print(summary(nearest_dist))
cat("Mean distance to nearest neighbor:", mean(nearest_dist), "\n")

stats_text <- capture.output({
  cat("--- NEAREST NEIGHBOR DISTANCE STATISTICS (METERS) ---\n")
  print(summary(nearest_dist))
  cat("Mean distance to nearest neighbor:", mean(nearest_dist), "\n")
})

writeLines(stats_text, "spatial_distance_stats.txt")

# Visualization
evaluator <- fmesher::fm_evaluator(mesh, dims = c(200, 200))
field_proj <- fmesher::fm_evaluate(evaluator, result_spde$summary.random$spatial$mean)
fields::image.plot(evaluator$x, evaluator$y, field_proj,
                   col = viridis::viridis(100),
                   main = "Posterior Mean of the Spatial Field (SPDE)",
                   xlab = "Easting (m)", 
                   ylab = "Northing (m)")

points(coords_matrix_m, pch = 20, col = "black", cex = 0.5)

field_df <- expand.grid(x = evaluator$x, y = evaluator$y)
field_df$value <- as.vector(field_proj)
coords_df <- as.data.frame(coords_matrix_m)
names(coords_df) <- c("x", "y")

ggplot() +
  geom_raster(data = field_df, aes(x = x, y = y, fill = value)) +
  scale_fill_viridis_c(option = "viridis", na.value = "transparent") +
  geom_point(data = coords_df, aes(x = x, y = y), 
             color = "black", alpha = 0.6, size = 1.4) +
  coord_fixed() +
  labs(title = "Latent Spatial Demand (SPDE Mean)", 
       subtitle = "Glasgow EV Network - Meters (BNG)",
       x = "Easting (m)", 
       y = "Northing (m)", 
       fill = "Effect") +
  theme_minimal()

temporal_effect <- result_spde$summary.random$time_index %>%
  mutate(Date = min(df_all$Date) + (ID - 1))

ggplot(temporal_effect, aes(x = Date, y = mean)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "grey50", linewidth = 0.5) +
  geom_ribbon(aes(ymin = `0.025quant`, ymax = `0.975quant`), 
              fill = viridisBlue, alpha = 0.2) +
  geom_line(color = viridisBlue, linewidth = 1) +
  labs(
    title = "Estimated Temporal Trend (RW2)",
    subtitle = "Log-relative change in EV charging demand over time",
    x = "Date",
    y = "Temporal Effect (Log-scale)",
    caption = "Shaded area represents the 95% Bayesian credible interval"
  ) +
  theme_minimal(base_family = "serif") + # Use serif font for an academic look
  theme(
    plot.title = element_text(face = "bold", size = 14),
    axis.title = element_text(size = 11),
    panel.grid.minor = element_blank()
  )

# Evaluation
index_est <- inla.stack.index(stack_est, "est")$data
df_all$pred_spde_rw2 <- result_spde$summary.fitted.values$mean[index_est]
df_test_results <- df_all %>% filter(predict == 1)

evaluate_model <- function(y_true, y_pred) {
  data.frame(
    RMSE = sqrt(mean((y_true - y_pred)^2, na.rm = TRUE)),
    MAE  = mean(abs(y_true - y_pred), na.rm = TRUE)
  )
}
eval_test <- evaluate_model(df_test_results$daily_sessions, 
                            df_test_results$pred_spde_rw2)
print("--- TEST SET PERFORMANCE (SPDE) ---")
print(eval_test)
write.csv(df_all, "df_all_predictions_spde_rw2.csv", row.names = FALSE)

# ==============================================================================
# 4. SPDE + RW2 vs ICAR + RW2
# ==============================================================================

test_rows_logical <- df_all$predict == 1
df_test_clean <- df_all %>% filter(predict == 1)
pred_icar <- result_car_rw2$summary.fitted.values$mean[test_rows_logical]
obs_index <- inla.stack.index(stack_est, "est")$data
pred_spde_all <- result_spde$summary.fitted.values$mean[obs_index]
pred_spde_test <- pred_spde_all[test_rows_logical]
calculate_metrics <- function(y_true, y_pred, model_label, cpid_vector) {
  data.frame(
    CPID = cpid_vector,
    True = y_true,
    Pred = y_pred
  ) %>%
    group_by(CPID) %>%
    summarise(
      MAE  = mean(abs(True - Pred)),
      RMSE = sqrt(mean((True - Pred)^2)),
      MAPE = mean(abs(True - Pred) / (True + 1) * 100),
      .groups = "drop"
    ) %>%
    mutate(Model = model_label)
}
metrics_icar <- calculate_metrics(df_test_clean$daily_sessions, pred_icar, "ICAR-RW2", df_test_clean$CPID)
metrics_spde <- calculate_metrics(df_test_clean$daily_sessions, pred_spde_test, "SPDE-RW2", df_test_clean$CPID)
comparison_by_cpid <- bind_rows(metrics_icar, metrics_spde)
print(head(comparison_by_cpid))
global_summary <- comparison_by_cpid %>%
  group_by(Model) %>%
  summarise(
    Avg_MAE  = mean(MAE),
    Avg_RMSE = mean(RMSE),
    Avg_MAPE = mean(MAPE)
  )
print(global_summary)

# Visualization
library(ggnewscale)
evaluator <- fmesher::fm_evaluator(mesh, dims = c(200, 200))
field_proj <- fmesher::fm_evaluate(evaluator, result_spde$summary.random$spatial$mean)
field_df <- expand.grid(x = evaluator$x, y = evaluator$y)
field_df$value <- as.vector(field_proj)
spatial_effect <- result_car_rw2$summary.random$id_cpid %>%
  rename(id_cpid = ID) %>%
  left_join(distinct(df_all, id_cpid, x_m, y_m), by = "id_cpid")
ggplot() +
  geom_raster(data = field_df, aes(x = x, y = y, fill = value)) +
  scale_fill_viridis_c(option = "viridis", name = "SPDE (Field)", na.value = "transparent") +
  new_scale_color() +
  geom_point(data = spatial_effect, aes(x = x_m, y = y_m, color = mean), 
             size = 2.5, stroke = 1, shape = 21, fill = "white") +
  scale_color_viridis_c(option = "viridis", name = "ICAR (Points)") +
  coord_fixed() +
  labs(
    title = "Spatial Overlay: SPDE vs ICAR",
    subtitle = "Coordinated in British National Grid (m)",
    x = "Easting (m)",
    y = "Northing (m)"
  ) +
  theme_minimal(base_family = "serif")


