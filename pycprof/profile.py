from __future__ import absolute_import, print_function

import networkx as nx

from pycprof.dom import API, Allocation, Value
from pycprof.reader import Reader


class Profile:
    def __init__(self, path):
        self.values = {}
        self.apis = {}
        self.allocations = {}
        self.graph = nx.DiGraph()

        pass1 = {Value: self.handle_value,
                 Allocation: self.handle_allocation}
        pass2 = {API, self.handle_api}
        with Reader(path) as input_file:
            input_file.run_pass(pass1)
            input_file.run_pass(pass2)

    def handle_value(self, obj):
        self.values[obj.id_] = obj
        self.graph.add_node(obj)

    def handle_allocation(self, obj):
        self.allocations[obj.id_] = obj

    def handle_api(self, api):
        self.apis[api.id_] = api

        if "cudaLaunch" in api.functionName:
            for i in api.inputs:  # input transfers
                inVal = self.values[i]
                self.graph.add_edge(api, inVal)
            for o in api.outputs:  # output transfers
                outVal = self.values[o]
                self.graph.add_edge(outVal, api)
        elif "cudaMemcpy" == api.functionName:
            assert len(api.inputs) == 1
            assert len(api.outputs) == 1
            srcVal = self.values[api.inputs[0]]
            dstVal = self.values[api.outputs[0]]
            self.graph.add_edge(dstVal, srcVal)
        else:
            print("Unexpected api", api.functionName)
            raise TypeError
