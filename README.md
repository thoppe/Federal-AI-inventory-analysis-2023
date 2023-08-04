# Federal AI inventory analysis 2022
Analysis of the projects reported on the Federal inventory in 2022

## Data collection

Projects were downloaded from the [AGENCY INVENTORIES OF AI USE CASES](https://www.ai.gov/ai-use-case-inventories/)

> Consistent with this principle of transparency, EO 13960 directed agencies to conduct an annual inventory of their AI use cases, and to publish them to the extent possible. As specified by EO 13960, agencies' inventories are not required to include AI use cases that are classified, sensitive, used in defense or national security systems, used by the Department of Defense or Intelligence Community, embedded within common commercial products, or used for AI research and development activities.

Each inventory was downloaded and saved to [data/department_org_src](data/department_org_src).
All data were collected on Aug 3rd, 2023 and may not reflect any updates on ai.gov.
Basic stats, information, and links can be found [here](data/high_level_stats_from_AI_gov.csv).

## Data processing

Most Departments provided some form of machine readable table or easily parsed web version. Some only provided PDFs (HHS, Commerce, Energy, Treasury, Justice) and these required considerable human parsing along with a custom script using

...
