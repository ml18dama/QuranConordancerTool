#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Developer: Dalal Aldowaihi
Concordances Search System
2019/2020
"""
# ----------------------- Libraries -----------------------
import pandas as pd
import xml.etree.ElementTree as ET
import json
import codecs
import os
import re
import nltk
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import arabic_reshaper
from bidi.algorithm import get_display
import pyarabic.arabrepr
from tashaphyne.stemming import ArabicLightStemmer
# Download Arabic stop words
nltk.download('stopwords')

# ----------------------- Files path -----------------------
# Arabic Quran corpus
quran_corpus = 'data/arabic-original.csv'
# Arabic verses interpretation corpus
interpretation_corpus = 'data/ar.jalalayn.xml'
# A concordances dataset (words and their concordance)
concordances_dataset_json = 'data/concordances_dataset.json'
# Words dictionary (Quran words)
words_dictionary_json = 'data/words_dictionary.json'
# Roots dictionary (Quran root words)
roots_dictionary_json = 'data/roots_dictionary.json'
# unique Quran words (clean text - exclude stopwords)
cleaned_corpus_text ='data/cleaned_corpus.txt'
# External file contains extra stop words
arabic_stopwords = 'data/arabic_stopwords.txt'
currdir = 'data/'

# ----------------------- Dictionaries and Lists -----------------------
# Dictionary for a concordances dataset (Quran words and their concordance)
concordances_dictionary = {}
# Dictionary for words dictionary (id, word)
words_dictionary = {}
# Dictionary for roots dictionary (root, derived words)
roots_dictionary = {}
# Quran words list (Exclude stopwords)
words_list = []
# Verse concordances list
verses_concordances_list = []


# ----------------------- Read CSV file ---------------------------------
# Load data into Dataframe
_quran_data = pd.read_csv(quran_corpus, encoding = 'UTF-8', sep='|', header='infer');

# Text Pre-Processing (Normalization Step): Remove diacrtics from the verses to simplify the corpus
clean_text = _quran_data['verse'].map(lambda x: re.sub('[ًٌٍَُِّٰۘۚۙ~ْۖۗ]', '', x))

# Text Pre-Processing (Tokenization Step): Tokinize words from verses and vectorize them
tokenized_text = clean_text.str.split()

# You can filter for one surah if you want
verses = tokenized_text.values.tolist()

# ----------------------- Text Pre-Processing (Exclude Arabic stop words) ---------------------------------
# Fist stop word list from nltk
arb_stopwords = set(nltk.corpus.stopwords.words('arabic'))
# Second stop word list by developer
stopwords_list = ['كان','قال','قل','قالوا','يقولون','يكن','كنا','إنكم','إنك','وهم','فما','وقد','قبل','كانوا','بينكم','كنت','فقد','منا','منكم','إنهم','لمن','لكن','عليهم']
# Third stop word list from text file
with open(arabic_stopwords, 'r') as fh:
  for line in fh.readlines():
    arabic_stopwords_list = line.split()

# Remove Arabic stop words
filtered_verses = []

for verse in verses:
  for word in verse:
    #words_list.append(word)
    if word not in arb_stopwords:
      if word not in arabic_stopwords_list:
        if word not in stopwords_list:
          filtered_verses.append(word+' ')

fh = open (cleaned_corpus_text,'w')
fh.writelines(filtered_verses)
fh.close()

# ----------------------- 1. Implement the stemming process function.---------------------------------------------------

# List of non-arabic words to exclude them from the stemming process
stem_not = ['إسحاق', 'إسماعيل', 'إبراهيم','يعقوب' ,'يونس', 'يحيى', 'عيسى', 'سليمان', 'يوسف', 'فرعون','مريم' ,'موسى', 'إلياس', 'نوح', 'داود', 'يسوع', 'هارون', 'يعقوب', 'إبليس', 'لوط','جالوت' ]

def stemmingـprocess(word):
  # Initialize Arabic stemmer
  arepr = pyarabic.arabrepr.ArabicRepr()
  repr = arepr.repr
  ArListem = ArabicLightStemmer()

  if word in stem_not:
    wordRoot = word
  elif len(word) <= 3:
    wordRoot = word
  else:
    # Stemming word
    stem = ArListem.light_stem(word)
    # Extract root
    wordRoot = ArListem.get_root()
  return wordRoot


# ----------------------- 2. Build Words Dictionary (json file) --------------------------------------------------------
# Save list of words in JSON formate
def build_wordsـdictionary():
  id = 1
  for verse in verses:
    for word in verse:
      if word not in words_list:
        words_list.append(word)
        words_dictionary[id] = word
        id = id + 1
      else:
        continue
  # store the roots dictionary into json format
  with open(words_dictionary_json, 'w', encoding='utf8') as file:
    json.dump(words_dictionary, file, ensure_ascii=False)
  # load the json to print the roots dictionary
  with open(words_dictionary_json) as f:
    data = json.load(f)
  print(data)


# ----------------------- 3. Build Roots Dictionary (json file) --------------------------------------------------------
# Save list of root words in JSON formate
def build_rootsـdictionary():
  for verse in verses:
    for word in verse:
      # Check if the word is stop word
      if word not in filtered_verses:
        # Stemming process
        wordRoot = stemmingـprocess(word)
        if not roots_dictionary.get(wordRoot):
          roots_dictionary[wordRoot] = []
        if not word in roots_dictionary[wordRoot]:
          roots_dictionary[wordRoot].append(word)
  # Store the roots dictionary into json format
  with open(roots_dictionary_json, 'w', encoding='utf8') as file:
    json.dump(roots_dictionary, file, ensure_ascii=False, indent=4)
  # Load the json to print the roots dictionary
  with open(roots_dictionary_json) as f:
    data = json.load(f)
  print(data)


# -------------- 4. Implement concordances word-based search. ---------------------------------------------

#  Read XMl file (arabic verses interpretation)
mytree = ET.parse(interpretation_corpus)
myroot = mytree.getroot()
tag = myroot.tag

def word_concordance(word):
  word_con_rows = clean_text[clean_text.str.contains('|'.join(word.split(' ')))]
  rows_index = word_con_rows.index.tolist()

#  Verses concordance count
  con_count =(clean_text.str.count(word).sum())
  con_count_str = str(con_count)
  print ('The word: "' + word + '" occured in the Quran : '+ con_count_str + ' times')
#  Print concordances
  print('Concordances : ')
  print(' -------------------------------------------------------------')
  for i in rows_index:
    row = _quran_data.iloc[i]
    surah_index = str (row.surah)
    verse_index = str (row.ayah)
    print('Verse : \n «' + row.verse + '»')
    verses_concordances_list.append(row.verse)

#  Print sura name and verse index
    for sura_tag in myroot.findall("sura["+surah_index+"]"):
      att = sura_tag.attrib
      sura_name = att.get('name')
      print('(سورة '+sura_name +' : '+ verse_index + ')')

      #  Print verse explanation
      for aya_tag in sura_tag.findall("aya["+verse_index+"]"):
        verse_tafseer = aya_tag.get('text')
        print ('Interpretation :\n', verse_tafseer)
        print (' -------------------------------------------------------------')

  return verses_concordances_list

# ----------------------- 5. Implement most frequent words function ----------------------------------------------------
def most_frequent_words():
  wordCounter = {}
  with open(cleaned_corpus_text,'r') as fh:
    for line in fh.readlines():
      # Spit the line into a list.
      word_list = line.split()
      for word in word_list:
        # Adding  the word into the wordCounter dictionary.
        if word not in wordCounter:
          wordCounter[word] = 1
        else:
          # If the word is already in the dictionary update its count.
          wordCounter[word] = wordCounter[word] + 1

  # Printing the words and its occurrence.
  print('\n{:15}{:3}'.format('الكلمة','عدد تكرار'))
  print('-' * 25)
  for  (word,occurance)  in sorted(wordCounter.items() , reverse=True, key=lambda x: x[1])[:200]:
    print('{:15}{:3}'.format(word,occurance))


# ----------------------- 6. Generate word cloud--------------------------------------------------------------------------------
def quran_word_cloud():
  file = codecs.open(os.path.join(cleaned_corpus_text), 'r', 'utf-8')
  mask = np.array(Image.open(os.path.join(currdir, 'cloud.png')))
  wc = WordCloud(background_color='white',
                mask=mask,
                max_words=200,
                stopwords=arb_stopwords,
                font_path='data/Shoroq-Font.ttf')
  # Make text readable for a non-Arabic library like wordcloud
  text = arabic_reshaper.reshape(file.read())
  text = get_display(text)

  # Generate a word cloud image
  wc.generate(text)
  # Export an image to file
  wc.to_file(os.path.join(currdir, 'CSV_wc.png'))
  # Show an image
  img = Image.open('data/CSV_wc.png')
  img.show()

# ------------------ 7. Implement concordance search based on a root word. ---------------------------------------------
def root_concordance(word):
  derived_list = []
  wordRoot = stemmingـprocess(word)
  print("Stemmed Word : ")
  print(wordRoot)
  with open(roots_dictionary_json) as f:
    data = json.load(f)
  print("All Derived Words : ")
  print(*data[wordRoot], sep="\n")
  derived_list = data[wordRoot]
  for Derived_Word in derived_list:
    print("Derived Word : ")
    print(Derived_Word)
    word_concordance(Derived_Word)

# ----------------------- 8. Construct the concordances dataset --------------------------------------------------------
# Produce dataset of words concordance in JSON file
def construct_concordances_dataset():
  verses_list = []
  for i in words_list:
    verses_list = word_concordance(i)
    concordances_dictionary[i] = verses_list
    verses_list = []
  with open(concordances_dataset_json, 'a', encoding='utf8') as file:
    json.dump(concordances_dictionary, file, ensure_ascii=False, indent=4)


# ------------------ 10. Implement Find all derived words of the root. ---------------------------------------------
def find_derived_words(root_word):
  with open(roots_dictionary_json) as f:
    data = json.load(f)
  print('All derived words: ')
  print(*data[root_word],sep='\n')

print("\n\nWelcome to the Concordancer Search based on Quran...\n\n"
      'Please select from the list:\n\n'
      '1: Find Root of the Word  \n'
      '2: Print the Words Dictionary  \n'
      '3: Print the Roots Dictionary\n'
      '4: Find all Derived Words for a Specific Word\n'
      '5: Find concordances for a Specific Word \n'
      '6: Find concordances for a Root Word \n'
      '7: Display the most frequent words in Quran\n'
      '8: Display the word cloud of Quran\n'
      '9: Construct the Concordances Dataset\n'
      '10: Exit\n')

while True:
  print('\n')
  choice = input('Please enter your choice: ')
  if choice == '1':
    user_input = input('Please enter your word: \n ')
    wordRoot = stemmingـprocess(user_input)
    print('Root of the word is: ' + wordRoot)

  elif choice == '2':
    build_wordsـdictionary()

  elif choice == '3':
    build_rootsـdictionary()

  elif choice == '4':
    user_input = input('Please enter your word:: \n ' )
    wordRoot = stemmingـprocess(user_input)
    find_derived_words(wordRoot)

  elif choice == '5':
    user_input = input('Please enter your word: \n ')
    wordRoot = stemmingـprocess(user_input)
    print('Root of the word: ' + wordRoot)
    word_concordance(user_input)

  elif choice == '6':
    user_input = input('Please enter your word: \n ')
    root_concordance(user_input)

  elif choice == '7':
    most_frequent_words()

  elif choice == '8':
    quran_word_cloud()

  elif choice == '9':
    print ('not activated because it take long time')
    construct_concordances_dataset()

  elif choice == '10':
    os._exit(1)
