# ==============================================================================
# config.R — Central configuration for the project
# All paths are relative to the project root.
# Edit only this file to adapt the project to a new machine.
# ==============================================================================

# ── Project root ─────────────────────────────
if (!require("here", quietly = TRUE)) install.packages("here")
library(here)

ROOT <- here()

# ── Input data paths ───────────────────────────────────────────────────────────
PATH_MASTER       <- here("data", "Master file scotland dataset", "master.csv")
PATH_SHAPEFILE    <- here("data", "shapefile for maps", "pub_commcnc.shp")
PATH_METEO        <- here("data", "Meteo dataset", "meteo.csv")
PATH_CPID_MAPPING <- here("data", "glasgow datasets", "cpid_zone_mapping.csv")
PATH_MODELING     <- here("data", "glasgow datasets", "df_final_modeling.csv")

# ── Output paths ──────────────────────────────────────────────────────────────
FIGURES_DIR       <- here("figures")
RESULTS_DIR       <- here("data", "glasgow datasets")

# Create output dirs if they don't exist
dir.create(FIGURES_DIR, showWarnings = FALSE, recursive = TRUE)
dir.create(RESULTS_DIR, showWarnings = FALSE, recursive = TRUE)

# ── Study area parameters ─────────────────────────────────────────────────────
GLASGOW_LON_MIN   <- -4.6
GLASGOW_LON_MAX   <- -4.0

EXCLUDED_CPIDS    <- c("62201", "62202", "62203", "62266", "62261", "50433", "62123")

SELECTED_ZONES    <- c("9", "15_32_23", "31_41", "3", "11", "29", "30",
                        "26", "7", "13", "28", "27", "2", "12", "4", "6", "16", "21")

# ── Model parameters ──────────────────────────────────────────────────────────
TRAIN_RATIO       <- 0.8
RANDOM_SEED       <- 123

cat("Config loaded. Project root:", ROOT, "\n")
