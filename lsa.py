from tokenization import tokenize
from tf_idf import TFIDF
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords
import operator
import sys, os
import string
import scipy.linalg, numpy

class LSA:
    def __init__(self):
        self.TF = TFIDF()
        self.articles_dir = "articles/"
        self.summaries_dir = "summaries/"
        self.keywords_dir = "keywords/"

    def keywords(self, filename, num_topics=5, keywords_per_topic=3):
        text = ""
        with open(filename) as f:
            for line in f:
                text += line

        words = tokenize(text, "word", return_spans=False)
        sentences = tokenize(text, "sentence", return_spans=False)

        wc = {}
        clean_sentences = []
        for sent in sentences:
            clean_sent = {}
            for word in tokenize(sent, "word", return_spans=False):
                word = self.TF.clean(word)
                clean_sent[word] = 1
                wc[word] = wc.get(word, 0) + 1 
            clean_sentences.append(clean_sent)

        matrix = []
        for word in wc.keys():
            row = []
            for sent in clean_sentences:
                if word in sent:
                    row.append(self.TF.weight(word, wc[word]))
                else:
                    row.append(0)
            matrix.append(row)

        matrix = numpy.matrix(matrix)
        U, s, Vh = scipy.linalg.svd(matrix, full_matrices=False)

        D = s * Vh

        keywords = []

        for topic in range(num_topics):
            try:
                words = sorted(enumerate([u for u in U[:,topic]]), key = lambda x: x[1])
            except IndexError:
                print "Problem indexing numpy array for", filename, "on topic", topic
                continue
            added = 0
            word_index = 0
            while added < keywords_per_topic and word_index < len(words):
                #print "Looking at", words[word_index], wc.keys()[words[word_index][0]]
                if wc.keys()[words[word_index][0]] not in keywords:
                    keywords.append(wc.keys()[words[word_index][0]])
                    added += 1
                word_index += 1

        return ", ".join(keywords)

    def summarize(self, filename):
        text = ""
        with open(filename) as f:
            for line in f:
                text += line

        words = tokenize(text, "word", return_spans=False)
        sentences = tokenize(text, "sentence", return_spans=False)

        wc = {}
        clean_sentences = []
        for sent in sentences:
            clean_sent = {}
            for word in tokenize(sent, "word", return_spans=False):
                word = self.TF.clean(word)
                clean_sent[word] = 1
                wc[word] = wc.get(word, 0) + 1 
            clean_sentences.append(clean_sent)

        matrix = []
        for word in wc.keys():
            #print "adding", word
            row = []
            for sent in clean_sentences:
                if word in sent:
                    row.append(self.TF.weight(word, wc[word]))
                else:
                    row.append(0)
            matrix.append(row)

        matrix = numpy.matrix(matrix)
        #print "matrix", matrix
        U, s, Vh = scipy.linalg.svd(matrix, full_matrices=False)

    #    print "U", U
    #    print "s", s
    #    print "Vh", Vh
    #
        D = s * Vh
        #print "D", D

        num_sentences = 5
        summary_sentence_indices = []

        #for topic in range(3):
        #    print "Topic", topic
        #    sent_weights = D[topic,:]
        #    #top_words = sorted(enumerate([u for u in U[:,topic]]), key = lambda x: x[1], reverse=True)[:5]
        #    bottom_words = sorted(enumerate([u for u in U[:,topic]]), key = lambda x: x[1])[:5]
        #    #print "TOP:", ", ".join(wc.keys()[x[0]] for x in top_words)
        #    print "BOTTOM WORDS:", ", ".join(wc.keys()[x[0]] for x in bottom_words)
        #    top_sents = sorted(enumerate([s for s in sent_weights]), key = lambda x: x[1]) [:3]
        #    print "TOP SENTS:", "\n".join([sentences[s[0]] for s in top_sents])

        topic = 0
        while len(summary_sentence_indices) < num_sentences:
            
            sent_weights = D[topic,:]
            top_sents = sorted(enumerate([s for s in sent_weights]), key = lambda x: x[1]) 
            for sent in top_sents:
                if sent[0] > 0 and sent[0] not in summary_sentence_indices:
                    summary_sentence_indices.append(sent[0])
                    break

            topic += 1
            
        summary = ""
        summary_sentence_indices.sort()
        for i in summary_sentence_indices:
            summary += sentences[i] + "\n"
        return summary

def main():
    lsa = LSA()
    for filename in os.listdir(lsa.articles_dir):
        with open(lsa.keywords_dir + filename, "w") as outfile:
        #with open(lsa.summaries_dir + filename, "w") as outfile:
            #summary = lsa.summarize(lsa.articles_dir + filename)
            #outfile.write(summary)
            keywords = lsa.keywords(lsa.articles_dir + filename)
            outfile.write(keywords)

if __name__ == "__main__":
    main()
