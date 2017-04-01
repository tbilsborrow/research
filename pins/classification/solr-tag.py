from __future__ import print_function
import solr
import sys
import re

con = solr.Solr('http://localhost:8983/solr/wikipedia_core')
mlt = solr.SearchHandler(con, "/mlt")

THRESHOLD = 0.9

def process(line):
    # replace some known utf-8 chars with ascii
    line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
    line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
    # remove the rest of the non-ascii chars
    line = re.sub(r'[^\x00-\x7F]+', ' ', line)

    r = mlt(mlt_fl='page_text', mlt_mindf=1, mlt_mintf=1, stream_body=line)
    return ",".join([d['page_name'] for d in r.results if d['score']/r.maxScore >= THRESHOLD]).encode('utf-8')


def main():
    try:
        for line in sys.stdin:
            print(process(line.strip()))
    except:
        print("FAIL! " + line, file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
