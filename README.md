# 
Wrapper for netCDF read/write utilities  
Author: Alex T. Chartier (Johns Hopkins University Applied Physics Laboratory)  
  
Install the package in editable mode (from one directory up):  
```
$ python3 -m pip install -e .
```

Usage (assumes valid netCDF file 'ncfname' exists)

#1  Read the whole file, including the attributes  

```
file =  nc_utils.load_nc(ncfname)

```
#2  Read the variables from a file  
```
vars = nc_utils.ncread_vars(ncfname)  
```

#3  Write netCDF (note header-setting must be done via a function)  
```
def def_vars():  
    stdin = {'dims':['npts', 'npts'], 'type': 'float'}   
    return {  
        'testarr': dict({'units': 'none', 'long_name': 'test array to demonstrate code'}, **stdin),  
    }     

def set_header(rootgrp, out_vars):  
    rootgrp.description = 'test nc for numpy array writing'  
    return rootgrp  

out_fn = 'test.nc'  
out_vars = {'testarr': np.ones((10, 10)).asarray()}  
dim_defs = {'npts': len(out_vars['testarr'])}  
var_defs = def_vars()  
write_nc(out_fn, var_defs, out_vars, set_header, dim_defs, overwrite=True)  

```



