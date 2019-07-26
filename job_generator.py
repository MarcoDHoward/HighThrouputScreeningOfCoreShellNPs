#!/usr/bin/env python

import sys
import os.path
import os

import glob
import re
import commands
import math
import pickle

code_path = "./codes.txt"
db_path = "./database"
calc_folder_path = "./calc_folder"
bnp38_template_path = "./templates/bnp38"
finished_path = "./finished"
problem_folder = "./problem_calcs"
converged_folder = "./converged"
not_converged_folder = "./not_converged_bnp"
submitted_path = "./submitted"
waiting_path = "./waiting"

shell_metal79 = ['Sc','Cr','Mn','Fe','Zn', 'Y', 'Nb', 'Mo', 'Tc','Ru', 'Rh', 'Ag', 'Cd', 'Hf','Ta','Re', 'Os', 'Pt']
shell_metal38 = ['Hf','Ta','W','W','Re','Os','Ir','Au']
core_metal38  = ['Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd','Hf', 'Ta',  'W', 'Re', 'Os', 'Ir', 'Pt', 'Au','Hg']

 

def get_outcar_energy(filename):
#    print filename
#    status, result = commands.getstatusoutput("grep 'energy(sigma->0)' %s" % filename)
    status, result = commands.getstatusoutput("grep 'energy  without entropy' %s" % filename)
    if status != 0:
        return 0
    try:
        energy = float(result.split("\n")[-1].split()[-1])
    except NameError:
        energy = 0
    return energy
    
def get_energy(filename):
    path = os.path.join(os.path.dirname(filename), "OUTCAR_ENERGY")
    if os.path.isfile(path):
        return float(open(path, 'r').readline().strip())
    energy = get_outcar_energy(filename)
    f = open(path, 'w')
    f.write(str(energy))
    f.close()
    return energy

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

def generate_code_list():
	path = code_path
	
	bimetallic_bnp79_codes = []
	singlecomp_bnp79_codes = []
	
	bimetallic_bnp38_codes = []
	singlecomp_bnp38_codes = []
	
	bimetallic_npo79_codes = []
	singlecomp_npo79_codes = []

	bimetallic_npo38_codes = []
	singlecomp_npo38_codes = []

	bimetallic_sbn38_codes = []
	
	lines = open (path , 'r').readlines()
	for line in lines:
		compare = parseCode(line)
		
	####Generate lists for 79 atom nanoparticle calculations ####
		if compare["kind"] == "bnp" and (compare['M2'] in shell_metal79) and (compare['aM1'] == 19):
			bimetallic_bnp79_codes.append(compare)

		if compare["kind"] == "bnp" and (compare['M1'] in shell_metal79) and compare ['aM1'] == 79:
			singlecomp_bnp79_codes.append(compare)

		if compare["kind"] == "npo" and (compare['M2'] in shell_metal79) and (compare['aM1'] == 19):
			bimetallic_npo79_codes.append(compare)

		if compare["kind"] == "npo" and (compare['M1'] in shell_metal79) and compare ['aM1'] == 79:
			singlecomp_npo79_codes.append(compare)
		
		###Generate lists for 38 atom nanoparticle calculations###
		
		if compare["kind"] == "bnp" and (compare['M2'] in shell_metal38 and compare['M1'] in core_metal38) and compare['aM1'] == 6 and compare['aM1'] != 60:
			bimetallic_bnp38_codes.append(compare)

		if compare["kind"] == "bnp" and (compare['M1'] in shell_metal38) and compare ['aM1'] == 38:
			singlecomp_bnp38_codes.append(compare)

		if compare["kind"] == "npo" and (compare['M2'] in shell_metal38) and (compare['aM1'] == 6):
			bimetallic_npo38_codes.append(compare)

		if compare["kind"] == "npo" and (compare['M1'] in shell_metal38) and compare ['aM1'] == 38:
			singlecomp_npo38_codes.append(compare)
	
		if compare["kind"] == "sbn" and (compare['M2'] in shell_metal38 and compare['M1'] in core_metal38) and compare['aM1'] == 6 and compare['aM1'] != 60:
			bimetallic_sbn38_codes.append(compare)

	return [bimetallic_bnp79_codes, singlecomp_bnp79_codes, bimetallic_npo79_codes, singlecomp_npo79_codes, bimetallic_bnp38_codes, singlecomp_bnp38_codes, bimetallic_npo38_codes, singlecomp_npo38_codes, bimetallic_sbn38_codes]

def assemble_bimetallic_filename(codedict):
	x = codedict
	filename = "%d%s@%d%s_%s" %  (x['aM1'], x['M1'], x['aM2'], x['M2'], x['kind'])
	return filename

def assemble_bimetallic_jobname(codedict):
	x = codedict
	name = "%d%s_%d%s_%s" %  (x['aM1'], x['M1'], x['aM2'], x['M2'], x['kind'])
	return name	

def assemble_singlecomp_filename(codedict):
	x = codedict
	filename = "%d%s_%s" %(x['aM1'],x['M1'],x['kind'])
	return filename
	
def makeCalcFolders(jobname):
	if os.path.isfile(jobname) == False:
		os.mkdir(calc_folder_path + '/' + jobname)

def mod_POSCARdual(path):	
	dir_list = os.listdir(path)
	print dir_list
	for x in range (0, len(dir_list)):
		print dir_list[x]		
		os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		i = parseCode(dir_list[x])		
		lines = open("POSCAR", 'r').readlines() 
		print lines[0]
		print lines [5]
		lines[0] = "%s %s   \n" %(i['M2'], i['M1'])
		lines[5] = "%d %d   \n" %(i['aM2'], i['aM1'])
		f = open("POSCAR", 'w')
		for line in lines:
			f.write(line)
		f.close()
		os.chdir("../..")


def mod_POTCARdual(path):
	dir_list = os.listdir(path)
	for x in range (0, len(dir_list)):		
		os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		i = parseCode(dir_list[x])
		os.system("getpotpaw.pl %s %s" %(i['M2'], i['M1'] ))
		os.chdir("../..")

def submit_jobs(path,subfile):
	dir_list = os.listdir(path)
	x = 0
	for x in range (0, len(dir_list) ):
		os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		os.system("qsub %s" %subfile)
		os.chdir("../..")





def rename_jobs(path, subfile):
	dir_list = os.listdir(path)
	if subfile == "lonestar.sub" or subfile == "frilab1.sub":	
		for x in range (0, len(dir_list)):		
			os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
			lines = open("%s" %subfile, 'r').readlines()
			lines[1] = "#$ -N j%s \n" %(assemble_bimetallic_jobname(parseCode(dir_list[x]) ) )
			print(lines[1])
			f = open("%s" %subfile , 'w')
			for line in lines:
				f.write(line)
			f.close()
			os.chdir("../..")
			
	if subfile == "hopper.sub":
		for x in range (0, len(dir_list)):		
			os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
			lines = open("%s" %subfile, 'r').readlines()
			lines[1] = "#PBS -N \n" %(assemble_bimetallic_jobname(parseCode(dir_list[x]) ) )
			print(lines[1])
			f = open("%s" %subfile , 'w')
			for line in lines:
				f.write(line)
			f.close()
			os.chdir("../..")
	if subfile == "stampede.sub":
		for x in range (0, len(dir_list)):		
			os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
			lines = open("%s" %subfile, 'r').readlines()
			lines[1] = "#SBATCH -J \n" %(assemble_bimetallic_jobname(parseCode(dir_list[x]) ) )
			print(lines[1])
			f = open("%s" %subfile , 'w')
			for line in lines:
				f.write(line)
			f.close()
			os.chdir("../..")
			
def check_jobs(path,filename):
	if get_energy("%s/%s" %(path, filename)) > 0:
		print "%s did not finish" %path
		os.system("mv -r %s ./problem_calcs"  %path)

def check_finished(path):
	dir_list = os.listdir(path)
	x = 0
	for x in range(0, len(dir_list) ):
		if os.path.isfile("%s/%s/OUTCAR" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) ):
			os.system("mv %s/%s/ ./finished" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
			print "foo"
			#print ("%s finished" %dir_list[x])
 

def submit_toDB(path):
	dir_list = os.listdir(path)
	print dir_list	
	x = 0
	for x in range (0, len(dir_list) ):	
		os.chdir("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		os.system("fridb %s -u mdh2736" %dir_list[x])
		print ("fridb %s -u mdh2736" %dir_list[x])
		os.chdir("../..")
		os.system("mv %s/%s %s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) , submitted_path) ) 
		#os.chdir("..")
		

def cleanup(path):
	dir_list = os.listdir(path)	
	for x in range (0, len(dir_list) ):
		print "%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) )		
		os.chdir("%s/%s" %(path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		if os.path.isfile("CONTCAR.xyz"):
			os.system("rm -rf CONTCAR.xyz")

		if os.path.isfile("DOSCAR"):
			os.system("rm -rf DOSCAR")

		if os.path.isfile("ll_out"):
			os.system("rm -rf ll_out")

		if os.path.isfile("OUTCAR"):
			os.system("rm -rf OUTCAR")

		if os.path.isfile("OUTCAR_ENERGY"):
			os.system("rm -rf OUTCAR_ENERGY")

		if os.path.isfile("OSZICAR"):
			os.system("rm -rf OSZICAR")

		if os.path.isfile("OUTCAR"):
			os.system("rm -rf OUTCAR")

		if os.path.isfile("PCDAT"):
			os.system("rm -rf PCDAT")

		if os.path.isfile("REPORT"):
			os.system("rm -rf REPORT")

		if os.path.isfile("WAVECAR"):
			os.system("rm -rf WAVECAR")

		if os.path.isfile("XDATCAR"):
			os.system("rm -rf XDATCAR")

		if os.path.isfile("CHGCAR"):
			os.system("rm -rf CHGCAR")

		if os.path.isfile("EIGENVAL"):
			os.system("rm -rf EIGENVAL")

		if os.path.isfile("IBZKPT"):
			os.system("rm -rf IBZKPT")

		if os.path.isfile("CONTCAR"):
			os.system("rm -rf CONTCAR")

		os.chdir("../..")

def modify_EDIFFG(ediffg, path): #modify EDIFFG in INCAR
		dir_list = os.listdir(path)
		for x in range (0, len(dir_list)):		
			os.chdir("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
			lines = open("INCAR", 'r').readlines() 
			lines[7] = "EDIFFG=%f \n" %(ediffg)
			print(lines[7])
			f = open("INCAR" , 'w')
			for line in lines:
				f.write(line)
			
			f.close()
			os.chdir("../..")

def modify_NCORE(ncore, path): #modify NCORE in INCAR
		dir_list = os.listdir(path)
		for x in range (0, len(dir_list)):		
			os.chdir("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
			lines = open("INCAR", 'r').readlines() 
			lines[17] = "NCORE=%f \n" %(ncore)
			print(lines[17])
			f = open("INCAR" , 'w')
			for line in lines:
				f.write(line)
			
			f.close()
			os.chdir("../..")

def getINCARvalue(string):
	lines = open("INCAR", 'r').readlines()
	for line in lines:
		if string in line:
			f =  line.strip().split("=")
			return f[1]
			

def checkConverged(path):
	f = []	
	converged = []
	notconverged = []
	problem = []
	dir_list = os.listdir(path)
	print dir_list
	for x in range (0, len(dir_list )):
		os.chdir("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		if os.path.isfile("OUTCAR") and os.path.isfile("INCAR"):
			maxatomforce = commands.getstatusoutput("grep RMS OUTCAR | tail -n 1 | awk '{print $5}'")
			print maxatomforce
			print getINCARvalue("EDIFFG"), dir_list[x]
			ediffg = float(getINCARvalue("EDIFFG"))
			try:
				if float(maxatomforce[1]) <= math.fabs(ediffg):
					converged.append(assemble_bimetallic_filename(parseCode(dir_list[x]) ) )
				else:
					notconverged.append(assemble_bimetallic_filename(parseCode(dir_list[x]) ) )
			except ValueError:
				print "%s not working correctly" %dir_list[x]
				problem.append(assemble_bimetallic_filename(parseCode(dir_list[x]) ) )
				
		os.chdir("../..")
	return (converged, notconverged,problem)

def moveFiles(loc_from, loc_to, folder1, folder2):
	os.system("mv %s/%s %s/%s" %(loc_from,folder1,loc_to,folder2) )
	print ("mv %s/%s %s/%s" %(loc_from,folder1,loc_to,folder2) )

def copyFiles(loc_from, loc_to, file1, folder2):
	os.system("cp -r %s/%s %s/%s" %(loc_from,file1,loc_to,folder2) )
	print ("cp -r %s/%s %s/%s" %(loc_from,file1,loc_to,folder2) )

def separateConverged(path):
	conv_list = checkConverged(path)
	converged = conv_list[0]
	not_converged = conv_list[1]
	problem = conv_list[2]
	for i in range (0, len(converged) ):	
		moveFiles(path, converged_folder, converged[i], converged[i]) 
	for i in range(0, len(not_converged) ):
		moveFiles(path, not_converged_folder, not_converged[i], not_converged[i])
	for i in range(0, len(problem) ):
		moveFiles(path,problem_folder,  problem[i], problem[i])

###Helper method to modifyINCAR
def parseINCAR(path):
	lines = open("%s/INCAR" %path,'r' ).readlines()
	data = []
	tags = []
	value = []
	for line in lines:
		data.append(line.strip().split("="))
		
	for i in range (0, len(data)):
		data_pair = data[i]
		tags.append(data_pair[0])
		value.append(data_pair[1])

	return dict(zip(tags,value) )
	
##Helper method to modifyINCAR method
def writeINCAR(path, INCARdict):  
	f = open("%s/INCAR" %path, 'w' )
	for k,v in INCARdict.items():	
		print k,v		
		f.write('%s=%s\n' %(k,v) )

def modifyINCAR(key,value,path):
	print path	
	dir_list = os.listdir(path)
	print dir_list
	for x in range (0, len(dir_list) ):
		d = parseINCAR("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		d["%s"%key] = value
		writeINCAR("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ),d )

def pluginSD(path):  ##updates INCAR to the correct settings for a steepest descent calculation
	modifyINCAR("IBRION", 3 , path)
	modifyINCAR("POTIM", 0 , path)
	modifyINCAR("IOPT", 4, path)
	modifyINCAR("MAXMOVE", 0.1, path)
	modifyINCAR("SDALPHA", 0.01, path)

##Helper Function for the reconverge method##

def updatePreviousRun(previous_run):
	s = re.search(r"previous_run", previous_run)
	n = re.search(r"(\d+)", previous_run)
	increment = int(n.group() ) + 1
	return s.group() + str(increment)

def reconverge(path):
	dir_list = os.listdir(path)
	print dir_list
	for x in range (0, len(dir_list) ):
		print "%s" %assemble_bimetallic_filename(parseCode(dir_list[x]) )
		os.chdir("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		if os.path.isfile("INCAR") and os.path.isfile("CONTCAR"):
			##updates previous_run1 to previous_run2 etc...##			
			previous_runs = glob.glob("previous_run*")
			previous_runs.sort()
			if previous_runs != []:		
				os.system("vfin.pl %s" %updatePreviousRun(previous_runs[-1]))
			else:
				os.system("vfin.pl previous_run1")
		os.chdir("../..")
		#os.system("mv %s/%s %s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ), waiting_path ) ) 

def checkForces(path):
	dir_list = os.listdir(path)
	for x in range (0, len(dir_list) ):
		os.chdir("%s/%s" %(path, assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		if os.path.isfile("INCAR") and os.path.isfile("CONTCAR"):		
			#os.system("vef.pl")
			output = commands.getstatusoutput("vef.pl" ) 
			print output[1]
			f = open("./forces", "w")
			f.write(output[1])			
			os.chdir("../..")

def makeJobs(codedict, templatepath, calcfolderpath):
	for i in range (0, len(codedict)):
		os.system("cp -r %s %s/%s" %(templatepath, calcfolderpath, assemble_bimetallic_filename(dir_list[i]) ) )
		print ("cp -r %s %s/%s" %(templatepath, calcfolderpath, assemble_bimetallic_filename(dir_list[i]) ) )

	mod_POSCARdual("%s" %calcfolderpath)
	mod_POTCARdual("%s" %calcfolderpath)	

def copySubmissionScript(filename, path):
	dir_list = os.listdir(path)
	for x in range (0, len(dir_list)):
		os.system("cp -r %s %s/%s"  %(filename, path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )
		print ("cp -r %s %s/%s" %(filename,path,assemble_bimetallic_filename(parseCode(dir_list[x]) ) ) )

def makeJobsFromPickle(pickleList, calcfolderpath):
	code_list = pickle.load( open( pickleList, "rb" ) )
	for i in range (0, len(code_list)):
		codedict = parseCode(code_list[i])
		if codedict["aM1"] == 6 and codedict["aM2"] == 32:
			
			if codedict['kind'] == "bnp":
				templatepath = "./templates/bnp38"
				
			if codedict['kind']  == "npo":
				templatepath = "./templates/npo38"
		
			if codedict['kind'] == "sbn":
				templatepath = "./templates/sbn38"

		if codedict["aM1"] == 19 and codedict["aM2"] == 60:

			if codedict['kind'] == "bnp":
				templatepath = "./templates/bnp79"
				
			if codedict['kind']  == "npo":
				templatepath = "./templates/npo79"
			
		os.system("cp -r %s %s/%s" %(templatepath, calcfolderpath, assemble_bimetallic_filename(codedict) ) )
		print ("cp -r %s %s/%s" %(templatepath, calcfolderpath, assemble_bimetallic_filename(codedict) ) )
				 

	mod_POSCARdual("%s" %calcfolderpath)
	mod_POTCARdual("%s" %calcfolderpath)	
		
	
	



###main##










