# ==============================================================================
# 01_spatial_distribution.R
# PROJECT: Spatio-Temporal Modelling of EV Charging Demand
# PURPOSE: Study area selection & spatial zoning for Glasgow
# Run after: —  (first script in the pipeline)
# Outputs:  data/glasgow_datasets/cpid_zone_mapping.csv
#           figures/map_glasgow_sessions.pdf
#           figures/map_study_zones.pdf
# ==============================================================================

source("config.R")

# ── 1. Libraries ──────────────────────────────────────────────────────────────
libs <- c("tidyverse", "sf", "viridis", "ggpubr", "lubridate",
          "spdep", "mgcv", "MASS", "forecast", "tscount",
          "xgboost", "randomForest", "Metrics", "AER")

missing_libs <- libs[!(libs %in% installed.packages()[, "Package"])]
if (length(missing_libs)) install.packages(missing_libs, dependencies = TRUE)
invisible(lapply(libs, library, character.only = TRUE))

# ── 2. Data loading & cleaning ────────────────────────────────────────────────
cat("Loading master dataset...\n")
master <- read.csv(PATH_MASTER, stringsAsFactors = FALSE)

df_clean <- master %>%
  filter(tolower(local_authority) == "glasgow city") %>%
  filter(!is.na(longitude) & !is.na(latitude)) %>%
  mutate(CPID = as.character(CPID)) %>%
  rename(connector_type = Connector_Type,
         public_prive = `public/prive`) %>%
  mutate(Month  = month(Date, label = TRUE, abbr = TRUE),
         is_free = (Amount == 0)) %>%
  group_by(CPID, Date) %>%
  summarise(
    longitude      = first(longitude),
    latitude       = first(latitude),
    connector_type = first(connector_type),
    weekday        = first(weekday),
    YearMonth      = first(YearMonth),
    public_prive   = first(public_prive),
    is_free        = first(is_free),
    Month          = first(Month),
    daily_sessions = n(),
    .groups = "drop"
  ) %>%
  filter(longitude >= GLASGOW_LON_MIN, longitude <= GLASGOW_LON_MAX)

# ── 3. Spatial processing ─────────────────────────────────────────────────────
cat("Loading shapefile...\n")
scotland_cc <- st_read(PATH_SHAPEFILE)

glasgow_cc <- scotland_cc %>%
  filter(grepl("Glasgow City", local_auth, ignore.case = TRUE))

points_sf <- df_clean %>%
  st_as_sf(coords = c("longitude", "latitude"), crs = 4326) %>%
  st_transform(st_crs(glasgow_cc))

sessions_geo <- st_join(points_sf, glasgow_cc, join = st_within)

# ── 4. District-level metrics ─────────────────────────────────────────────────
cpid_per_district <- sessions_geo %>%
  st_drop_geometry() %>%
  group_by(cc_name) %>%
  summarise(n_cpid = n_distinct(CPID), .groups = "drop")

sessions_per_district <- sessions_geo %>%
  st_drop_geometry() %>%
  group_by(cc_name) %>%
  summarise(total_sessions = n(), .groups = "drop") %>%
  arrange(desc(total_sessions)) %>%
  mutate(district_rank = row_number())

glasgow_map <- glasgow_cc %>%
  left_join(cpid_per_district,     by = "cc_name") %>%
  left_join(sessions_per_district, by = "cc_name") %>%
  mutate(
    across(c(n_cpid, total_sessions), ~replace_na(., 0)),
    session_cat = case_when(
      total_sessions == 0     ~ "0 sessions",
      total_sessions < 1000   ~ "< 1,000",
      TRUE                    ~ "≥ 1,000"
    ),
    session_cat = factor(session_cat, levels = c("0 sessions", "< 1,000", "≥ 1,000"))
  )

# ── 5. Strategic zoning ───────────────────────────────────────────────────────
glasgow_benchmarking <- glasgow_map %>%
  mutate(
    zone_id = case_when(
      district_rank %in% c(31, 41)     ~ "31_41",
      district_rank %in% c(15, 32, 23) ~ "15_32_23",
      TRUE                             ~ as.character(district_rank)
    ),
    study_area = ifelse(zone_id %in% SELECTED_ZONES, "Selected for Study", "Other")
  )

# ── 6. Export cpid → zone mapping (needed by script 04) ──────────────────────
cpid_zone_mapping <- sessions_geo %>%
  st_drop_geometry() %>%
  left_join(sessions_per_district, by = "cc_name") %>%
  mutate(
    zone_centrale = case_when(
      district_rank %in% c(31, 41)     ~ "31_41",
      district_rank %in% c(15, 32, 23) ~ "15_32_23",
      TRUE                             ~ as.character(district_rank)
    )
  ) %>%
  dplyr::select(CPID, zone_centrale) %>%
  distinct()

write.csv(cpid_zone_mapping,
          file.path(RESULTS_DIR, "cpid_zone_mapping.csv"),
          row.names = FALSE)
cat("✓ Saved cpid_zone_mapping.csv\n")

# ── 7. Figures ────────────────────────────────────────────────────────────────
cols <- viridis::viridis(3, option = "D")

p_sessions <- ggplot(glasgow_map) +
  geom_sf(aes(fill = session_cat), color = "white", size = 0.2) +
  geom_sf_text(aes(label = district_rank), size = 2, color = "black", check_overlap = TRUE) +
  scale_fill_manual(values = c("0 sessions" = "grey90",
                               "< 1,000"    = cols[3],
                               "≥ 1,000"    = cols[2])) +
  labs(title    = "EV Charging Intensity by Glasgow District",
       subtitle = "Aggregated session counts by Community Council boundaries",
       fill     = "Total Sessions") +
  theme_minimal() +
  theme(legend.position = "right", text = element_text(family = "serif"))

ggsave(file.path(FIGURES_DIR, "map_glasgow_sessions.pdf"),
       p_sessions, width = 8, height = 7)
cat("✓ Saved map_glasgow_sessions.pdf\n")

p_zones <- ggplot(glasgow_benchmarking) +
  geom_sf(aes(fill = study_area), color = "white") +
  geom_sf_text(aes(label = zone_id), size = 2.5) +
  scale_fill_manual(values = c("Selected for Study" = cols[2], "Other" = "grey90")) +
  labs(title = "Defined Study Zones for Forecast Benchmarking", fill = "Zone Type") +
  theme_minimal()

ggsave(file.path(FIGURES_DIR, "map_study_zones.pdf"),
       p_zones, width = 8, height = 7)
cat("✓ Saved map_study_zones.pdf\n")

cat("\n✅ Script 01 completed.\n")
