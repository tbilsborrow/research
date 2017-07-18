from __future__ import print_function
from dandelion import DataTXT
import sys
import os

client = DataTXT(app_id='9d7ee60076304802b131eccf185700c4', app_key='9d7ee60076304802b131eccf185700c4')


def process(line):
    if len(line) > 0:
        response = client.nex(line,
                            lang='en',
                            social_hashtag='true')
        return ",".join([os.path.basename(annotation.uri) for annotation in response.annotations]).encode('utf-8')
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
