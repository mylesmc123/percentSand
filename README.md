# Percent sand Raster to initial/constant loss rates for various AEP events

GLDAS soil textures source; https://ldas.gsfc.nasa.gov/gldas/soils/
USACE Ft. Worth District provided a lookup table of percent sand to initial/constant loss rates for various AEP events.

This script will read in the GLDAS soil texture data and map it clipped over the GLO watershed extent.
The script will then use the zonal statistics tool to calculate the percent sand for each subbasin (TBD).
The script will then use the lookup table to assign the appropriate loss rate to each subbasin based on the percent sand.
