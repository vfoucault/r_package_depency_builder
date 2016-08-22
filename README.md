# Python R Dependencies builder

a simple class to generate a dict of dependent packages for a list of R modules.
Useful for offline download and later install on cluster nodes.

## usage : 

```python
from resolv_deps import ResolveRDeps
from pprint import pprint

deps = ResolveRDeps(mod_list=['vmsbase'], download=False)

pprint(deps.result)

```

This will download all the required packages including 'vmsbase' into the './pacakges' directory

## Parameters : 

- ```repo``` (string): the CRAN repo to download packages and fetch index from. Default : http://cran.univ-paris1.fr
- ```mod_list``` (list) : a list of modules to fetch dependencies from. Default empty
- ```download``` (bool.) : Default False. specify True to download the required modules
-  ```dlpath``` (string) : the download path. Default ('./packages')

