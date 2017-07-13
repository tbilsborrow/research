from __future__ import print_function
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as Features
import sys
import os
import re
import solr

client = NaturalLanguageUnderstandingV1(
    username="965122cb-7ed1-4c71-8c64-ae638144a945",
    password="q8okYylfC1jz",
    version="2017-02-27")

con = solr.SolrConnection('http://10.1.11.210:8983/solr/wikipedia_core')
cache = set()

def query(w):
    if w in cache:
        return [w]
    results = [d['page_name'] for d in con.query('page_name:"%s" AND is_disambiguation:false' % w, fl='page_name')]
    cache.update(results)
    return results

def process(line):
    # replace some known utf-8 chars with ascii
    line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
    line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
    # remove the rest of the non-ascii chars
    line = re.sub(r'[^\x00-\x7F]+', ' ', line)

    if len(line) > 15:
        response = client.analyze(
            text=line,
            features=[
                Features.Entities()
            ],
            language='en'
        )
        tags = set()
        for entity in response['entities']:
            name = entity['text'].encode('ascii', 'ignore')
            tags.update(query(name))

        return ",".join(tags).encode('utf-8')
    else:
        return ""


def main():
    try:
        for line in sys.stdin:
            print(process(line.strip()))
    except:
        print("FAIL! " + line, file=sys.stderr)
        raise

if __name__ == "__main__":
    main()