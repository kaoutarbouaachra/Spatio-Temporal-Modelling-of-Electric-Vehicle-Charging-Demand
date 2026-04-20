# ==============================================================================
# 04_weather_preparation.R  (runs after 01 — needs cpid_zone_mapping.csv)
# PROJECT: Spatio-Temporal Modelling of EV Charging Demand
# PURPOSE: Session + weather data integration → final modeling dataset
# Run after: 01_spatial_distribution.R
# Outputs:  data/glasgow_datasets/df_final_modeling.csv
# ==============================================================================

source("config.R")

# ── 1. Libraries ──────────────────────────────────────────────────────────────
packages <- c("tidyverse", "lubridate", "corrplot", "sf", "dplyr")
missing_pkgs <- packages[!(packages %in% installed.packages()[, "Package"])]
if (length(missing_pkgs)) install.packages(missing_pkgs, dependencies = TRUE)
invisible(lapply(packages, library, character.only = TRUE))

# ── 2. Load data ──────────────────────────────────────────────────────────────
cat("Loading data...\n")
master            <- read.csv(PATH_MASTER,       stringsAsFactors = FALSE)
cpid_zone_mapping <- read.csv(PATH_CPID_MAPPING, stringsAsFactors = FALSE)
meteo             <- read.csv(PATH_METEO,         stringsAsFactors = FALSE)

# ── 3. Session data cleaning ──────────────────────────────────────────────────
df <- master %>%
  filter(tolower(local_authority) == "glasgow city") %>%
  mutate(CPID = as.character(CPID)) %>%
  filter(!is.na(longitude) & !is.na(latitude)) %>%
  dplyr::select(longitude, latitude, CPID, Connector_Type,
                Date, weekday, YearMonth, `public/prive`, Amount) %>%
  rename(connector_type = Connector_Type,
         public_prive   = `public/prive`) %>%
  mutate(Month  = month(Date, label = TRUE, abbr = TRUE),
         gratuit = Amount == 0) %>%
  group_by(CPID, Date) %>%
  mutate(nombre_sessions_jour = n()) %>%
  summarise(
    longitude            = first(longitude),
    latitude             = first(latitude),
    connector_type       = first(connector_type),
    weekday              = first(weekday),
    YearMonth            = first(YearMonth),
    public_prive         = first(public_prive),
    gratuit              = first(gratuit),
    Month                = first(Month),
    nombre_sessions_jour = first(nombre_sessions_jour),
    .groups = "drop"
  ) %>%
  drop_na(longitude, latitude, connector_type, CPID, Date) %>%
  filter(longitude >= GLASGOW_LON_MIN, longitude <= GLASGOW_LON_MAX)

# ── 4. Attach zone mapping ────────────────────────────────────────────────────
df <- df %>%
  mutate(CPID = as.character(CPID)) %>%
  left_join(
    cpid_zone_mapping %>%
      mutate(CPID = as.character(CPID)) %>%
      dplyr::select(CPID, zone_centrale),
    by = "CPID"
  ) %>%
  filter(zone_centrale %in% SELECTED_ZONES)

# ── 5. Weather data processing ────────────────────────────────────────────────
cat("Processing weather data...\n")
meteo_daily <- meteo %>%
  mutate(across(c(tmpf, dwpf, relh, sknt, feel), as.numeric),
         Date = as.Date(valid)) %>%
  group_by(Date) %>%
  summarise(
    temp_avg       = mean(tmpf, na.rm = TRUE),
    temp_min       = min(tmpf,  na.rm = TRUE),
    temp_max       = max(tmpf,  na.rm = TRUE),
    humidity_avg   = mean(relh, na.rm = TRUE),
    wind_speed_avg = mean(sknt, na.rm = TRUE),
    feels_like_avg = mean(feel, na.rm = TRUE),
    .groups = "drop"
  )

# ── 6. Merge & standardize ────────────────────────────────────────────────────
df_final_modeling <- df %>%
  left_join(meteo_daily, by = "Date") %>%
  drop_na(temp_avg) %>%
  rename(
    is_public_access = public_prive,
    is_free          = gratuit,
    daily_sessions   = nombre_sessions_jour
  ) %>%
  mutate(
    is_public_access = ifelse(tolower(is_public_access) == "public", "Public", "Private"),
    is_free          = ifelse(is_free == TRUE | tolower(is_free) == "yes", "Yes", "No"),
    is_public_access = factor(is_public_access),
    is_free          = factor(is_free),
    zone_centrale    = factor(zone_centrale),
    weekday          = factor(weekday),
    Month            = factor(Month)
  )

# ── 7. Inspect ────────────────────────────────────────────────────────────────
glimpse(df_final_modeling)
summary(df_final_modeling)

# ── 8. Export ─────────────────────────────────────────────────────────────────
# Fixed: was "C:/Users/Lenovo/Downloads/df_final_modeling.csv"
output_path <- file.path(RESULTS_DIR, "df_final_modeling.csv")
write.csv(df_final_modeling, output_path, row.names = FALSE)
cat("Saved df_final_modeling.csv →", output_path, "\n")

# ── 9. Correlation analysis ───────────────────────────────────────────────────
cor_data <- df_final_modeling %>%
  dplyr::select(daily_sessions, temp_avg, humidity_avg, wind_speed_avg) %>%
  cor(use = "complete.obs")

pdf(file.path(FIGURES_DIR, "correlation_weather_demand.pdf"), width = 7, height = 6)
corrplot(cor_data, method = "color", type = "upper",
         addCoef.col = "black", tl.col = "black",
         title = "Correlation: Weather vs. Charging Demand",
         mar = c(0, 0, 1, 0))
dev.off()
cat("Saved correlation_weather_demand.pdf\n")
