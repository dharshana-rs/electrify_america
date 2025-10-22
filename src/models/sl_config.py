from dataclasses import dataclass
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

@dataclass
class SLPaths:
    data_path: Path
    results_dir: Path
    models_dir: Path

def build_paths( data_path = "data/processed/final_data/FinalFeaturesDF.csv", results_dir = "src/results/supervised", models_dir = "models" ):
    p = SLPaths(
        data_path=Path(data_path),
        results_dir=Path(results_dir),
        models_dir=Path(models_dir)
    )
    p.results_dir.mkdir(parents=True, exist_ok=True)
    p.models_dir.mkdir(parents=True, exist_ok=True)
    return p

#print( build_paths() )