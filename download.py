from datasets import load_dataset

# This downloads and caches the dataset
print("Downloading Cebuano Speech Dataset...")
ds = load_dataset("Speech-data/Cebuano-Speech-Dataset")

# Look at the first entry
print(ds['train'][0])