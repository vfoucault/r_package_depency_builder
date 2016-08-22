# -*- coding: utf-8 -*-
"""
Class that will generate a dependency graph
of R modules.
It will download each module dependency for the specified modules.
"""
import os
import shutil
import requests
from collections import deque


class ResolveRDeps:
    """
    the class itself.
    """

    def __init__(self, repo="http://cran.univ-paris1.fr", mod_list=[], download=False, dlpath='./packages'):
        """
        Instantiate the class
        @repo : The CRAN repository to fetch index from, default setted
        @mod_list : a list of module to resolve deps for, default empty
        @download : downlad each dependent module True/False
        @dlpath : the path to packages to if downloading
        """
        self.repo = repo
        self.depgraph = {}
        self.parsed_index = {}
        self.mod_list = mod_list
        self.result = None
        self.download = download
        self.dlpath = dlpath

        # now parse the index and generate the depgraph
        self.parse_index()
        self.generate_dep_graph()

        # Now search for the specified mods and print them
        if len(self.mod_list) > 0:
            self.result = self.fetch_result()
            if self.download:
                if not os.path.exists(self.dlpath):
                    os.mkdir(dlpath)
                for pkg in self.result[0]:
                    if pkg in self.parsed_index:
                        moddata = self.parsed_index[pkg]
                        self.download_module(pkg, moddata['Version'])




    def fetch_result(self):
        """
        print the result if mod_list is not null in __init__
        """
        retlist = [self.bfs_module(module) for module in self.mod_list]
        return retlist[0]


    def get_index(self):
        """
        this method will download and return the Package file from the CRAN repo
        """
        r = requests.get("%s/src/contrib/PACKAGES" % self.repo)
        return r.text

    def parse_index(self):
        """
        This method will parse the index file and cut the
        contents into a dict (self.depgraph)
        """
        index = self.get_index()
        # each module is separated by a double \n\n
        rawmodules = index.split("\n" * 2)
        # then each line in a module in divided with a single \n
        for rawmodule in rawmodules:
            # lines = [ x.split(":") for x in rawmodule.split("\n")]
            cleaned = dict(map(lambda x: [ y.strip() for y in x.split(":") ], rawmodule.replace("\n        "," ").splitlines()))
            self.parsed_index[cleaned['Package']] = cleaned
            self.depgraph[cleaned['Package']] = set([])
        return 1

    @staticmethod
    def parse_depends_imports(line):
        """
        simple static method for code clarification
        will only fetch the module names and discard the version from
        Imports and Depends dict entries"""
        deps = [x.split(" ")[0] for x in [x.strip() for x in line.split(",")]] or []
        return deps

    def generate_dep_graph(self):
        """
        Generate the dep graph
        will fetch the Imports & Depends, and inject them in
        the corresponding set
        """
        for pkg, moduleinfo in self.parsed_index.items():
            deps = []
            if 'Depends' in moduleinfo:
                deps += self.parse_depends_imports(moduleinfo['Depends'])
            if 'Imports' in moduleinfo:
                deps += self.parse_depends_imports(moduleinfo['Imports'])
            for dep in deps:
                self.depgraph[pkg].add(dep)

    def bfs_module(self, start_module):
        """
        Input : a dependency graph, the module name to look dependencies for.
        Output : A set of module, the dependencies for start_module
        This function will browse the self.depgraph to look for each connected module for start_module
        """
        visited = set([start_module])
        visited_queue = deque()
        visited_queue.append(start_module)
        while visited_queue:
            current_item = visited_queue.popleft()
            if current_item in self.depgraph:
                for depmodule in self.depgraph[current_item]:
                    if depmodule not in visited:
                        visited.add(depmodule)
                        visited_queue.append(depmodule)
        return visited


    def download_module(self, modulename, version):
        """
        Input : the module name to download and it's version.
        Output : Nothing
        This function will download the specified module from the CRAN repository.
        """
        url = "%s/src/contrib/%s_%s.tar.gz" % (self.repo, modulename, version)
        print "Downloading %s" % url
        response = requests.get(url, stream=True)
        with open("%s/%s" % (self.dlpath, os.path.basename(url)), "wb") as local_file:
            shutil.copyfileobj(response.raw, local_file)
        return 1

