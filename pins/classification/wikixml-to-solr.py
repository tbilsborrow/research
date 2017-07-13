from __future__ import print_function
import sys
from xml.dom import pulldom
import bz2
import solr

'''
This script will extract all pages from a wikipedia dump file and create solr documents
for each article. The wikipedia dump file must be a '-pages-articles.xml.bz2' file
from a location like https://dumps.wikimedia.org/enwiki/

You'll need this file locally, and specified as the argument to this script. This
script only works on a local solr instance that is assumed to have a 'wikipedia_core'
core already created.

Loading the full 5+ million articles will take many hours.
'''

def getNodeText(node):
    return ' '.join(t.nodeValue for t in node.childNodes if t.nodeType == t.TEXT_NODE)

def getText(nodelist):
    rc = []
    for node in nodelist:
        rc.append(getNodeText(node))
    return ''.join(rc)

if len(sys.argv) <= 1:
    print('Usage: python wikixml-to-solr.py <wikipedia xml.bz2 article dump file>')
    sys.exit(1)

con = solr.Solr('http://localhost:8983/solr/wikipedia_core')

filename = sys.argv[1]
f = bz2.BZ2File(filename)
xml = pulldom.parse(f)

counter = 0
docs = []
for event, node in xml:
    if event == pulldom.START_ELEMENT and node.tagName == 'page':
        xml.expandNode(node)
        if not node.getElementsByTagName('redirect'):
            id = getNodeText(node.getElementsByTagName('id')[0])
            title = getNodeText(node.getElementsByTagName('title')[0])
            text = getText(node.getElementsByTagName('text'))
            is_disambiguation = title.endswith('(disambiguation)')

            doc = {
                'id':id,
                'page_name':title,
                'page_text':getText(node.getElementsByTagName('text')),
                'is_disambiguation':is_disambiguation
            }
            docs.append(doc)
            counter += 1

            if counter % 100 == 0:
                print('[%d] last title: %s' % (counter, title))
                #print('writing %d to solr' % len(docs))
                con.add_many(docs, commit=True)
                #print('  written!')
                docs = []

if len(docs) > 0:
    print('writing last %d to solr' % len(docs))
    con.add_many(docs, commit=True)

print('done!')