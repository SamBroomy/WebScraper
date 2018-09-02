#!/usr/bin/python

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import operator
from itertools import islice

class DataAnalyser:
    'Analyses the data found from the Web Scraper'

    def __init__(self, folder_name):
        """
        for file in os.listdir("BBC-NEWS"):
            if file.endswith(".txt"):
                print(os.path.join(file))#"/mydir", file))
        """
        stop_words = set(stopwords.words('english'))
        word_dict = {}
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                if file.lower().endswith(".txt") and file.lower():#.startswith("main"):
                    print(os.path.join(root, file))
                    try:
                        with open(os.path.join(root, file), 'r') as content_file:
                            head = list(islice(content_file, 3))
                            print(head[2].strip(), "\n\n")
                            content = ''.join([head[2], content_file.read()])
                            #print(content)
                        word_tokens = word_tokenize(content)
                        for word in word_tokens:
                            if word.lower() not in stop_words and word.isalpha():
                                if word not in word_dict:
                                    word_dict[word] = 1
                                else:
                                    word_dict[word] += 1
                    except IndexError as e:
                        print("Something went wrong:\n{}".format(e))

        sorted_x = sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True)
        for x in sorted_x:
            if x[1] < 25:
                break
            
            #print("{0} - {1}\t".format(x[0], x[1]), end='')
        
                    #for w in sorted_x:

        #print(sorted_x)

                    #exit()
                
        
"""
        example_sent = "--{{[This 'is' A sample \"sentence\", showing off the stop words filtration."
        #example_sent.startswith("")
        stop_words = set(stopwords.words('english'))
        print(example_sent, "\n\n")
        word_tokens = word_tokenize(example_sent)
        print(word_tokens, "\n\n")
        
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        print(filtered_sentence, "\n\n")
        filtered_sentence = []
        
        for word in word_tokens: 
            if word.lower() not in stop_words and word.isalpha():
                filtered_sentence.append(word)
        
        print(word_tokens)
        print(filtered_sentence)
"""

if __name__ == '__main__':
    print ("DataAnalyser.__module__:\t{}".format(DataAnalyser.__module__).expandtabs(2))
    print ("DataAnalyser.__name__:\t{}".format(DataAnalyser.__name__).expandtabs(8))
    print ("DataAnalyser.__doc__:\t{}\n".format(DataAnalyser.__doc__).expandtabs(8))
    DataAnalyser("BBC-NEWS")
