#!/usr/bin/env python

import sys
import os.path
import os
from numpy import *
import glob
import re
import json
import commands

####variables###
code_path = "./codes.txt"
db_path = "./database"
e_cos = 0
e_bind = 0
total_info = dict({"M1":None, "M2":None, "a1":None, "a2":None, "result_type":None, "result":None, "metadata":None, "url":{"s1":None, "s2":None} })
s= 0

tableData = json.load( open("./allresults.json", 'r'))


##### Utility Methods ##################################################################################

#args are path to the database probably /home/fri/public_html/fridb/database
#Returns a List of directories in the database.  This is the list we will check against to see if we have all of the right folders to do a calculation
def dir_list(head_dir):
        dirList = []
        dirList = os.listdir(head_dir)
        return (dirList)

#args are the code corresponding to a calculation of interest

def parseCode(value):
	core_shell = []
	core_shell = re.findall(r'[0-9]+', value)
	pieces = " ".join(re.findall("[a-zA-Z]+", value)).split()		
	if len(pieces) == 2 and core_shell == []:
		return dict({'M1':pieces[0], 'M2':None, 'kind':pieces[1], 'aM1':1, 'aM2':0})
	if len(pieces) == 2 and core_shell != []:
		return dict({'M1':pieces[0], 'M2':None, 'kind':pieces[1], 'aM1':int(core_shell[0]), 'aM2':0})		
	if len(pieces) == 3 and len(core_shell) == 2:
		return dict({'aM1':int(core_shell[0]), 'aM2':int(core_shell[1]),  'M1':pieces[0], 'M2':pieces[1], "kind":pieces[2]})
	if len(pieces) == 3 and len(core_shell) == 1:
		return dict({'aM1':int(core_shell[0]), 'aM2':0,  'M1':pieces[0], 'M2':pieces[1], "kind":pieces[2]})

def getUser(path):
	userName = "unknown"	
	if os.path.isfile(path+"/metadata.txt"):
		lines = open (path+"/metadata.txt", 'r').readlines()
		userName = lines[0].strip()
		return userName
	else:
		return userName

def get_outcar_energy(filename):
#    print filename
    status, result = commands.getstatusoutput("grep 'energy(sigma->0)' %s" % filename)
    #status, result = commands.getstatusoutput("grep 'energy  without entropy' %s" % filename)
    if status != 0:
        return 0
    try:
        energy = float(result.split("\n")[-1].split()[-1])
    except NameError:
        energy = 0
    return energy
    
def get_energy(filename):
    path = os.path.join(os.path.dirname(filename), "OUTCAR_ENERGY")
    if os.path.isfile(path):  ##commented out to re-write all OUTCAR_ENERGY
        return float(open(path, 'r').readline().strip())
    energy = get_outcar_energy(filename)
    f = open(path, 'w')
    f.write(str(energy))
    f.close()
    return energy


    

#################################### Methods for Combination Calculations ####################################
#args are path to required OUTCAR [particle, M1, M2].  M1_atoms and M2_atoms are integers that correspond to the number of atoms of each componenet
def e_cos(particle, M1, M2, M1_atoms, M2_atoms):
	particle_e = get_energy(particle)
	M1_e = get_energy(M1)
	M2_e = get_energy(M2)
	#print("particle %s" %particle_e)
	#print("M1 %s" %M1_e)
	#print("M2 %s" %M2_e)	
	e = particle_e - (M1_atoms*M1_e + M2_atoms*M2_e)
	return e 

#args are path to requiedr OUTCAR
def e_bin(particle_o, particle, ref):
	particle_oe = get_energy(particle_o)
	particle_e = get_energy(particle)
	o_e = get_energy(ref)
	e = particle_oe - particle_e - o_e*0.5
	#print("particle npo %s" %particle_oe)	
	#print("particle %s" %particle_e)
	#print("o sng %s" %o_e)
	return e 
	
def e_segregation(particle_sbn, particle_bnp):
	e = get_energy(particle_sbn) - get_energy(particle_bnp)
	return e

def e_segregationOxygen(particle_sno, particle_bnp):
	e = get_energy(particle_sno) - get_energy(particle_bnp)
	return e


####Method for Comparison Calculation args, need to test ###
#def e_lowest(lowest, lowestTry):
#	if get_energy(lowestTry) < get_energy(lowest):
#		return get_energy(lowestTry) 



### Methods that check if the correct files are present for a Derivative calculation ###
### If all the correct files are present these will return the paths to the correct files ####


#returns paths to OUTCARS for a cohesive energy calculation

	#args: codedict is a dictionary containing the code info, db_path is the path to the database
		#use parsecode method defined above to generate a dictionary from the code
def e_cos_dir_present(codedict,db_path):
	x = codedict
	path = db_path
	m1 = ""
	m2 = ""	
	file1 = []
	file2=[]
	file3=[]	
	m1_atoms = x['aM1']
	m2_atoms = x['aM2']	
	m1 = x['M1']
	m2 = x['M2']

	if x['kind'] == "sng":
		return []
	if x['kind'] == "npo":
		return []

	if m2_atoms == None or m2 == None:	
		folder1 = str(x['aM1'])+str(x['M1'])+"_"+str(x['kind'])
		folder2 = m1+"_sng"
		folder3 = folder2  ##this was done becasue we return a list with three elements. Only folder1 and folder2 have relevant information
	else:
		folder1 = str(x['aM1'])+str(x['M1'])+"@"+str(x['aM2'])+str(x['M2'])+"_"+str(x['kind'])
		folder2 = m1+"_sng"
		folder3 = m2+"_sng"
		
	
	if folder1 in dir_list(path) and folder2 in dir_list(path) and folder3 in dir_list(path):		
		file1 = glob.glob(path+'/'+folder1+'/*')
		file2 = glob.glob(path+'/'+folder2+'/*')
		file3 = glob.glob(path+'/'+folder3+'/*')
		file1.sort(key = lambda s: os.path.getmtime(s))
		file2.sort(key = lambda s: os.path.getmtime(s))	
		file3.sort(key = lambda s: os.path.getmtime(s))
		if file1 == [] or file2 == [] or file3 == []:
			return []
		else:		
			p1 = file1[-1]
			p2 = file2[-1]
			p3 = file3[-1]	
			return [p1,p2,p3]
	else:
		return []

#### Returns Paths to OUTCARS for oxygen binding energy #####
def ebin_dir_present(codedict,db_path):
	x = codedict
	path = db_path
	f1 = []
	f2=[]
	f3=[]
	folder1 = ""
	folder2 = ""
	folder3 = ""
	
	if x['kind'] == "nph":
		return []
	
	if x['aM2'] == "0":  #we have a single component particle, so we do not want to include "0" in the name of the folder
		if x['kind'] == "npo":	
			folder1 = "%d%s_%s" %(x['aM1'],x['M1'],x['kind'])
			folder2 = "%d%s_bnp" %(x['aM1'],x['M1'])
			folder3 = "O_sng"
		if x['kind'] == "bnp":
			folder1 = "%d%s_npo" %(x['aM1'],x['M1'])
			folder2 = "%d%s_%s" %(x['aM1'],x['M1'],x['kind'])
			folder3 = "O_sng"
	
	else:  # we have a two component particle, so the number of metal2 atoms should be present

		if x['kind'] == "npo":	
			folder1 ="%d%s@%d%s_%s" %(x['aM1'],x['M1'],x['aM2'],x['M2'],x['kind'])
			folder2 = "%d%s@%d%s_bnp" %(x['aM1'],x['M1'],x['aM2'],x['M2'])
			folder3 = "O_sng"
		if x['kind'] == "bnp":
			folder1 = "%d%s@%d%s_npo" % (x['aM1'], x['M1'], x['aM2'], x['M2'])
			folder2 = "%d%s@%d%s_%s" %  (x['aM1'], x['M1'], x['aM2'], x['M2'], x['kind'])
			folder3 = "O_sng"
	
	#look to see if there are any folders in the directtory structure that match our criteria###	
	if folder1 in dir_list(path) and folder2 in dir_list(path) and folder3 in dir_list(path):
		file1 = glob.glob(path+'/'+folder1+'/*')
		file2 = glob.glob(path+'/'+folder2+'/*')
		file3 = glob.glob(path+'/'+folder3+'/*')
		file1.sort(key = lambda s: os.path.getmtime(s))
		file2.sort(key = lambda s: os.path.getmtime(s))	
		file3.sort(key = lambda s: os.path.getmtime(s))		
		if file1 == [] or file2 == [] or file3 == []:
			return []
		else:		
			p1 = file1[-1]
			p2 = file2[-1]
			p3 = file3[-1]	
			return [p1,p2,p3]
	else:
		return []

def eHbin_dir_present(codedict,db_path):
	x = codedict
	path = db_path
	f1 = []
	f2=[]
	f3=[]
	folder1 = ""
	folder2 = ""
	folder3 = ""
	if x["kind"] == "npo":
		return []
	
	if x['aM2'] == "0":  #we have a single component particle, so we do not want to include "0" in the name of the folder
		if x['kind'] == "nph":	
			folder1 = "%d%s_%s" %(x['aM1'],x['M1'],x['kind'])
			folder2 = "%d%s_bnp" %(x['aM1'],x['M1'])
			folder3 = "H_sng"
		if x['kind'] == "bnp":
			folder1 = "%d%s_nph" %(x['aM1'],x['M1'])
			folder2 = "%d%s_%s" %(x['aM1'],x['M1'],x['kind'])
			folder3 = "H_sng"
	
	else:  # we have a two component particle, so the number of metal2 atoms should be present

		if x['kind'] == "nph":	
			
			folder1 ="%d%s@%d%s_%s" %(x['aM1'],x['M1'],x['aM2'],x['M2'],x['kind'])
			folder2 = "%d%s@%d%s_bnp" %(x['aM1'],x['M1'],x['aM2'],x['M2'])
			folder3 = "H_sng"
			#print folder1, folder2, folder3
			
		if x['kind'] == "bnp":
			folder1 = "%d%s@%d%s_nph" % (x['aM1'], x['M1'], x['aM2'], x['M2'])
			folder2 = "%d%s@%d%s_%s" %  (x['aM1'], x['M1'], x['aM2'], x['M2'], x['kind'])
			folder3 = "H_sng"
	
	#look to see if there are any folders in the directtory structure that match our criteria###	
	if folder1 in dir_list(path) and folder2 in dir_list(path) and folder3 in dir_list(path):
		file1 = glob.glob(path+'/'+folder1+'/*')
		file2 = glob.glob(path+'/'+folder2+'/*')
		file3 = glob.glob(path+'/'+folder3+'/*')
		file1.sort(key = lambda s: os.path.getmtime(s))
		file2.sort(key = lambda s: os.path.getmtime(s))	
		file3.sort(key = lambda s: os.path.getmtime(s))		
		if file1 == [] or file2 == [] or file3 == []:
			return []
		else:		
			p1 = file1[-1]
			p2 = file2[-1]
			p3 = file3[-1]
			return[p1, p2, p3]	
			
	else:
		return []

###returns path to paths for segregation energy####		
def e_seg_dir_present(codedict, dbpath):
	x = codedict
	path = db_path
	m1 = ""
	m2 = ""	
	file1 = []
	file2=[]
	file3=[]	
	m1_atoms = x['aM1']
	m2_atoms = x['aM2']	
	m1 = x['M1']
	m2 = x['M2']

	if x['kind'] == "sng":
		return []
	if x['kind'] == "npo":
		return []
	if x['kind'] == "sno":
		return []

	if m2_atoms == None or m2 == None:	#we have a single component particle and there is nothing to snpregate#
		return []
	if x['kind'] == "sbn":
		folder1 = str(x['aM1'])+str(x['M1'])+"@"+str(x['aM2'])+str(x['M2'])+"_"+str(x['kind'])
		folder2 = "%d%s@%d%s_bnp" %  (x['aM1'], x['M1'], x['aM2'], x['M2'])
	
	if x['kind'] == "bnp":
		folder1 = "%d%s@%d%s_sbn" %  (x['aM1'], x['M1'], x['aM2'], x['M2'])
		folder2 = "%d%s@%d%s_%s" %  (x['aM1'], x['M1'], x['aM2'], x['M2'], x['kind'])
		
		
	if folder1 in dir_list(path) and folder2 in dir_list(path):
		file1 = glob.glob(path+'/'+folder1+'/*')
		file2 = glob.glob(path+'/'+folder2+'/*')
		file1.sort(key = lambda s: os.path.getmtime(s))
		file2.sort(key = lambda s: os.path.getmtime(s))	
		if file1 == [] or file2 == []:
			return []
		else:		
			p1 = file1[-1]
			p2 = file2[-1]	
			return [p1,p2]
	else:
		return []


###returns paths for segregation energy with oxygen adsorbed on surface###
def e_sno_dir_present(codedict, dbpath):
	x = codedict
	path = db_path
	m1 = ""
	m2 = ""	
	file1 = []
	file2=[]
	file3=[]	
	m1_atoms = x['aM1']
	m2_atoms = x['aM2']	
	m1 = x['M1']
	m2 = x['M2']

	if x['kind'] == "sng":
		return []
	if x['kind'] == "bnp":
		return []
	if x['kind'] == "sbn":
		return []

	if m2_atoms == None or m2 == None:	#we have a single component particle and there is nothing to snpregate#
		return []
	if x['kind'] == "sno":
		folder1 = str(x['aM1'])+str(x['M1'])+"@"+str(x['aM2'])+str(x['M2'])+"_"+str(x['kind'])
		folder2 = "%d%s@%d%s_npo" %  (x['aM1'], x['M1'], x['aM2'], x['M2'])
	
	if x['kind'] == "npo":
		folder1 = "%d%s@%d%s_sno" %  (x['aM1'], x['M1'], x['aM2'], x['M2'])
		folder2 = "%d%s@%d%s_%s" %  (x['aM1'], x['M1'], x['aM2'], x['M2'], x['kind'])
		
		
	if folder1 in dir_list(path) and folder2 in dir_list(path):
		file1 = glob.glob(path+'/'+folder1+'/*')
		file2 = glob.glob(path+'/'+folder2+'/*')
		file1.sort(key = lambda s: os.path.getmtime(s))
		file2.sort(key = lambda s: os.path.getmtime(s))	
		if file1 == [] or file2 == []:
			return []
		else:		
			p1 = file1[-1]
			p2 = file2[-1]	
			return [p1,p2]
	else:
		return []

###returns for lowestEnergy###
##need to test ##
'''
def e_low_dir_present(codedict, dbpath):
	x = codedict
	path = db_path
	m1 = ""
	m2 = ""	
	file1 = []
	file2=[]
	file3=[]	
	m1_atoms = x['aM1']
	m2_atoms = x['aM2']	
	m1 = x['M1']
	m2 = x['M2']

	if x['kind'] == "sng":
		return []
	if x['kind'] == "bnp":
		return []
	if x['kind'] == "sbn":
		return []

	if m2_atoms == None or m2 == None:	#we have a single component particle and there is nothing to snpregate#
		return []
	if x['kind'] == "low":
		folder1 = str(x['aM1'])+str(x['M1'])+"@"+str(x['aM2'])+str(x['M2'])+"_"+str(x['kind'])
		folder2 = "%d%s@%d%s_bnp" %  (x['aM1'], x['M1'], x['aM2'], x['M2'])
	
	if folder1 in dir_list(path) and folder2 in dir_list(path):
		file1 = glob.glob(path+'/'+folder1+'/*')
		file1.sort(key = lambda s: os.path.getmtime(s))
		lowestEnergy = 10000 #gurantees we we enter the loop
		lowestIndex = 0
		for i in range(0, len(file1) ):
			if ( get_energy(file1[i]+"/OUTCAR") < lowestEnergy ): #search all of the low tags and compare to the lowest energy.
				lowestEnergy =  get_energy(file1[i]+"/OUTCAR" #if its lower then we have found a more stabel struct
				lowestIndex = i  #rember the index so we can return the path
		file2 = glob.glob(path+'/'+folder2+'/*')
		file2.sort(key = lambda s: os.path.getmtime(s))	
		if file1 == [] or file2 == []:
			return []
		else:		
			p1 = file1[lowestIndex]
			p2 = file2[-1]	
			return [p1,p2]
	else:
		return []

'''


###method used to generate a list of possible codes when we get an sng code###
def generate_code_list(codedict):
	x = codedict
	path = code_path
	possible_codes = []	
	lines = open (path , 'r').readlines()
	for line in lines:
		compare = parseCode(line)
		if compare["kind"] != "sng" and (x['M1'] == str(compare['M1']) or x['M1'] == str(compare['M2']) and compare['kind'] == "bnp"):
			possible_codes.append(line)
		if compare["kind"] != "sng" and x['M1'] == "O" and  compare['kind'] == "npo":
			possible_codes.append(line)
		if compare["kind"] != "sng" and x['M1'] == "H" and  compare['kind'] == "nph":
			possible_codes.append(line)
	return possible_codes 
			
#####assemble metadata#####

def assemble_ecos_meta(codedict): ##for cohesive energy##
	meta_info = codedict
	return "%d%s@%d%s_bnp: %f by %s<br> %s_sng: %f by %s<br> %s_sng: %f by %s"  % (meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[0]+"/OUTCAR"), getUser(calc_paths[0]), meta_info['M1'], get_energy(calc_paths[1]+"/OUTCAR"), getUser(calc_paths[1]), meta_info['M2'], get_energy(calc_paths[2] + "/OUTCAR"),getUser(calc_paths[2]))
	
def assemble_ebin_meta(codedict): ##for oxygen binding energy##
	meta_info = codedict
	return "%d%s@%d%s_npo: %f by %s<br> %d%s@%d%s_bnp: %f by %s<br> O_sng:%f by %s<br>"  %(meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[0]+"/OUTCAR"), getUser(calc_paths[0]), meta_info['a1'], 	meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[1]+"/OUTCAR"), getUser(calc_paths[1]), get_energy(calc_paths[2] + "/OUTCAR"), getUser(calc_paths[2])  )

def assemble_eHbin_meta(codedict): ##for hydrogen binding energy##
	meta_info = codedict
	return "%d%s@%d%s_nph: %f by %s<br> %d%s@%d%s_bnp: %f by %s<br> H_sng:%f by %s<br>"  %(meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[0]+"/OUTCAR"), getUser(calc_paths[0]), meta_info['a1'], 	meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[1]+"/OUTCAR"), getUser(calc_paths[1]), get_energy(calc_paths[2] + "/OUTCAR"), getUser(calc_paths[2])  )


def assemble_eseg_meta(codedict): ##for segregation energy##
	meta_info = codedict
	return "%d%s@%d%s_sbn: %f by %s<br> %d%s@%d%s_bnp: %f by %s" %(meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[0]+"/OUTCAR"), getUser(calc_paths[0]), meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[1]+"/OUTCAR"), getUser(calc_paths[1]) )

def assemble_esno_meta(codedict): ##for segregation energy with oxygen adsorbed##
	meta_info = codedict
	return "%d%s@%d%s_sno: %f by %s<br> %d%s@%d%s_npo: %f by %s" %(meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[0]+"/OUTCAR"), getUser(calc_paths[0]), meta_info['a1'], meta_info['M1'], meta_info['a2'], meta_info['M2'], get_energy(calc_paths[1]+"/OUTCAR"), getUser(calc_paths[1]) )
	
	
	
####### Main #########

code = sys.argv[1]
code_info = parseCode(code)
calc_paths = []

total_info["M1"] = code_info["M1"]
total_info["M2"] = code_info["M2"]
total_info["a1"] = code_info["aM1"]
total_info["a2"] = code_info["aM2"]


 

### If the code we get is a bnp do this###
if code_info['kind'] == "bnp":
	
	#then calculate cohesive energy#

	calc_paths = e_cos_dir_present(code_info, db_path)	
	if len(calc_paths) == 3:
		e_cose = e_cos(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR", int(code_info['aM1']), int(code_info['aM2']))
		total_info["result_type"] = "Cohesive Energy"
		total_info["result"] = str(e_cose)
		total_info["metadata"] = assemble_ecos_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR" 		
		print json.dumps(total_info)
	
	#calculate oxygen binding energy#

	calc_paths = ebin_dir_present(code_info, db_path)
	if len(calc_paths) == 3:
		e_bind = e_bin(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR")
		total_info["result_type"] = "Binding Energy"	
		total_info["result"] = str(e_bind)
		total_info["metadata"] = assemble_ebin_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		
		print json.dumps(total_info)

	#calculate hydrogen binding energy#

	calc_paths = eHbin_dir_present(code_info, db_path)
	if len(calc_paths) == 3:
		e_bind = e_bin(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR")
		total_info["result_type"] = "Hydrogen Binding Energy"	
		total_info["result"] = str(e_bind)
		total_info["metadata"] = assemble_ebin_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)
		
	#calculate snpregation energy#
	calc_paths = e_seg_dir_present(code_info, db_path)
	if len(calc_paths) == 2:
		e_seg = e_segregation(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR")
		total_info["result_type"] = "Segregation Energy"
		total_info["result"] = str(e_seg) 
		total_info["metadata"] = assemble_eseg_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)

	


### If the code we get is npo do this###

if code_info['kind'] == "npo":

	#then only calculate the binding energy#
	
	calc_paths = ebin_dir_present(code_info, db_path)
	if len(calc_paths) ==3:
		e_bind = e_bin(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR")
		total_info["result_type"] = "Binding Energy"
		total_info["result"] = str(e_bind)
		total_info["metadata"] = assemble_ebin_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)

	#calculate segregation energy with oxygen adsorbed#
	calc_paths = e_sno_dir_present(code_info, db_path)
	if len(calc_paths) == 2:
		e_sno = e_segregationOxygen(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR")
		total_info["result_type"] = "Segregation Energy With Oxygen"
		total_info["result"] = str(e_sno) 
		total_info["metadata"] = assemble_esno_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)


####If the code we get is nph do this#####

if code_info['kind'] == "nph":

	#then only calculate the binding energy#
	
	calc_paths = eHbin_dir_present(code_info, db_path)
	if len(calc_paths) ==3:
		e_bind = e_bin(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR")
		total_info["result_type"] = "Hydrogen Binding Energy"
		total_info["result"] = str(e_bind)
		total_info["metadata"] = assemble_eHbin_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)


###if the code we get is sng do this###
if code_info['kind'] == "sng" and code_info['M1'] != "O" and code_info['M1'] != "H":
	code_list = generate_code_list(code_info)
	code_list_dict = []
	calc_paths_list = []
	i = 0
	while i < len(code_list):
		code_list_dict.append(parseCode(code_list[i]))
		i = i + 1
	i = 0	
	while i < len(code_list_dict):		
		code_list_test = code_list_dict[i]
		if code_list_test['kind'] == "bnp":		
			calc_paths = e_cos_dir_present(code_list_test, db_path)
			
		if len(calc_paths) == 3:
			calc_code = parseCode(calc_paths[0].split('/')[2]) # use this code for calculation
			e_cose = e_cos(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR", int(calc_code['aM1']), int(calc_code['aM2']))
			total_info["result"] = str(e_cose)
			total_info["a1"] = calc_code['aM1']			
			total_info["a2"] = calc_code['aM2']
			total_info["result_type"] = "Cohesive Energy"
			total_info["M2"] = calc_code['M2']
			total_info["M1"] = calc_code['M1']
			total_info["metadata"] = assemble_ecos_meta(total_info)
			total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
			#total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
			print json.dumps(total_info)
		i = i + 1

if code_info['kind'] == "sng" and code_info['M1'] == "O":
	code_list = generate_code_list(code_info)
	code_list_dict = []
	calc_paths_list = []
	i = 0
	while i < len(code_list):
		code_list_dict.append(parseCode(code_list[i]))  ##create a dictionary out of a set of list of string codes
		i = i + 1
	
	i = 0	
	while i < len(code_list_dict):		
		code_list_test = code_list_dict[i]		
		calc_paths = ebin_dir_present(code_list_test, db_path)	
		if len(calc_paths) == 3:
			calc_code = parseCode(calc_paths[0].split('/')[2]) # use this code for calculation
			e_bine = e_bin(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR")
			total_info["result"] = str(e_bine)
			total_info["a1"] =  calc_code['aM1']			
			total_info["a2"] = calc_code['aM2']
			total_info["result_type"] = "Binding Energy"
			total_info["M2"] = calc_code['M2']
			total_info["M1"] = calc_code['M1']
			total_info["metadata"] = assemble_ebin_meta(total_info)
			total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
			total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
			print json.dumps(total_info)
		i = i + 1
###Do this if we get the Hydrogen Reference###
if code_info['kind'] == "sng" and code_info['M1'] == "H":
	code_list = generate_code_list(code_info)
	code_list_dict = []
	calc_paths_list = []
	i = 0
	while i < len(code_list):
		code_list_dict.append(parseCode(code_list[i]))  ##create a dictionary out of a set of list of string codes
		i = i + 1
	
	i = 0	
	while i < len(code_list_dict):		
		code_list_test = code_list_dict[i]		
		calc_paths = eHbin_dir_present(code_list_test, db_path)	
		if len(calc_paths) == 3:
			e_bine = e_bin(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR", calc_paths[2]+"/OUTCAR")
			total_info["result"] = str(e_bine)
			total_info["a1"] =  code_list_test['aM1']			
			total_info["a2"] = code_list_test['aM2']
			total_info["result_type"] = "Binding Energy"
			total_info["M2"] = code_list_test['M2']
			total_info["M1"] = code_list_test['M1']
			total_info["metadata"] = assemble_ebin_meta(total_info)
			total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
			total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
			print json.dumps(total_info)
		i = i + 1

## if we get code sbn do this###
if code_info['kind'] == "sbn":
	
	#calculate snpregation energy#
	calc_paths = e_seg_dir_present(code_info, db_path)
	if len(calc_paths) == 2:
		e_seg = e_segregation(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR")
		total_info["result_type"] = "Segregation Energy"
		total_info["result"] = str(e_seg)
		total_info["metadata"] = assemble_eseg_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)

## if we get code sno do this###
if code_info['kind'] == "sno":
	
	#calculate snpregation energy#
	calc_paths = e_sno_dir_present(code_info, db_path)
	if len(calc_paths) == 2:
		e_sno = e_segregationOxygen(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR")
		total_info["result_type"] = "Segregation Energy With Oxygen"
		total_info["result"] = str(e_sno)
		total_info["metadata"] = assemble_esno_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)

###need to test for lowest calc###
'''
if code_info['kind'] == "low":
	
	#calculate snpregation energy#
	calc_paths = e_low_dir_present(code_info, db_path)
	if len(calc_paths) == 2:
		e_sno = e_segregationOxygen(calc_paths[0]+"/OUTCAR", calc_paths[1]+"/OUTCAR")
		total_info["result_type"] = "Segregation Energy With Oxygen"
		total_info["result"] = str(e_sno)
		total_info["metadata"] = assemble_esno_meta(total_info)
		total_info["url"]["s1"] = calc_paths[0]+"/CONTCAR"
		total_info["url"]["s2"] = calc_paths[1]+"/CONTCAR"
		print json.dumps(total_info)
	
'''	




	

	


		


	


		
	
	
	
	
	
	
	
	

 









