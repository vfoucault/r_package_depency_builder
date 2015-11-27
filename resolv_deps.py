"""
Program that will generate a dependency graph
of R modules.
It will download each module dependency for the specified modules.
"""

import re
import os
import sys
from urllib2 import urlopen, Request
from datetime import datetime
from collections import deque

BASE_URL = "http://cran.univ-paris1.fr/"
DEPGRAPH = {}
MODS_TO_PROCESS = []
PARSED_DICT = {}

def format_index(rawlines):
    """
    input : Raw index file (readlines())
    output : formated index (read())
    """
    formated_list = []
    index = 0
    ## Regexp used to remove leading spaces or new lines
    regexp = re.compile(" {1,}|\n")
    for line in rawlines:
        if line.startswith("        "):
            newline = "%s %s\n" %(formated_list[index-1].replace("\n", ""),\
             re.sub(regexp, "", line))
            formated_list[index-1] = re.sub(r'\([\ >=0-9\.-]{0,}\)', '', newline)
            index -= 1
        else:
            formated_list.append(re.sub(r'\([\ >=0-9\.-]{0,}\)', '', line))
        index += 1
    return ''.join(formated_list)

def parse_index(index):
    """
    Input : a formatted index files for the R modules.
    Output : a dictionary with the modules  :
    {modulename: {version : 'version', data: 'data' }}
    index is a formated text file that contains
    the modules list along with it's dependencies
    this function also init a dependency graph
    """
	## each block is spearated by a blank line, let's split it
    parsed_index = []
    parsed_dict = {}
    for mod in index.split("\n\n"):
        parsed_index.append(mod.split("\n"))
    ## let's create an Dictionary with the module name
    for module in parsed_index:
        ## every module name is in module[0], just need to remove the leading "package:" string
        modulename = module[0][9:len(module[0])]
        DEPGRAPH[modulename] = set([])
        version = module[1][9:len(module[1])]
        parsed_dict[modulename] = {'version' : version, 'data' : module}
    return parsed_dict

def update_deps_recurse(keys):
    """
    Input : a dictionary of all the modules, made from the index file parsed with parse_index
    Output : nothing
    this function will update the dependency graph for each modules.
    It will recurse itself until the smallest part can be reached.
    It's only a loop over a dictionary
    """
    regexp = re.compile("^Depends:|^Imports:")
    if len(keys) < 2:
        key = keys[0]
        value = PARSED_DICT[key]
        depends = [x for x in value['data'] if regexp.match(x)]
        if len(depends) > 0:
            for dep_module in depends:
                tmp1 = dep_module.replace("Depends:", "")
                tmp1 = tmp1.replace("Imports:", "")
                tmp1 = tmp1.split(",")
                for item in tmp1:
                    tmp2 = item.lstrip()
                    tmp2 = item.split(" ")
                    tmp2 = [x for x in tmp2 if x]
                    if len(tmp2) > 0:
                        DEPGRAPH[key].add(tmp2[0])
    else:
        length = len(keys)/2
        update_deps_recurse(keys[:length])
        update_deps_recurse(keys[length::])

def bfs_module(depgraph, start_module):
    """
    Input : a dependency graph, the module name to look dependencies for.
    Output : A set of module, the dependencies for start_module
    This function will browse the DEPGRAPH to look for each connected module for start_module
    """
    visited = set([start_module])
    visited_queue = deque()
    visited_queue.append(start_module)
    while visited_queue:
        current_item = visited_queue.popleft()
        if depgraph.has_key(current_item):
            for depmodule in depgraph[current_item]:
                if depmodule not in visited:
                    visited.add(depmodule)
                    visited_queue.append(depmodule)
    return visited

def download_module(modulename, version):
    """
    Input : the module name to download and it's version.
    Output : Nothing
    This function will download the specified module from the CRAN repository.
    """
    url = BASE_URL + "src/contrib/" + modulename + "_" + version + ".tar.gz"
    print "Downloading %s" % url
    filetodl = urlopen(url)
    with open("%s/%s" % ("./packages", os.path.basename(url)), "wb") as local_file:
        local_file.write(filetodl.read())

def main():
    """
	main prog
	This function will init the call to the various functions of this prog.
	"""
    ## Let's keep track of time for analysis
    starttime = datetime.now()
    ## Globals Call
    global PARSED_DICT
	## the INDEX file is PACKAGE
    req = Request(BASE_URL + "src/contrib/PACKAGES")
    response = urlopen(req)
    data = response.readlines()
    formated_index = format_index(data)
    ## Creating the dictionary from the index file.
    PARSED_DICT = parse_index(formated_index)
    ## Generate the Deps (updating the graph)
    keystoworkwith = PARSED_DICT.keys()
    update_deps_recurse(keystoworkwith)
    dependencies = set([])
    ## Let's browse the graph for each module to process
    for module in MODS_TO_PROCESS:
        deps = bfs_module(DEPGRAPH, module)
        dependencies.update(deps)
    print dependencies
    print "nbs deps %s" % len(dependencies)
    for dep in dependencies:
        if DEPGRAPH.has_key(dep):
            version = PARSED_DICT[dep]['version']
            download_module(dep, version)
    endtime = datetime.now() - starttime
    print "Running Time : %s " % endtime

if __name__ == "__main__":
    """
    main init & globals setup
    """
    ## init argv
    if len(sys.argv) > 1:
        sys.argv.pop(0)
        print "Module to process %s" % sys.argv
    ## init Globals
    MODS_TO_PROCESS = sys.argv
    main()
