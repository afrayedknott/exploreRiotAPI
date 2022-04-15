from typing import final
import requests
import json
import pandas as pd
import numpy
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class APIDataAggregator(object):
    def __init__(self, base_url, api_key):
        self.query_param_list = []
        self.query_param_dashb = pd.DataFrame()
        self.base_url = base_url
        self.api_key = api_key

    def add_query_param_list(self, qp_list):
        self.query_param_list.append(qp_list)
        print("added query parameters")
        print(qp_list)

    def clear_query_param_list(self):
        self.query_param_list = []
        print("clearing the query paramaters list")
        print(self.query_param_list)

    def convert_query_param_list_to_df(self): # create a df of every iteration of all the query params so we pull complete data sets
        qpl_list_count = len(self.query_param_list)
        list_lengths = []
        repeat_elements = []
        repeat_lists = []
        api_url = []

        for qpl_i in self.query_param_list:
            list_lengths.append(len(qpl_i))
        
        print("lengths of query parameter list of values")
        print(list_lengths)

        for length_iter in range(qpl_list_count):
            repeat_elements.append(int(numpy.prod(list_lengths[length_iter + 1:])))
            repeat_lists.append(int(numpy.prod(list_lengths[:length_iter])))
        
        print("repeat list multipliers")
        print(repeat_lists)
        print("repeat elements mulitpliers")
        print(repeat_elements)
        

        for qpdf_iter in range(qpl_list_count):
            repeat_element_multiplier = repeat_elements[qpdf_iter]
            repeat_list_multiplier = repeat_lists[qpdf_iter]
            col_name = "query_param_"+str(qpdf_iter+1)

            multiplied_lists = numpy.repeat([self.query_param_list[qpdf_iter]], repeat_list_multiplier, axis = 0)
            multiplied_elements_flattened = numpy.repeat(multiplied_lists, repeat_element_multiplier)
            self.query_param_dashb[col_name] = multiplied_elements_flattened
        
        print(self.query_param_dashb)

        # 

        col_names = list(self.query_param_dashb.columns)
        self.query_param_dashb["api_url"] = ""
        for index, column_name in enumerate(col_names):
            print("current column {column_name}".format(column_name=column_name))
            self.query_param_dashb["api_url"] = self.query_param_dashb["api_url"] + self.query_param_dashb[column_name].astype(str) + "/"
        
        self.query_param_dashb["api_url"] = self.base_url + self.query_param_dashb["api_url"] + "?page=1&api_key=" + self.api_key
        print(self.query_param_dashb["api_url"])
    
## try an api call

    def data_transfer(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)

        with requests.Session() as http:
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            status_code = []
            df_list = []
        
            for iter, row in self.query_param_dashb.iterrows():
            
                print(self.query_param_dashb.loc[iter,:])
                response = http.get(row["api_url"], timeout=10)

                print(response.status_code)
                status_code.append(response.status_code)

                api_content = json.loads(response.content.decode('utf8'))
                df_list.append(pd.DataFrame(api_content))
            
                time.sleep(3)

            self.query_param_dashb.insert(0, "status_code", status_code)
            final_df = pd.concat(df_list)

            print(final_df)
            final_df.to_csv('content.csv')