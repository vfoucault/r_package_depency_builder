from resolv_deps import ResolveRDeps
from pprint import pprint

deps = ResolveRDeps(mod_list=['vmsbase'], download=False)

pprint(deps.result)

