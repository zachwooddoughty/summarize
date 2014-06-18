import os

class Keyword:
    def __init__(self):
        self.keywords_dir = "keywords/"
        self.keyword_rec_dir = "keyword_recs/"
        self.keyword_dict = {}
        self.similarity_dict = {}

    def load(self):
        '''Look in keywords directory, and load keywords for each article'''
        for filename in os.listdir(self.keywords_dir):
            with open(self.keywords_dir + filename) as keyword_file:
                self.keyword_dict[filename] = keyword_file.readline().split(", ")

    def compare(self):
        '''Calculate jaccard similarity pairwise for each article'''
        for one in self.keyword_dict.keys():
            self.similarity_dict[one] = {}
            for two in self.keyword_dict.keys():
                if one == two:
                    continue
                #if "facebook" not in one.lower() or "facebook" not in two.lower():
                    #continue
                self.similarity_dict[one][two] = self.jaccard(one, two)

    def jaccard(self, one, two, debug=False):
        ''' Calculate jaccard similarity between two article. 
            one and two should both be filenames for articles'''
        one_set = set(self.keyword_dict[one])
        two_set = set(self.keyword_dict[two])
        if debug:
            print one, ", ".join(sorted(one_set))
            print two, ", ".join(sorted(two_set))
            print "int", ", ".join(sorted(one_set.intersection(two_set)))
            print "uni", ", ".join(sorted(one_set.union(two_set)))
        similarity = len(one_set.intersection(two_set)) / float(len(one_set.union(two_set)))
        return similarity
                
    def compute(self):
        '''Compute recommendations for each article and write to file'''
        for one in k.similarity_dict.keys():
            if len(k.similarity_dict[one]) > 0:
                twos = sorted(k.similarity_dict[one].items(), key = lambda x: x[1], reverse=True)
                with open(k.keyword_rec_dir + one, "w") as outfile:
                    for two in twos:
                        if two[1] > 0:
                            outfile.write(two[0].split(".")[0] + "\n")

    def run(self):
        self.load()
        self.compare()
        self.compute()

def main():
    k = Keyword()
    k.run()

if __name__ == "__main__":
    main()
