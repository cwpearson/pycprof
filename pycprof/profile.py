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

        def handle_allocation(obj):
            self.allocations[obj.id_] = obj

        def handle_value(obj):
            assert isinstance(obj, Value)
            if not isinstance(obj.allocation_id, Allocation):
                obj.allocation = self.allocations[obj.allocation]

            self.values[obj.id_] = obj
            self.graph.add_node(obj)

        def handle_api(api):
            for n, i in enumerate(api.inputs):
                api.inputs[n] = self.values[i]
            for n, o in enumerate(api.outputs):
                api.inputs[n] = self.values[o]

            self.apis[api.id_] = api


            if "cudaMemcpy" in api.functionName or "Bcast" in api.functionName or "AllReduce" in api.functionName:
                for srcVal in api.inputs:
                    for dstVal in api.outputs:
                        self.graph.add_edge(dstVal, srcVal)
            else:
                for inVal in api.inputs:  # input transfers
                    self.graph.add_edge(api, inVal)
                for outVal in api.outputs:  # output transfers
                    self.graph.add_edge(outVal, api)


        pass1 = {Allocation: handle_allocation}
        pass2 = {Value: handle_value}
        pass3 = {API: handle_api}
        with Reader(path) as input_file:
            input_file.run_pass(pass1)
        with Reader(path) as input_file:
            input_file.run_pass(pass2)
        with Reader(path) as input_file:
            input_file.run_pass(pass3)
