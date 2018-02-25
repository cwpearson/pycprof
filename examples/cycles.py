#! /usr/bin/env python

from __future__ import absolute_import, print_function

import sys

import networkx as nx

from pycprof.profile import Profile

print("Reading profile...")
profile = Profile(sys.argv[1])
print("done")

cycle = nx.find_cycle(profile.graph)

if cycle == []:
    print("no cycles")
    sys.exit(0)

nodes = [u for (u,v) in cycle] + [cycle[-1][1]]
for node in nodes:
    print(node, node.id)
