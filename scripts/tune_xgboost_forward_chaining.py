from __future__ import annotations

import json
import time
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / 'data' / 'frix_enriched_dataset_v3.csv'
FEATURE_FILE = ROOT / 'models' / 'milestone24_core_pretransaction_features.json'
RESULTS_FILE = ROOT / 'models' / 'milestone24_xgb_tuning_results.csv'
BEST_FILE = ROOT / 'models' / 'milestone24_xgb_best_configs.json'
SUMMARY_FILE = ROOT / 'docs' / 'milestone24_xgb_tuning_summary.md'
TARGET = 'isFraud'
RANDOM_STATE = 42
STABILITY_PENALTY = 0.25
N_ESTIMATORS = 350

BASE = {'amount', 'oldbalanceOrg', 'oldbalanceDest', 'is_high_risk_type'}
GRAPH = {
    'possible_mule_receiver_v2', 'sender_out_degree_prior',
    'receiver_in_degree_prior', 'receiver_total_amount_prior',
    'receiver_avg_amount_prior', 'receiver_high_risk_txn_count_prior',
    'funnel_alert_v2',
}
FOLDS = [(1, 0.50, 0.60), (2, 0.60, 0.70), (3, 0.70, 0.80)]
GRID = {
    'max_depth': [4, 6, 8],
    'learning_rate': [0.03, 0.05],
    'reg_lambda': [1.0, 5.0],
}


def load_data():
    print('Loading dataset...')
    df = pd.read_csv(DATA_FILE)
    core = json.loads(FEATURE_FILE.read_text(encoding='utf-8'))
    source = [f for f in core if not f.startswith('type_')]
    x = df[source].copy()
    if 'type' in x.columns:
        x = pd.get_dummies(x, columns=['type'], prefix='type', dtype=np.int8)
    for feature in core:
        if feature not in x.columns:
            x[feature] = 0
    x = x[core]
    y = df[TARGET].astype(np.int8)
    print(f'Rows: {len(df):,}')
    print('Latest 20% remains excluded from tuning.')
    return x, y, core


def feature_sets(core):
    types = {f for f in core if f.startswith('type_')}
    return {
        'base_only': sorted(BASE | types),
        'base_plus_graph': sorted(BASE | GRAPH | types),
    }


def parameter_configs():
    keys = list(GRID)
    return [dict(zip(keys, values)) for values in product(*(GRID[k] for k in keys))]


def make_model(y_train, params):
    positives = int((y_train == 1).sum())
    negatives = int((y_train == 0).sum())
    return XGBClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=params['max_depth'],
        learning_rate=params['learning_rate'],
        min_child_weight=2,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=params['reg_lambda'],
        objective='binary:logistic',
        eval_metric='aucpr',
        scale_pos_weight=negatives / positives,
        tree_method='hist',
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )


def run_config(name, selected, config_id, params, x, y):
    scores = []
    elapsed = 0.0
    total = len(x)
    print(f"\n{name} config {config_id}: depth={params['max_depth']}, lr={params['learning_rate']}, lambda={params['reg_lambda']}")
    for fold, train_fraction, valid_fraction in FOLDS:
        train_end = int(total * train_fraction)
        valid_end = int(total * valid_fraction)
        x_train, y_train = x.iloc[:train_end][selected], y.iloc[:train_end]
        x_valid, y_valid = x.iloc[train_end:valid_end][selected], y.iloc[train_end:valid_end]
        model = make_model(y_train, params)
        start = time.perf_counter()
        model.fit(x_train, y_train)
        elapsed += time.perf_counter() - start
        probability = model.predict_proba(x_valid)[:, 1]
        score = average_precision_score(y_valid, probability)
        scores.append(float(score))
        print(f'  Fold {fold}: PR-AUC={score:.6f}')
    mean = float(np.mean(scores))
    std = float(np.std(scores, ddof=1))
    stability = mean - STABILITY_PENALTY * std
    print(f'  Mean={mean:.6f}, Std={std:.6f}, Stability={stability:.6f}')
    return {
        'feature_set': name,
        'config_id': config_id,
        'feature_count': len(selected),
        **params,
        'n_estimators': N_ESTIMATORS,
        'fold_1_pr_auc': scores[0],
        'fold_2_pr_auc': scores[1],
        'fold_3_pr_auc': scores[2],
        'mean_pr_auc': mean,
        'std_pr_auc': std,
        'min_pr_auc': min(scores),
        'max_pr_auc': max(scores),
        'stability_score': stability,
        'training_seconds': round(elapsed, 2),
    }


def main():
    x, y, core = load_data()
    sets = feature_sets(core)
    configs = parameter_configs()
    print(f'Configurations per feature set: {len(configs)}')
    print(f'Total model fits: {len(configs) * len(sets) * len(FOLDS)}')
    rows = []
    for name, selected in sets.items():
        for config_id, params in enumerate(configs, start=1):
            rows.append(run_config(name, selected, config_id, params, x, y))
    results = pd.DataFrame(rows).sort_values(
        ['feature_set', 'stability_score', 'mean_pr_auc'],
        ascending=[True, False, False],
    )
    results.to_csv(RESULTS_FILE, index=False)
    best = {}
    for name in sets:
        row = results[results.feature_set == name].iloc[0].to_dict()
        best[name] = {k: (v.item() if hasattr(v, 'item') else v) for k, v in row.items()}
    BEST_FILE.write_text(json.dumps(best, indent=2), encoding='utf-8')
    lines = [
        '# Milestone 24H — XGBoost Hyperparameter Tuning', '',
        'Tuning used only three forward-chaining development folds. The latest 20% was excluded.', '',
        f'Selection score: `mean PR-AUC - {STABILITY_PENALTY} × PR-AUC standard deviation`', '',
        '| Feature set | Mean PR-AUC | Std PR-AUC | Stability | Depth | Learning rate | Lambda |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for name, row in best.items():
        lines.append(
            f"| {name} | {row['mean_pr_auc']:.6f} | {row['std_pr_auc']:.6f} | "
            f"{row['stability_score']:.6f} | {row['max_depth']} | "
            f"{row['learning_rate']} | {row['reg_lambda']} |"
        )
    lines += ['', 'No final-holdout rows or classification thresholds were used during tuning.']
    SUMMARY_FILE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'\nSaved tuning results: {RESULTS_FILE}')
    print(f'Saved best configs: {BEST_FILE}')
    print(f'Saved summary: {SUMMARY_FILE}')
    print('\nSelected configurations:')
    for name, row in best.items():
        print(
            f"{name}: depth={row['max_depth']}, lr={row['learning_rate']}, "
            f"lambda={row['reg_lambda']}, mean PR-AUC={row['mean_pr_auc']:.6f}, "
            f"std={row['std_pr_auc']:.6f}, stability={row['stability_score']:.6f}"
        )


if __name__ == '__main__':
    main()
