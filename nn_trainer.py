from tokenization import tokenize
from featureextraction import FeatureExtractor
import sys, os

sys.path.append("../pybrain/")
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer

import cPickle

class SummaryFilter:

    def __init__(self):
        self.articles_dir = "articles/"
        self.done_articles_file = "nn_trained_articles.pkl"
        self.dataset_file = "nn_dataset.pkl"
        self.nn_file = "nn.pkl"
        self.features = FeatureExtractor.get_all_feature_function_names(include_nested=True)

    def build_dataset(self):

        if os.path.isfile(self.dataset_file):
            with open(self.dataset_file, "rb") as f:
                dataset = cPickle.load(f)
        else:
            dataset = SupervisedDataSet(len(features), 1)

        if os.path.isfile(self.done_articles_file):
            with open(self.done_articles_file, "rb") as f:
                done_articles = cPickle.load(f)
        else:
            done_articles = {}

        value = -1
        decision = "y"

        for file_name in os.listdir(self.articles_dir):
            print "\n\n"
            print "---"*10
            decision = raw_input("Do another article? [y/n] ")
            if decision[0].lower() != "y":
                break

            with open("articles/" + file_name) as article:
                text = ""
                first = True
                for line in article.readlines()[1:]:
                    text += line
                sentences = tokenize(text, "sentence", return_spans=False)

                article_position = done_articles.get(file_name, 0) 
                if article_position >= len(sentences):
                    continue

                print "Looking at:", file_name, "from position", article_position
                
                for sentence in sentences[article_position:]:
                    extractor = FeatureExtractor(sentence)
                    vectors = extractor.get_feature_vectors(features, "sentence")[0]
                    print sentence

                    value = -1
                    while value == -1:
                        rating = raw_input("nothing=OK, space=bad, q=quit: ")
                        if rating == "":
                            value = [0]
                        elif rating[:1].lower() == "q":
                            value = None
                        elif rating[:1] == " ":
                            value = [1]

                    # quit on q
                    if value == None:
                        break
                    
                    dataset.appendLinked(vectors, value)
                    done_articles[file_name] = done_articles.get(file_name, 0) + 1

        with open(self.dataset_file, "wb") as f:
            cPickle.dump(dataset, f)
        with open(self.done_articles_file, "wb") as f:
            cPickle.dump(done_articles, f)

    def build_nn(self):
        nn = buildNetwork(len(self.features), len(self.features)/2, 1)
        dataset = None

        if os.path.isfile(self.dataset_file):
            with open(self.dataset_file, "rb") as f:
                dataset = cPickle.load(f)

        if dataset:
            trainer = BackpropTrainer(nn, dataset)
            trainer.trainEpochs(epochs=1000)

        with open(self.nn_file, "wb") as f:
            cPickle.dump(nn, f)
        
        s = " "
        while len(s) > 0:
            s = raw_input("Test sentence: ")
            extractor = FeatureExtractor(s)
            vectors = extractor.get_feature_vectors(self.features, "sentence")[0]
            print nn.activate(vectors)
            print "__"*8

def main():
    summary_filter = SummaryFilter()
    #build_dataset()
    summary_filter.build_nn()

if __name__ == "__main__":
    main()
