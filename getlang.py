import pandas as pd
from langdetect import detect
import re

# Read the CSV file into a DataFrame
df = pd.read_csv('comments_01-2018.csv')

# Function to clean the text in the 'comment' column
def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove non-alphabetical characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize the text (split into words)
    words = text.split()
    
    # Remove stopwords (common words like "the", "and", etc.)
    stopwords = set(["the", "and", "is", "it", "to", "i", "you", "u", "a", "in", "for", "so", "that", "when"])
    words = [word for word in words if word not in stopwords]
    
    # Remove extra whitespace
    cleaned_text = ' '.join(words)
    
    return cleaned_text

# Apply the clean_text function to the 'comment' column
df['comment'] = df['comment'].apply(clean_text)

# Function to detect the language of the cleaned text
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

# Apply the detect_language function to the 'comment' column and create a new 'language' column
df['language'] = df['comment'].apply(detect_language)

# Save the DataFrame to a new CSV file with the 'language' column added
df.to_csv('cleaned_data.csv', index=False)

# Display the cleaned DataFrame with the 'language' column
print(df.head())
