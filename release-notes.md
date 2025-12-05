QA4SM v3.4.0 - Release notes 2025-12-05
======================================================
# Updates
1. Added Dataset ESA CCI SM combined medium resolution.
2. Improved test performance by adding conftest.py to reduce execution time.

# Fixes
1. Fixed anomaly calculation bug.
2. Updated map to include all ISMN stations.
3. Fixed ISMN legend display issue on the map in dark mode.
4. Fixed threshold-filter label visualization issue.


QA4SM v3.3.0 - Release notes 2025-11-17
======================================================
# Updates
1. Added support for ESA CCI SM GAPFILLED v09.2.
2. Upgraded the frontend framework: Angular and PrimeNG updated to v20, improving performance and long-term compatibility.

# Fixes
1. The validation name field is now correctly limited to 80 characters. A clear user notification and input constraint have been introduced to prevent errors.

# New features
1. A fully redesigned plots interface has been introduced:
Improved visualization clarity
Enhanced color schemes and layout consistency
More intuitive user experience for exploring validation results


QA4SM v3.2.2 - Release notes 2025-09-29
======================================================
# Updates
1. New ASCAT version H121
2. User manual model discarded and PDF added to the repository instead

# Fixes
1. Comparison module re-introduced

# New features
1. Additional format check with improved feedback for user uploads
2. Improved documentation for upload and advanced plotting
3. Basic public API with documentation to use the service via CLI
4. Added is_scattered_data to the validator dataset model

QA4SM v3.2.1 - Release notes 2025-07-28
======================================================
# Updates
New dataset versions: 
ISMN: Version 20250617, Extended time period, additional sensors
ESA_CCI_active_passive_combined: Version 9.2, time until 2024-12-31
ESA_CCI_RZSM: New rootzone soilmoisture product, time until 2024-12-31, 
	different rootzone soiltmoisture layers: 0-10 cm, 10-40 cm, 40 cm - 1m + weighted average over 1 meter
ERA5, ERA5_LAND: New layers swvl1-4, stl1-4, 
GLDAS: time extension to 2024-12-31

QA4SM v3.2.0 - Release notes 2025-06-19
======================================================
# Updates
1. Added new dataset versions ( ESA_CCI_SM_(active, passive, combinded) V9.2 and ESA_CCI_RZSM V9.2)

QA4SM v3.1.0.1 - Release notes 2025-05-13
=======================================================
# Fixes
1. Missing filters added

QA4SM v3.1.0 - Release notes 2025-05-12
=======================================================
# Updates
1. Automatic account verification via email
2. Handling of validation config reloading with outdated datasets
3. Outdated dataset versions removed
4. SMAP3 data v9 added 
5. Variable now stored in version model, not dataset model
6. 'Deleted validation' model added, stores metadata on removed validations
7. User data can be used as spatial reference

QA4SM v3.0.4 - Release notes 2025-03-24
=======================================================
# Updates
1. Default permanent validation removal retrieved

# New features
1. Validation filtering added

QA4SM v3.0.3 - Release notes 2025-03-18
=======================================================
# Updates
1. Non-permanent validation removal updated

QA4SM v3.0.2 - Release notes 2025-03-12
=======================================================
# Updates
1. Pytesmo version updated

QA4SM v3.0.1.2 - Release notes 2025-03.09
=======================================================
# Updates
1. Docker settings updated

QA4SM v3.0.1.1 - Release notes 2025-03.03
=======================================================
# Updates
1. Docker settings updated

QA4SM v3.0.1 - Release notes 2025-02-27
=======================================================
# Updates
1. Docker settings updated

QA4SM v3.0.0 - Release notes 2025-02-23
=======================================================

# Updates
1. Python updated to 3.12
2. PostgreSQL updated to version 17

# New features
1. Log in via modal window


