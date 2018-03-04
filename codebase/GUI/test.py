import sqlite3
import pandas as pd

con = sqlite3.connect('PREPROCESSING.db')
processed_dataset_table = pd.read_sql_query("SELECT * from processed_dataset;",con)
print(processed_dataset_table)