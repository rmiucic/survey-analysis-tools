import pandas as pd
import sys

# Set encoding to handle Serbian characters
sys.stdout.reconfigure(encoding='utf-8')

# Load the data
df = pd.read_excel('jovana.xlsx')

print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
print("\nFirst 15 column names:")
for i, col in enumerate(df.columns[:15]):
    print(f"{i+1}: {col}")

print(f"\nSample data from first 3 columns:")
print(df.iloc[:5, :3])

print(f"\nData types:")
print(df.dtypes[:10])

print(f"\nUnique values in first few columns:")
for i, col in enumerate(df.columns[:5]):
    unique_count = df[col].nunique()
    print(f"{col}: {unique_count} unique values")
    if unique_count < 20:
        print(f"  Values: {df[col].unique()[:10].tolist()}")
    print()