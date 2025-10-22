from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, KFold, cross_validate
from sklearn.metrics import make_scorer, mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


'''
def split_features( df, target_col, drop_cols = None ) :
    drop_cols = drop_cols or []
    df = df.copy()
    y = df[target_col]
    X = df.drop(columns=[target_col])

    # infer column types
    num_cols = X.select_dtypes(include=["int", "int32", "int64", "float", "float32", "float64"]).columns.tolist()
    return X, y, num_cols
'''

def split_features( df, target_col, drop_cols = None ) :
    drop_cols = drop_cols or []
    df = df.copy()
    y = df[target_col]
    #X = df.drop(columns=[target_col])
    X = df.drop(columns=[target_col] + drop_cols, errors="ignore")

    # infer column types
    num_cols = X.select_dtypes(include=["int", "int32", "int64", "float", "float32", "float64"]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]
    return X, y, num_cols, cat_cols

def build_preprocessor(num_cols, cat_cols):
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            #("num", RobustScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=True
    )


#complexity_settings = [
#    {"n_estimators": 10, "max_depth": 5},
#    {"n_estimators": 100, "max_depth": 10},
#    {"n_estimators": 500, "max_depth": 20},
#]




def get_model_spaces():
    models = {
        "ridge": ( Ridge(random_state=42), {"model__alpha": [0.1, 1.0, 3.0, 10.0]} ),

        #rf = RandomForestRegressor(
        #    n_estimators=params["n_estimators"],
        #    max_depth=params["max_depth"],
        #    n_jobs=-1,
        #    random_state=42
        #)

        
        "rf": (
            RandomForestRegressor(random_state=42, n_jobs=-1),
            {
                "model__n_estimators": [200, 400],
                "model__max_depth": [None, 10, 20],
                "model__min_samples_leaf": [1, 3, 5],
            }
        ),
        "gbr": (
            GradientBoostingRegressor(random_state=42),
            {
                "model__n_estimators": [200, 400],
                "model__learning_rate": [0.05, 0.1],
                "model__max_depth": [2, 3],
            }
        ),
    }
    return models

def scorer_dict() -> Dict[str, callable]:
    return {
        "rmse": make_scorer(lambda y_true, y_pred: mean_squared_error(y_true, y_pred, squared=False)),
        "mae": make_scorer(mean_absolute_error),
        "r2": make_scorer(r2_score),
    }

def cv_and_tune( X, y, preprocessor, model_key, model_space, cv_splits = 5, n_jobs = -1, refit_metric = "rmse" ):
    model, param_grid = model_space
    pipe = Pipeline(steps=[("prep", preprocessor), ("model", model)])

    #grid_search = GridSearchCV(
    #    estimator=rfreg_pipeline,
    #    param_grid=param_grid,
    #    cv=cv,
    #    scoring=scoring,
    #    n_jobs=-1,  # Use all processors
    #    verbose=1,  # Verbose to get feedback during fitting
    #)
    

    grid = GridSearchCV(
        estimator=pipe,
        param_grid=param_grid,
        scoring=scorer_dict(),
        refit=refit_metric,  
        cv=KFold(n_splits=cv_splits, shuffle=True, random_state=42),
        n_jobs=n_jobs,
        verbose=1,
        return_train_score=False
    )
    grid.fit(X, y)
    df = pd.DataFrame(grid.cv_results_)
    summary = df[[
        "rank_test_rmse", "mean_test_rmse", "std_test_rmse",
        "mean_test_mae", "std_test_mae",
        "mean_test_r2", "std_test_r2",
        "params"
    ]].sort_values("rank_test_rmse")
    summary.insert(0, "model", model_key)
    return grid, summary

def export_feature_importance( fitted_pipeline, X, y, out_path ):
    r = permutation_importance( fitted_pipeline, X, y, n_repeats=10, random_state=42, n_jobs=-1 )
    prep = fitted_pipeline.named_steps["prep"]
    feat_names = []
    if hasattr(prep, "get_feature_names_out"):
        #feat_names = prep.get_feature_names_out()
        #try:
        #    feat_names = prep.get_feature_names_out()
        #except ValueError:
        #    feat_names = prep.get_feature_names_out()
        #    feat_names = pd.Index(feat_names).duplicated(keep=False).astype(str) + "_" + feat_names
        
        feat_names = prep.get_feature_names_out()
        feat_names = pd.Index(feat_names).map(lambda x: x.replace(" ", "_")).to_list()
        feat_names = pd.Index(feat_names + [f"dup_{i}" for i in range(len(feat_names))]).unique().to_list()
    else:
        feat_names = X.columns

    imp = (
        pd.DataFrame({
            "feature": feat_names,
            "mean_importance": r.importances_mean,
            "std_importance": r.importances_std
        })
        .sort_values("mean_importance", ascending=False)
    )
    imp.to_csv(out_path, index=False)