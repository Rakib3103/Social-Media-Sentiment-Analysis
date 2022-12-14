# -*- coding: utf-8 -*-
"""Social Media Sentiment Analysis

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SUA2CDL3Sr3jZEhdiWJynvS1XSyRHKAA

**Importing Libraries**
"""

# Commented out IPython magic to ensure Python compatibility.
#Data Manipulation
import pandas as pd
import numpy as np

#Matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline

#Scikit-learn
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, classification_report

#Utility
import re     
import string
import seaborn as sns
from wordcloud import WordCloud

#nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# import nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('stopwords')  
stop_words = set(stopwords.words('english'))

import warnings
warnings.filterwarnings("ignore")

"""**Reading and Loading the dataset**

Train Dataset
"""

train_data = pd.read_csv('/content/train.csv')

train_data.head()
# train_data.columns

"""Test Dataset"""

test_data = pd.read_csv('/content/test.csv')
# test_data.head()
# test_data.columns

"""Length of both datasets"""

print('length of dataset is: ', len(train_data))

print('length of dataset is: ', len(test_data))

"""Shape of the dataset"""

train_data.shape
# train_data.info

test_data.shape
# test_data.info

"""Checking Datatypes of all columns"""

# train_data.dtypes
#test_data.dtypes

"""Checking Null Values existing in the dataset"""

np.sum(train_data.isnull().any(axis=1))

"""Printing the rows and columns of the dataset"""

print('Number of Columns Train Dataset: ', len(train_data.columns))
print('Number of Rows: ', len(train_data))
print('------------------------------------')
print('Number of Columns Test Dataset: ', len(test_data.columns))
print('Number of Rows: ', len(test_data))

"""Checking Target Values that are unique"""

train_data['text'].unique()

"""Checking the number of target vlaues"""

train_data['text'].nunique()

"""Data Visualization (Target Values)"""

#Plotting
x = train_data.groupby('Y').count().plot(kind='bar', title='Data Distribution', legend=False)
x.set_xticklabels(['0','1','2'], rotation=0)
print(train_data)
#Data storing in lists
text, sentiment = list(train_data['text']), list(train_data['Y'])

"""**Oversampling**"""

from sklearn.utils import resample
#create two different dataframe of majority and minority class 
df_majority = train_data[(train_data['Y']==0)] 
df_minority = train_data[(train_data['Y']==1)]
df_constant = train_data[(train_data['Y']==2)]  
# upsample minority class
df_minority_upsampled = resample(df_minority, 
                                 replace=True,    # sample with replacement
                                 n_samples= 17500, # to match majority class
                                 random_state=42)  # reproducible results
df_majority_upsampled = resample(df_majority, 
                                 replace=True,    # sample with replacement
                                 n_samples= 17500, # to match majority class
                                 random_state=42)  # reproducible results
# Combine majority class with upsampled minority class
df_upsampled = pd.concat([df_minority_upsampled, df_majority_upsampled, df_constant])

sns.countplot(x='Y', data=df_upsampled)

print(df_upsampled.describe())

"""**Data Preprocessing**

Printing unique values of the target variables
"""

data=df_upsampled[['text','Y']]

data['text'].unique()

"""Now separating the positive and negative tweets"""

# positive_data = data[data['text'] == 2]
# neutral_data = data[data['text'] == 1]
# negative_data = data[data['text'] == 0]

positive_data = data[data['Y'] == 2]
neutral_data = data[data['Y'] == 1]
negative_data = data[data['Y'] == 0]

"""Making text into lowercase"""

data['text'] = data['text'].str.lower()
data['text'].tail()

"""Defining list of stopwords"""

list_of_stopwords = ['a', 'about', 'above', 'after', 'again', 'ain', 'all', 'am', 'an',
             'and','any','are', 'as', 'at', 'be', 'because', 'been', 'before',
             'being', 'below', 'between','both', 'by', 'can', 'd', 'did', 'do',
             'does', 'doing', 'down', 'during', 'each','few', 'for', 'from',
             'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
             'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
             'into','is', 'it', 'its', 'itself', 'just', 'll', 'm', 'ma',
             'me', 'more', 'most','my', 'myself', 'now', 'o', 'of', 'on', 'once',
             'only', 'or', 'other', 'our', 'ours','ourselves', 'out', 'own', 're','s', 'same', 'she', "shes", 'should', "shouldve",'so', 'some', 'such',
             't', 'than', 'that', "thatll", 'the', 'their', 'theirs', 'them',
             'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
             'through', 'to', 'too','under', 'until', 'up', 've', 'very', 'was',
             'we', 'were', 'what', 'when', 'where','which','while', 'who', 'whom',
             'why', 'will', 'with', 'won', 'y', 'you', "youd","youll", "youre",
             "youve", 'your', 'yours', 'yourself', 'yourselves']

"""Cleaning the stopwords from tweets"""

stopwords = set(list_of_stopwords)

def cleaning(text):
    return " ".join([word for word in str(text).split() if word not in stopwords])
data['text'] = data['text'].apply(lambda text: cleaning(text))
data['text'].head()

"""Cleaning Punctuations from tweets"""

punctuations = string.punctuation
list_of_punctuations = punctuations
def cleaning(text):
    translator = str.maketrans('', '', list_of_punctuations)
    return text.translate(translator)
data['text'] = data['text'].apply(lambda text: cleaning(text))
data['text'].tail()

"""Cleaning Repeating Characters"""

def cleaning_repeating_char(text):
    return re.sub(r'(.)1+', r'1', text)
data['text'] = data['text'].apply(lambda x: cleaning_repeating_char(x))
data['text'].tail()

"""Cleaning URL's"""

def clean_URL(data):
    return re.sub("http\S+|www\S+|https\S+", "", data)
data['text'] = data['text'].apply(lambda x: clean_URL(x))
data['text'].tail()

"""Cleaning Numbers"""

def clean_num(data):
    return re.sub('[0-9]+', '', data)
data['text'] = data['text'].apply(lambda x: clean_num(x))
data['text'].tail()

"""Stemming"""

ps = nltk.PorterStemmer()
def stemming(data):
    text = [ps.stem(word) for word in data]
    return data
data['text'] = data['text'].apply(lambda x: stemming(x))
data['text'].head()

"""Lemmatizer"""

nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()
def lemmatizer_text(data):
    text = [lemmatizer.lemmatize(word) for word in data]
    return data
data['text'] = data['text'].apply(lambda x: lemmatizer_text(x))
data['text'].head()

"""Separation of input and label"""

X=data.text
y=data.Y

"""Positive Tweets"""

positive_data = data['text']
# positive_data = positive_data
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,
               collocations=False).generate("".join(positive_data))
plt.figure(figsize = (20,20))
plt.imshow(wc)

"""Negative Tweets"""

negative_data = data['text']
# negative_data = negative_data
plt.figure(figsize = (20,20))
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,
               collocations=False).generate(" ".join(negative_data))
plt.imshow(wc)

"""Neutral Tweets"""

neutral_data = data['text']
# neutral_data = neutral_data
plt.figure(figsize = (20,20))
wc = WordCloud(max_words = 1000 , width = 1600 , height = 800,
               collocations=False).generate(" ".join(neutral_data))
plt.imshow(wc)

"""Transforming Dataset into a Vectorizer"""

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.05, random_state =25)

vectoriser = TfidfVectorizer(ngram_range=(1,2), max_features=5000)
vectoriser.fit(X_train)
print('No. of feature_words: ', len(vectoriser.get_feature_names()))
#----------------------------------------------------------------------------#
X_train = vectoriser.transform(X_train)
X_test  = vectoriser.transform(X_test)

"""Model Evaluation (LinearSVC)"""

def model_Evaluate(model):
# Predict values for Test dataset
    y_pred = model.predict(X_test)
    # Print the evaluation metrics for the dataset.
    print(classification_report(y_test, y_pred))
    # Compute and plot the Confusion matrix
    cf_matrix = confusion_matrix(y_test, y_pred)
    categories = ['Negative','Positive','Neutral']
    group_names = ['True Neg','False Pos', 'False Neg','True Pos']
    group_percentages = ['{0:.2%}'.format(value) for value in cf_matrix.flatten() / np.sum(cf_matrix)]
    labels = [f'{v1}n{v2}' for v1, v2 in zip(group_names,group_percentages)]
    labels = np.asarray(labels).reshape(2,2)
    sns.heatmap(cf_matrix, annot = True, cmap = 'Blues',fmt = '',
    xticklabels = categories, yticklabels = categories)
    plt.xlabel("Predicted values", fontdict = {'size':14}, labelpad = 10)
    plt.ylabel("Actual values" , fontdict = {'size':14}, labelpad = 10)
    plt.title ("Confusion Matrix", fontdict = {'size':18}, pad = 20)

SVCmodel = LinearSVC()
SVCmodel.fit(X_train, y_train)
model_Evaluate(SVCmodel)
y_pred2 = SVCmodel.predict(X_test)

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
tokenizer = Tokenizer(5000)
validation_sentence = ['I am sad']
validation_sentence_tockened = tokenizer.texts_to_sequences(validation_sentence)
validation_sentence_padded = pad_sequences(validation_sentence_tockened, maxlen=5000, truncating ='post', padding='post')
# print(validation_sentence[0])
print(np.argmax(SVCmodel.predict(validation_sentence_padded)[0]))

"""** Random Forest Classifier**"""

from sklearn.ensemble import RandomForestClassifier

text_classifier = RandomForestClassifier(n_estimators=200, random_state=25)
text_classifier.fit(X_train, y_train)

predictions = text_classifier.predict(X_test)

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
model_Evaluate(text_classifier)

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
tokenizer = Tokenizer(5000)
validation_sentence = ['All month crowding supermarkets restaurants, however reducing hours closing malls means everyone using entrance dependent single supermarket.']
validation_sentence_tockened = tokenizer.texts_to_sequences(validation_sentence)
validation_sentence_padded = pad_sequences(validation_sentence_tockened, maxlen=5000, truncating ='post', padding='post')
print(validation_sentence[0])
print(np.argmax(text_classifier.predict(validation_sentence_padded)[0]))

"""**Logistic Regression**"""

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state=0).fit(X_train, y_train)
clf.score(X_test, y_test)

LRmodel = LogisticRegression(C = 2, max_iter = 1000, n_jobs=-1)
LRmodel.fit(X_train, y_train)
model_Evaluate(LRmodel)
y_pred3 = LRmodel.predict(X_test)

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
tokenizer = Tokenizer(5000)
validation_sentence = ['All month crowding supermarkets restaurants, however reducing hours closing malls means everyone using entrance dependent single supermarket.']
validation_sentence_tockened = tokenizer.texts_to_sequences(validation_sentence)
validation_sentence_padded = pad_sequences(validation_sentence_tockened, maxlen=5000, truncating ='post', padding='post')
print(validation_sentence[0])
print(np.argmax(clf.predict(validation_sentence_padded)[0]))