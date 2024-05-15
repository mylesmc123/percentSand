# GLDAS soil textures source; https://ldas.gsfc.nasa.gov/gldas/soils/
# USACE Ft. Worth District provided a lookup table of percent sand to initial/constant loss rates for various AEP events.

# This script will read in the GLDAS soil texture data and map it clipped over the GLO watershed extent.
# The script will then use the zonal statistics tool to calculate the percent sand for each subbasin (TBD).
# The script will then use the lookup table to assign the appropriate loss rate to each subbasin based on the percent sand.

# %%
import xarray as xr
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio
import rasterio.plot
from rasterio.plot import show
from rasterstats import zonal_stats
import rioxarray as rxr

gldas = 'GLDASp4_soilfraction_025d.nc4'
lookup_table = 'FtWorthLossRateTable.csv'
GLO_extent = 'GLO RAS Domain.geojson'

# %%
# open the GLDAS soil texture netCDF data in xArray
ds = xr.open_dataset(gldas)
ds
# %%
ds['GLDAS_soilfraction_sand'].plot()

# %%
# open the watershed extent shapefile in geopandas
glo = gpd.read_file(GLO_extent)
glo.plot()

# %%
glo.crs
# %%
# subset ds to the GLO watershed extent
bounds = glo.bounds
bounds

# %%
slice(bounds.minx.min(), bounds.maxx.max())
# %%
ds_zoomedOut = ds.sel(lon=slice(bounds.minx.min()-1, bounds.maxx.min()+1), lat=slice(bounds.miny.min()-1, bounds.maxy.min()+1))
ds_glo_extent = ds.sel(lon=slice(bounds.minx.min()+.1, bounds.maxx.min()-.1), lat=slice(bounds.miny.min()-.1, bounds.maxy.min()+.1))
# ds['GLDAS_soilfraction_sand'].plot()
# %%
# plot ds['GLDAS_soilfraction_sand'] with the GLO watershed extent on a basemap of Texas
fig, ax = plt.subplots(figsize=(10, 10))
ds_zoomedOut['GLDAS_soilfraction_sand'].plot(ax=ax)
glo.boundary.plot(ax=ax, color='black')
plt.show()
# %%
fig, ax = plt.subplots(figsize=(10, 10))
ds_glo_extent['GLDAS_soilfraction_sand'].plot(ax=ax)
glo.boundary.plot(ax=ax, color='black')
plt.show()
# %%
# get the zonal statistics for the soil fraction sand within the GLO watershed extent

# user rasterstats to get the zonal statistics for the soil fraction sand within the GLO watershed extent
zs = zonal_stats(glo, 
    ds_glo_extent['GLDAS_soilfraction_sand'].squeeze().values, 
    affine=ds_glo_extent['GLDAS_soilfraction_sand'].rio.transform(), stats=['mean'])
zs
# %%
# export ds_glo_extent['GLDAS_soilfraction_sand'] to a raster with a crs of EPSG:4326
ds_glo_extent['GLDAS_soilfraction_sand'].rio.to_raster('GLDAS_soilfraction_sand.tif', driver='GTiff', crs='EPSG:4326')
# %%
zs = zonal_stats(GLO_extent, 'GLDAS_soilfraction_sand.tif', stats=['mean'])
# %%
raster = rio.open('GLDAS_soilfraction_sand.tif')
affine = raster.transform

# %%
zs = zonal_stats(GLO_extent, 'GLDAS_soilfraction_sand.tif', stats=['mean'])

# %%
# because of an rasterstats error, that i didnt bother to fix,
#  the mean was taken from QGIS using the output percent sand raster.
mean = 0.391
# use the lookup table to assign the appropriate loss rate to the GLO watershed extent
lookup = pd.read_csv(lookup_table)
lookup
# %%
# add two columns to the lookup table for the initial and constant loss rates
lookup['Initial Abstrasction (in)'] = (
    (lookup['Initial Abstraction 100% Sand (in)'] - lookup['Initial Abstraction 0% Sand (in)'])
      * mean) + lookup['Initial Abstraction 0% Sand (in)']

lookup['Infitration Rate (in/hr)'] = (
    (lookup['Infiltration Rate 100% Sand (in/hr)'] - lookup['Infiltration Rate 0% Sand (in/hr)'])
        * mean) + lookup['Infiltration Rate 0% Sand (in/hr)']
# %%
lookup = lookup.round(2)
lookup.to_csv('GLOLossRateTable.csv', index=False)
# %%
