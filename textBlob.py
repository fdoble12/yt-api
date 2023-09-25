from textblob.classifiers import NaiveBayesClassifier
import pandas as pd

df = pd.read_csv('processed_comments.csv')
train = [(row['text'], row['label']) for index, row in df.iterrows()]


cl = NaiveBayesClassifier(train)
print(cl.classify("manipulating us"))