from __future__ import absolute_import, print_function

import logging

import networkx as nx
import ujson as json

from pycprof.dom import make_allocation, API, CudaLaunch, Dependence, Value


class Profile:
    def __init__(self, path, num_lines=0):
        self.values = {}
        self.apis = {}
        self.allocations = {}
        self.graph = nx.DiGraph()

        with open(path, 'r') as input_file:
            self.init_from_lines(input_file, num_lines)

    def init_from_lines(self, lines, num_lines):

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

        values_json = []
        apis_json = []
        allocations_json = []
        correlation_json = []

        for i, line in enumerate(lines):
            if num_lines == 0 or i < num_lines:
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
                elif "correlationId" in lineJson: # this to be fixed in cupti
                    lineJson["correlation_id"] = lineJson["correlationId"]
                    correlation_json.append(lineJson)
                elif "correlation_id" in lineJson:
                    correlation_json.append(lineJson)
                elif "power" in lineJson:
                    pass
                elif lineJson == {}:
                    pass
                else:
                    print(lineJson)
                    raise TypeError
        print("file done")

        correlation = {}
        for j in correlation_json:
            if "start" in j:
                correlation_id = int(j["correlation_id"])
                correlation[correlation_id] = j
        del correlation_json
        print("correlation done")

        for j in allocations_json:
            obj = make_allocation(j)
            self.allocations[obj.id_] = obj
        del allocations_json
        print("allocation done")

        for j in values_json:
            alloc = self.allocations[int(j["allocation"])]
            val = Value(j, alloc)
            self.values[val.id] = val
            graph_handle_value(val)
        del values_json
        print("value done")

        for j in apis_json:
            inVals = [self.values[int(i)] for i in j["inputs"]]
            outVals = [self.values[int(o)] for o in j["outputs"]]

            if j["name"] == "cudaLaunch":
                correlation_json = correlation[int(j["correlation_id"])]
                api = CudaLaunch(j, correlation_json, inVals, outVals)
            else:
                api = API(j, inVals, outVals)

            self.apis[api.id] = api
            graph_handle_api(api)
        del apis_json
        print("apis done")





