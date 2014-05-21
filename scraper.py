from bs4 import BeautifulSoup, UnicodeDammit
import urllib2
import re, string

class Scraper:
    def __init__(self):
        self.domains = {
            "wired" : WiredScraper
        }

    def get_scraper(self, link):
        domain = get_domain(link)
        scraper_class = self.domains.get(domain, None)
        if scraper_class is None:
            return None
        return scraper_class(link)

    def find_more(self, link, n):
        new_links = [link]
        i = 0
        while len(new_links) < n:
            cur_link = new_links[i]
            add_links = self.get_scraper(cur_link).links
            for add_link in add_links:
                if add_link not in new_links:
                    new_links.append(add_link)
            i += 1

        return new_links

class WiredScraper:

    def __init__(self, link):
        try:
            html = urllib2.urlopen(link).read()
            self.soup = BeautifulSoup(html)
            self.title = strip_html(str(self.soup.title)).split('|')[0]
            articleBody = self.soup.body.find('span', attrs={'itemprop' : 'articleBody'})
            self.text = strip_html("\n".join([str(p) for p in articleBody.find_all('p', attrs={'class' : None})]))
            self.links = []
            for a in self.soup.body.find_all('a'):
                if a.has_attr('href'):
                    link = a['href']
                    if get_domain(link) == "wired" and "2014" in link:
                        if "mailto" not in link and "#respond" not in link and "jpg" not in link:
                            self.links.append(link)
        except:
            self.title = "None"
            self.text = ""
            self.links = []



def strip_html(text):
    p = re.compile(r'<.*?>')
    return p.sub('', text)

def get_domain(link):
    try:
        return link.split("/")[2].split(".")[-2].lower()
    except:
        return None

def main():

    s = Scraper()
    
    with open("links.txt") as link_file:
        for link in link_file:
            scraper = s.get_scraper(link)
            title = string.replace(scraper.title, " ", "-")
            title = string.translate(title, None, "?/\"\\:*|")
            with open("articles/" + title + ".txt", "w") as outfile:
                try:
                    outfile.write(scraper.title)
                    outfile.write("\n\n")
                    outfile.write(scraper.text)
                except:
                    outfile.write(scraper.title)
                    outfile.write("\n\n")
                    outfile.write(scraper.text.encode('ascii', 'ignore'))

#    links = ['http://www.wired.com/2014/05/fantastically-wrong-jackalope/']
#    for link in links:
#        #scraper = s.get_scraper(link)
#        new = s.find_more(link, 250)
#        with open("links.txt", "w") as link_file:
#            for n in new:
#                try:
#                    asc = n.encode('ascii', 'ignore')
#                    link_file.write(asc + "\n")
#                except:
#                    continue
#        

main()
