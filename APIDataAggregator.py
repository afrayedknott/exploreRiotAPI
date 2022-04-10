import requests
import sched, time
import json
import pandas
import numpy

class APIDataAggregator(object):
    def __init__(self, base_url, api_key):
        self.query_param_list = []
        self.query_param_dashb = pandas.DataFrame()
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
        self.query_param_dashb["status"] = ""
        print(self.query_param_dashb["api_url"])

    #def check_qp_df():
    #    currentside = randomize_side(); # test code from DICE
    #    return self.count * self.currentside; # test code from DICE

    #def print_status():
    #    print(str(api_response.status_code) + " | " + q + " | " +  t + " | " + d)

#def loop_action(api_response, q, t, d):
#    print(str(api_response.status_code) + " | " + q + " | " +  t + " | " + d)
#    api_obj = json.loads(api_response, sort_keys=True, indent=4)
#    df = pandas.DataFrame(api_obj)

#for q in queues:
#    for t in tiers:
#        for d in divisions:

#            s = sched.scheduler(time.time, time.sleep)

#            first_loop_check = 0
#            if first_loop_check == 0:
#                first_loop_check = 1

#            response = requests.get("https://na1.api.riotgames.com/lol/league-exp/v4/entries/" + q + "/" + t + "/" + d + "?page=1&api_key=" + api_key_str)
            
#            s.enter(1, 1, loop_action(response, q, t, d))
#            s.run

## try an api call

# response = requests.get("https://na1.api.riotgames.com/lol/league-exp/v4/entries/" + q + "/" + t + "/" + d + "?page=1&api_key=" + api_key_str)
# print(str(response.status_code) + " | " + q + " | " +  t + " | " + d)
# api_obj = json.loads(response.content.decode('utf8'))
# print(api_obj)
# df = pandas.DataFrame(api_obj)
# df.info()
# print(df)