from typing import final
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import pandas as pd
import decimal
import time
import re
from itertools import product
import os
import numpy
from ParamTypeEnum import ParamType
import datetime

class APIHandler(object):
    def __init__(self, config_fn, scheme_fn):
        print("instantiatiating an APIHandler Object")
        # dashboard will let us see the state of api call for each api call
        self.base_dashboard = pd.DataFrame()
        self.base_dashboard['status_code'] = [ ]
        self.base_dashboard['full_url'] = [ ]
        self.data_payload = pd.DataFrame()
        self.param_keys = [ ]
        self.int_iter_param_col_i = [ ]
        self.int_iter_keys = [ ]
        with open(config_fn, mode="r") as json_file:
            data = json.load(json_file)
            self.api_key = data['api_key']
        with open(scheme_fn, mode="r") as json_file:
            data = json.load(json_file)
            self.info_schema = data['source']
            self.current_table_name = data["table_name"]
            self.full_page_record_count = self.info_schema["full_page_record_count"]
        print("set api key as " + self.api_key, end="\n \n")
        print("\ninfo_schema_json:")
        print(self.info_schema, end="\n \n")
        self.path_param_sep = "/"
        self.param_delim = "?"
        self.query_param_sep = "="
        self.query_param_delim = "&"

    def assemble_dashboard(self):
        print("assembling dashboard for " + self.current_table_name)

        # put pieces of url into dashboard
        base_url = self.info_schema['base_url']
        path_params = self.info_schema['pathParams']
        query_params = self.info_schema['queryParams']

        self.base_dashboard['base_url'] = [base_url]

        print("adding path parameter values to dashboard \n")
        for key in path_params.keys():
            # value_type expected to be of value set ['presets", "int_iter", "long", "databased']
            match path_params[key]['value_type']:
                case "presets":
                    print(key + ": preset values pulled from info schema")
                    path_param_df=pd.DataFrame(path_params[key]['values'], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(path_param_df, how='cross')
                case "int_iter" | "long": 
                    print(key + ": int_iter values pulled from info schema")
                    path_param_df=pd.DataFrame(path_params[key]['starting_value'], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(path_param_df, how='cross')
                case "databased": None # TODO: figure out what to do here
                case _: None
        print("finished path parameter values to dashboard \n \n \n")

        print("adding query parameters to dashboard \n")
        for key in query_params.keys():
            match query_params[key]['value_type']:
                case "presets":
                    print(key + ": preset values pulled from info schema")
                    path_param_df=pd.DataFrame([query_params[key]['values']], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(path_param_df, how='cross')
                case "int_iter" | "long": 
                    print(key + ": int_iter values pulled from info schema")
                    path_param_df=pd.DataFrame([query_params[key]['starting_value']], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(path_param_df, how='cross')
                case "databased": None # TODO: figure out what to do here
                case _: None
        print("finished query parameter values to dashboard \n \n \n")
        
        # make full url from all url components
        print("constructing full urls \n")
        full_urls = [base_url]

        # identify path param columns in dashboard and how many there are
        # prepare regex pattern of keys
        path_param_keys_regex_patterns = [ "^(" + _ + ")$" for _ in path_params.keys()]
        path_param_col_i = \
            self.base_dashboard.columns.str. \
            match("|".join(path_param_keys_regex_patterns),case=False)
        path_param_count = sum(path_param_col_i)
        print("counting " + str(path_param_count) + " path_params")

        # identify query param columns in dashboard and how many there are
        query_param_keys_regex_patterns = [ "^(" + _ + ")$" for _ in query_params.keys()]
        query_param_col_i = \
            self.base_dashboard.columns.str. \
            match("|".join(query_param_keys_regex_patterns),case=False)
        query_param_count = sum(query_param_col_i)
        query_param_keys = list(query_params.keys())
        print("counting " + str(query_param_count) + " query_params \n")
        
        print("for api call purposes, identifying which path param and query param are int_iter type")
        self.int_iter_param_col_i.extend([ path_params.get(_)['value_type'] for _ in path_params ])
        self.int_iter_param_col_i.extend([ query_params.get(_)['value_type'] for _ in query_params ])
        self.int_iter_param_col_i = [ _ == "int_iter" for _ in self.int_iter_param_col_i ]
        self.param_keys = list(path_params.keys())
        self.param_keys.extend(query_param_keys)
        self.int_iter_keys = [ e for i, e in enumerate(self.param_keys) if self.int_iter_param_col_i[i] == True]

        print("saved to self.int_iter_param_col_i \n \n \n")

        # add path params to full url

        match path_param_count:
            case 0:
                print("no path params to add, continuing url assembly")
            case _:
                print("adding path_params to full url")
                path_param_joined_list = [self.path_param_sep.join(self.base_dashboard.loc[i, path_param_col_i]) \
                                for i in range(len(self.base_dashboard))]
                full_urls = [base_url + self.path_param_sep + _ for _ in path_param_joined_list]
                print("finished path param concatenation \n")
                
        print("concatenating query params to url")
        
        # add query params to full url
        match query_param_count:
            case 0:
                print("no query params to add, continuing url assembly")
            case 1:
                print("adding query_params to full url")
                # TODO: figure out what to do here, only works assuming int_iter
                full_urls = [_ + self.param_delim + query_param_keys[0] + self.query_param_sep + query_params.get(query_param_keys[0])['starting_value'] for _ in full_urls]
                print("finished query param concatenation \n \n \n")
            case _:
                print("adding query_params to full url")
                # TODO: figure out what to do here

                print("finished query param concatenation \n \n \n")

        full_urls = [_ + self.query_param_delim + "api_key" + self.query_param_sep + self.api_key for _ in full_urls]
        self.base_dashboard['full_url'] = full_urls
        self.base_dashboard['status_code'] = 0 # converts status_code col to dtype int because the cross join turns the NaN to float
        print("api_key added to full url and full url added to dashboard \n")

        print("finished assembling dashboard \n \n \n")



    def call_api(self, api_url):

        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=['HEAD", "GET", "OPTIONS'],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        with requests.Session() as http:
            http.mount("https://", adapter)
            http.mount("http://", adapter)
          
            response = http.get(api_url, timeout=10)

            status_code = response.status_code
            apicontent_df = pd.DataFrame(json.loads(
                response.content.decode('utf8'))
                                         )
            pd.concat([self.data_payload,apicontent_df]).\
                reset_index(drop=True)

            time.sleep(3)

        self.data_payload = apicontent_df
        return status_code 



    def csv_upsave(self, dataframe, filename):
        #if file exists
        #   read csv data into dataframe
        #   append data to csv dataframe
        #   write the full data back to csv file
        #else
        #   write new csv data
        fp = "./"+filename
        if os.path.exists(filename):
            csv_data = pd.read_csv(filename)
            pd.concat([csv_data, dataframe]).reset_index(drop=True).\
                to_csv(filename, index = False)
            print("Saved to " + filename + ".")
        else:
            dataframe.to_csv(filename, index = False)



    def url_updater(self, curr_url: str, old_param_value: str, new_param_value: str, param_type: ParamType, param_name):
        param_type = ParamType(param_type)
        if not isinstance(param_type, ParamType):
            raise TypeError('param_type must be an instance of ParamType Enum')
        new_url = None
        match param_type:
            case ParamType.PATH:
                finished_path_param_str = self.path_param_sep + str(old_param_value)
                new_path_param_str = self.path_param_sep + str(new_param_value)
                new_url = curr_url.replace(finished_query_param_str, new_path_param_str)
            case ParamType.QUERY:
                finished_query_param_str = param_name + self.query_param_sep + str(old_param_value)
                new_query_param_str = param_name + self.query_param_sep + str(new_param_value)
                new_url = curr_url.replace(finished_query_param_str, new_query_param_str)
            case _:
                None
        return new_url
    


    def loop_through(self):
        
        # I know I can delete this now and grab this code from git but keeping it for now
        # for convenience sake
        
        # just used for file name and batch id
        curr_date = datetime.datetime.now().timestamp()
        decimal_digits = decimal.Decimal(str(curr_date))
        batch_id = int(curr_date * 10 ^ (-1 * decimal_digits.as_tuple().exponent))

        # measure dimensions
        int_iter_count = sum(self.int_iter_param_col_i)
        record_count = self.full_page_record_count

        # set starting values
        current_dashboard = pd.DataFrame(columns = list(self.base_dashboard.columns))
        curr_dashboard_row = self.base_dashboard.iloc[0:1]
        current_url = curr_dashboard_row['full_url'][0]
        first_int_iter = 1
        match int_iter_count:
            case 0:
                # just loop through path params only
                for index in self.base_dashboard.index[1:]:
                    while record_count >= self.full_page_record_count:
                        status_code = self.call_api(current_url)
                        record_count = len(self.data_payload)
                        curr_dashboard_row['full_url'] = current_url
                        current_dashboard = pd.concat([current_dashboard, curr_dashboard_row])
                        self.csv_upsave(curr_dashboard_row,
                                            "temp_dashboard"
                                            + str(batch_id)
                                            + ".csv")
                        if status_code == 200:
                            record_count = len(self.data_payload)
                            self.data_payload.loc[:,self.int_iter_keys[0]] = [first_int_iter] * record_count
                            self.csv_upsave(self.data_payload,
                                                "temp_data_payload" 
                                                + str(batch_id) 
                                                + ".csv")
                        else: record_count = 0

                        # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard

            case 1:
                # loop through int iter for 1 query param > loop through path params
                for index in self.base_dashboard.index[1:]:
                    while record_count >= self.full_page_record_count:
                        status_code = self.call_api(current_url)
                        curr_dashboard_row.loc[:, self.int_iter_keys[0]] = first_int_iter
                        curr_dashboard_row.loc[:,'full_url'] = current_url
                        curr_dashboard_row.loc[:,'status_code'] = status_code 
                        current_dashboard = pd.concat([current_dashboard, curr_dashboard_row])
                        self.csv_upsave(curr_dashboard_row,
                                            "temp_dashboard"
                                            + str(batch_id)
                                            + ".csv")
                        if status_code == 200:
                            record_count = len(self.data_payload)
                            self.data_payload.loc[:,self.int_iter_keys[0]] = [first_int_iter] * record_count
                            self.csv_upsave(self.data_payload,
                                                "temp_data_payload" 
                                                + str(batch_id) 
                                                + ".csv")
                        else: record_count = 0

                        # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard
                        
                        first_int_iter += 1
                        current_url = self.url_updater(current_url,
                                                        str(first_int_iter-1),
                                                        str(first_int_iter),
                                                        ParamType.QUERY,
                                                        self.int_iter_keys[0])
                    
            case _:
                # loop through query param > loop through int iter of each query param > loop through path params
                final_check = True
                first_int_iter_key = self.int_iter_keys[0]
                curr_higher_key = self.int_iter_keys[1]
                higher_int_iter_keys = self.int_iter_keys[1:]
                highest_int_iter_key_ind = len(higher_int_iter_keys)-1

                for index in self.base_dashboard.index[1:]:
                    # the index range allows it to be saved as a DataFrame, otherwise, it will save as a Series
                    # that makes it cleaner to concat the two objects because DataFrame has Index and Series does not
                    curr_dashboard_row = self.base_dashboard.iloc[index:(index+1)]
                    current_url = curr_dashboard_row['full_url'][index]

                    # assuming all int_iters for this API starts at 1 which I think they do TODO: check int_iter starts
                    higher_int_iter_dict = {key: 1 for key in higher_int_iter_keys}
                    higher_int_iter_attempted = [ False ] * len(higher_int_iter_dict)
                    higher_int_iter_empty = [ False ] * len(higher_int_iter_dict)
                    current_higher_key_ind = 0

                    while final_check:
                        # TODO: turn url updater into its own helper function, probably in APIDA?
                        # TODO: update dashboard every url update

                        if not higher_int_iter_empty[current_higher_key_ind]:
                            # reset the loop except for the highest key we reached
                            higher_int_iter_empty = [ False ] * len(higher_int_iter_dict)
                            current_higher_key_ind = 0
                            higher_int_iter_dict[curr_higher_key] = higher_int_iter_dict[curr_higher_key]+1
                            current_url = self.url_updater(current_url,
                                                            str(higher_int_iter_dict[curr_higher_key]-1),
                                                            str(higher_int_iter_dict[curr_higher_key]),
                                                            ParamType.QUERY,
                                                            curr_higher_key)

                        else: 
                            # this is the key movement and iter value movement that gets us to final_check == False
                            # if when all the keys seem to have exhausted record count

                            # reset all lower int iter values
                            for key in higher_int_iter_keys[:current_higher_key_ind]: higher_int_iter_dict[key] = 1
                            # move up in key
                            current_higher_key_ind+=1
                            curr_higher_key = higher_int_iter_keys[current_higher_key_ind]
                            # move up in key value
                            higher_int_iter_dict[curr_higher_key] = higher_int_iter_dict[curr_higher_key]+1
                            current_url = self.url_updater(current_url,
                                                            str(higher_int_iter_dict[curr_higher_key]-1),
                                                            str(higher_int_iter_dict[curr_higher_key]),
                                                            ParamType.QUERY,
                                                            curr_higher_key)
                        

                        
                        # assuming all int_iters for this API starts at 1 which I think they do TODO: check all int_iter starts
                        # reset the value of the lowest int_iter
                        first_int_iter = 1
                        record_count = self.full_page_record_count
                        full_page_check = True

                        while full_page_check:
                            status_code = self.call_api(current_url)
                            record_count = len(self.data_payload)
                            self.data_payload[first_int_iter_key] = [first_int_iter] * record_count
                            curr_dashboard_row[first_int_iter_key] = first_int_iter
                            curr_dashboard_row['full_url'] = current_url
                            current_dashboard = pd.concat([current_dashboard, curr_dashboard_row])
                            self.csv_upsave(curr_dashboard_row,
                                                "temp_dashboard"
                                                + str(batch_id)
                                                + ".csv")
                            if status_code == 200:
                                record_count = len(self.data_payload)
                                self.data_payload.loc[:,self.int_iter_keys[0]] = [first_int_iter] * record_count
                                self.csv_upsave(self.data_payload,
                                                    "temp_data_payload" 
                                                    + str(batch_id) 
                                                    + ".csv")
                            else: record_count = 0
                            
                            # TODO: sql upload, oh shit, I gotta make a dashboard for this too OR add to the existing dashboard

                            first_int_iter += 1
                            current_url = self.url_updater(current_url,
                                                            str(first_int_iter-1),
                                                            ParamType.QUERY,
                                                            first_int_iter_key)

                            # exit while loop?
                            full_page_check = record_count == self.full_page_record_count
                        
                        # set up all the checks
                        higher_int_iter_empty[current_higher_key_ind] = record_count == 0
                        final_check = sum(higher_int_iter_empty) == len(higher_int_iter_empty)