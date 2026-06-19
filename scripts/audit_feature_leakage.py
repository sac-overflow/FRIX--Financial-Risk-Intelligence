from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "frix_enriched_dataset_v3.csv"
REGISTRY = ROOT / "docs" / "frix_feature_availability_registry.csv"
FEATURES = ROOT / "models" / "milestone24_strict_pretransaction_features.json"
REPORT = ROOT / "models" / "milestone24_leakage_audit_report.csv"
SUMMARY = ROOT / "docs" / "milestone24_leakage_audit_summary.md"
TARGET = "isFraud"

FORBIDDEN = {
    "isFraud","isFlaggedFraud","nameOrig","nameDest",
    "sender_txn_count","receiver_txn_count","risk_score_v1",
    "rule_alert_v1","is_large_amount","newbalanceOrig",
    "newbalanceDest","origin_balance_error","dest_balance_error",
    "sender_emptied_account",
}

SUSPICIOUS_TOKENS = {
    "newbalance","balance_error","emptied_account",
    "chargeback","reversal","settlement",
}

def add(rows, check, feature, severity, status, details):
    rows.append({
        "check": check,
        "feature": feature,
        "severity": severity,
        "status": status,
        "details": details,
    })

def main():
    for path in (DATA, REGISTRY, FEATURES):
        if not path.exists():
            raise FileNotFoundError(path)

    print("Loading dataset and registry...")
    df = pd.read_csv(DATA)
    registry = pd.read_csv(REGISTRY)
    strict = json.loads(FEATURES.read_text(encoding="utf-8"))

    rows = []
    registered = set(registry["feature"])
    dataset_cols = set(df.columns)
    lookup = registry.set_index("feature")

    missing_registry = sorted(dataset_cols - registered)
    if missing_registry:
        for feature in missing_registry:
            add(rows, "registry_coverage", feature, "high", "fail",
                "Dataset feature missing from registry.")
    else:
        add(rows, "registry_coverage", "", "none", "pass",
            "Every dataset feature is registered.")

    for feature in strict:
        base = "type" if feature.startswith("type_") else feature
        if base not in lookup.index:
            add(rows, "strict_permission", feature, "high", "fail",
                "Strict model feature is not registered.")
            continue

        status = str(lookup.loc[base, "strict_model_status"]).lower().strip()
        if status == "no":
            add(rows, "strict_permission", feature, "critical", "fail",
                "Forbidden feature appears in strict model.")
        elif status == "review":
            add(rows, "strict_permission", feature, "medium", "review",
                "Feature requires manual review or ablation.")
        else:
            add(rows, "strict_permission", feature, "none", "pass",
                "Feature approved for strict model.")

    present_forbidden = sorted(set(strict) & FORBIDDEN)
    if present_forbidden:
        for feature in present_forbidden:
            add(rows, "explicit_forbidden", feature, "critical", "fail",
                "Known forbidden feature appears in strict model.")
    else:
        add(rows, "explicit_forbidden", "", "none", "pass",
            "No explicitly forbidden features found.")

    suspicious = []
    for feature in strict:
        hits = [t for t in SUSPICIOUS_TOKENS if t in feature.lower()]
        if hits:
            suspicious.append((feature, hits))
    if suspicious:
        for feature, hits in suspicious:
            add(rows, "name_pattern", feature, "critical", "fail",
                "Suspicious token(s): " + ", ".join(sorted(hits)))
    else:
        add(rows, "name_pattern", "", "none", "pass",
            "No suspicious post-transaction names found.")

    numeric = [f for f in strict if f in df.columns and pd.api.types.is_numeric_dtype(df[f])]
    for feature in numeric:
        if df[feature].nunique(dropna=False) <= 1:
            add(rows, "constant_feature", feature, "medium", "review",
                "Feature is constant.")

    for feature in numeric:
        if df[feature].nunique(dropna=False) <= 1:
            continue
        corr = df[feature].corr(df[TARGET])
        if pd.isna(corr):
            continue
        ac = abs(float(corr))
        if ac >= 0.95:
            add(rows, "target_correlation", feature, "critical", "fail",
                f"Absolute Pearson correlation with target is {ac:.6f}.")
        elif ac >= 0.50:
            add(rows, "target_correlation", feature, "medium", "review",
                f"Absolute Pearson correlation with target is {ac:.6f}.")

    report = pd.DataFrame(rows)
    order = {"critical":0,"high":1,"medium":2,"low":3,"none":4}
    report["_order"] = report["severity"].map(order)
    report = report.sort_values(["_order","status","check","feature"]).drop(columns="_order")
    report.to_csv(REPORT, index=False)

    failures = int((report["status"] == "fail").sum())
    reviews = int((report["status"] == "review").sum())

    lines = [
        "# Milestone 24C — FRIX Leakage Audit Summary",
        "",
        f"- Confirmed failures: {failures}",
        f"- Review items: {reviews}",
        "",
        "## Conclusion",
        "",
        "PASS" if failures == 0 else "FAIL",
        "",
        "Automated checks do not replace manual feature review.",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Saved: {REPORT}")
    print(f"Saved: {SUMMARY}")
    print(f"Confirmed failures: {failures}")
    print(f"Review items: {reviews}")

    if failures:
        raise SystemExit("Leakage audit failed.")
    print("Leakage audit passed.")

if __name__ == "__main__":
    main()
