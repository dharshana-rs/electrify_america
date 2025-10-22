pip install -r requirements.txt

python -m src.models.train_supervised \
  --data data/processed/final_data/FinalFeaturesDF.csv \
  --target demand_score \
  --drop STATE_NAME STATE id station_name


python -m src.models.train_supervised \
  --data data/processed/final_data/FinalFeaturesDF.csv \
  --target ENERGY_KWH