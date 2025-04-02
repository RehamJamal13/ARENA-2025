import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Load the CSV file
file_path = "/Users/rehamjamal/Desktop/ARENA 2025/extracted_text/csv/extracted_data.csv"
df = pd.read_csv(file_path)

# Debug: Check if data is loaded correctly
print(df.head())

# Check for column names
print(f"Columns: {df.columns}")

# Combine all titles and abstracts into a single string (row by row)
all_text = " ".join(
    f"{title} {abstract}" 
    for title, abstract in zip(df['Title'].fillna(""), df['Abstract'].fillna(""))
)
# Tokenize and clean text (remove stopwords/punctuation)
stop_words = set(stopwords.words("english"))
words = word_tokenize(all_text.lower())
filtered_words = [word for word in words if word.isalpha() and word not in stop_words]

# Debug: Check tokenized words
print(f"Filtered words sample: {filtered_words[:20]}")

# Get top 20 keywords
keyword_counts = Counter(filtered_words)
top_keywords = keyword_counts.most_common(20)

# Debug: Show top keywords
print("Top 20 Keywords:", top_keywords)


wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(dict(top_keywords))
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
