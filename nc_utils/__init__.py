"""
nc_utils.py
Some basic netCDF and other file manipulation routines 

Author: Alex T. Chartier, 2023
"""
import os
import datetime as dt
import numpy as np
import pdb 
import errno
import netCDF4
import pickle as pkl
import pandas as pd
import xarray

def load_nc(fname):
    fn = os.path.expanduser(fname)
    if not os.path.isfile(fn):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fn)
    #try:
    #    from netCDF4 import Dataset
    return netCDF4.Dataset(fn, 'r', format='NETCDF4')
    #except:
    #    import scipy.io.netcdf as nc
    #    return nc.netcdf_file(fn, 'r', version=2)


def ncread_vars(fname):
    if isinstance(fname, str):
        fin = load_nc(fname)
    elif isinstance(fname, netCDF4._netCDF4.Dataset):
        fin = fname
    else:
        raise ValueError('fname needs to be string or netCDF dataset')
    out = {}
    """
    if hasattr(fin, 'groups'):
        for key in fin.groups.keys():
            out[key] = {}
            for k in fin.groups[key].variables.keys():
                out[key][k] = fin.groups[key].variables[k][...]
    else:
    """
    for key in fin.variables.keys():
        out[key] = fin.variables[key][...]
    fin.close()
    return out 


def write_nc(
        fname, var_defs, out_vars, set_header, dim_defs, 
        overwrite=True, atts=None,
):
    fn = os.path.expanduser(fname)
    if overwrite:
        try:
            os.remove(fn)
        except:
            None
    else:
        assert not os.path.isfile(fn), \
        '%s already exists and overwrite set to False. Stopping...' % fn
    os.makedirs(os.path.dirname(fn), exist_ok=True)

    # Create netCDF file
    try:
        from netCDF4 import Dataset
        print('writing with netCDF4')
        rootgrp = Dataset(fn, 'w', format='NETCDF4')
    except:
        import scipy.io.netcdf as nc
        print('writing with scipy')
        rootgrp = nc.netcdf_file(fn, mode="w")

    if atts:
        rootgrp.setncatts(atts)

    write_grp(rootgrp, dim_defs, set_header, var_defs, out_vars)
    rootgrp.close()
    print('File written to %s' % fn)


def write_grp(grp, dim_defs, set_header, var_defs, out_vars):
    # write all the dimensions, variable definitions and variables into a group
    # (could be nested or overall group)

    # Define the dimensions
    for k, v in dim_defs.items():
        grp.createDimension(k, v)  
    
    # Write the header stuff
    grp = set_header(grp, out_vars)

    # Define variables 
    ncvars = {}  
    for key, var in var_defs.items():
        vd = [var['dims'],] if type(var['dims']) == str else var['dims']
        ncvars[key] = grp.createVariable(key, var['type'], vd)
        ncvars[key].units = var['units']
        ncvars[key].long_name = var['long_name']

    # Write to variables
    for key, var in out_vars.items():
        if (len(var.shape) == 0) or (len(var.shape) == 1): 
            ncvars[key][:] = var 
        elif len(var.shape) == 2:
            ncvars[key][:, :] = var 
        elif len(var.shape) == 3:
            ncvars[key][:, :, :] = var 
        elif len(var.shape) == 4:
            ncvars[key][:, :, :, :] = var 


def example_write_nc():
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


def pickle(struct, pkl_fn):
    """ Pickle write wrapper including filename and directory handling """
    pkl_fn = os.path.abspath(os.path.expanduser(pkl_fn))
    os.makedirs(os.path.dirname(pkl_fn), exist_ok='True')
    with open(pkl_fn, 'wb') as f:
        pkl.dump(struct, f)
    print('Wrote to %s' % pkl_fn)


def unpickle(pkl_fn):
    """ Pickle read wrapper including filename and directory handling """
    print('trying to unpickle %s' % pkl_fn)
    assert os.path.isfile(pkl_fn), 'no such file'
    pkl_fn = os.path.abspath(os.path.expanduser(pkl_fn))
    with open(pkl_fn, 'rb') as f:
        struct = pkl.load(f)
    print('Loaded %s' % pkl_fn)

    return struct


def write_netcdf_from_df(df, metadata, global_atts, nc_fname):
    """ write dataframe to netCDF """
    #TODO Make this all generic
    # Add POSIX time
    df['POSIXtime'] = (df.index - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    
    # create xarray Dataset from Pandas DataFrame 
    xr = xarray.Dataset.from_dataframe(df)

    # add variable attribute metadata  
    for k, v in metadata.items():
        xr[k].attrs = v

    # add global attribute metadata
    xr.attrs = global_atts

    # save to netCDF
    xr.to_netcdf(nc_fname)


def example_df_metadata_define():
    return {
        'POSIXtime': {'units':'Seconds', 'long_name':'POSIX time (seconds since 1/1/1970)'},
        'Latitude': {'units':'degrees', 'long_name':'Latitude'},
        'Longitude'].attrs = {'units':'degrees', 'long_name':'Longitude'},
        'Radius': {'units':'Metres', 'long_name':'Radius'},
        'Vn': {'units':'m/s', 'long_name':'North component of vi'},
        'Ve': {'units':'m/s', 'long_name':'East component of vi'},
        'Vc': {'units':'m/s', 'long_name':'Down component of vi'},
        'Viy': {'units':'m/s', 'long_name':'S/C right component of vi'},
        'Viy_error': {'units':'m/s', 'long_name':'error in S/C right component of vi'},
    }


def example_df_global_atts_define():
    return {
        'Conventions':'CF-1.6', 
        'title':'Swarm cross-track drift data', 
        'summary':'Data generated',
    }


def load_cdf(cdf_fn):
    """ loads generic CDF into a dict """
    cdf_fn = os.path.abspath(os.path.expanduser(cdf_fn))

    cdf = pycdf.CDF(cdf_fn)
    data = {}
    for k, v in cdf.items():
        data[k] = v[...]


    return data




if __name__ == '__main__':
    print('writing example netCDF file to demonstrate code')




