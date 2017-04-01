from __future__ import print_function
from __future__ import division
import sys

# compare 1 or more results files against a "baseline" file

class Result:
    def __init__(self, num=0):
        self.match = 0
        self.s1 = 0
        self.s2 = 0
        self.num = num

    def add(self, r):
        self.match += r.match
        self.s1 += r.s1
        self.s2 += r.s2
        self.num += r.num

    def score(self):
        return self.match * 2 / (self.match * 2 + self.s1 + self.s2)


def compare_entities(set1, set2):
    result = Result(1)
    for e in set1:
        if e in set2:
            result.match += 1
        else:
            result.s1 += 1
    for e in set2:
        if e not in set1:
            result.s2 += 1 
    return result


# for scoring and reporting, this checks the overlap PER PIN (not overall)
def compare(baseline_filename, compare_filename):
    result = Result()
    with open(baseline_filename, 'r') as baseline, open(compare_filename, 'r') as compare:
        b_line = baseline.readline()
        c_line = compare.readline()
        while b_line and c_line:
            b_set = {s for s in b_line.strip().split(',')}
            c_set = {s for s in c_line.strip().split(',')}
            result.add(compare_entities(b_set, c_set))
            
            b_line = baseline.readline()
            c_line = compare.readline()
            # break

    print('--------------------')
    print('number of lines: %d' % result.num)
    print('matching: %d' % result.match)
    print('%s only: %d' % (baseline_filename, result.s1))
    print('%s only: %d' % (compare_filename, result.s2))
    print('score: %f' % result.score())


def main():
    if len(sys.argv) < 3:
        print("Usage: scorer.py <baseline file> <test file>+")
        print(" - need at least 2 files to compare")
        sys.exit(1)

    baseline = sys.argv[1]
    for x in range(2, len(sys.argv)):
        compare(baseline, sys.argv[x])

if __name__ == "__main__":
    main()
