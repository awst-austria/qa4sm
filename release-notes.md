QA4SM v1.5.0 - Release notes 2021-03-29
=======================================================

# New features

1.  The possibility of reloading settings of an existing validation;
2.  The possibility of attaching a published validation to 'my results' page;
3.  SMOS, SMAP and ASCAT datasets can be used as the reference ones;
4.  A quick inspection table with a summary of basic metrics of a validation;
5.  Sorting on result pages;
6.  Searching for an existing validation with exactly the same settings as the one which is about to be run;
7.  CDF matching included.


# Improvements

1.  Default time range depends on the chosen datasets;
2.  New buttons layout;
3.  New datasets: CCI v6, C3S v202012, ISMN 20210131;
4.  Results where there are too few input data tuples are masked out;
5.  Temporal matching improved.



# Other changes

1. In the resulting netCDF file:
  - information on the actual time range covered by each dataset used in the validation included;
2. Bugs fixed:
  - problem with loading ISMN networks on dialog window;
  - problem with the lack of plots in validations where the same dataset with the same version was used more than once.
