import sqlite3
import pandas as pd

con = sqlite3.connect('PREPROCESSING.db')
processed_dataset = pd.read_sql_query("SELECT * from processed_dataset;",con)
#processed_dataset.drop('level_0', axis=1, inplace=True)
#processed_dataset.drop('index', axis=1, inplace=True)

print(processed_dataset)
processed_dataset.to_sql("processed_dataset", con, if_exists="replace", index=False)
