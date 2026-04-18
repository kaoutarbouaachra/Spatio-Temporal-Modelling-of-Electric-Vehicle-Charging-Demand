# ==============================================================================
# run_all.R — Master pipeline script
# PROJECT: Spatio-Temporal Modelling of EV Charging Demand
#
# Runs the full pipeline in order:
#   01 → spatial distribution & zone mapping
#   04 → weather + session data integration
#   02 → INLA model fitting
#   03 → benchmarking vs ML
#
# Usage (from project root in R):
#   source("run_all.R")
#
# Or from the terminal:
#   Rscript run_all.R
# ==============================================================================

source("config.R")

run_step <- function(script, label) {
  cat("\n", strrep("=", 60), "\n", sep = "")
  cat(" ", label, "\n", sep = "")
  cat(strrep("=", 60), "\n")
  t0 <- proc.time()
  source(script, local = FALSE)
  elapsed <- (proc.time() - t0)["elapsed"]
  cat("\n Done in", round(elapsed / 60, 1), "min\n")
}

run_step("models/01_spatial_distribution.R", "STEP 1 — Spatial distribution & zoning")
run_step("models/04_weather_preparation.R",  "STEP 2 — Weather data integration")
run_step("models/02_inla_model.R",           "STEP 3 — INLA model fitting")
run_step("models/03_local_vs_inla.R",        "STEP 4 — ML benchmarking")

cat("\n", strrep("=", 60), "\n")
cat(" Full pipeline completed!\n")
cat(" Figures saved in: ", FIGURES_DIR, "\n")
cat(" Results saved in: ", RESULTS_DIR, "\n")
cat(strrep("=", 60), "\n")
