pip install -r requirements.txt

cp .env.example .env
# edit .env with your CENSUS_API_KEY

python -m src.main_data_build
