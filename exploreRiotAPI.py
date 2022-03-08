import requests
import sched, time
import json
import pandas
import numpy
from APIDataAggregator import APIDataAggregator

# API key

with open("api_key.txt") as api_key_txt:
    api_key_str = str(api_key_txt.read())

print(api_key_str)

# API parameters

queues = ["RANKED_SOLO_5x5", "RANKED_TFT", "RANKED_FLEX_SR", "RANKED_FLEX_TT"]
tiers = ["CHALLENGER", "GRANDMASTER", "MASTER", "DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"]
divisions = ["I", "II", "III", "IV"]

# data pulling

### set up API data aggregator obj

apida = APIDataAggregator("https://na1.api.riotgames.com/lol/league-exp/v4/entries/", api_key_str)
apida.add_query_param_list(queues)
apida.add_query_param_list(tiers)
apida.add_query_param_list(divisions)
apida.convert_query_param_list_to_df()
apida.clear_query_param_list()