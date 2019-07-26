import json

def findEmptyBoxes(jsonfile, calctable):
	db= json.loads(open(jsonfile).read())
	names = db.keys()
	names = [filterfunc(name, calctable) for name in names]
	names = set(names)
	all_elements = ['Sc', 'Ti',  'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 
                      'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 
                      'Hf', 'Ta',  'W', 'Re', 'Os', 'Ir', 'Pt', 'Au'] 
	all_names = []
	for a in all_elements:
		for b in all_elements:
			all_names.append("%s@%s" %(a,b))

	print set(all_names) - names


def filterfunc(name, calctable):
	pieces = []
	if calctable in name: ##we can specify if we want binding energy, cohesive energy, etc##
		pieces = name.split('/')
		return "%s@%s" %(pieces[1], pieces[3])

findEmptyBoxes( "allresults.json","Cohesive Energy")
