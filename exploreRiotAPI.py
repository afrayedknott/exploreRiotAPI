import requests
import sched, time
import json
import pandas as pd
import numpy
from APIDataAggregator import APIDataAggregator
import SqlHandler

# testing

sql_testing = False

# API key

with open("api_key.txt") as api_key_txt:
    api_key_str = str(api_key_txt.read())

print(api_key_str)

# API parameters
# I removed ["CHALLENGER", "GRANDMASTER", "MASTER"] because it was mostly returning status code 400

queues = ["RANKED_SOLO_5x5", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]
tiers = ["DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
divisions = ["I", "II", "III", "IV"]
pages = ["1"]

# data pulling

## settings
apida = APIDataAggregator()
apida.set_api_key(api_key_str)
apida.set_base_api_url('https://na1.api.riotgames.com/lol/league/v4/entries')

sqlh = SqlHandler.SqlHandler('sql_credentials.json')
sqlh.establish_connection()

if sql_testing:
    apida.data_payload = pd.read_csv('content.csv')
else:
    ## url params

    ### with code as is, it's important to add path params before query params
    apida.add_path_params('queue', queues)
    apida.add_path_params('tier', tiers)
    apida.add_path_params('division', divisions)
    apida.add_query_params('page', pages)
    apida.add_query_params('api_key', [apida.api_key])

    ## data transfers and checks
    apida.complete_api_call()
    apida.clear_path_params()
    apida.clear_query_params()

    apida.data_payload.to_csv('content.csv')

#sqlh.upsert_df(apida.data_payload, 'test')

