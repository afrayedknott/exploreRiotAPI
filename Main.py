import requests
import sched, time
import json
import pandas as pd
import numpy
from LeagueExpV4Handler import LeagueExpV4Handler
from RunModeEnum import RunMode

# TODO: look into using mypy to check argument types being used at compile time
# TODO: switch based on testing and sql use
# TODO: databased data querying

runmode = RunMode(RunMode.CSV_CSV_FULL)

match runmode:
            case RunMode.CSV_CSV_TESTING:
                print("")
            case RunMode.SQL_SQL_TESTING:
                print("")
            case RunMode.CSV_SQL_TESTING:
                print("")
            case RunMode.SQL_CSV_TESTING:
                print("")
            case RunMode.CSV_CSV_FULL:
                leagueExpV4Handler = LeagueExpV4Handler()
                leagueExpV4Handler.api_call_loop()
            case RunMode.SQL_SQL_FULL:
                print("")
            case RunMode.CSV_SQL_FULL:
                print("")
            case RunMode.SQL_CSV_FULL:
                print("")
            case _:
                print("")