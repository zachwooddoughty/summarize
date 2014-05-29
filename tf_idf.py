from tokenization import tokenize
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords
import operator, math
import sys, os
import string
import pickle

class TFIDF:

    def __init__(self):
        self.pickle_docs = "tfidf_pickle_docs"
        self.pickle_corpus = "tfidf_pickle_corpus"
        self.lan = LancasterStemmer()
        self.construct()
        #print sorted(self.words.iteritems(), key = operator.itemgetter(1), reverse=True)[:20]

    def clean(self, word):
        '''cleans a word or returns None if it should not be considered'''
        word = word.strip(string.punctuation)
        word = self.lan.stem(word)
        return word
    
    def construct(self):
        corpus = {}

        # Check to see if we should simply load a pickle
        if os.path.isfile(self.pickle_docs):
            with open(self.pickle_docs) as docs_file:
                current_doclist = pickle.load(docs_file)
                if os.listdir('articles/') == current_doclist:
                    # current article list is the same as pickled article list
                    # so we want to just load the stored pickled corpus data
                    with open(self.pickle_corpus) as corpus_file:
                        self.words = pickle.load(corpus_file)
                        self.n = len(current_doclist)
                        return
        
        # If we don't load a pickle, build the corpus from articles/ dir
        num_docs = 0.0
        for file_name in os.listdir('articles/'):
            num_docs += 1
            doc = {}
            with open("articles/" + file_name) as article:
                for line in article:
                    for word in tokenize(line, "word", return_spans=False):
                        word = self.clean(word)
                        doc[word] = 1
            for key in doc.keys():
                corpus[key] = corpus.get(key, 0) + 1

        self.words = corpus
        self.n = num_docs

        print "Pickling a new TFIDF corpus"
        # pickle corpus and document list
        with open(self.pickle_docs, "w") as docs_file:
            pickle.dump(os.listdir('articles/'), docs_file)
        with open(self.pickle_corpus, "w") as corpus_file:
            pickle.dump(self.words, corpus_file)

    def weight(self, word, count, debug=False):
        if debug:
            return (word, count, self.words.get(word, 1))
        return  count * math.log(self.n / self.words.get(word, 1))

def main():
    TF = TFIDF()
    text = ""
    with open(sys.argv[1]) as f:
        for line in f:
            text += line

    words = tokenize(text, "word", return_spans=False)
    sentences = tokenize(text, "sentence", return_spans=False)

    wc = {}
    for word in words:
        word = TF.clean(word)
        if word is not None:
            wc[word] = wc.get(word, 0) + 1 

    tf_dict = {}
    for k in wc.keys():
        tf_dict[k] = TF.weight(k, wc[k])

    top = sorted(tf_dict.iteritems(), key = operator.itemgetter(1), reverse=True)[:15]
    for (k,v) in top:
        print k, v, TF.weight(k, wc[k], debug=True)

#    # p holds the probability dictionary for each word
#    p = {word : wc[word] / float(len(words)) for word in wc.keys()}
#    #print "p", p
#
#    summary_size= 5
#    summary_sentences = []
#
#    while len(summary_sentences) < summary_size:
#
#        best_sent_score = 0 
#        best_sent_words = []
#        best_sent = ""
#        for sent in sentences:
#            sig_words = [TF.clean(word) for word in tokenize(sent, "word", return_spans=False)
#                 if TF.clean(word) in p]
#
#            score = sum([p[word] for word in sig_words]) / float(len(sig_words))
#
#            if score > best_sent_score:
#                best_sent_score = score
#                best_sent = sent
#                best_sent_words = sig_words
#        
#        # add our best sent to our summary, then update p values
#        summary_sentences.append(best_sent)
#        #print "Sentence added:", best_sent
#        for word in best_sent_words:
#            p[word] = p[word] ** 2
#
#    print "Here is your summary:"
#    for sentence in summary_sentences:
#        print sentence

if __name__ == "__main__":
    main()
    
