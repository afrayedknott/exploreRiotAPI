from typing import final
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import pandas as pd
import numpy
import time
from itertools import product

class APIDataAggregator(object):
    def __init__(self):
        self.assembled_pps = []
        self.assembled_qps = []
        self.base_url = None
        self.api_key = None
        self.status_codes = []
        self.dashboard = pd.DataFrame(data=None, columns=['placeholder'])
        self.data_payload = None

    def set_api_key(self, api_key_str):
        self.api_key = api_key_str
        print("set api key as " + api_key_str)

    def set_base_api_url(self, url_str):
        self.base_url = url_str
        print("set base url as " + url_str)

    def add_path_params(self, listname, listvalues):
        print("adding path parameters")
        pp_sep = "/"
        temp_pps = pd.DataFrame(data=listvalues, columns=[listname])

        if len(self.assembled_pps) == 0:
            self.assembled_pps=[pp_sep + _ for _ in listvalues]
        else:
            pp_tuples = product(self.assembled_pps, [pp_sep + _ for _ in listvalues])
            self.assembled_pps = list("".join(_) for _ in pp_tuples)

        if self.dashboard.shape[0] == 0:
            self.dashboard = temp_pps
        else:
            self.dashboard = self.dashboard.merge(temp_pps, how='cross')

        #if len(self.path_params['assembled']) == 0:
        #    self.path_params['assembled'] = [pp_sep + pp for pp in listvalues]
        #else:
        #    temp_pp = [pp_sep + pp for pp in listvalues]
        #    pp_tuples = product(self.path_params['assembled'], temp_pp)
        #    self.path_params['assembled'] = list("".join(pp_tuple) for pp_tuple in pp_tuples)
        print("path parameters: ")
        print(self.assembled_pps)
        print(self.dashboard)

    def add_query_params(self, listname, listvalues):
        print("adding query parameters")
        qp_sep = "="
        qp_delim = "&"
        temp_qps = pd.DataFrame(data=listvalues, columns=[listname])

        if len(self.assembled_qps) == 0:
            self.assembled_qps=[listname + qp_sep + _ for _ in listvalues]
        else:
            qp_tuples = product(self.assembled_qps, [qp_delim + listname + qp_sep + _ for _ in listvalues])
            self.assembled_qps = list("".join(_) for _ in qp_tuples)

        if self.dashboard.shape[0] == 0:
            self.dashboard = temp_qps
        else:
            self.dashboard = self.dashboard.merge(temp_qps, how='cross')

        print("query parameters: ")
        print(self.assembled_qps)
        print(self.dashboard)

    def clear_query_params(self):
        self.assembled_qps = {}
        print("Cleared the query paramaters")

    def clear_path_params(self):
        self.assembled_pps = {}
        print("Cleared the path paramaters")

    # create a cartesian product of all the params for easy assembly of the url
    # eventually integrate this process into add_query_param_list()

## try an api call

    def complete_api_call(self):

        #assemble the api url
        param_delim = "?"
        assembled_urls = [self.base_url + _ + param_delim for _ in self.assembled_pps]
        url_tuples = product(assembled_urls, self.assembled_qps)
        assembled_urls = list("".join(url_tuple) for url_tuple in url_tuples)

        print("assembled urls")

        #assemble the sc_dashb
        #for db_values in 

        #self.sc_dashb = pd.DataFrame(
        #    product(),
        #    columns=self.path_params.keys().append((self.query_params.keys())
        #)

        status_code = []

        #if api url has 'page', then do this loop pull
        if 'page' in list(self.dashboard):
            
            for url in assembled_urls:
                print("pulling " + url)

                #each iteration of param combo to cycle through pages
                ## start with first dataset
                returned_api_call = self._api_call_shunt(url)
                self.data_payload = returned_api_call['data_payload']
                status_code.append(returned_api_call['status_code'])
                expected_rowcount = returned_api_call['data_payload'].shape[0]
                print("page " + str(1) + " rowcount: " + str(expected_rowcount))

                #while loop until dataset is shorter than the first page
                pageiter = 2
                new_page_url = url.replace("page="+str(pageiter-1), "page="+str(pageiter))
                rowcount = expected_rowcount
                while rowcount == expected_rowcount:
                    new_page_url = new_page_url.replace("page="+str(pageiter-1), "page="+str(pageiter))
                    print("pulling " + new_page_url)
                    returned_api_call = self._api_call_shunt(new_page_url)
                    pd.concat([self.data_payload,returned_api_call['data_payload']])
                    status_code.append(returned_api_call['status_code'])
                    rowcount = len(returned_api_call['data_payload'])
                    print("page " + str(pageiter) + " rowcount: " + str(rowcount))
                    pageiter+=1

        else:
            for url in assembled_urls:
                print("pulling " + url)

                #each iteration of param combo
                returned_api_call = self._api_call_shunt(url)
                self.data_payload = returned_api_call['data_payload']
                status_code.append(returned_api_call['status_code'])

    def _api_call_shunt(self, api_url):

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
          
            response = http.get(api_url, timeout=10)

            status_code = response.status_code
            apicontent_df = pd.DataFrame(json.loads(response.content.decode('utf8')))

            pd.concat([self.data_payload,apicontent_df]).reset_index(drop=True)

            time.sleep(3)

        return {'status_code': status_code, 
                'data_payload': apicontent_df}
                    

