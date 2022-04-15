import requests
import sched, time
import json
import pandas as pd
import numpy
from APIDataAggregator import APIDataAggregator

# API key

with open("api_key.txt") as api_key_txt:
    api_key_str = str(api_key_txt.read())

print(api_key_str)

# API parameters
# I removed ["CHALLENGER", "GRANDMASTER", "MASTER"] because it was mostly returning status code 400

queues = ["RANKED_SOLO_5x5", "RANKED_TFT", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]
tiers = ["DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
divisions = ["I", "II", "III", "IV"]

# data pulling

apida = APIDataAggregator("https://na1.api.riotgames.com/lol/league-exp/v4/entries/", api_key_str)
apida.add_query_param_list(queues)
apida.add_query_param_list(tiers)
apida.add_query_param_list(divisions)
apida.convert_query_param_list_to_df()
apida.data_transfer()
apida.query_param_dashb.to_csv('check.csv')
apida.clear_query_param_list()