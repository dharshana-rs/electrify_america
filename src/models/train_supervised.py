import argparse
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from src.models.sl_config import build_paths
from src.models.sl_utils import split_features, build_preprocessor, get_model_spaces, cv_and_tune, export_feature_importance 

def parse_args():
    p = argparse.ArgumentParser(description="Train supervised EV demand models.")
    p.add_argument("--data", default="data/processed/final_data/FinalFeaturesDF.csv", help="Input features CSV")
    p.add_argument("--target", default="demand_score", help="Target column name")
    p.add_argument("--drop", nargs="*", default=["STATE_NAME","STATE","station_name","id"], help="Columns to drop from features")
    p.add_argument("--test_size", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="results/supervised", help="Results dir")
    p.add_argument("--models", default="models", help="Models dir")
    return p.parse_args()

def main():
    args = parse_args()
    print(args)
    paths = build_paths(args.data, results_dir=args.out, models_dir=args.models)

    print(f"Loading data: {paths.data_path}")
    df = pd.read_csv(paths.data_path)
    assert args.target in df.columns, f"Target '{args.target}' not found in columns."

    # Split features
    X, y, num_cols, cat_cols = split_features(df, args.target, drop_cols=args.drop)
    print(f"Features: {len(num_cols)} numeric, {len(cat_cols)} categorical")

    # Train/test split for final reporting 
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed
    )

    preprocessor = build_preprocessor(num_cols, cat_cols)
    model_spaces = get_model_spaces()

    all_cv_rows = []
    best_models = {}

    for key, space in model_spaces.items():
        print(f"\nTuning model: {key}")
        grid, cv_summary = cv_and_tune(Xtr, ytr, preprocessor, key, space, cv_splits=5, n_jobs=-1)
        cv_summary.to_csv(paths.results_dir / f"cv_{key}.csv", index=False)
        all_cv_rows.append(cv_summary.head(5))
        best_models[key] = grid.best_estimator_
        # Save model
        joblib.dump(grid.best_estimator_, paths.models_dir / f"{key}_best.joblib")
        print(f"best params: {grid.best_params_}")

        export_feature_importance(
            fitted_pipeline=grid.best_estimator_,
            X=Xtr, y=ytr,
            out_path=str(paths.results_dir / f"feat_importance_{key}.csv")
        )

    rows = []
    for key, pipe in best_models.items():
        y_pred = pipe.predict(Xte)
        rmse = ((yte - y_pred) ** 2).mean() ** 0.5
        mae  = (yte - y_pred).abs().mean()
        # avoid division by zero
        y_bar = yte.mean()
        ss_res = ((yte - y_pred) ** 2).sum()
        ss_tot = ((yte - y_bar) ** 2).sum()
        r2 = 1 - ss_res/ss_tot if ss_tot != 0 else float("nan")
        rows.append({"model": key, "rmse_test": rmse, "mae_test": mae, "r2_test": r2})

    test_table = pd.DataFrame(rows).sort_values("rmse_test")
    test_table.to_csv(paths.results_dir / "test_summary.csv", index=False)
    print("\nTest summary:")
    print(test_table.to_string(index=False))

if __name__ == "__main__":
    main()