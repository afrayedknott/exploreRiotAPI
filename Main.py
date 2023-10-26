import requests
import sched, time
import json
import pandas as pd
import numpy
from LeagueExpV4Handler import LeagueExpV4Handler
from ParamTypeEnum import ParamType

# TODO: look into using mypy to check argument types being used at compile time

league_handler = LeagueExpV4Handler()
league_handler.api_call_loop()