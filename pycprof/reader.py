from __future__ import absolute_import, print_function

import json

from pycprof.dom import Allocation, API, Dependence, Value

class Reader:
    def __init__(self, path):
        self.path = path
        self.file = open(path, 'r')

    def __enter__(self):
        try:
            self.file = open(self.path, 'r')
            return self
        except Exception as e:
            raise e
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def construct_obj(self, j):
        if "val" in j:
            obj = Value(j["val"])
        elif "allocation" in j:
            obj = Allocation(j["allocation"])
        elif "api" in j:
            obj = API(j["api"])
        elif "dep" in j:
            obj = Dependence(j["dep"])
        else:
            raise TypeError
        return obj

    def __iter__(self):
        for i, line in enumerate(self.file):
            try:
                j = json.loads(line)
                yield self.construct_obj(j)
            except ValueError as e:
                print("problem at line", i, line)
                raise e

    def run_pass(self, handler_dict):
        for obj in self:
            if type(obj) in handler_dict:
                handler_dict[type(obj)](obj)
