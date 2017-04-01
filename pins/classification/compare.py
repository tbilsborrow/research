from __future__ import print_function
import sys
from collections import Counter

# compare 2 results files, show:
# - top 20 matching tags
# - top 20 tags only in each of the files but not the other

def printtop(title, counter):
    print('-------------------------')
    print(title)
    for item in counter.most_common(20):
        print('%4d: %s' % (item[1], item[0]))
    print(len(counter))

def main():
    if len(sys.argv) != 3:
        print("Usage: compare.py <file> <file>")
        print(" - need exacly 2 files to compare")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    matching = Counter()
    hist1 = Counter()
    hist2 = Counter()

    set1 = set()
    set2 = set()

    # get the sets of topics represented in each file
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        line1 = f1.readline()
        line2 = f2.readline()
        while line1 and line2:
            set1.update({s for s in line1.strip().split(',') if len(s) > 0})
            set2.update({s for s in line2.strip().split(',') if len(s) > 0})

            line1 = f1.readline()
            line2 = f2.readline()

    # line by line compare, and count pins with topics that match/don't match
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        line1 = f1.readline()
        line2 = f2.readline()
        while line1 and line2:
            s1 = {s for s in line1.strip().split(',') if len(s) > 0}
            s2 = {s for s in line2.strip().split(',') if len(s) > 0}

            for e in s2:
                if e in set1:
                    matching[e] += 1
                else:
                    hist2[e] += 1
            for e in s1:
                if e not in set2:
                    hist1[e] += 1

            line1 = f1.readline()
            line2 = f2.readline()

    
    printtop('Matching', matching)
    printtop('only in ' + file1, hist1)
    printtop('only in ' + file2, hist2)

if __name__ == "__main__":
    main()
