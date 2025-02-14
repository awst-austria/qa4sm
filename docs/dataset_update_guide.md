# How to add a new dataset (version) to QA4SM

QA4SM currently supports a number of pre-intergrated datasets. These should act as state-of-the-art reference data
for users to compare their uploaded research data to.

This guide describes how a new, previously unsupported dataset can be added to the service. 
The procedure to add a new version for an existing dataset to the application (e.g. ISMN_20191222 -> ISMN_20210131) 
requires only some of the steps to integrate a complete new dataset; these steps will be highlighted.
Data preparation (generation of the NetCDF files containing the data and all previous steps) is *not* part of this guide.
For this there are usually separate packages at TUW-GEO Github (e.g. [smos](https://github.com/TUW-GEO/smos), 
[smap](https://github.com/TUW-GEO/smap_io), [gldas](https://github.com/TUW-GEO/gldas), 
[ecmwf_models](https://github.com/TUW-GEO/ecmwf_models), etc.)

In summary, adding a new dataset requires:
    - Getting the raw data from some external source
    - Reformatting them into one of the [pynetCF](https://github.com/TUW-GEO/pynetcf) format that is used by all datasets in QA4SM
    - **Implementing the new dataset in QA4SM and uploading it to the server (this guide)**
    - Testing and deploying a new version of the application to the production instance
        - i) **local development** -> ii) merge into GitHub repository -> iii) deploy to test instance -> iv) deploy to production instance (you probably only to the first step)

## Prerequisites

1) You have a prepared a time series dataset and a reader class that implements a ``.read(lon, lat)`` function (compare with
   other datasets in the service). You know that the read function returns the correct time series for that location.
2) You have a Dataset name and Version name in mind for the data you want to add. You know what kind of filters you 
   want to implement for your dataset and if they are already available in the service or not.
3) You have [ssh access](https://www.digitalocean.com/community/tutorials/how-to-use-ssh-to-connect-to-a-remote-server)
   to the ``qa4sms1.geo.tuwien.ac.at`` server (if not, GEO IT can give you access).

To put data on the AWST-internal test system, you need access to AWST's VPN / 
internal network and also have your ssh key added to the authorized_keys file of 
that VM. Contact Zoltan (bakcsa@awst.at) for details.

## Update Fixtures

Make sure to checkout the fixture submodule at the latest state (``git submodule init && git submodule update``).
Then make a new branch for your dataset
```shell
cd .../validator/fixtures
git checkout -B new_dataset
```

### Variables fixture

Every dataset integrate a soil moisture variable to use in a validation run. If you add a new version for an existing
dataset, you can usually use the same variable as in the previous version. If you add a completely new dataset, you
have to add a variable. If the variable name or the unit in the netcdf time series files has changed for a version, 
you might have to add a new variable too. Let's assume the variable is not there yet.

1) Add a new entry to the ``variables.json`` fixture file and assign a new "pk" ID.
2) Add the fields ``short_name`` (how the soil moisture variable is called in the netcdf time series files)
3) Add a ``pretty_name`` (a nice, descriptive name to use in plots, not too long)
4) Define the correct ``unit`` for your dataset.
5) Define the lowest allowed ``min_value`` (usually 0) and the maximum allowed ``max_value`` (usually 1 or 100, depending on the units).

### Filters fixture

If you want to provide options to subset your time series based on certain fields in the record to e.g. select or exclude data under certain
conditions (e.g. to pick only data from one overpass), you need to define data filters. Most filters are dataset specific,
but you might be able to re-use some (e.g. filter "1" is used in almost all versions.). Especially when a dataset already
exists and you just add another version, you probably use the same filters as before.

#### Defining new filters

Filters are a way of selecting datapoints in a time series under certain conditions.
``SELECT ROWS WHERE <FIELD> <OPERATION> <THRESHOLD>``.
There are currently 2 types of filters in QA4SM. "parameterised" filters use a
variable threshold (that the user can pick), while the "normal" (non-parameterised)
filters are hard-coded in the source code.

If the filter you need is not yet available (e.g. all datasets use the "1" filter to drop , define the filter parameters in the fixture
and the filter logic in the source code at `validator/validation/filters.py`. Let's assume

**Fixtures**

1) Add a new entry with a new "pk" ID, pick a descriptive filter name and provide a description and help text
2) Decide whether you need a parameterised filter or if you want to hard-code the filter logic. And set the 
   "parameterised" field to true or false. If the filter is "parameterised", also provide the default threshold as a 
   string in ``default_parameter``, otherwise "null".
3) The ``dialog_name`` is probably "null".
4) The fields ``to_include`` and ``to_exclude`` allow to connect multiple filters
   and make them mutually inclusive or exclusive. 
5) If you set ``default_set_active`` to "true", the filter will be turned
   on by default. 
6) ``readonly`` means that the filter cannot be changed by the user in the GUI.

**Code**

Having defined the filters in the fixtures, add the filter logic to the python code at
`validator/validation/filters.py` (this is a bit of a mess still). 
Just check the other filters available to see how it works. You can use whatever necessary to select the data, use basic 
operations (>, <, ==), regular expressions, pytesmo adapters, bitwise selectors, etc.

If a filter requires a certain column in the dataset, make sure to add it to the variables to read in `get_used_variables`.
In the end the filter list goes to a 
pytesmo [AdvancedMaskingAdapter](https://github.com/TUW-GEO/pytesmo/blob/8812f9f30203845b4bc8ad0b2f00ba64512137a6/src/pytesmo/validation_framework/adapters.py#L254),
which applies all filters in order and only keeps the data that fulfills all conditions. These data are then used for the validation.

### Version fixture

1) Add a new entry to the end of the ``versions.json`` fixture file (choose the next free "pk" version id).
2) Fill out all fields. Pick a (short, unique) short_name (no spaces) and (descriptive) pretty_name, e.g. "SMOSL2_v700", and "v700". 
3) Fill out the help text in line with the other datasets
4) Provide the first and the last available date of the new time series in the ``time_range_start`` and ``time_range_end`` field. 
5) If your dataset covers only a spatial subset (usually we only add global dataset because everything regional is not very 
   useful to other people), add the bounding box (check e.g. the CGLS_CSAR_SSM1km_V1_1 data), otherwise add "null". 
6) Add the ID of the filters to use to the ``filters`` list. If a previous version for your dataset
   exists, you probably use the same filters.

### Dataset fixtures

You only need to add a new Dataset to the fixtures if there is no previous version
for your dataset in the service. Otherwise skip this step.

1) Add a new entry to the end of the ``datsets.json`` fixture file (choose the next free "pk" dataset id).
2) Fill out all fields. Pick a (short, unique) short_name (no spaces) and (descriptive) pretty_name, e.g. "SMAP_L2" and "SMAP L2". 
3) For the ``storage_path`` use `testdata/input_data/<SHORT_NAME>/`. 
4) Add the description, source and reference fields  in line with the other datasets. 
5) ``is_spatial_reference`` should be false, except if the dataset is ALWAYS the spatial reference in a validation run (only for ISMN).
6) add the ``version`` field with the version ID you picked in the previous step. 
7) Add the ``variables`` field and assign the variable for this dataset from the previous step. 
8) The ``resolution`` should be chosen to match the dataset grid. For L2 data, this is usually
   in "km" for L3 in "deg". It's not too much of a problem if this value is not exact (it defines the level of detail
   for maps). Rather pick a too large than too small value here, otherwise there might be gaps/stripes in the plots. 
9) The ``user`` is usually "null" except if a dataset should be private and only accessible to a certain user group.
   In that case (e.g. for the SMOS L2 experimental data) you can add "1" for now, and later - after deployment - assign
   the real user(s) in the admin panel, that should have exclusive access.

## Add reader
If you add a new dataset, you have to define the reader. Theoretically, each version can can have a different reader, 
although in practice, usually different versions of the same dataset also use the same reader (so you probably can skip this
step if you just add a new version of an existing dataset). 
Make sure the reader class for the new dataset is created correctly in `validator/validation/readers.py`. Don't forget
to include ``ioclass_kws={'read_bulk': True}`` for all time series datasets, or processing will be slowed down significantly!

If you have defined any filters before, make sure that they work correctly with the reader!

### Reader with time series extensions
Some dataset versions consist of two (compatible) temporal subsets, a base record and a temporal extension record. 
The temporal extension part is regularly updated by the [qa4sm airflow](https://github.com/awst-austria/qa4sm-airflow) 
service. In this case there is a wrapper ``ReaderWithTsExtension`` for the 2 readers that sticks the 2 time series 
together upon using the dataset in a validation run.

## Add testdata

Currently, all datasets in QA4SM are automatically tested. A very basic parameterised test is automatically
created for each dataset in the service that checks at least if the reading works 
and if the data can be used in a validation run. Therefore, a small data sample for 
every dataset / version  that is implemented in the service needs to be provided 
in the [testdata repository](https://github.com/awst-austria/qa4sm-testdata). Make sure that the testdata is ALWAYS
provided over Hawaii (usually cells 165 and 166), and include the grid file as well.

1) Check out / clone the testdata repository
2) If you add a completely new dataset, add the directory from the ``storage_path`` defined in the ``dataset.json`` fixture 
   to the `testdata/input_data` directory. Data for a version has to be stored in a subdirectory which has the 
   [same name as the version](https://github.com/awst-austria/qa4sm/blob/02032c0389ad4d0db14e54c85b7e1cb8b6592201/validator/validation/readers.py#L120).
3) Add the `grid.nc` file and data over Hawaii. The files should not be too large, we want the testdata repo to remain as small as possible.
4) Make sure that your testdata is not empty for the (nearest) test location (see ``test_readers()`` in `tests/test_validation.py`).
   Currently, the test reads data closest to Lon: -155.42°, Lat: 19.87°. If necessary, fake some testdata, but make sure that your file structure
   does not change (otherwise the reader might not work anymore).
5) Finally, when the testdata is updated, commit and push / open a PR to the master branch of the testdata repo (you should do this only 
   once you are sure that the implementation was successful)

## Local testing

To test if the update was successfully update the database and launch your local instance
(see the developers guide). Remember to check the .log file (the path is defined in your 
`valentina/settings.conf` file) if something goes wrong, as it might point you towards the problem.

1) Run ``pytest`` to make sure that all unit tests pass.
2) Run a validation over Hawaii through the GUI of your local instance (where the testdata is available) 
   and make sure that some results are produced.
3) Optional: At TUW we have a copy of the service data at `~/shares/climers/Projects/QA4SM_HR/07_data/SERVICE_DATA`. You can call 
   ``python manage.py setdatasetpaths`` to change the data root directory and use the full dataset collection, instead of the
   testdata (``python manage.py getdatasetpaths`` to check). Afterwards, you can run some larger-scale tests anywhere.
4) If everything works, push the testdata, and make sure it gets merged (if you haven't done it yet). Then make sure your testdata submodule
   points to the latest commit (with the new testdata, or it won't be found when the branch is checked out). The same applies to the fixtures submodule.
   Commit your changes, and open a Pull Request to qa4sm.
5) Make sure that all automated tests in the pull request pass, and that someone reviews and merges it.


## Copying data to the qa4sms1 server

Before your changes can be used on the production or test instance, the new dataset has to be copied to the server.
1) ssh onto qa4sms1. CD into the data directory (`/qa4sm/data`) and make a new subfolder for your dataset and, for now,
   allow writing into it
   ```shell
   sudo mkdir /qa4sm/data/<DATASET>/<VERSION>
   sudo chmod -R 777 /qa4sm/data/<DATASET>/<VERSION>
   ```
2) From your local PC, use the ``scp`` (or rsync) command to transfer the data to the server, into the correct directory. e.g,
   ```shell
   scp /home/wpreimes/shares/climers/Projects/QA4SM_HR/07_data/SERVICE_DATA/SMOS_SBPCA/V781_FinalMetrics/* qa4sms1:/qa4sm/data/SMOS_SBPCA/V781_FinalMetrics
   ``` 
3) Back on the server, set the permissions of your data directory (again)
   (``sudo chmod 775 -R /qa4sm/data/<DATASET>/<VERSION>``) or the docker 
   container where QA4SM runs, might not be able to read the data.

## Testing after deployment

If the data is available on the server, and your code has been merged, everything is in place to be deployed. Deployments
are handled by AWST. When your changes are deployed to the test instance, perform another round of testing to make sure 
that everything will work later on the production instance.