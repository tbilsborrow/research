from __future__ import print_function
import sys
from collections import Counter

# show top 20 tags from a results file in terms of number of pins

def main():

    num = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    h = Counter()

    try:
        for line in sys.stdin:
            h.update([w for w in line.strip().split(',') if len(w) > 0])
    except:
        print("FAIL! " + line, file=sys.stderr)
        raise

    # print(h)
    for item in h.most_common(num):
        print('%4d: %s' % (item[1], item[0]))
    print(len(h))

if __name__ == "__main__":
    main()
