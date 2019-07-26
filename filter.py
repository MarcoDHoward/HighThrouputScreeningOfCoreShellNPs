import json 
import job_generator

atom_list38 = []
atom_list79 = []

cohesive_38 = []
o_bin_38 = []
seg_38 = []
h_bin_38 = []

cohesive_79 = []
o_bin_79 = []
seg_79 = []
h_bin_79 = []

def sortByParticleSize(dict_list):
	atoms_79 = dict()
	atoms_38 = dict()
	keys = dict_list.keys()
	for key in keys:
		if int(dict_list[key]["a1"]) + int(dict_list[key]["a2"])  == 38:
			atoms_38.update({key:dict_list[key]})
		if int(dict_list[key]["a1"]) + int(dict_list[key]["a2"])  == 79:
			atoms_79.update( {key:dict_list[key]} )
	
	return atoms_38 ,  atoms_79

def sortByResultType(dict_list):
	cohesive = dict()
	binding = dict()
	segregation = dict()
	keys = dict_list.keys()
	for key in keys:
		if dict_list[key]["result_type"] == "Cohesive Energy":
			cohesive.update( {key:dict_list[key]} )
		if dict_list[key]["result_type"] == "Binding Energy":
			binding.update( {key:dict_list[key]} )
		if dict_list[key]["result_type"] == "segregation Energy":
			segregation.update( {key:dict_list[key]} )
	
	return cohesive, binding , segregation

def resultTypeBySize(dict_list):
	cohesive, binding, segregation = sortByResultType(dict_list)
	cohesive38, cohesive79 = sortByParticleSize(cohesive)
	binding38, binding79 = sortByParticleSize(binding)
	segregation38, segregation79 = sortByParticleSize(segregation)
	return [(cohesive38, binding38, segregation38), (cohesive79, binding79, segregation79)]




	
db = json.load( open("allresults.json", 'r') )

atoms38, atoms79 = resultTypeBySize(db)

print atoms38[1].keys()

		
		
			
		
		






		
