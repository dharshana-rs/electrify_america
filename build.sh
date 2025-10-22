pip install -r requirements.txt

cp .env.example .env
# edit .env with your CENSUS_API_KEY

python -m src.data.main_data_build
