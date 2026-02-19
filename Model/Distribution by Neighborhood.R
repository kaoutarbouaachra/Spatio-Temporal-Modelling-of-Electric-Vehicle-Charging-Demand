# ==============================================================================
# PROJECT: SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND
# SCRIPT: Spatial Pre-processing and District-Level Zoning
# PURPOSE: STUDY AREA SELECTION & SPATIAL ZONING
# ==============================================================================

# ---------------------------
# 1. Environment Setup
# ---------------------------

libs <- c(
  "tidyverse", "sf", "viridis", "ggpubr", "lubridate", 
  "spdep", "mgcv", "MASS", "forecast", "tscount", 
  "xgboost", "randomForest", "Metrics", "AER"
)

# Automated installation and loading
missing_libs <- libs[!(libs %in% installed.packages()[,"Package"])]
if(length(missing_libs)) install.packages(missing_libs, dependencies = TRUE)
invisible(lapply(libs, library, character.only = TRUE))

# ---------------------------
# 2. Data Cleaning & Preparation
# ---------------------------

#change this to the path where the folder you got from our git is located
path_file_master  <- "SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/Master file scotland dataset/master.csv"
master <- read.csv(path_file_master, stringsAsFactors = FALSE)

df_clean <- master %>%
  # Filter for study area (Glasgow City) and valid coordinates
  filter(tolower(local_authority) == "glasgow city") %>%
  filter(!is.na(longitude) & !is.na(latitude)) %>%
  mutate(CPID = as.character(CPID)) %>%
  rename(connector_type = Connector_Type, public_prive = `public/prive`) %>%
  mutate(
    Month = month(Date, label = TRUE, abbr = TRUE),
    is_free = (Amount == 0)
  ) %>%
  # Daily aggregation per Charge Point (CPID)
  group_by(CPID, Date) %>%
  summarise(
    longitude = first(longitude),
    latitude = first(latitude),
    connector_type = first(connector_type),
    weekday = first(weekday),
    YearMonth = first(YearMonth),
    public_prive = first(public_prive),
    is_free = first(is_free),
    Month = first(Month),
    daily_sessions = n(),
    .groups = "drop"
  ) %>%
  
  # Geographic bounding box for Glasgow core
  filter(longitude >= -4.6, longitude <= -4.0)

# ---------------------------
# 3. Spatial Processing
# ---------------------------

# Load Shapefile (Community Councils)

#change this to the path where the folder you got from our git is located
path_shapefile <- "SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/shapefile for maps/pub_commcnc.shp"
scotland_cc <- st_read(path_shapefile)


# Filter for Glasgow Districts
glasgow_cc <- scotland_cc %>%
  filter(grepl("Glasgow City", local_auth, ignore.case = TRUE))

# Convert Charging Points to Spatial Object (SF)
# EPSG 4326 is WGS84; Transform to match the shapefile's CRS
points_sf <- df_clean %>%
  st_as_sf(coords = c("longitude", "latitude"), crs = 4326) %>%
  st_transform(st_crs(glasgow_cc))

# Spatial Join: Assign each session/point to a Community Council (District)
sessions_geo <- st_join(points_sf, glasgow_cc, join = st_within)

# ---------------------------
# 4. District-Level Metrics
# ---------------------------

# 4.1. Count unique CPIDs per District
cpid_per_district <- sessions_geo %>%
  st_drop_geometry() %>%
  group_by(cc_name) %>%
  summarise(n_cpid = n_distinct(CPID), .groups = "drop")

# 4.2. Count total sessions per District
sessions_per_district <- sessions_geo %>%
  st_drop_geometry() %>%
  group_by(cc_name) %>%
  summarise(total_sessions = n(), .groups = "drop") %>%
  arrange(desc(total_sessions)) %>%
  mutate(district_rank = row_number())

# Merge stats back to the spatial map
glasgow_map <- glasgow_cc %>%
  left_join(cpid_per_district, by = "cc_name") %>%
  left_join(sessions_per_district, by = "cc_name") %>%
  mutate(
    across(c(n_cpid, total_sessions), ~replace_na(., 0)),
    session_cat = case_when(
      total_sessions == 0 ~ "0 sessions",
      total_sessions < 1000 ~ "< 1,000",
      TRUE ~ "≥ 1,000"
    ),
    session_cat = factor(session_cat, levels = c("0 sessions", "< 1,000", "≥ 1,000"))
  )

# ---------------------------
# 5. Visuals
# ---------------------------

# Figure: Total Sessions per District with ID Numbering
cols <- viridis::viridis(3, option = "D") 

# 2. Plot with manual color reassignment
ggplot(glasgow_map) +
  geom_sf(aes(fill = session_cat), color = "white", size = 0.2) +
  geom_sf_text(aes(label = district_rank), size = 2, color = "black", check_overlap = TRUE) +
  scale_fill_manual(
    values = c(
      "0 sessions" = "grey90",    
      "< 1,000"    = cols[3],    
      "≥ 1,000"    = cols[2]     
    )
  ) +
  labs(
    title = "EV Charging Intensity by Glasgow District",
    subtitle = "Aggregated session counts by Community Council boundaries",
    fill = "Total Sessions"
  ) +
  theme_minimal() +
  theme(
    legend.position = "right", 
    text = element_text(family = "serif")
  )

# ---------------------------
# 6. Strategic Zoning 
# ---------------------------

# Define target zones for modeling (high-density or specific interest)
target_ids <- c("9", "15_32_23", "31_41", "3", "11", "29", "30", "26", "7", "13", "28", "27", "2", "12", "4", "6", "16", "21")

# Create custom clusters/zones to ensure statistical power (>2 CPIDs per zone)
glasgow_benchmarking <- glasgow_map %>%
  mutate(
    zone_id = case_when(
      district_rank %in% c(31, 41) ~ "31_41",
      district_rank %in% c(15, 32, 23) ~ "15_32_23",
      TRUE ~ as.character(district_rank)
    ),
    study_area = ifelse(zone_id %in% target_ids, "Selected for Study", "Other")
  )

# Map of Final Study Zones
ggplot(glasgow_benchmarking) +
  geom_sf(aes(fill = study_area), color = "white") +
  geom_sf_text(aes(label = zone_id), size = 2.5) +
  scale_fill_manual(values = c("Selected for Study" =cols[2], "Other" = "grey90")) +
  labs(title = "Defined Study Zones for Forecast Benchmarking", fill = "Zone Type") +
  theme_minimal()



