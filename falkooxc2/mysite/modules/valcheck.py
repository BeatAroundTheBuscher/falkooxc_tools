from modules.config import staticpath, basepasswd, showtraceback
from modules.config import linestring, instancedatastring, nomergestring, hasnotypestring, extraspritedelemiter, formatdictname
import functools
import traceback
import re
import random
import itertools
import yaml
from yaml.composer import Composer
from yaml.constructor import Constructor
try:
	from yaml import CSafeLoader as Loader
	from yaml import CSafeDumper as Dumper
except ImportError:
	from yaml import SafeLoader as Loader
	from yaml import SafeDumper as Dumper
from jsonschema import validate, Draft4Validator
from jsonschema.exceptions import ValidationError
from jsonschema.validators import extend
import copy

checklist={} #contains all checkfunctions filed by decorator at compile time
schemavalidators={}  #contains all additional validation functions for schema check


#schemacdata={} #for global read! access to cdata in schema checks
#schemacdatatest={}


def adderror(errors,categ,name,cont,pos,tip=""):
	errors.append((categ,name,cont,pos,tip))

def checkfunc(func):    
	def inner(wraperr,wrapcdata,wrapparam):
		try:          
			func(wraperr,wrapcdata,wrapparam)
		except Exception as e:
			adderror(wraperr,"runfailed",func.__name__[6:], traceback.format_exc() if showtraceback else repr(e),"in code") 
	ret=functools.update_wrapper(inner, func)
	checklist[func.__name__[6:]]=ret        
	return ret


@checkfunc
def check_tabs(err,cdata,param):
	for li,line in enumerate(cdata.get("datastr","").split("\n")):
		if "\t" in line:
			adderror(err,"syntax","tabs",line,li) 							
@checkfunc
def check_indentation(err,cdata,param):	
	cpos=0
	for li,line in enumerate(cdata.get("datastr","").splitlines()):
	#for li,line in enumerate(cdata.get("datastr","").split("\n")):
		if len(line.strip())==0 or line.strip()[0]=="#":
			continue
		spaces=len(re.split("[^ ]",line)[0])
		if not spaces in range(0,cpos+param.get("space",2)+1,param.get("space",2)):
			adderror(err,"syntax","indentation",line,li)
		#else:
		cpos=spaces
@checkfunc
def check_forbiddenwords(err,cdata,param):
	for li,line in enumerate(cdata.get("datastr","").split("\n")):
		for word in param.get("words",[]):
			if word in line:
				adderror(err,"syntax","forbiddenwords",word+" not allowed: "+line,li) 
@checkfunc
def check_yamlload(err,cdata,param):
	if not cdata.get("yamlloaderror",None) is None:
		exc=cdata["yamlloaderror"]
	#try:
	#	test=yaml.safe_load(cdata.get("datastr",""))
	#except yaml.YAMLError as exc:
		if hasattr(exc, 'problem_mark'):
			mark = exc.problem_mark
			adderror(err,"syntax","yamlload","problem_mark@ line:%s col:%s " % (mark.line+1, mark.column+1),mark.line+1) 			
		else:
			adderror(err,"syntax","yamlload","unknown yamlerror","-1") 			

def compmodlen(mod1,mod2,errors,path):
	if isinstance(mod1,dict) and len (mod1)!=len(mod2):
		xinfo=[]
		xdiff=[int(str(x)[20:]) if isinstance(x,int) else x[20:] for x in mod1]		
		adderror(errors,"syntax","uniqdict","property defined multiple times: "+repr(list(set([x for x in xdiff if xdiff.count(x)>1]))),path) 			
	if isinstance(mod1,list):
		for ei,elem in enumerate(mod1):
			compmodlen(mod1[ei],mod2[ei],errors,path+[ei])
	elif isinstance(mod1,dict):
		for elem in mod1:			
			ekey=elem
			#print(elem)
			if (not "__len__" in dir(elem) or  len(elem)>=20):				
				try:
					eskey=int(str(elem)[20:])				
				except TypeError :
					eskey=ekey[20:]				
				except ValueError :
					eskey=ekey[20:]				
				if (isinstance(eskey,int) and eskey<0):
					adderror(errors,"syntax","negativekey","uniqedict cant handle negative keys",path) 			
				else:
					compmodlen(mod1[ekey],mod2[eskey],errors,path+[eskey])

@checkfunc
def check_uniqdict(err,cdata,param):
	kcteststr=re.sub(r'[^\x00-\x7F]', 'x', cdata.get("datastr",""))
	kclines=[]
	for x in kcteststr.split("\n"):
		kclines.append(x+"\n")
	kctestnewstr=""
	p=re.compile('[A-Z0-9a-z_-]+\ *:')
	for kcl in kclines:
		for x in p.findall(kcl):
			#print(98,x)
			kcl=kcl.replace(x,"%d"%random.randint(10**19,10**20-1)+x)
		kctestnewstr+=kcl
	test=yaml.load(cdata.get("datastr",""), Loader=Loader)
	test2=yaml.load(kctestnewstr, Loader=Loader)
	compmodlen(test2,test,err,[])

@checkfunc
def check_checkdelete(err,cdata,param):
	for categ in cdata["dellist"]:
		clist=cdata["data"].get(categ,[])
		if not isinstance(clist,list): continue
		found={}
		ditems=[]
		for ei,elem in enumerate(clist):
			if not isinstance(elem,dict): continue
			if "delete" in elem:
				fstr=repr(elem["delete"])
				found[fstr]=found.get(fstr,[])
				found[fstr].append(elem.get(linestring,1))
				if len([x for x in elem if not x in [linestring,formatdictname]])!=1: 
					adderror(err,"delete","amountproperties",fstr,elem.get(linestring,1),"in: "+categ)
				nodeltype="nodeletetype %d"%random.randint(10**19,10**20-1)
				foundelems=len([x for x in cdata["base"][categ] if x.get(cdata["unlist"][categ],nodeltype)==elem["delete"]])
				if foundelems==0:
					adderror(err,"delete","amounttarget","no target found: "+fstr,elem.get(linestring,1),"in: "+categ)
				if foundelems>1:
					adderror(err,"delete","amounttarget","more than one target found: "+fstr,elem.get(linestring,1),"in: "+categ)
			else:
				if cdata["unlist"][categ] in elem:
					ditems.append(repr(elem[cdata["unlist"][categ]]))
		for fstr in found:
			if len(found[fstr])>1:
				adderror(err,"delete","multipledeletion","delete entry exists more than once("+str(len(found[fstr]))+") /  lines: "+repr(found[fstr])+" : "+fstr,elem.get(linestring,1),"in: "+categ)					
			if fstr in 	ditems:
				adderror(err,"delete","deleteexisting","deletes an existing/nonbase object  lines: "+repr(found[fstr])+" : "+fstr,found[fstr][0],"in: "+categ)					

@checkfunc
def check_uniqlist(err,cdata,param):
	for categ in cdata["unlist"]:		
		clist=cdata["data"].get(categ,[])
		if not isinstance(clist,list): continue
		found={}
		for ei,elem in enumerate(clist):
			if not isinstance(elem,dict): continue
			if "delete" in elem: continue
			if cdata["unlist"][categ] in elem:
				found[elem[cdata["unlist"][categ]]]=found.get(elem[cdata["unlist"][categ]],[])
				found[elem[cdata["unlist"][categ]]].append(elem.get(linestring,1))				
		for fstr in found:
			if len(found[fstr])>1:
				for l in found[fstr]:
					adderror(err,"semantic","multiplelistelems","entry with same '"+cdata["unlist"][categ]+": "+fstr+"' exists more than once lines: "+repr(found[fstr]),l,"in: "+categ)					

@checkfunc
def check_oxcautoreference(err,cdata,param):	

	 for xi,x in enumerate(cdata["data"].get("research",[])):
	 	if not x.get("name",hasnotypestring) in cdata["lists"]["refall"]["unlockableresearch"]:
	 		if x.get("needItem",False) and  not x.get("name",hasnotypestring) in cdata["lists"]["refall"]["items:type"]:	 			
	 			adderror(err,"semantic","oxcautoreference","research object "+x.get("name",hasnotypestring)+" needs item but no item referenced",x.get(linestring,1),repr(["research",xi,"needItem"]))					
	 for xi,x in enumerate(cdata["data"].get("manufacture",[])):
	 	if not "producedItems" in x   \
	 		and not x.get("name",hasnotypestring) in cdata["lists"]["refall"]["items:type"] \
 			and not x.get("name",hasnotypestring) in cdata["lists"]["refall"]["crafts:type"]:
 			adderror(err,"semantic","oxcautoreference","manufacture object "+x.get("name",hasnotypestring)+" has no producedItems but name not in crafts/item list referenced",x.get(linestring,1),repr(["manufacture",xi,"name"]))					
	 # for xi,x in enumerate(cdata["data"]["manufacture"]):
	 # 	if not "producedItems" in  x and \


	 # 		.get("name",hasnotypestring) in cdata["lists"]["refall"]["unlockableresearch"]:
	 # 		if x.get("needItem",False) and  not x.get("name",hasnotypestring) in [y.get("type",hasnotypestring+"notthere") for y in cdata["alldata"]["items"]]:	 			
	 # 			adderror(err,"semantic","oxcautoreference","research object "+x.get("name",hasnotypestring)+" needs item but no item referenced",x.get(linestring,1),repr(["research",xi,"needItem"]))					

	# if value[0]+":"+value[2] in alllists: 		
	# 	if not instance in alllists[value[0]+":"+value[2]]:
	# 		yield ValidationError('oxc;{} is referenced to /{} but not found there'.format(instance, value[0]))
	# pass
	# for categ in cdata["unlist"]:
	# 	clist=cdata["data"].get(categ,[])
	# 	if not isinstance(clist,list): continue
	# 	found={}
	# 	for ei,elem in enumerate(clist):
	# 		if not isinstance(elem,dict): continue
	# 		if "delete" in elem: continue
	# 		if cdata["unlist"][categ] in elem:
	# 			found[elem[cdata["unlist"][categ]]]=found.get(elem[cdata["unlist"][categ]],[])
	# 			found[elem[cdata["unlist"][categ]]].append(elem.get(linestring,1))				
	# 	for fstr in found:
	# 		if len(found[fstr])>1:
	# 			for l in found[fstr]:
	# 				adderror(err,"semantic","oxcautoreference","todo",l,"in: "+categ)					

@checkfunc
def check_langmissesstring(err,cdata,param):	
	test={}
	langl={}
	for l in cdata["data"].get("extraStrings",[]):
		if "type" in l:
			langl[l["type"]]=1
			for w in l.get("strings",[]):
				test[w]=test.get(w,{})
				test[w][l["type"]]=1
	for w in test:
		if len(test[w])<len(langl):

			adderror(err,"semantic","langmissesstring","the string {} is missing for languages {}".format(w,list(set(langl.keys()).difference(set(test[w].keys())))),"ExtraStrings","ExtraStrings")					
@checkfunc
def check_aliendeployment(err,cdata,param):	
	if "alienDeployments" in cdata["data"] and "alienItemLevels" in cdata["data"]:
		maxalienl=max([max(x) for x in cdata["data"]["alienItemLevels"]])
		
		for xi,x in enumerate(cdata["data"]["alienDeployments"]):
			for d in x.get("data",[]):
				if len(d.get("itemSets",[]))-1 != maxalienl:
					adderror(err,"semantic","aliendeployment","the aliendeployment itemset list of {} rank {} needs to be {} long".format(x.get("type","NOTYPE!"), d.get("alienRank","NORANK!"),maxalienl+1),d.get(linestring,1),repr(["alienDeployments",xi,"type"]))

@checkfunc
def check_listorder(err,cdata,param):	
	lcategs="items,craft,facility,inv,research,manufacture,ufopaedia".split(",") 
	for categ in cdata["unlist"]:
		if not categ in lcategs: continue
		clist=cdata["data"].get(categ,[])
		for ei,elem in enumerate(clist):
			if "delete" in elem: continue			
			if "listOrder" in elem: continue
			k=elem.get(cdata["unlist"][categ],hasnotypestring)
			if k in cdata["lists"]["refbase"][categ+":"+cdata["unlist"][categ]]: continue
			if categ=="items" and not elem.get("recover",True): continue
			if categ=="research" and elem.get("cost",0)==0: continue
			if categ=="ufopaedia" and elem.get("section","NOSECTION")=="STR_NOT_AVAILABLE": continue
			adderror(err,"info","listorder","no listorderproperty for {}-{}={} ".format(categ,cdata["unlist"][categ],k),elem.get(linestring,1),repr([categ,ei,cdata["unlist"][categ]]))

@checkfunc
def check_mapscriptcheck(err,cdata,param):	

	"""TODO?
addcraft/ufo should be before addBlock
addcraft/ufo rect bigger than crafts/ufos
"""
	allowedprop=dict(
    addBlock=["size", "rects", "groups", "blocks", "freqs", "maxUses"],
    fillArea=["size", "rects", "groups", "blocks", "freqs", "maxUses"],
    addCraft=["size", "rects", "groups", "blocks", "freqs", "maxUses"],
    addUFO=["size", "rects", "groups", "blocks", "freqs", "maxUses"],
    addLine=["size", "rects", "direction"],
    digTunnel=["size", "rects", "tunnelData", "direction"],# , "groups", "blocks", "freqs", "maxUses", ?
    checkBlock=["size", "rects", "groups", "blocks"],
    removeBlock=["size", "rects", "groups", "blocks"],
    resize=["size", "rects", "groups", "blocks"],
    ALL=[linestring,"type","conditionals", "executionChances", "executions", "label"]
    )
	mapdata=cdata["alldata"].get("mapScripts",[])		
	terdata=cdata["alldata"].get("terrains",[])		
	termcdamount={}	
	terscripts=set()
	defaultterscripts=set()
	noterscripts=set()
	defaultnoterscripts=set()
	possiblescripts=set()
	terdict={}	
	for ter in terdata:		
		gtmp=[]
		for ti,t in enumerate(ter.get("mapBlocks",[])):
			if "groups" in t:
				groupconv=t["groups"] if isinstance(t["groups"],list) else [t["groups"]]
			else:
				groupconv=[0]
			gtmp.append([ti,groupconv,t.get("width",10),t.get("length",10),t.get("name",hasnotypestring),False])
		terdict[ter.get("name",hasnotypestring)]=gtmp
		termcdamount[ter.get("name",hasnotypestring)]=len(ter.get("mapDataSets",[]))
		if ter.get("textures",[]):
			if "script" in ter:
				terscripts.add((ter.get("name",hasnotypestring),ter.get("script","NOTDEFAULT")))
			else:
				defaultterscripts.add((ter.get("name",hasnotypestring),"DEFAULT"))
		else:
			if "script" in ter:
				noterscripts.add((ter.get("name",hasnotypestring),ter.get("script","NOTDEFAULT")))
			else:
				defaultnoterscripts.add((ter.get("name",hasnotypestring),"DEFAULT"))

	allscripts=set()
	allscripts=allscripts.union(terscripts)
	allscripts=allscripts.union(defaultterscripts)
	allscripts=allscripts.union(noterscripts)
	allscripts=allscripts.union(defaultnoterscripts)
	defaultallscripts=set()	
	defaultallscripts=defaultallscripts.union(defaultterscripts)	
	defaultallscripts=defaultallscripts.union(defaultnoterscripts)

	depldata=cdata["alldata"].get("alienDeployments",[])		
	for depl in depldata:
		if not "script" in depl and not "terrains" in depl: #normal ufo
			possiblescripts=possiblescripts.union(defaultterscripts)
			possiblescripts=possiblescripts.union(terscripts)
		if "script" in depl and not "terrains" in depl: #weird  but possible
			possiblescripts=possiblescripts.union(set([(x[0],depl["script"]) for x in defaultterscripts]))
		if not "script" in depl and  "terrains" in depl: #base, terror, ... missions
			for t in depl.get("terrains",[]):
				possiblescripts=possiblescripts.union(set([x for x in allscripts if x[0]==t]))
		if "script" in depl and  "terrains" in depl: #alienbase, cydonia2
			for t in depl.get("terrains",[]):
				possiblescripts=possiblescripts.union(set([x for x in terscripts if x[0]==t]))
				possiblescripts=possiblescripts.union(set([x for x in noterscripts if x[0]==t]))
				possiblescripts=possiblescripts.union(set([(x[0],depl["script"]) for x in defaultallscripts if x[0]==t]))
	tmp=[x for x in terdict if not x in [y[0] for y in possiblescripts]]
	if tmp: adderror(err,"mapscriptcheck","unusedterrain","the terrains {} is never used".format(tmp),"-",repr(["terrains"]))
	tmp=[x.get("type",hasnotypestring) for x in mapdata if not x.get("type",hasnotypestring) in [y[1] for y in possiblescripts]]
	if tmp: adderror(err,"mapscriptcheck","unusedscripts","the scripts {} is never used".format(tmp),"-",repr(["mapScripts"]))

	listconversion=["conditionals", "groups", "blocks", "freqs", "maxUses"]
	properties=dict([("size",[1,1]),("label",0),("type",""),("rects",[]),("tunnelData",{}),("direction",""),("executionChances",100),("executions",1)])
	for ei,script in enumerate(mapdata):
		labels={}
		scriptname=script.get("type",hasnotypestring)
		possibleterrains=[x[0] for x in possiblescripts if x[1]==scriptname]
		addblockdone=[]
		for ci,command in enumerate(script.get("commands",[])):			
			data=dict()
			for x in properties:
				data[x]=command.get(x,properties[x])
			if isinstance(data["size"],int):
				data["size"]=[data["size"],data["size"]]
			for x in listconversion:
				if x in command:
					if isinstance(command[x],int):
						data[x]=[command[x]]
					else:
						data[x]=command[x]
			if data["type"] =="addCraft" and addblockdone:
				adderror(err,"mapscriptcheck","craftufoafteraddblocks","the {} should be before any blockadding {}, script {}".format(data["type"],addblockdone,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))
			if data["type"] =="addUFO" and addblockdone:
				adderror(err,"mapscriptcheck","craftufoafteraddblocks","the {} should be before any blockadding {}, script {}".format(data["type"],addblockdone,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))
			if data["type"] in ["addBlock", "fillArea"]:
				addblockdone.append((ci,data["type"]))

			if 0 in data.get("conditionals",[]):
				adderror(err,"mapscriptcheck","conditionzero","conditional '0' is useless, script {}".format(scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))
			condlabelcheck=set([abs(x) for x in data.get("conditionals",[]) if  x!=0]).difference(set(labels.keys()))
			if condlabelcheck:
				adderror(err,"mapscriptcheck","conditionmissref","conditional {} references a label {} that is not in earlier commands, script {}".format(data.get("conditionals",[]),condlabelcheck,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))			
			rectcheck=[ rect for rect in data["rects"] if rect[2]<data["size"][0] or rect[3]<data["size"][1]]
			if rectcheck:
				adderror(err,"mapscriptcheck","rectsize","the block size: {} does not fits into rects {}, script {}".format(data["size"],rectcheck,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))			
			if "groups" in data and "blocks" in data:
				adderror(err,"mapscriptcheck","blockandgroup","having block and group in the same command is wierd, script {}".format(scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))			
			for tmp in ["maxUses","freqs"]:
				if tmp in data and len(data[tmp])!=max(len(data.get("blocks",[])),len(data.get("groups",[]))):
					adderror(err,"mapscriptcheck","blockinfoarray","the length of {} should be the same as blocks/groups list, script {}".format(tmp,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))			
			if command.get("type",hasnotypestring) in allowedprop:
				tmp=[x for x in command if  x not in allowedprop[command.get("type",hasnotypestring)]+allowedprop["ALL"]]
				if tmp:
					adderror(err,"mapscriptcheck","unusedparameter","the command {} does not use these commands {}, script {}".format(command.get("type",hasnotypestring),tmp,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))

			for poter in possibleterrains:
				if "tunnelData" in command:
					tmp=[x for x in command["tunnelData"].get("MCDReplacements",[]) if x.get("set",999)>=termcdamount.get(poter,-1)]
					if tmp:
						adderror(err,"mapscriptcheck","mcdsetwrong","the tunnel set {} does not match to mapDataSets in {} , script {}".format([(x.get("type",hasnotypestring),x.get("set",999)) for x in tmp],poter,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))
				if "blocks" in command:
					btmp=[]
					if "blocks" in allowedprop[command.get("type",hasnotypestring)]:
						if "blocks" in command:
							btmp=data["blocks"]
					bproblem1=[]
					for b in btmp:						
						foundoneb=False
						for x in terdict.get(poter,[]):
							if b == x[0]:
								if x[2]==10*data["size"][0] and x[3]==10*data["size"][1]: 
									foundoneb=True
									terdict[poter][x[0]][5]=True
						if not foundoneb: bproblem1.append(b)
					if bproblem1:
						adderror(err,"mapscriptcheck","nonfittingblock","no fitting mapblock-blocks in terrain {} found for blocks {} , script {}".format(poter,bproblem1,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))
				else:					
					gtmp=[]
					if command.get("type",hasnotypestring)=="addLine":
						if command.get("direction",hasnotypestring)=="both": gtmp=[2,3,4]
						if command.get("direction",hasnotypestring)=="horizontal": gtmp=[2]
						if command.get("direction",hasnotypestring)=="vertical": gtmp=[3]
					elif "groups" in allowedprop[command.get("type",hasnotypestring)]:
						if not "groups" in command:
							gtmp=[0]
							if command.get("type",hasnotypestring) in ["addCraft", "addUFO"]: gtmp=[1]
						else:
							gtmp=data["groups"]
					gproblem1=[]					
					for g in gtmp:						
						foundoneg=False
						for x in terdict.get(poter,[]):
							if g in x[1]:
								if x[2]==10*data["size"][0] and x[3]==10*data["size"][1]: 
									foundoneg=True
									terdict[poter][x[0]][5]=True
						if not foundoneg: gproblem1.append(g)
					if gproblem1:
						adderror(err,"mapscriptcheck","nonfittinggroup","no fitting mapblock-group in terrain {} found for groups {} , script {}".format(poter,gproblem1,scriptname),command.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))

			labels[data["label"]]=labels.get(data["label"],[])
			labels[data["label"]].append((ci,command.get("type",hasnotypestring)))

		for label in labels:
			if len(labels[label])>1 and label>0:
				adderror(err,"mapscriptcheck","nonuniquelabel","label {} should be unique in script {} used in {}".format(label,scriptname,labels[label]),script.get(linestring,1),repr(["mapScripts",ei,cdata["unlist"]["mapScripts"]]))
	
	for t in terdict:
		if t != "XBASE": #xcom base is setup without scriptrefernce :/
			tmp=[(x[0],x[4]) for x in terdict[t] if not x[5]]
			if tmp:
				adderror(err,"mapscriptcheck","unusedterrainblocks","in terrain {} the blocks {} are unused ".format(t,tmp),"-",repr(["terrains"]))
			#print()
#		tmp=[x for x in terdict if not x in [y[0] for y in possiblescripts]]
#	if tmp: adderror(err,"mapscriptcheck","unusedterrain","the terrains {} is never used".format(tmp),"-",repr(["terrains"]))


def guessline(obj,path,lastline="noline"):	
	if isinstance(obj,list):
		if len(path)>0 and isinstance(path[0],int) and len(obj)>path[0]:
			return guessline(obj[path[0]],path[1:],lastline=lastline)
		else:
			return lastline
	elif isinstance(obj,dict):
		if linestring in obj:
			lastline=obj[linestring]
		if len(path)>0 and path[0] in obj:
			return guessline(obj[path[0]],path[1:],lastline=lastline)
		else:
			return lastline
	else:
		return lastline

		
#import time
@checkfunc
def check_schema(err,cdata,param):
#	globals()["schemacdata"]=cdata

#	globals()["schemacdatatest"][repr(time.clock())]=time.clock()
#	print (999,globals()["schemacdatatest"])
	valdict={}
	for x in param.get("extendvalidator",[]):
		if x in schemavalidators:
			valdict[schemavalidators[x][0]]=schemavalidators[x][1]
			#print(inspect.getframeinfo(inspect.currentframe()))
			#print(inspect.getsourcelines(schemavalidators[x][1]))
		else:
			adderror(err,"config","validatormissing",repr(x),"config") 	
	#print(valdict)
	customValidator  = extend(Draft4Validator, valdict, 'oxcschema')
#	customValidator  = extend(Draft4Validator, {'oxcGL_refFileId': oxcrefFileIdOneK}, 'oxcschema')
	newschema=copy.deepcopy(cdata["schema"])
	newschema[instancedatastring]=cdata
	newschema[instancedatastring]["params"]=param
	v = customValidator(newschema)

	for error in v.iter_errors(cdata["data"]):
		ep=list(error.path)
		#if len(ep)>1 and isinstance(data,dict) and isinstance(ep[0],str) and isinstance(ep[1],int) and ep[0] in unlist and ep[0] in data and isinstance(data[ep[0]],list) and ep[1]<len(data[ep[0]]) and isinstance(data[ep[0]][ep[1]],dict) and unlist[ep[0]] in data[ep[0]][ep[1]]:
		#	ep[1]=str(ep[1])+":"+unlist[ep[0]]+"="+data[ep[0]][ep[1]][unlist[ep[0]]]
		#adderror(err,"schema-","multiplelistelems","entry with same '"+cdata["unlist"][categ]+": "+fstr+"' exists more than once lines: "+repr(found[fstr]),l)					
#		print(99,"schema-"+ (error.message.split(";")[0] if error.message.startswith("oxc") else "data"),error.validator,error.message,guessline(cdata["data"],list(ep)),list(ep))		
		if error.message.startswith("oxc;"):
			em=";".join(error.message.split(";")[1:])
		else:
			em=re.sub(", '"+linestring+"': [0-9]+", '', error.message)
			em=re.sub("'"+linestring+"': [0-9]+, ", '', em)
#			em=re.sub(linestring, '', error.message)
		adderror(err,"schema-"+ (error.message.split(";")[0] if error.message.startswith("oxc") else "data"),error.validator,em,guessline(cdata["data"],list(ep)),repr(list(ep)))
		#print(error.validator,error.message," -  in - /"+"/".join([str(x) for x in ep]))
	


def oxcrefFileIdOneK(validator, value, instance, schema):
	validator.schema[instancedatastring]["haha"]=validator.schema[instancedatastring].get("haha",0)+1
	#print ("HAHAHAHAHAHA",globals()["schemacdata"]["unlist"])	
	for v in value:      
		if (instance*v[3]+v[2]) >=1000:
			yield ValidationError('oxc;fileid {}->{} is bigger than 1000'.format(instance*v[3],(instance*v[3]+v[2])))
schemavalidators["oxcrefFileIdOneK"]=("oxcGL_refFileId",oxcrefFileIdOneK)

def oxcKey(validator, value, instance, schema):
#	alllists=globals()["schemacdata"]["lists"]["refall"]	
	alllists=validator.schema[instancedatastring]["lists"]["refall"]		
#	print(dir(value),dir(instance),dir(schema),dir(validator))
	#print(validator.schema[instancedatastring])
	#print(ValidationError("").args)
	for sk in value:		
		elist=[]
		if not isinstance(instance,dict):continue
		for vk in instance.keys():
			if vk == linestring: continue
			if not isinstance(vk,str): continue
			if re.match(sk[0],vk):
				if not vk in alllists[sk[1][0]+":"+sk[1][2]]:
					elist.append(vk)
		if elist:
			yield ValidationError('oxc;{} is referenced to /{} but not found there'.format(elist, sk[1][0]))
schemavalidators["oxcKey"]=("oxcGL_checkKey",oxcKey)

def oxcValue(validator, value, instance, schema):
	#alllists=globals()["schemacdata"]["lists"]["refall"]	
	alllists=validator.schema[instancedatastring]["lists"]["refall"]	
	if value[0]+":"+value[2] in alllists: 		
		if not instance in alllists[value[0]+":"+value[2]]:
			yield ValidationError('oxc;{} is referenced to /{} but not found there'.format(instance, value[0]))
schemavalidators["oxcValue"]=("oxcGL_lookupVal",oxcValue)

# def oxcrefFileId(validator, value, instance, schema):
# 	#print(value,instance)
# 	#filecategories=globals()["schemacdata"]["filecategories"]
# 	#reffileids=globals()["schemacdata"]["lists"]["reffileids"]
# 	#csprites=globals()["schemacdata"]["csprites"]
# 	filecategories=validator.schema[instancedatastring]["filecategories"]
# 	reffileids=validator.schema[instancedatastring]["lists"]["reffileids"]
# 	csprites=validator.schema[instancedatastring]["csprites"]
# 	print(csprites)
# 	print(reffileids)
# 	print(filecategories)
# 	#print(99,value)
# 	for sk in value: #for all fileidschecks in object
# 		elist=[]
# 		if not isinstance(instance,dict):continue
# 		for vk in instance.keys(): #for all properties
# 			if not isinstance(vk,str): continue
# 			if sk[0]==vk: #if propertiy=check-property
# 				for v in sk[3]: #for all implied references (crafts->3 references
# 					if v[0] in csprites:
# 						if instance[vk]>csprites[v[0]][0]:
# 							refkey=(filecategories[csprites[v[0]][2]],v[0])
# 							fid=(instance[vk]*v[3]+v[2])
# 							elestr='{}.{}: {} => {}'.format(sk[2],sk[0],instance[vk],fid)
# 							if v[1]>1: elestr+='-{}'.format(fid-1+v[1])
# 							if not refkey in reffileids:
# 								yield ValidationError('oxc;{} needs a {} entry'.format(elestr,refkey))
# 							else:
# 								nofileids=[]
# 								for i in range(v[1]):
# 									if not fid+i in reffileids[refkey]:
# 										nofileids.append(fid+i)
# 									else:
# 										reffileids[refkey][fid+i].append(elestr)
# 								if nofileids:
# 									yield ValidationError('oxc;{} needs fileids {} in {}'.format(elestr,('{}-{}'.format(fid,fid+v[1]-1) if len(nofileids)==v[1] else nofileids),refkey))
# 								test={}
# 								if fid in reffileids[refkey]:
# 									oset=set(reffileids[refkey][fid])
# 									for i in range(1,v[1]):
# 										if fid+i in reffileids[refkey]:
# 											tset=set(reffileids[refkey][fid+i])
# 											if tset!=oset:
# 												tset.symmetric_difference(oset)
# 												testk=tuple(sorted(list(tset.symmetric_difference(oset))))
# 												test[testk]=test.get(testk,[])
# 												test[testk].append(fid+i)
# 									if test:
# 										yield ValidationError('oxc;there is overlapp near these file ids {} object: {} refers to {}'.format(test,elestr,refkey))
# schemavalidators["oxcrefFileId"]=("oxcGL_checkFileId",oxcrefFileId)

def oxcArmorInv(validator, value, instance, schema):
	#alllists=globals()["schemacdata"]["lists"]["refall"]
	alllists=validator.schema[instancedatastring]["lists"]["refall"]
	
	if isinstance(instance,dict):
		if instance.get("storeItem",""):
			if not (
					 all([instance.get(value[3],"")+x[0]+str(x[1])+".SPK" in alllists[value[0]+":"+value[2]] for x in itertools.product(["M","F"],range(4))]) 
					or instance.get(value[3],"")+".SPK" in alllists[value[0]+":"+value[2]]
				 ):
				yield ValidationError('oxc;{} is referenced to /{} but not found there'.format(instance.get(value[3],""), value[0]))
		else:
			if instance.get(value[3],""):
				if not instance.get(value[3],"") in alllists[value[0]+":"+value[2]]:
					yield ValidationError('{} is referenced to /{} but not found there'.format(instance.get(value[3],""), value[0]))

schemavalidators["oxcArmorInv"]=("oxcGL_lookupArmorInv",oxcArmorInv)

def oxcMissingstrings(validator, value, instance, schema):
	for prop in value:				
		if not prop in instance: continue		
		canavoid=False
		if isinstance(value[prop],bool) and value[prop]==False: canavoid=True
		if isinstance(value[prop],list):
			for pelem in value[prop]:				
				if pelem[1]=="eq":
					if instance.get(pelem[0],pelem[2])==pelem[3]: canavoid=True
				if pelem[1]=="endswith":
					if instance.get(pelem[0],pelem[2]).endswith(pelem[3]): canavoid=True
				if pelem[1]=="hasprop":					
					if pelem[0] in  instance: canavoid=True
		if canavoid: continue
		if not instance[prop] in validator.schema[instancedatastring]["lists"]["alllang"]: 
			for l in validator.schema[instancedatastring]["params"].get("langs",[]):
				foundinlang=False
				if instance[prop] in validator.schema[instancedatastring]["lists"].get("langdata",{}).get(l,[]):
					foundinlang=True
				if not foundinlang:
					yield ValidationError('oxc;extraString for {} in {} is missing'.format(instance[prop], l))
schemavalidators["oxcMissingstrings"]=("oxcGL_language",oxcMissingstrings)

