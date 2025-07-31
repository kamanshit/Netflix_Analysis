import pandas as pd

# load the csv file
df=pd.read_csv("mymoviedb.csv", engine="python")

# show Shape and preview

# print("Shape of dataset: ",df.shape)
# print("\nFirst 5 rows:\n", df.head())

# print(df.columns)
# print(df.info())
print(df.isnull().sum())