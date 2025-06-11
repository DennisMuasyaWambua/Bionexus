# How to Fix the GDAL/GEOS Library Issue

## Problem
The BioNexus Gaia application requires GeoDjango which depends on the GDAL and GEOS C libraries. When these libraries are not installed, you'll see errors like:

```
OSError: /usr/lib/libgeos_c.so: cannot open shared object file: No such file or directory
```

## Solution
You have two options to resolve this issue:

### Option 1: Install the Required Libraries (Recommended)
For Ubuntu/Debian-based systems:
```bash
sudo apt-get update
sudo apt-get install -y binutils libproj-dev gdal-bin python3-gdal libgeos-dev
```

For other operating systems, please refer to the GeoDjango installation documentation:
https://docs.djangoproject.com/en/4.2/ref/contrib/gis/install/

### Option 2: Run Without GeoDjango Features (Temporary Workaround)
If you can't install the required libraries, we've temporarily disabled GeoDjango-dependent features in the codebase. This means:

1. The biodiversity app is disabled
2. The ai app is disabled (it depends on biodiversity)
3. The citizen app is disabled (it depends on biodiversity)
4. Only the basic user authentication and profile features are available

This is not recommended for production use but allows basic development and testing.

## Reverting the Temporary Changes
To revert the temporary workaround and use the full application:

1. Install the required GDAL/GEOS libraries as shown in Option 1
2. Edit `bionexus_gaia/settings.py` to:
   - Uncomment 'django.contrib.gis'
   - Uncomment all project apps
   - Restore the PostGIS database configuration
   - Uncomment the GDAL and GEOS library paths

3. Edit `bionexus_gaia/urls.py` to uncomment all the app URL includes

After making these changes, you should be able to run the full application with all features.