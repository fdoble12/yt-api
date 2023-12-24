import pandas as pd
from lingua import Language, LanguageDetectorBuilder
import re
from collections import defaultdict

languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.TAGALOG]
detector = LanguageDetectorBuilder.from_languages(*languages).build()

# Read the first 50 rows from the CSV file into a DataFrame
df = pd.read_csv('comments_01-2018.csv')
print(df.head())

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
    #stopwords = set(["the", "and", "is", "it", "to", "i", "you", "u", "a", "in", "for", "so", "that", "when"])
    #words = [word for word in words if word not in stopwords]
    
    # Remove extra whitespace
    cleaned_text = ' '.join(words)
    
    return cleaned_text

# Apply the clean_text function to the 'comment' column
df['comment'] = df['comment'].apply(clean_text)

# Function to detect the language of each word in the cleaned text
def detect_language(word):
    try:
        print(word)
        return detector.detect_language_of(word)
    except:
        return 'unknown'
def getConfLevel(word):
    result = ""
    confidence_values = detector.compute_language_confidence_values(word)
    for confidence in confidence_values:
        result+=(f"{confidence.language.name}: {confidence.value:.2f}\n")
    return result

# Function to process the language detection results and count words for each language
def process_results(words):
    language_count = defaultdict(int)
    result = ""
    for res in detector.detect_multiple_languages_of(words):
        result+=(f"{res.language.name}: '{words[res.start_index:res.end_index]}'\n")
    #result = {f'{lang}: {count}': [word for word in words if detect_language(word) == lang] for lang, count in language_count.items()}
    print(result)
    return result

# Function to process the language detection results and count words for each language
def process_language_results(words):
    language_count = defaultdict(int)
    for word in words:
        lang = detector.detect_language_of(word)
        language_count[lang] += 1
    result = {f"{lang}: {count}": [word for word in words if detect_language(word) == lang] for lang, count in language_count.items()}
    return result

df['comment language'] = df['comment'].apply(lambda x: detect_language(x))

# Apply the process_language_results function to each comment in the 'comment' column and create a new 'languages' column
df['word_level_languages'] = df['comment'].apply(lambda x: process_language_results(x.split()))

df['word_languages'] = df['comment'].apply(lambda x: process_results(x))

df['conf_level'] = df['comment'].apply(lambda x: getConfLevel(x))
# Save the DataFrame to a new CSV file with the 'languages' column added
df.to_csv('word_level_languages.csv', index=False)

# Display the DataFrame with the 'languages' column
print(df.head())
