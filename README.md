# Federal AI inventory analysis 2023
_Last updated September 1st, 2023_

**Abstract**: The Federal AI Inventory Analysis project for 2023 is a comprehensive examination of the public AI projects reported in the federal inventory during that collection cycle. The complexity of this task is due to the variation in reporting formats and the inclusion of non-machine-readable reports from different Departments and independent agencies.

The analysis includes data collection from published AI use case inventories, data preparation, which required a blend of manual parsing and automated processing, and the use of a high-powered language model (LLM) for summarizing the collected data. Themes were then extracted from these summaries to categorize projects into specific domains like security, infrastructure, and healthcare. Visualization was employed to understand the general clustering of projects, using OpenAI’s text-embedding model. The project also included a mechanism for daily data integrity checks and provided transparent cost calculations for API usage. The outcomes include detailed and summarized reports of AI projects, interactive visualizations, and insights into prominent AI themes across various federal Departments and agencies, thereby contributing to a transparent understanding of AI's role within the federal government.

**Disclaimer**: This project extensively utilized multiple Language Models (LLMs). While the results are valuable, they offer a broad overview of each project, theme, and the Federal AI portfolio. This analysis exclusively covers publicly released projects.

**Reports**: The methodology documented below has been utilized to create the following reports:

+ [AI Themes throughout the Federal Government](results/AI_themes.md)
+ [Complete Text of AI Projects by Agencies](results/AI_projects_full_text_by_Department.md)
+ [Summarized GPT Text for Project Descriptions](results/AI_projects_summary_text_by_Department.md)
+ [Prominent AI Highlights across Departments](results/AI_highlights_by_Department.md)


## Data collection

Projects were downloaded from [AGENCY INVENTORIES OF AI USE CASES](https://www.ai.gov/ai-use-case-inventories/), provided by the National AI Initiative Office (NAIIO).

> Consistent with this principle of transparency, EO 13960 directed agencies to conduct an annual inventory of their AI use cases, and to publish them to the extent possible. As specified by EO 13960, agencies' inventories are not required to include AI use cases that are classified, sensitive, used in defense or national security systems, used by the Department of Defense or Intelligence Community, embedded within common commercial products, or used for AI research and development activities.

Each inventory was downloaded and [saved](data/department_org_src).
All data were collected on September 1st, 2023 and may not reflect any updates on ai.gov or linked reports.
Basic stats, information, and links can be found [here](data/data_ingestion_statistics_AI_inv.csv).

### Data preparation

Most Departments provided some form of machine readable table or easily parsed web version. Some only provided PDFs (Commerce, Energy, Treasury, Justice, NASA) and these required considerable human parsing along with a [custom script](src/P0_parse_pdf2table.py) using [Camelot](https://github.com/camelot-dev/camelot). Entries that were exact duplicates in the Title and Summary were removed HHS (6), DOS (6), DOE (5).

After manual parsing and cleanup the record level data was saved to [data/record_level_information_FedAI_2023.csv](data/record_level_information_FedAI_2023.csv)

+ `Use_Case_ID` (automatically assigned by this project)
+ `Department_Code` (Acronym for the Department)
+ `Agency` (or Bureau / Institute as appropriate)
+ `Office` (or Center as appropriate)
+ `Title`
+ `Summary`
+ `Development_Stage` (if provided)
+ `Techniques` (methodologies, models, or AI techniques if provided)
+ `Source_Code` (link to source code if provided)

### Natural Language Processing

A high powered LLM (in this case Chat GPT: gpt-3.5-turbo) is used to summarize each response as the quality of the summaries provided by the agencies is variable. For example, consider the response from the IRS and the associated summary:

> **Projected Contract Award Date Web App** Projected contract award dates are generated with a machine learning  model that statistically predicts when procurement requests will become  signed contracts. Input data includes funding information, date / time of  year, and individual Contract Specialist workload. The model outputs  projected contract award timeframes for specific procurement requests.   'When will a contract be signed?' is a key question for the IRS and  generally for the federal government. This tool gives insight about when  each request is likely to turn into a contract. The tool provides a technique  other federal agencies can implement, potentially affecting $600 billion in  government contracts. Weblink: https://www.irs.gov/newsroom/irs- announces-use-of-projected-contract-award-date-web-app-that-predicts- when-contracts-will-be-signed.

> The IRS has developed a web app that uses a machine learning model to predict when procurement requests will become signed contracts. The tool provides valuable insight for the IRS and other federal agencies on when contracts are likely to be signed, potentially impacting $600 billion in government contracts.

Using the summarized response, we iteratively ask for a set of high level topics. The topics are human refined (human edits in parenthesis)

+ Artificial Intelligence in Healthcare (healthcare)
+ Data-driven approach using regional data and machine learning models (spatial)
+ Autonomous Maritime Awareness system (maritime)
+ Cyber Threat Intelligence Feed Correlation (cyber intelligence)
+ Security Operations with AI (security)
+ Environmental Monitoring with AI (environmental)
+ Prototype System for Global Audience Segmentation (customer service or engagement)
+ Power system resilience and grid operation (power systems)
+ Predictive maintenance and infrastructure monitoring (infrastructure)
+ Machine learning in various domains (dropped, generic)
+ Fraud Prevention System Prioritization (fraud)
+ Machine learning for wildfire damage assessment (dropped, small)

Each project was scored across the themes holistically by asking the LLM to return a JSON object. Observationally, this is a high recall medium precision task, so we further refined each positive response with an explanation of why the theme matched the project. By taking the final refinement step, about 25% of the projects were removed from their original theme.

|       | Theme                           | Projects |
|------------|---------------------------------|-------|
| 🔒         | security                        | 90    |
| 🏗️         | infrastructure                  | 72    |
| 🌍         | environmental                   | 66    |
| 🌍         | spatial                         | 63    |
| 🏥         | healthcare                      | 55    |
| 🔍         | cyber intelligence              | 25    |
| 🔌         | power systems                   | 24    |
| 🤝         | customer service or engagement  | 18    |
| 🌊         | maritime                        | 13    |
| 🕵️‍♂️       | fraud                           | 11    |
| 🔥         | wildfire                        | 1     |

## Visualization

To get a sense of the general clustering, each of the summarized projects were embedded through the latest OpenAI model (text-embedding-ada-002) and projected onto two dimensions using UMAP. A numpy array containing the embeddings is saved [here](data/GPT_embedding.npy). To interactively visualize the embeddings run `make streamlit`

![Visualization of Federal AI Projects](results/streamlit_demo.jpg)

### Costs calculation and data integrity 

Costs were calculated from a final run of the program, intermediate API calls during the exploration phase were not recorded.

```
Cost   : $0.79
Tokens : 393,474
Calls  : 1658
```

Each day, a github action is called to check the hash of the ai.gov source website. If the latest hash has not changed from `ac4984917f9a2195c37c6cd008d56ab1` then the data is up-to-date. If the hash has changed, some aspect of the website has been updated though it may not reflect a change in the data.

+ [Log of the daily hash](data/ai_gov_md5hash.csv)
+ [Github action](.github/workflows/md5_website_check.yml)
