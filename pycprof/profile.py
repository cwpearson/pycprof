from __future__ import absolute_import, print_function

import networkx as nx
import ujson as json

from pycprof.dom import make_allocation, API, Dependence, Value


class Profile:
    def __init__(self, path):
        self.values = {}
        self.apis = {}
        self.allocations = {}
        self.graph = nx.DiGraph()

        values_json = []
        apis_json = []
        allocations_json = []


        with open(path, 'r') as input_file:
            for i, line in enumerate(input_file):
                try:
                    lineJson = json.loads(line)
                except ValueError as e:
                    print("problem at line", i, line)
                    raise e
                if "allocation" in lineJson:
                    allocations_json.append(lineJson["allocation"])
                elif "val" in lineJson:
                    values_json.append(lineJson["val"])
                elif "api" in lineJson:
                    apis_json.append(lineJson["api"])
                elif "dep" in lineJson:
                    pass
                else:
                    raise TypeError

        for j in allocations_json:
            obj = make_allocation(j)
            self.allocations[obj.id_] = obj
        del allocations_json

        for j in values_json:
            alloc = self.allocations[j["id"]]
            val = Value(j, alloc)
            self.values[val.id_] = val
            graph_handle_value(val)
        del values_json

        for j in apis_json:
            inVals = [self.values[int(i)] for i in j["inputs"]]
            outVals = [self.values[int(o)] for o in j["outputs"]]
            api = API(j, inVals, outVals)
            self.apis[api.id_] = api
            graph_handle_api(api)
        del apis_json


        def graph_handle_value(obj):
            assert isinstance(obj, Value)
            self.graph.add_node(obj)

        def graph_handle_api(api):
            assert isinstance(api, API)
            if "cudaMemcpy" in api.functionName or "Bcast" in api.functionName or "AllReduce" in api.functionName:
                for srcVal in api.inputs:
                    for dstVal in api.outputs:
                        assert isinstance(srcVal, Value)
                        assert isinstance(dstVal, Value)
                        self.graph.add_edge(dstVal, srcVal)
            else:
                for inVal in api.inputs:  # input transfers
                    self.graph.add_edge(api, inVal)
                for outVal in api.outputs:  # output transfers
                    self.graph.add_edge(outVal, api)
