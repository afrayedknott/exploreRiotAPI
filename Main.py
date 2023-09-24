import requests
import sched, time
import json
import pandas as pd
import numpy
from APIDataAggregator import APIDataAggregator
from ParamTypeEnum import ParamType
import datetime

riot_apida = APIDataAggregator("config.json")
riot_apida.assemble_dashboard("league-exp-v4")

# I decided that Main.py should handle the looping 
# until I figure out a good way to continue an interrupted loop
# based on parameters
int_iter_count = sum(riot_apida.int_iter_param_col_i)
full_page_record_count = 205
current_dashboard = pd.DataFrame(columns = list(riot_apida.base_dashboard.columns))
curr_date = datetime.datetime.now()

match int_iter_count:
    case 0:
        for index in riot_apida.base_dashboard.index:
            curr_dashboard_row = riot_apida.base_dashboard.iloc[index:(index+1)]
            curr_url = curr_dashboard_row['full_url'][index]
            record_count = full_page_record_count
            while record_count >= full_page_record_count:
                riot_apida.call_api(curr_url)
                record_count = len(riot_apida.data_payload)
                curr_dashboard_row['full_url'] = curr_url
                current_dashboard = pd.concat([current_dashboard, curr_dashboard_row])
                riot_apida.csv_upsave(curr_dashboard_row,
                                      "temp_dashboard"
                                      + str(int(curr_date.strftime("%Y%m%d%H%M%S")))
                                      + ".csv")
                riot_apida.csv_upsave(riot_apida.data_payload,
                                      "temp_data_payload" 
                                      + str(int(curr_date.strftime("%Y%m%d%H%M%S"))) 
                                      + ".csv")
                
                # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard

    case 1:
        for index in riot_apida.base_dashboard.index:
            curr_dashboard_row = riot_apida.base_dashboard.iloc[index:(index+1)]
            curr_url = curr_dashboard_row['full_url'][index]
            first_int_iter = 1
            record_count = full_page_record_count
            while record_count >= full_page_record_count:
                status_code = riot_apida.call_api(curr_url)
                curr_dashboard_row.loc[:, riot_apida.int_iter_keys[0]] = first_int_iter
                curr_dashboard_row.loc[:,'full_url'] = curr_url
                curr_dashboard_row.loc[:,'status_code'] = status_code 
                current_dashboard = pd.concat([current_dashboard, curr_dashboard_row])
                riot_apida.csv_upsave(curr_dashboard_row,
                                      "temp_dashboard"
                                      + str(int(curr_date.strftime("%Y%m%d%H%M%S")))
                                      + ".csv")
                if status_code == 200:
                    record_count = len(riot_apida.data_payload)
                    riot_apida.data_payload.loc[:,riot_apida.int_iter_keys[0]] = [first_int_iter] * record_count
                    riot_apida.csv_upsave(riot_apida.data_payload,
                                        "temp_data_payload" 
                                        + str(int(curr_date.strftime("%Y%m%d%H%M%S"))) 
                                        + ".csv")
                else: record_count = 0

                # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard
                
                first_int_iter += 1
                curr_url = riot_apida.url_updater(curr_url,
                                                  str(first_int_iter-1),
                                                  str(first_int_iter),
                                                  ParamType.QUERY,
                                                  riot_apida.int_iter_keys[0])
            
    case _:
        final_check = True
        first_int_iter_key = riot_apida.int_iter_keys[0]
        curr_higher_key = riot_apida.int_iter_keys[1]
        higher_int_iter_keys = riot_apida.int_iter_keys[1:]
        highest_int_iter_key_ind = len(higher_int_iter_keys)-1

        for index in riot_apida.base_dashboard.index:
            # the index range allows it to be saved as a DataFrame, otherwise, it will save as a Series
            # that makes it cleaner to concat the two objects because DataFrame has Index and Series does not
            curr_dashboard_row = riot_apida.base_dashboard.iloc[index:(index+1)]
            curr_url = curr_dashboard_row['full_url'][index]

            # assuming all int_iters for this API starts at 1 which I think they do TODO: check int_iter starts
            higher_int_iter_dict = {key: 1 for key in higher_int_iter_keys}
            higher_int_iter_attempted = [ False ] * len(higher_int_iter_dict)
            higher_int_iter_empty = [ False ] * len(higher_int_iter_dict)
            curr_higher_key_ind = 0

            while final_check:
                # TODO: turn url updater into its own helper function, probably in APIDA?
                # TODO: update dashboard every url update

                if not higher_int_iter_empty[curr_higher_key_ind]:
                    # reset the loop except for the highest key we reached
                    higher_int_iter_empty = [ False ] * len(higher_int_iter_dict)
                    curr_higher_key_ind = 0
                    higher_int_iter_dict[curr_higher_key] = higher_int_iter_dict[curr_higher_key]+1
                    curr_url = riot_apida.url_updater(curr_url,
                                                      str(higher_int_iter_dict[curr_higher_key]-1),
                                                      str(higher_int_iter_dict[curr_higher_key]),
                                                      ParamType.QUERY,
                                                      curr_higher_key)

                else: 
                    # this is the key movement and iter value movement that gets us to final_check == False
                    # if when all the keys seem to have exhausted record count

                    # reset all lower int iter values
                    for key in higher_int_iter_keys[:curr_higher_key_ind]: higher_int_iter_dict[key] = 1
                    # move up in key
                    curr_higher_key_ind+=1
                    curr_higher_key = higher_int_iter_keys[curr_higher_key_ind]
                    # move up in key value
                    higher_int_iter_dict[curr_higher_key] = higher_int_iter_dict[curr_higher_key]+1
                    curr_url = riot_apida.url_updater(curr_url,
                                                      str(higher_int_iter_dict[curr_higher_key]-1),
                                                      str(higher_int_iter_dict[curr_higher_key]),
                                                      ParamType.QUERY,
                                                      curr_higher_key)
                

                
                # assuming all int_iters for this API starts at 1 which I think they do TODO: check all int_iter starts
                # reset the value of the lowest int_iter
                first_int_iter = 1
                record_count = full_page_record_count
                full_page_check = True

                while full_page_check:
                    riot_apida.call_api(curr_url)
                    record_count = len(riot_apida.data_payload)
                    riot_apida.data_payload[first_int_iter_key] = [first_int_iter] * record_count
                    curr_dashboard_row[first_int_iter_key] = first_int_iter
                    curr_dashboard_row['full_url'] = curr_url
                    current_dashboard = pd.concat([current_dashboard, curr_dashboard_row])
                    riot_apida.csv_upsave(curr_dashboard_row,
                                        "temp_dashboard"
                                        + str(int(curr_date.strftime("%Y%m%d%H%M%S")))
                                        + ".csv")
                    riot_apida.csv_upsave(riot_apida.data_payload,
                                        "temp_data_payload" 
                                        + str(int(curr_date.strftime("%Y%m%d%H%M%S"))) 
                                        + ".csv")
                    
                    # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard

                    first_int_iter += 1
                    curr_url = riot_apida.url_updater(curr_url,
                                                      str(first_int_iter-1),
                                                      ParamType.QUERY,
                                                      first_int_iter_key)

                    # exit while loop?
                    full_page_check = record_count == full_page_record_count
                
                # set up all the checks
                higher_int_iter_empty[curr_higher_key_ind] = record_count == 0
                final_check = sum(higher_int_iter_empty) == len(higher_int_iter_empty)