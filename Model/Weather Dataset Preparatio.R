# ==============================================================================
# PROJECT: SPATIO-TEMPORAL MODELLING OF EV CHARGING DEMAND
# SCRIPT: Data Integration (Sessions & Meteorology)
# PURPOSE: Preparing the final modeling dataset for Glasgow
# ==============================================================================

# 1. LOAD LIBRARIES
packages <- c("tidyverse", "lubridate", "corrplot", "sf", "dplyr")
invisible(lapply(packages, library, character.only = TRUE))

# 2. SESSION DATA CLEANING -----------------------------------------------------

# Preparing the core session dataset for Glasgow City
#change this to the path where the folder you got from our git is located

path_file_mapping <- "SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/glasgow datasets/cpid_zone_mapping.csv"
path_file_master  <- "SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/Master file scotland dataset/master.csv"

cpid_zone_mapping <- read.csv(path_file_mapping, stringsAsFactors = FALSE)
master <- read.csv(path_file_master, stringsAsFactors = FALSE)

path_file_weather<-"SPATIO-TEMPORAL MODELLING OF ELECTRIC VEHICLE CHARGING DEMAND/datasets/Meteo dataset/meteo.csv"
meteo<-read.csv(path_file_weather, stringsAsFactors = FALSE)

  
  
df <- master

df <- df %>%
  
  filter(tolower(local_authority) == "glasgow city") %>%
  
  mutate(CPID = as.character(CPID)) %>%
  
  filter(!is.na(longitude) & !is.na(latitude))  


df_subset <- df %>% dplyr::select(longitude, latitude, CPID, Connector_Type, Date, weekday, YearMonth, `public/prive`, Amount)

df_clean <- df_subset %>%
  
  rename(
    
    connector_type = Connector_Type,
    
    public_prive = `public/prive`
    
  ) %>%
  
  mutate(
    
    Month = month(Date, label = TRUE, abbr = TRUE),
    
    gratuit = Amount == 0
    
  ) %>%
  
  group_by(CPID, Date) %>%
  
  mutate(nombre_sessions_jour = n()) %>%
  
  summarise(
    
    longitude = first(longitude),
    
    latitude = first(latitude),
    
    connector_type = first(connector_type),
    
    weekday = first(weekday),
    
    YearMonth = first(YearMonth),
    
    public_prive = first(public_prive),
    
    gratuit = first(gratuit),
    
    Month = first(Month),
    
    nombre_sessions_jour = first(nombre_sessions_jour),
    
    .groups = "drop"
    
  ) %>%
  
  drop_na(longitude, latitude, connector_type, CPID, Date)


df_clean  <- df_clean %>%filter(longitude >= -4.6, longitude <= -4.0)

df_clean <- df_clean %>%
  mutate(CPID = as.character(CPID)) %>%
  left_join(
    cpid_zone_mapping %>%
      mutate(CPID = as.character(CPID)) %>%
      dplyr::select(CPID, zone_centrale),
    by = "CPID"
  )

# 3. SPATIAL FILTERING BY STUDY ZONES -----------------------------------------

# We join the charging points with the previously defined target study zones

selected_zones <- c("9", "15_32_23", "31_41", "3", "11", "29", "30", "26", "7", "13", "28", "27", "2", "12", "4", "6", "16", "21")

df_clean_filtered <- df_clean %>%
  
  filter(zone_centrale %in% selected_zones)


# 4. WEATHER DATA PROCESSING

meteo_daily <- meteo %>%
  mutate(
    across(c(tmpf, dwpf, relh, sknt, feel), as.numeric),
    Date = as.Date(valid)
  ) %>%
  group_by(Date) %>%
  summarise(
    temp_avg = mean(tmpf, na.rm = TRUE),
    temp_min = min(tmpf, na.rm = TRUE),
    temp_max = max(tmpf, na.rm = TRUE),
    humidity_avg = mean(relh, na.rm = TRUE),
    wind_speed_avg = mean(sknt, na.rm = TRUE),
    feels_like_avg = mean(feel, na.rm = TRUE),
    .groups = "drop"
  )

# 5. DATA MERGING & FINAL STANDARDIZATION
df_final_modeling <- df_clean_filtered %>%
  
  left_join(meteo_daily, by = "Date") %>%
  
  drop_na(temp_avg) %>%
  
  rename(
    is_public_access = public_prive,
    is_free = gratuit,
    daily_sessions = nombre_sessions_jour
  ) %>%
  
  mutate(
    is_public_access = ifelse(tolower(is_public_access) == "public", "Public", "Private"),
    is_free = ifelse(is_free == TRUE | tolower(is_free) == "yes", "Yes", "No"),
    is_public_access = factor(is_public_access),
    is_free = factor(is_free),
    zone_centrale = factor(zone_centrale),
    weekday = factor(weekday),
    Month = factor(Month)
  )


# 6. INSPECTION & EXPORT
glimpse(df_final_modeling)
summary(df_final_modeling)

write.csv(df_final_modeling,
          "C:/Users/Lenovo/Downloads/df_final_modeling.csv",
          row.names = FALSE)
# 7. CORRELATION ANALYSIS
cor_data <- df_final_modeling %>%
  dplyr::select(daily_sessions, temp_avg, humidity_avg, wind_speed_avg) %>%
  cor(use = "complete.obs")

corrplot(cor_data, method = "color", type = "upper", 
         addCoef.col = "black", tl.col = "black", 
         title = "Correlation: Weather vs. Charging Demand", 
         mar = c(0,0,1,0))

print("Final modeling dataset exported successfully.")
