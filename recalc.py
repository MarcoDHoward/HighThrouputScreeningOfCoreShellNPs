import os
import glob
import commands 
import json

allresults = dict()

codes = glob.glob("database/*@????_???")

for code in codes:
    print os.path.basename(code)
    # Find the most recent entry for this code
    entryPaths = glob.glob(os.path.join(code, "*"))
    entryPaths.sort(key= lambda x: os.path.getmtime(x))
    recentPath = entryPaths[-1]
    # Try to get the metadata.
    metadata = dict ( username = "unknown", 
                      hostname = "unknown",
                      pwd = "unknown",
                      timestamp = "unknown" )
    metapath = os.path.join(recentPath, "metadata.txt")
    if os.path.isfile(metapath):
        lines = open(metapath, 'r').readlines()
	if len(lines) == 4:
        	metadata = dict ( username = lines[0].strip(), 
                         	 hostname = lines[1].strip(),
                         	 pwd = lines[2].strip(),
                         	 timestamp = lines[3].strip() )
    status, lines = commands.getstatusoutput('python calculations.py %s' % os.path.basename(code))
    if status != 0:
        print "======== FAIL IN CALCULATIONS.PY ========"
        print lines
        import sys 
        sys.exit()
    if len(lines) > 0:
        for line in lines.split('\n'):
            if len(line) > 0:
		print line
                result = json.loads("%s" %line)
                result['username'] = metadata['username']
                key = "%d/%s/%s/%s/%s" % (result['a1'], result['M1'], result['a2'], result['M2'], result['result_type'])
                allresults[key] = result

json.dump(allresults, open('allresults.json', 'w'))
