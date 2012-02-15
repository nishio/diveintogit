#!/usr/bin/env python

import git
import gitdb
from optparse import OptionParser

def shorten_hash(x):
    h = x[0]
    if not options.fullhash:
        h = h[:4]
    return tuple([h] + list(x)[1:])


def print_content(k):
    sha = gitdb.util.to_bin_sha(k)
    content = r.odb.stream(sha).read()
    try:
        s = content.decode("utf-8")
        print "=" * 10
        print s
        print "=" * 10
        print 
    except:
        print repr(content)


def print_full():
    print "HEAD:", new["HEAD"]
    for t in "branches tags index objs".split():
        print "%s:" % t
        for k in new[t]:
            print " ", shorten_hash(k)
            if t == "objs" and options.verbose:
                print_content(k[0])



parser = OptionParser()
parser.add_option("-v", "--verbose", help="print object's contents",
                  action="store_true", dest="verbose", default=False)
parser.add_option("-f", "--full_hash", help="print full(not shortened) hash",
                  action="store_true", dest="fullhash", default=False)
parser.add_option("-s", "--show", help="show particular object's detail",
                  action="store", dest="show_target")

(options, args) = parser.parse_args()


r = git.Repo(".")
new = {}

try:
    deref_head = r.head.object.hexsha
except ValueError:
    deref_head = None
new["HEAD"] = (open(".git/HEAD").read().strip(), deref_head)
new["index"] = set()

index = r.index.entries
for k in index:
    o = index[k] # IndexEntry
    new["index"].add((o.hexsha, o.path, o.flags, o.stage))

new["branches"] = set((b.object.hexsha, b.name) for b in r.branches)
new["tags"] = set((t.object.hexsha, t.name) for t in r.tags)

new["objs"] = set()
for k in r.odb.sha_iter():
    sha, typ, size = r.odb.info(k)
    new["objs"].add((git.to_hex_sha(sha), typ))
                

if options.show_target:
    target = [(sha, typ) for sha, typ in new["objs"] if sha.startswith(options.show_target)]
    for (k, typ) in target:
        sha = gitdb.util.to_bin_sha(k)
        content = r.odb.stream(sha).read()

        print "=" * 10
        print typ, k
        print "---contents---"
        try:
            s = content.decode("utf-8")
            # if it succeeded, it may readable text
            print s
        except:
            print content.decode("latin-1").encode("ascii", "replace")

        print "=" * 10
        print

else:
    print_full()
