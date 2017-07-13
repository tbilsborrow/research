from __future__ import print_function
import solr
import sys
import nltk
import re
from pattern.en import singularize

con = solr.SolrConnection('http://10.1.11.210:8983/solr/wikipedia_core')

stopwords = nltk.corpus.stopwords.words('english')

cache = set()

def accept_word(w):
    return len(w) > 2 and w.lower() not in stopwords and w[0].isalpha()

def remove_nonalpha(w):
    return re.sub('[\W_]+', '', w)

def query(w):
    if w in cache:
        return [w]
    results = [d['page_name'] for d in con.query('page_name:%s AND is_disambiguation:false' % w, fl='page_name')]
    cache.update(results)
    return results

def process(line):
    # replace some known utf-8 chars with ascii
    line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
    line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
    # remove the rest of the non-ascii chars
    line = re.sub(r'[^\x00-\x7F]+', ' ', line)

    sentences = nltk.tokenize.sent_tokenize(line)

    # print('---------------')
    tags = set()
    for sentence in sentences:
        # words
        all_words = [singularize(w).capitalize() for w in nltk.tokenize.word_tokenize(sentence)]
        words = {remove_nonalpha(w) for w in all_words if accept_word(w)}
        # search solr
        for word in words:
            # print(word)
            tags.update(query(word))

        # bigrams
        all_bigrams = nltk.bigrams(all_words)
        bigrams = {b for b in all_bigrams if accept_word(b[0]) and accept_word(b[1])}
        for bigram in bigrams:
            b = '%s_%s' % (remove_nonalpha(bigram[0]), remove_nonalpha(bigram[1]).lower())
            # print(b)
            tags.update(query(b))

    return ",".join(tags).encode('utf-8')


def main():
    try:
        for line in sys.stdin:
            print(process(line.strip()))
    except:
        print("FAIL! " + line, file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
