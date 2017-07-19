from __future__ import print_function
import solr
import sys
import re
import rake

con = solr.SolrConnection('http://localhost:8983/solr/wikipedia_core')

cache = set()


def remove_nonalpha(w):
    return re.sub('[\W_]+', '', w)


def query(w):
    if w in cache:
        return [w]
    # print('>>>> [%s]' % w)
    results = [d['page_name'] for d in con.query('page_name_lower:%s AND is_disambiguation:false' % w, fl='page_name')]
    cache.update(results)
    return results


def process(rake_object, line):
    # replace some known utf-8 chars with ascii
    line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
    line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
    # remove the rest of the non-ascii chars
    line = re.sub(r'[^\x00-\x7F]+', ' ', line)

    tags = set()
    keywords = rake_object.run(line)
    for word in keywords:
        wiki_title = '_'.join([remove_nonalpha(w) for w in word[0].split(' ')]).lower()
        tags.update(query(wiki_title))

    return ",".join(tags).encode('utf-8')


def main():
    try:
        rake_object = rake.Rake("SmartStoplist.txt", 5, 3, 1)
        for line in sys.stdin:
            print(process(rake_object, line.strip()))
    except:
        print("FAIL! " + line, file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
