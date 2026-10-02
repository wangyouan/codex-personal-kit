args <- commandArgs(trailingOnly = TRUE)
repo <- if (length(args)) args[1] else "https://cloud.r-project.org"
options(repos = c(CRAN = repo), timeout = 600)
minor <- paste(R.version$major, strsplit(R.version$minor, ".", fixed = TRUE)[[1]][1], sep = ".")
lib <- Sys.getenv("R_LIBS_USER")
if (!nzchar(lib)) lib <- file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", minor)
dir.create(lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))
groups <- list(
  data = c("data.table", "dplyr", "tidyr", "readr", "haven", "readxl", "openxlsx", "stringr", "lubridate", "janitor"),
  econometrics = c("fixest", "did", "rdrobust", "rddensity", "ivreg", "sandwich", "lmtest", "plm"),
  output = c("ggplot2", "modelsummary", "broom", "flextable", "officer"),
  reproducibility = c("renv", "here", "jsonlite", "httr2")
)
pkgs <- unique(unlist(groups, use.names = FALSE))
available <- available.packages(type = "binary")
unavailable <- setdiff(pkgs, rownames(available))
if (length(unavailable)) stop("No CRAN binary available: ", paste(unavailable, collapse = ", "))
missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) install.packages(missing, lib = lib, type = "binary", dependencies = NA)
failed <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
if (length(failed)) stop("Installation incomplete: ", paste(failed, collapse = ", "))
versions <- data.frame(package = pkgs, version = vapply(pkgs, function(p) as.character(packageVersion(p)), character(1)))
print(versions, row.names = FALSE)
if (length(args) >= 2) write.csv(versions, args[2], row.names = FALSE)
cat("All", length(pkgs), "requested research packages loaded successfully.\n")
