import sys
import json
from annotation import *
import argparse

class App(object):
    def __init__(self, json, json1):
        self.json = json
        self.json1 = json1
        self.retrieve_input()



    def retrieve_input(self):
        global query_old
        global query_new
        global desc
        global result
        # result_old = self.get_query_result(query_old)
        # result_new = self.get_query_result(query_new)
        result_old_obj = self.json
        result_new_obj = self.json1

        result_old_nlp = self.get_description(result_old_obj)
        result_new_nlp = self.get_description(result_new_obj)

        result_old_tree = self.get_tree(result_old_obj)
        result_new_tree = self.get_tree(result_new_obj)

        result_diff = self.get_difference(result_old_obj, result_new_obj)
        print(result_old_nlp)
        print(result_old_tree)

        print(result_new_nlp)
        print(result_new_tree)

        print(result_diff)

    def get_description(self, json_obj):
        descriptions = get_text(json_obj)
        result = ""
        for description in descriptions:
            result = result + description + "\n"
        return result

    def get_tree(self, json_obj):
        head = parse_json(json_obj)
        return generate_tree("", head)

    def get_difference(self, json_object_A, json_object_B):
        diff = get_diff(json_object_A, json_object_B)
        return diff


if __name__ == "__main__":
    f = open("./TestJson/test1.json")
    json_obj = json.load(f)
    json_obj1 = json.load(open("./TestJson/test3.json"))
    # print(json_obj)
    app = App(json_obj, json_obj1)

