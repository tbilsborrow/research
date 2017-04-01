from __future__ import print_function
import textrazor
import sys
import os
import re

textrazor.api_key = "078fbfb764d9d56ce09815299032d845fd776bf1b7b1ec6afd2bc838"

client = textrazor.TextRazor(extractors=["entities"])
client.set_language_override("eng")

def process(line):
    # replace some known utf-8 chars with ascii
    line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
    line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
    # remove the rest of the non-ascii chars
    line = re.sub(r'[^\x00-\x7F]+', ' ', line)

    if len(line) > 0:
        response = client.analyze(line)
        return ",".join({os.path.basename(l.wikipedia_link) for l in response.entities() if l.wikipedia_link}).encode('utf-8')
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
