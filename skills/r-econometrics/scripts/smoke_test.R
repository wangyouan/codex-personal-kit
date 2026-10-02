required <- c("fixest", "did", "rdrobust", "rddensity")
missing_packages <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages)) {
  stop("Missing packages: ", paste(missing_packages, collapse = ", "))
}

set.seed(20261002)
n_units <- 120L
n_periods <- 8L
df <- expand.grid(time = seq_len(n_periods), id = seq_len(n_units))
n <- nrow(df)
df$x <- rnorm(n)
df$z <- rnorm(n)
v <- rnorm(n)
df$endog <- 0.8 * df$z + 0.3 * df$x + v
df$y <- 1.5 * df$endog + 0.4 * df$x + rnorm(n_units)[df$id] +
  0.2 * df$time + 0.7 * v + rnorm(n, sd = 0.3)
stopifnot(!anyDuplicated(df[c("id", "time")]))

fe <- fixest::feols(y ~ endog + x | id + time, data = df, vcov = ~ id)
dummy_ols <- lm(y ~ endog + x + factor(id) + factor(time), data = df)
stopifnot(abs(coef(fe)["endog"] - coef(dummy_ols)["endog"]) < 1e-8)

iv <- fixest::feols(y ~ x | id + time | endog ~ z, data = df, vcov = ~ id)
X <- model.matrix(~ x + factor(id) + factor(time) + endog, data = df)
Z <- model.matrix(~ x + factor(id) + factor(time) + z, data = df)
X_hat <- qr.fitted(qr(Z), X)
iv_reference <- solve(crossprod(X_hat, X), crossprod(X_hat, df$y))
stopifnot(abs(unname(coef(iv)[1]) - iv_reference[ncol(X), 1]) < 1e-8)

cohorts <- rep(c(0L, 4L, 6L), each = n_units / 3L)
df$g <- cohorts[df$id]
df$treated <- as.integer(df$g > 0 & df$time >= df$g)
df$y_did <- rnorm(n_units)[df$id] + 0.2 * df$time +
  2 * df$treated + rnorm(n, sd = 0.2)
att <- did::att_gt(yname = "y_did", tname = "time", idname = "id", gname = "g",
                   xformla = ~ 1, data = df, control_group = "nevertreated",
                   bstrap = TRUE, biters = 199, cband = TRUE)
overall <- did::aggte(att, type = "simple")
stopifnot(abs(overall$overall.att - 2) < 0.3)

running <- runif(2000, -1, 1)
y_rd <- 1 + running + 2 * (running >= 0) + rnorm(2000, sd = 0.15)
rd <- rdrobust::rdrobust(y_rd, running, c = 0, p = 1)
density <- rddensity::rddensity(running, c = 0)
stopifnot(abs(rd$coef[1] - 2) < 0.4, all(is.finite(rd$ci)),
          !is.null(density$test))

print(data.frame(check = c("FE", "IV", "DiD", "RDD"),
                 estimate = c(coef(fe)["endog"], coef(iv)[1],
                              overall$overall.att, rd$coef[1])))
print(vapply(required, function(pkg) as.character(packageVersion(pkg)), character(1)))
sessionInfo()
cat("All synthetic R checks passed.\n")
