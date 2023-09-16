from typing import final
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import pandas as pd
import numpy
import time
import re
from itertools import product
import os
import numpy
import SqlHandler

class APIDataAggregator(object):
    def __init__(self, config_fn):
        print("instantiatiating an APIDataAggregator Object")
        # dashboard will let us see the state of api call for each api call
        self.base_dashboard = pd.DataFrame()
        self.base_dashboard['status_code'] = [ ]
        self.base_dashboard['full_url'] = [ ]
        self.data_payload = pd.DataFrame()
        self.current_table_name = None
        self.param_keys = [ ]
        self.int_iter_param_col_i = [ ]
        self.int_iter_keys = [ ]
        with open(config_fn, mode="r") as json_file:
            self.api_key = json.load(json_file)['api_key']
            self.info_schema = json.load(json_file)['info_schema']

        print("set api key as " + self.api_key, end="\n \n")
        print("\ninfo_schema_json:")
        print(self.info_schema, end="\n \n")



    def assemble_dashboard(self, table_name):

        print("assembling dashboard for " + table_name)
        self.current_table_name = table_name

        # put pieces of url into dashboard
        base_url = self.info_schema[table_name]["source"]["base_url"]
        path_params = self.info_schema[table_name]["source"]["pathParams"]
        query_params = self.info_schema[table_name]["source"]["queryParams"]

        self.base_dashboard['base_url'] = [base_url]

        print("adding path parameter values to dashboard \n")
        for key in path_params.keys():
            # param_type expected to be of value set ["presets", "int_iter", "long", "databased"]
            match path_params[key]["param_type"]:
                case "presets":
                    print(key + ": preset values pulled from info schema")
                    temp_pp=pd.DataFrame(path_params[key]["values"], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(temp_pp, how='cross')
                case "int_iter": 
                    print(key + ": int_iter values pulled from info schema")
                    temp_pp=pd.DataFrame(path_params[key]["min_value"], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(temp_pp, how='cross')
                case "databased": None # TODO: figure out what to do here
                case _: None
        print("finished path parameter values to dashboard \n \n \n")

        print("adding query parameters to dashboard \n")
        for key in query_params.keys():
            match query_params[key]["param_type"]:
                case "presets":
                    print(key + ": preset values pulled from info schema")
                    temp_pp=pd.DataFrame([query_params[key]["values"]], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(temp_pp, how='cross')
                case "int_iter": 
                    print(key + ": int_iter values pulled from info schema")
                    temp_pp=pd.DataFrame([query_params[key]["min_value"]], columns=[key])
                    self.base_dashboard=self.base_dashboard.merge(temp_pp, how='cross')
                case "databased": None # TODO: figure out what to do here
                case _: None
        print("finished query parameter values to dashboard \n \n \n")
        
        # make full url from all url components
        print("constructing full urls \n")
        full_urls = [base_url]

        # identify path param columns in dashboard and how many there are
        # prepare regex pattern of keys
        path_param_keys_re_patt = [ "^(" + _ + ")$" for _ in path_params.keys()]
        path_param_col_i = \
            self.base_dashboard.columns.str. \
            match("|".join(path_param_keys_re_patt),case=False)
        path_param_count = sum(path_param_col_i)
        print("counting " + str(path_param_count) + " path_params")

        # identify query param columns in dashboard and how many there are
        query_param_keys_re_patt = [ "^(" + _ + ")$" for _ in query_params.keys()]
        query_param_col_i = \
            self.base_dashboard.columns.str. \
            match("|".join(query_param_keys_re_patt),case=False)
        query_param_count = sum(query_param_col_i)
        qp_keys=list(query_params.keys())
        print("counting " + str(query_param_count) + " query_params \n")
        
        print("for api call purposes, identifying which path param and query param are int_iter type")
        self.int_iter_param_col_i.extend([ path_params.get(_)['param_type'] for _ in path_params ])
        self.int_iter_param_col_i.extend([ query_params.get(_)['param_type'] for _ in query_params ])
        self.int_iter_param_col_i = [ _ == "int_iter" for _ in self.int_iter_param_col_i ]
        self.param_keys = list(path_params.keys())
        self.param_keys.extend(qp_keys)
        self.int_iter_keys = [ e for i, e in enumerate(self.param_keys) if self.int_iter_param_col_i[i] == True]

        print("saved to self.int_iter_param_col_i \n \n \n")

        pp_sep = "/"
        param_delim = "?"
        qp_sep = "="
        qp_delim = "&"

        # add path params to full url

        match path_param_count:
            case 0:
                print("no path params to add, continuing url assembly")
            case _:
                print("adding path_params to full url")
                pp_conc_list = [pp_sep.join(self.base_dashboard.loc[i, path_param_col_i]) \
                                for i in range(len(self.base_dashboard))]
                full_urls = [base_url + pp_sep + _ for _ in pp_conc_list]
                print("finished path param concatenation \n")
                
        print("concatenating query params to url")
        
        # add query params to full url
        match query_param_count:
            case 0:
                print("no query params to add, continuing url assembly")
            case 1:
                print("adding query_params to full url")
                # TODO: figure out what to do here, only works assuming int_iter
                full_urls = [_ + param_delim + qp_keys[0] + qp_sep + query_params.get(qp_keys[0])["min_value"] for _ in full_urls]
                print("finished query param concatenation \n \n \n")
            case _:
                print("adding query_params to full url")
                # TODO: figure out what to do here

                print("finished query param concatenation \n \n \n")

        full_urls = [_ + qp_delim + "api_key" + qp_sep + self.api_key for _ in full_urls]
        self.base_dashboard["full_url"] = full_urls
        self.base_dashboard['status_code'] = 0 # converts status_code col to dtype int because the cross join turns the NaN to float
        print("api_key added to full url and full url added to dashboard \n")

        print("finished assembling dashboard \n \n \n")



    def call_api(self, api_url):

        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
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

        self.base_dashboard.loc[self.base_dashboard['full_url']==api_url, 'status_code'] = status_code 
        self.data_payload = apicontent_df

        print(self.base_dashboard.loc[self.base_dashboard['full_url']==api_url, ["status_code"] + self.param_keys])

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

    def csv_delete(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
            print("Deleting " + filename + ".")
        else:
            print(filename + " does not exist") 