# -*- coding: utf-8 -*-
from __future__ import print_function
import solr
import sys
import re
from rosette.api import API, DocumentParameters, RosetteException

api = API(user_key="fd9fd7eb4b3e8e1173ee99a73dc6ce6c")

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


def process(line):
    # replace some known utf-8 chars with ascii
    line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
    line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
    # remove the rest of the non-ascii chars
    line = re.sub(r'[^\x00-\x7F]+', ' ', line).strip()
    if len(line) == 0:
        return ""

    tags = set()
    params = DocumentParameters()
    params["content"] = line
    try:
        results = api.entities(params)

        for entity in results.get('entities'):
            word = entity.get('normalized')
            wiki_title = '_'.join([remove_nonalpha(w) for w in word.split(' ')]).lower()
            tags.update(query(wiki_title))
    except RosetteException:
        pass

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
