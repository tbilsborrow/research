from __future__ import print_function
import sys
import json
import re

def main():

    outfilename = sys.argv[1] if len(sys.argv) > 1 else 'pin-board.html'

    with open(outfilename, 'w') as out:
        out.write('<html><head><link rel="stylesheet" href="pins.css"></head><body><article>\n')

        try:
            for line in sys.stdin:
                # replace some known utf-8 chars with ascii
                line = re.sub("\xe2\x80\x99", "x", line)  # U+2019 (right single quotation mark)
                line = re.sub("\xe2\x80\x93", "-", line)  # U+2013 (EN-DASH)
                # remove the rest of the non-ascii chars
                line = re.sub(r'[^\x00-\x7F]+', ' ', line)

                j = json.loads(line)
                out.write('<section><img src="%s"/><p/><a href="%s">%s</a></section>\n' % (j['image_url'], j['link'], j['description']))
        except:
            print("FAIL! " + line, file=sys.stderr)
            raise

        out.write('</article></body></html>\n')

if __name__ == "__main__":
    main()
