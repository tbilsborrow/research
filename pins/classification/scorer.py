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
        # my own metric, turns out to be very close to jaccard, except I multiplied match by 2 because
        # I wanted to compare 2 sets (matching + only in s1, and matching + only in s2) so I figured
        # the matching set would count twice when combining these 2 sets
        return self.match * 2 / (self.match * 2 + self.s1 + self.s2)

    def jaccard(self):
        # https://en.wikipedia.org/wiki/Jaccard_index
        return self.match / (self.s1 + self.s2 + self.match)

    def precision(self):
        return self.match / (self.s2 + self.match)

    def recall(self):
        return self.match / (self.s1 + self.match)

    def fmeasure(self):
        # https://en.wikipedia.org/wiki/F1_score
        return 2 * (self.precision() * self.recall() / (self.precision() + self.recall()))


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
    print('jaccard: %f' % result.jaccard())
    print('precision: %f' % result.precision())
    print('recall: %f' % result.recall())
    print('F-measure: %f' % result.fmeasure())


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
