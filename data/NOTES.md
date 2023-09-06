Manually cleaned AI inventories should have the following columns

+ Use Case ID
+ Title
+ Summary
+ Department (top level)
+ Agency (secondary level)
+ Office (tertiary level) Office / Center / Institute / Bureau
+ Development Stage
+ Techniques
+ Source Code

Notes:

+ Use Case ID should be modified from the department response to be of the format `{DEPARMENT_CODE}-{ID:04d}` ID code. This ID will be manually generated as it seems to be inconnisitnat across the responses.
+ Deparment will be infered from the filename.
+ Filenames should be named `{DEPARTMENT_CODE}-{YEAR}.csv` where YEAR is 2023.
+ DOT has to be manually cleaned to remove the "REDACTED"