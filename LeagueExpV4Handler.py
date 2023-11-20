from typing import final
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import decimal
import datetime
from itertools import product
import os
from ParamTypeEnum import ParamType
from APIHandler import APIHandler
from RunModeEnum import RunMode

class LeagueExpV4Handler(object):
    def __init__(self):
        print("instantiating an APIHandler Object")
        self.apiHandler = APIHandler("config.json", "league-exp-v4_schema.json")
        self.apiHandler.assemble_dashboard()
    


    def api_call_loop(self, runmode: RunMode):

        if not isinstance(runmode, RunMode):
            raise TypeError("param_type must be an instance of RunMode Enum")

        batch_meta_fn = self.apiHandler.current_table_name + "_" + "batch_meta.csv"

        if os.path.exists(batch_meta_fn):
            print("batch_meta file exists")
            # pull existing batch and batch id
            batch_meta = pd.read_csv(batch_meta_fn)
            batch_id = batch_meta.loc[:,'batch_id'][0]
            dashboard_fn = self.apiHandler.current_table_name + "_" + "temp_dashboard" + "_" + str(batch_id) + ".csv"
            payload_fn = self.apiHandler.current_table_name + "_" + "temp_data_payload" + "_" + str(batch_id) + ".csv"

            # set loop starting values
            current_dashboard_row = batch_meta.drop(columns=['batch_id'])
            dashboard = pd.read_csv(dashboard_fn)
            starting_index = batch_meta.loc[:,'index'][0]
            page_iter = batch_meta.loc[:,'page_iter'][0]+1
        else:
            print("batch_meta file does not exist")
            # set loop starting values
            dashboard = pd.DataFrame(columns = list(self.apiHandler.base_dashboard.columns))
            current_dashboard_row = self.apiHandler.base_dashboard.iloc[0:1]
            starting_index = 0
            page_iter = 1

            # create new batch id
            current_date = datetime.datetime.now().timestamp()
            decimal_digits = decimal.Decimal(str(current_date))
            batch_id = int(current_date * 10 ** (-1 * decimal_digits.as_tuple().exponent))
            dashboard_fn = self.apiHandler.current_table_name + "_" + "temp_dashboard" + "_" + str(batch_id) + ".csv"
            payload_fn = self.apiHandler.current_table_name + "_" + "temp_data_payload" + "_" + str(batch_id) + ".csv"
        
        # loop through int iter for 1 query param > loop through path params
        print("start loop")
        print(range(starting_index,len(self.apiHandler.base_dashboard)-1))
        for index in range(starting_index,len(self.apiHandler.base_dashboard)-1):
            
            # set loop starting values
            record_count = self.apiHandler.full_page_record_count
            current_dashboard_row = self.apiHandler.base_dashboard.iloc[index:index+1]
            current_url = current_dashboard_row['full_url'][index]
            current_url = self.apiHandler.url_updater(current_url,
                                             str(page_iter-1),
                                             str(page_iter),
                                             ParamType.QUERY,
                                             self.apiHandler.int_iter_keys[0])

            print(current_dashboard_row)
            while record_count >= self.apiHandler.full_page_record_count:
                print("page " + str(page_iter))
                status_code = self.apiHandler.call_api(current_url)
                current_dashboard_row.loc[:, self.apiHandler.int_iter_keys[0]] = page_iter
                current_dashboard_row.loc[:,'full_url'] = current_url
                current_dashboard_row.loc[:,'status_code'] = status_code 
                dashboard = pd.concat([dashboard, current_dashboard_row])
                self.apiHandler.csv_upsave(current_dashboard_row, dashboard_fn)
                if status_code == 200:
                    record_count = len(self.apiHandler.data_payload)
                    self.apiHandler.data_payload.loc[:,self.apiHandler.int_iter_keys[0]] = [page_iter] * record_count
                    self.apiHandler.csv_upsave(self.apiHandler.data_payload, payload_fn)
                else: record_count = 0

                batch_meta = current_dashboard_row
                batch_meta.loc[:,'batch_id'] = batch_id
                batch_meta.loc[:,'index'] = index
                batch_meta.loc[:,'page_iter'] = page_iter
                batch_meta.to_csv(batch_meta_fn, index = False)

                # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard
                
                page_iter += 1
                current_url = self.apiHandler.url_updater(current_url,
                                                str(page_iter-1),
                                                str(page_iter),
                                                ParamType.QUERY,
                                                self.apiHandler.int_iter_keys[0])
                
                # test runmode breaks loop after an acceptable amount of data
                if runmode == RunMode.CSV_CSV_TESTING and page_iter == 5:
                    break
            
            if runmode == RunMode.CSV_CSV_TESTING and index == 5:
                print("runmode indicates testing therefore limited number of records will pull")
                break

        print("end loop")
        if os.path.exists(batch_meta_fn):
            os.remove(batch_meta_fn)