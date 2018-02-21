from __future__ import absolute_import
from __future__ import print_function

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
    def __init__(self, j, allocation):
        self.id = int(j["id"])
        self.size = int(j["size"])
        self.pos = int(j["pos"])
        self.allocation = allocation
        self.initialized = j["initialized"]


class Allocation(object):
    def __init__(self, j):
        self.id_ = int(j["id"])
        self.pos = int(j["pos"])
        self.size = int(j["size"])
        self.address_space = AddressSpace(json.loads(j["addrsp"]))
        self.mem = str(j["mem"])
        self.loc = Location(json.loads(j["loc"]))


class PinnedAllocation(Allocation):
    def __init__(self, j):
        Allocation.__init__(self, j)

class PageableAllocation(Allocation):
    def __init__(self, j):
        Allocation.__init__(self, j)

class API(object):
    def __init__(self, j, inputs, outputs):
        self.id = int(j["id"])
        self.functionName = j["name"]
        self.symbol = j["symbolname"]
        self.device = int(j["device"])
        self.inputs = inputs
        self.outputs = outputs
        self.api_start = int(j["start"])
        self.api_end = int(j["end"])

class CudaLaunch(API):
    def __init__(self, j, correlation_json, inputs, outputs):
        API.__init__(self, j, inputs, outputs)
        self.kernel_start = int(correlation_json["start"])
        self.kernel_end = int(correlation_json["end"])

class Dependence(object):
    def __init__(self, j):
        self.tid = int(j["tid"])
        self.dst = int(j["dst_id"])
        self.src = int(j["src_id"])
        self.api_cause = int(j["api_cause"])

def make_allocation(j):
    return {
        "pagelocked": PinnedAllocation(j),
        "pinned": PageableAllocation(j)
    }.get(j["mem"], Allocation(j))
