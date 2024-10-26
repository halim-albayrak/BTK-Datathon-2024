# Datathon-2024

## Description
This project contains a dataset of student profiles and evaluation scores who have applied for scholarships through the Turkish Entrepreneurship Foundation since 2014. Based on this dataset, we aimed to predict the evaluation scores of students in 2023.

Evaluation Score = Indicates students' eligibility for receiving a scholarship based on certain criteria.

## Project Files
- Data Folder = Our Test and Train data, the data required for mapping and the data we obtained from external sources are in this file.

- 7_preprocess.ipynb = We have collected the analyses, various visualizations and the models we tried under this file.

- preprocess.py = Contains all the data preprocessing and exploratory data analysis (EDA) steps required for our model. This file includes data cleaning, feature engineering, and transformations to prepare the dataset for analysis and modeling.

- Solution.ipynb = This file, the final notebook of our project, consolidating the entire workflow from data preprocessing to model evaluation. This file integrates key steps, findings, and results, presenting a clear and organized view of our approach to solving the problem.

## Details
- Tools = Pandas, Numpy, Seaborn, Catboost, NLTK, TfidfVectorizer, fuzzywuzzy

- Feature Engineering = There were numerous indices across almost all columns that conveyed the same meaning but contained typos, so we began by correcting these. During this process, we created various mappings, and the fuzzywuzzy library was particularly helpful for this task. We grouped some of the columns and consolidated those that represented the same information into single columns. Additionally, we researched various NGOs, volunteer projects, and entrepreneurial ideas online and performed NLP analysis on this data. In this analysis, we scored the words, created a new column based on these scores, and ranked them accordingly.

- Data = For the feature engineering part, to perform the mapping process I mentioned, we found a CSV file online containing the provinces and districts of Turkey. Additionally, we extracted data on universities from https://yokatlas.yok.gov.tr/.

- Performance = RMSE 5.8539 with Catboost
