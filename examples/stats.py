#! /usr/bin/env python

from __future__ import absolute_import, print_function

import sys

import networkx as nx

from pycprof.profile import Profile
from pycprof.dom import Value, API

print("Reading profile...", end='')
profile = Profile(sys.argv[1])
print("done")


print("Allocations: {}".format(len(profile.allocations)))
print("Values: {}".format(len(profile.values)))
print("API calls: {}".format(len(profile.apis)))

sources = set(n for n in profile.graph.nodes if (profile.graph.out_degree(n) != 0 and profile.graph.in_degree(n) == 0))
sinks = set(n for n in profile.graph.nodes if (profile.graph.out_degree(n) == 0 and profile.graph.in_degree(n) != 0))
orphans = [n for n in profile.graph.nodes if (profile.graph.out_degree(n) == 0 and profile.graph.in_degree(n) == 0)]
print("sources: {}".format(len(sinks)))
print("sinks: {}".format(len(sources)))
print("orphans: {}".format(len(orphans)))
for o in orphans[:5]:
    print("  ", o.id)
for o in orphans:
    if o.id == 4322:
        print("  ", o.id, o)

longest_path = nx.dag_longest_path(profile.graph)
print("Longest path: {}".format(len(longest_path)))
print("  values: {}".format(len([v for v in longest_path if isinstance(v, Value)])))
print("  apis: {}".format(len([v for v in longest_path if isinstance(v, API)])))