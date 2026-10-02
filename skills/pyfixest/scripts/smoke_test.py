"""Exercise the installed PyFixest API using synthetic, non-research data."""

import importlib.metadata
import json

import numpy as np
import pandas as pd
import pyfixest as pf


def main():
    rng = np.random.default_rng(20261002)
    n_units, n_periods = 60, 10
    n = n_units * n_periods
    df = pd.DataFrame({
        "id": np.repeat(np.arange(n_units), n_periods),
        "time": np.tile(np.arange(1, n_periods + 1), n_units),
        "x": rng.normal(size=n),
        "z": rng.normal(size=n),
    })
    alpha = rng.normal(size=n_units)[df["id"].to_numpy()]
    error = rng.normal(size=n)
    df["y"] = 1.5 * df["x"] + alpha + 0.2 * df["time"] + error
    dummies = np.column_stack([
        np.ones(n),
        pd.get_dummies(df["id"], drop_first=True, dtype=float).to_numpy(),
        pd.get_dummies(df["time"], drop_first=True, dtype=float).to_numpy(),
    ])
    X = np.column_stack([dummies, df["x"]])
    beta = np.linalg.lstsq(X, df["y"].to_numpy(), rcond=None)[0]
    fit = pf.feols("y ~ x | id + time", data=df, vcov={"CRV1": "id"},
                   ssc=pf.ssc(k_adj=False, G_adj=False))
    np.testing.assert_allclose(fit.coef().loc["x"], beta[-1], rtol=1e-7, atol=1e-8)

    residuals = df["y"].to_numpy() - X @ beta
    scores = np.stack([
        X[df["id"].to_numpy() == unit].T @ residuals[df["id"].to_numpy() == unit]
        for unit in range(n_units)
    ])
    bread = np.linalg.inv(X.T @ X)
    covariance = bread @ (scores.T @ scores) @ bread
    se_reference = np.sqrt(covariance[-1, -1])
    np.testing.assert_allclose(fit.se().loc["x"], se_reference, rtol=1e-6, atol=1e-8)

    v = rng.normal(size=n)
    df["endog"] = 0.8 * df["z"] + 0.3 * df["x"] + v
    df["y_iv"] = 1.5 * df["endog"] + 0.4 * df["x"] + alpha + 0.2 * df["time"] + 0.7 * v + error
    X_iv = np.column_stack([dummies, df["x"], df["endog"]])
    Z = np.column_stack([dummies, df["x"], df["z"]])
    X_hat = Z @ np.linalg.lstsq(Z, X_iv, rcond=None)[0]
    beta_iv = np.linalg.solve(X_hat.T @ X_iv, X_hat.T @ df["y_iv"].to_numpy())
    iv = pf.feols("y_iv ~ x | id + time | endog ~ z", data=df,
                  vcov={"CRV1": "id"})
    np.testing.assert_allclose(iv.coef().loc["endog"], beta_iv[-1], rtol=1e-7, atol=1e-8)

    cohorts = np.repeat([0, 4, 6], n_units // 3)
    df["g"] = cohorts[df["id"].to_numpy()]
    df["treat"] = ((df["g"] > 0) & (df["time"] >= df["g"])).astype(int)
    df["y_did"] = alpha + 0.2 * df["time"] + 2 * df["treat"] + rng.normal(scale=0.1, size=n)
    did = pf.did2s(data=df, yname="y_did", first_stage="~0 | id + time",
                   second_stage="~treat", treatment="treat", cluster="id")
    did_effect = float(did.coef().loc["treat"])
    if abs(did_effect - 2) > 0.25 or not np.isfinite(did.se().loc["treat"]):
        raise AssertionError("Synthetic DiD did not recover the known effect with finite inference")

    # Confirm inference is extracted from each model, rather than a mixed table cache.
    for model in (fit, iv, did):
        table = model.tidy()
        if table.empty or not np.isfinite(model.pvalue().to_numpy()).all():
            raise AssertionError("Missing model output or invalid p-values")

    print(json.dumps({
        "pyfixest_version": importlib.metadata.version("pyfixest"),
        "synthetic_N": n,
        "fe_coefficient": float(fit.coef().loc["x"]),
        "fe_cluster_se": float(fit.se().loc["x"]),
        "iv_coefficient": float(iv.coef().loc["endog"]),
        "did_effect_true": 2.0,
        "did_effect_estimated": did_effect,
        "checks_passed": ["FE coefficient", "cluster covariance", "IV coefficient", "DiD effect", "model output"],
    }, indent=2))


if __name__ == "__main__":
    main()
