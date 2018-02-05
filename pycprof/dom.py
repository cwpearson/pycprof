from __future__ import absolute_import, print_function

import json

class AddressSpace(object):
    def __init__(self, o):
        self.type = str(o["type"])

class Location(object):
    def __init__(self, j):
        self.type = str(j["type"])
        self.id_ = int(j["id"])

    def __str__(self):
        return "Location{type:" + self.type + ", id_:" + str(self.id_) + "}"

    def __eq__(self, other):
        if isinstance(other, Location):
            return (self.type == other.type) and (self.id_ == other.id_)
        return False

    def __ne__(self, other):
        return not self == other

class Value(object):
    def __init__(self, j):
        self.id_ = int(j["id"])
        self.size = int(j["size"])
        self.pos = int(j["pos"])
        self.allocation_id = int(j["allocation"])
        self.initialized = j["initialized"]


class Allocation(object):
    def __init__(self, j):
        self.id_ = int(j["id"])
        self.pos = int(j["pos"])
        self.size = int(j["size"])
        self.address_space = AddressSpace(json.loads(j["addrsp"]))
        self.mem = str(j["mem"])
        self.loc = Location(json.loads(j["loc"]))


class API(object):
    def __init__(self, j):
        self.id_ = int(j["id"])
        self.functionName = j["name"]
        self.symbol = j["symbolname"]
        self.device = int(j["device"])

        inputs = j["inputs"]
        outputs = j["outputs"]
        if inputs == "":
            self.inputs = []
        else:
            self.inputs = [int(x) for x in inputs]
        if outputs == "":
            self.outputs = []
        else:
            self.outputs = [int(x) for x in outputs]

        if "dstCount" in j:
            self.dstCount = int(j["dstCount"])

class Dependence(object):
    def __init__(self, j):
        self.tid = int(j["tid"])
        self.dst = int(j["dst_id"])
        self.src = int(j["src_id"])
        self.api_cause = int(j["api_cause"])