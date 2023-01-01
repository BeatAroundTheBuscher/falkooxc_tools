from modules.config import staticpath, basepasswd, showtraceback
from werkzeug import secure_filename
import os
#import functools
import traceback
import copy
import re
import pickle
#import random
import yaml
from yaml.composer import Composer
from yaml.constructor import Constructor
try:
	from yaml import CSafeLoader as Loader
	from yaml import CSafeDumper as Dumper
except ImportError:
	from yaml import SafeLoader as Loader
	from yaml import SafeDumper as Dumper
import math

from modules.valcheck import checklist, adderror, guessline
from modules.config import linestring, instancedatastring, nomergestring, hasnotypestring, extraspritedelemiter, formatdictname

import json

import functools
#import datetime
#import itertools
#from jsonschema import validate, Draft4Validator
#from jsonschema.exceptions import ValidationError
#from jsonschema.validators import extend

import time #for testing
class Timer:    
	def __enter__(self):
		self.start = time.clock()
		return self

	def __exit__(self, *args):
		self.end = time.clock()
		self.interval = self.end - self.start
#checklist={} #contains all checkfunctions filed by decorator at compile time
import pprint
def newbase(data):
	with Timer() as t:
		p=staticpath+"static"+os.sep+"ruldata"+os.sep+secure_filename(data["name"])
		if data["pwd"]==basepasswd:
			if not os.path.isdir(p): os.mkdir(p)
			for opt in ["basefile","addfile","schemafile","langfile"]:
				with  open(p+os.sep+opt+".yaml","w") as fh:
					fh.write(data[opt].replace("\r","\n").replace("\n\n","\n").replace("\n\n","\n"))
				with  open(p+os.sep+opt+".pickle","wb") as fh:
					pickle.dump(yaml.load(data[opt], Loader=Loader),fh)
			cdata=makecdata(secure_filename(data["name"]))
			jsontree=makejsontree(cdata["recschema"])
			with  open(p+os.sep+"tree.json","w") as fh:
#				fh.write(pprint.pformat(json))			
				fh.write(json.dumps(jsontree))			
				
			with  open(p+os.sep+"cdata.pickle","wb") as fh:
				pickle.dump(cdata,fh)
			#with open(staticpath+"static"+os.sep+"ruldata"+os.sep+'out.yml', 'w') as outfile:
			#	outfile.write( yaml.dump(cdata["schema"], Dumper=Dumper) )	
	print('savebase took %.03f sec.' % t.interval)

def getcdata(dataname):
	p=staticpath+"static"+os.sep+"ruldata"+os.sep+secure_filename(dataname)
	r={}
	with open(p+os.sep+"cdata"+".pickle","rb") as fh:
		r=pickle.load(fh)
	return r

def getbase(dataname,cdata):
	p=staticpath+"static"+os.sep+"ruldata"+os.sep+secure_filename(dataname)
	cdata["base"]={}
	cdata["add"]={}
	cdata["lang"]={}
	cdata["schema"]={}
	with open(p+os.sep+"basefile"+".pickle","rb") as fh:
		cdata["base"]=pickle.load(fh)
	with open(p+os.sep+"addfile"+".pickle","rb") as fh:
		cdata["add"]=pickle.load(fh)
	with open(p+os.sep+"langfile"+".pickle","rb") as fh:
		cdata["lang"]=pickle.load(fh)
	with open(p+os.sep+"schemafile"+".pickle","rb") as fh:
		cdata["schema"]=pickle.load(fh)
#	with open(p+os.sep+"basefile"+".yaml","r") as fh:
#		cdata["base"]=yaml.load(fh.read(), Loader=Loader)
#	with open(p+os.sep+"addfile"+".yaml","r") as fh:
#		cdata["add"]=yaml.load(fh.read(), Loader=Loader)
#	with open(p+os.sep+"langfile"+".yaml","r") as fh:
#		cdata["lang"]=yaml.load(fh.read(), Loader=Loader)
#	with open(p+os.sep+"schemafile"+".yaml","r") as fh:
#		cdata["schema"]=yaml.load(fh.read(), Loader=Loader)

def addschemalines(schema):
	if isinstance(schema,dict):
		n={}		
		for k in schema:
			n[k]=addschemalines(schema[k])
		if (schema.get("type","notobject")=="object"):
			n["oxcT_properties"]=n.get("oxcT_properties",[])
			n["oxcT_properties"].append({linestring:{"type": "integer"}})					
			n["oxcT_properties"].append({formatdictname:{"type": "string"}})					
		return n
	elif isinstance(schema,list):
		return [addschemalines(x) for x in schema]	
	else:
		return schema

def dodel(bdat,mdat,cdata):
	for categ in cdata["dellist"]:
		mlist=mdat.get(categ,[])
		blist=bdat.get(categ,[])
		if not isinstance(mlist,list): continue
		found=[]
		for ei,elem in enumerate(mlist):
			if not isinstance(elem,dict): continue
			if "delete" in elem:
				if not  elem["delete"] in found: found.append(elem["delete"])
		delme=[]
		for ei,elem in enumerate(blist):
			if not isinstance(elem,dict): continue
			if cdata["unlist"][categ] in elem:
				if elem[cdata["unlist"][categ]] in found:
					delme.append(ei)
		for i in range(len(delme)-1,-1,-1):
			del (blist[delme[i]])

def removedel(dat,cdata):
	for categ in cdata["dellist"]:
		clist=dat.get(categ,[])
		if not isinstance(clist,list): continue
		found={}
		delme=[]
		for ei,elem in enumerate(clist):
			if not isinstance(elem,dict): continue
			if "delete" in elem:
				delme.append(ei)
		for i in range(len(delme)-1,-1,-1):
			del (clist[delme[i]])

def makelists(cdata):
	cdata["csprites"]=dict([ #put it in schema?
('HIT.PCK',(4,4,0, 'tactical1')),
('SMOKE.PCK',(56,56,0, 'tactical1')),
('GEO.CAT',(14,14,1,'')),
('INTERWIN.DAT',(11,11,0, 'geo')),
('FLOOROB.PCK',(73,73,0, 'tactical1')),
('HANDOB.PCK',(16,128,0, 'tactical1')),
('BIGOBS.PCK',(57,57,0,'tactical2')),
('Projectiles',(11,385,0, 'tactical1')),
('BATTLE.CAT',(55,55,1,'')),
('INTICON.PCK',(16,16,0, 'geo')),
('BASEBITS.PCK',(54,54,0, 'base')),
('TANKS.PCK',(128,128,0, 'tactical1')),
])
	cdata["lists"]={}
	cdata["lists"]["refbase"]={}
	cdata["lists"]["refall"]={}
	for categ in cdata["unlist"]:
		key=cdata["unlist"][categ]
		cdata["lists"]["refbase"][categ+":"+key]=[]
		cdata["lists"]["refall"][categ+":"+key]=[]
		if categ=="research":					
			cdata["lists"]["refall"]["unlockableresearch"]=[]		
		if categ in cdata["base"]:			
			for elem in cdata["base"][categ]:
				if key in elem:
					cdata["lists"]["refbase"][categ+":"+key].append(elem[key])
					cdata["lists"]["refall"][categ+":"+key].append(elem[key])
				if categ=="research":					
					#print (categ,elem)
					for x in elem.get("getOneFree",[]):
						cdata["lists"]["refall"]["unlockableresearch"].append(x)
					if "lookup" in elem:
						cdata["lists"]["refall"]["unlockableresearch"].append(elem["lookup"])
		if categ in cdata["data"]:
			for elem in cdata["data"][categ]:
				if key in elem:				
					cdata["lists"]["refall"][categ+":"+key].append(elem[key])
				if categ=="research":					
					for x in elem.get("getOneFree",[]):
						cdata["lists"]["refall"]["unlockableresearch"].append(x)
					if "lookup" in elem:
						cdata["lists"]["refall"]["unlockableresearch"].append(elem["lookup"])
	cdata["lists"]["alllang"]=[x for x in cdata["lang"]["en-US"]]
	cdata["lists"]["langdata"]={}

	for x in cdata["data"].get("extraStrings",[]):		
		if isinstance(x,dict) and "type" in x:
			cdata["lists"]["langdata"][x["type"]]=cdata["lists"]["langdata"].get(x["type"],[])
			for xs in x.get("strings",[]):
				cdata["lists"]["langdata"][x["type"]].append(xs)
	

	# cdata["lists"]["reffileids"]={}					
	# cdata["filecategories"]=["extraSprites","extraSounds"]
	# for fk in cdata["filecategories"]:
	# 	for elem in cdata["data"].get(fk,{}):
	# 		tmp=cdata["lists"]["reffileids"].get((fk,elem.get("type","UNKNOWN")),{})
	# 		for x in elem.get("files",{}):
	# 			i=0
	# 			for cx in range(elem.get("width",320)//elem.get("subX",320)):
	# 				for cy in range(elem.get("height",200)//elem.get("subY",200)):
	# 					if not isinstance(x,int): continue						
	# 					tmp[x+i]=[]
	# 					i+=1
	# 		cdata["lists"]["reffileids"][(fk,elem.get("type","UNKNOWN"))]=tmp			
	#print(cdata["lists"]["reffileids"])			
	#print (cdata["lists"]["refbase"]["extraSprites:type"])

def fixschema(cdat,d1,d2,p1=[],p2=[],k1=[],k2=[]):
	
	if isinstance(d1,list):
		for i,k in enumerate(d1):
			fixschema(cdat,d1[i],d2[i],p1+[d1],p2+[d2],k1+[i],k2+[i])		
	if isinstance(d1,dict):
		for k in d1.keys():
			fixschema(cdat,d1[k],d2[k],p1+[d1],p2+[d2],k1+[k],k2+[k])		
		if "oxcT_properties" in d1:
#			d1["properties"]={}
			d2["properties"]={}
			for i,x in enumerate(d1["oxcT_properties"]):
				klist=list(x.keys())
				d2["properties"][klist[0]]=copy.deepcopy(d2["oxcT_properties"][i][klist[0]])
				d2["properties"][klist[0]]["oxcF_poscounter"]=i				
#				d1["properties"][klist[0]]=copy.deepcopy(d1["oxcT_properties"][i][klist[0]])
#				d1["properties"][klist[0]]["oxcF_poscounter"]=i
			del (d2["oxcT_properties"])
			#del (d1["oxcT_properties"])
		if d1.get("oxcML_mtype",{}).get("action","nolist") == "elem_add_or_rec":
			if "oxcV_key" in d1 and not "key" in d1.get("oxcML_mtype",{}):
				
				d2["oxcML_mtype"]=copy.deepcopy(d2.get("oxcML_mtype",{}))
				d2["oxcML_mtype"]["key"]=d2["oxcV_key"]
		if "oxcGL_refFileId" in d1:						
			#p1[-3]["oxcML_mtype"]["modindexproperties"]=p1[-3]["oxcML_mtype"].get("modindexproperties",{})
			p2[-3]["oxcML_mtype"]["modindexproperties"]=p2[-3]["oxcML_mtype"].get("modindexproperties",{})
			#p1[-3]["oxcML_mtype"]["modindexproperties"][k1[-1]]=d1.get("oxcML_fileaddmax",0)
			p2[-3]["oxcML_mtype"]["modindexproperties"][k2[-1]]=dict(fmult=d2.get("oxcGL_refFileId",[[1,1,1,1]])[0][3],fmax=d2.get("oxcML_fileaddmax",0))
		if d1.get("oxcGL_lookupKey",False) and len (p1)>2:
			oxc_val=p2[-2].get("oxcGL_checkKey",[])
			oxc_val.append([k2[-1],d2["oxcGL_lookupKey"]])
			#oxc_val1=p1[-2].get("oxcGL_checkKey",[])
			#oxc_val1.append([k1[-1],d1["oxcGL_lookupKey"]])
			p2[-2]["oxcGL_checkKey"]=oxc_val
			#p1[-2]["oxcGL_checkKey"]=oxc_val1
		if "oxclang" in d1 and len (p1)>3 and isinstance(p1[-3],dict):	# 
			#print(99)
			#print(k1,d1)
			oxc_val=p2[-3].get("oxcGL_language",{})
			#oxc_val=p2[-2].get("oxcGL_checkFileId",[])
			oxc_val[k1[-1]]=copy.deepcopy(d1["oxclang"])
			p2[-3]["oxcGL_language"]=oxc_val
		if d1.get("oxcGL_refFileId",False) and len (p1)>3 and isinstance(p1[-3],dict):	# 
			oxc_val=p2[-3].get("oxcGL_checkFileId",[])
			#oxc_val=p2[-2].get("oxcGL_checkFileId",[])
			oxc_val.append([k1[-1],k1[-2],k1[-4],copy.deepcopy(d1["oxcGL_refFileId"]),k1])
			p2[-3]["oxcGL_checkFileId"]=oxc_val
		if d1.get("oxcT_makenomerge",False) and "$ref" in d1:			
			cdat["adddefinitions"].append(d2["$ref"].split("/")[-1])			
			d2["$ref"]+=nomergestring
			d2["$ref"]=copy.deepcopy(d2["$ref"])
		if d1.get("$ref","") and d1.get("$ref","").startswith("#/definitions/oxc"):
			refdef=p1[0]["definitions"][d1["$ref"].split("/")[2]]
			for k in refdef:
				d2[k]=copy.deepcopy(refdef[k])
				if "$ref" in d2:
					del (d2["$ref"])

def makerecschema(d,cdat):	
	if isinstance(d,list):
		for x in range(len(d)):
			makerecschema(d[x],cdat)		
	elif isinstance(d,dict):
		klist=list(d.keys())
		if "$ref" in klist:
			for x in cdat["recschema"]["definitions"][d["$ref"].split("/")[-1]]:
				d[x]=copy.deepcopy(cdat["recschema"]["definitions"][d["$ref"].split("/")[-1]][x])
			del(d["$ref"])
		klist=list(d.keys())
		for x in klist:
			makerecschema(d[x],cdat)

def lst2sortpath(lst):
	kt=";"
	for x in lst:
		#if x[0]=="/": kt+="b;"
		if x[0]=="*": kt+=";"
		else: kt+=x[0]+";" #print(lst)				
	return kt

def makerecschemaoptions(d,cdat,p=[],k=[],b=[]):	
	if isinstance(d,list):
		for x in range(len(d)):
			makerecschemaoptions(d[x],cdat,p+[d[x]],k+[x],b=b)		
	elif isinstance(d,dict):
		klist=list(d.keys())
		
		#addx=[]
		#if "oxcML_mtype" in d and d.get("type","notarrayobject") =="array":			
		#	addx=[0]
		#if "oxcML_mtype" in d and d.get("type","notarrayobject") =="object":			
		#	addx=["obj"]
		if d.get("oxcF_expandnumlist",False):
			cdat["numlistexception"].append(lst2sortpath(b)+k[-1]+";")
		if k[-1] != linestring:
			if "oxcF_poscounter" in d:
				kt=lst2sortpath(b)			
				cdat["orderyaml"][kt]=cdat["orderyaml"].get(kt,{})
				cdat["orderyaml"][kt][k[-1]]=d["oxcF_poscounter"]
		if d.get("type","notarrayorobject") in ["array" ]:
			b=copy.deepcopy(b)+[(k[-1],"L" if "oxcML_mtype" in d else -1)]
#			if len(p)>2 and "oxcF_poscounter" in [x for x in p[-3]]:
		if d.get("type","notarrayorobject") in ["object"]:
			if k[-1] in ["items","additionalProperties"]:
				b=copy.deepcopy(b)+[("*","D" if "oxcML_mtype" in d else -1)]
			else:
				b=copy.deepcopy(b)+[(k[-1],"D" if "oxcML_mtype" in d else -1)]
		if "oxcML_mtype" in d and d.get("type","notarrayobject") in ["array" ,"object"]:			
			#if p[-1].get("type","notarrayobject")=="array":
			#	print("array: ",k,d["oxcML_mtype"])
			if all([x[1]in["L","D"] for x in b ]):
				cdat["mergelist"].append((b,d.get("oxcML_mtype",{})))
				#print ("------------------")
				#print (b,d.get("oxcML_mtype",{}))
				#print (all([x[1]in[{},[]] for x in b ]))
			#print (k,d["oxcML_mtype"])
			#print (p[-1].get("type","notarrayobject"))
			#print ([(x,p[x].get("type","notarrayobject"),k[x]) for x in range(len(k)) if isinstance(p[x],dict) and p[x].get("type","notarrayobject") in ["array" ,"object"]])
		for x in klist:
			makerecschemaoptions(d[x],cdat,p+[d[x]],k+[x],b=b)


def mergebase(cdat,bdat,adat,k=[],mlist=[],addmod=None,lasttype=""):
	#laasttype=ugly hack
	ret=copy.deepcopy(bdat)
	newml=(k[-1],("D" if isinstance(bdat,dict) else ("L" if isinstance(bdat,list) else -1 )))
	testml=mlist+[newml]
	mlentry=None
	for mle in cdat["mergelist"]:
		if len(mlist)+1==len(mle[0]):
			
			if mle[0]==mlist+[newml] or mle[0]==mlist+[("*",newml[1])]:
				mlentry=mle
	op={"action":"replace"}
	if not mlentry is None:
		mlist=mlentry[0]
		op=mlentry[1]
	#print (mlist,op)
	
	if op.get("action","replace")=="prop_add_or_rec":
		for x in adat:			
			newk=x
			if not x in bdat:
				if "inc_key" in op and isinstance(x,int): 
					newk=x+cdat["modindex"]					
				if x in op.get("modindexproperties",{}) and adat[x] > op["modindexproperties"][x]["fmax"]:
					ret[newk]=int(math.ceil(cdat["modindex"]/op["modindexproperties"][x]["fmult"]))+copy.deepcopy(adat[x])
				else:
					ret[newk]=copy.deepcopy(adat[x])
			else:				
				if x in op.get("modindexproperties",{}) and adat[x] > op["modindexproperties"][x]["fmax"]:
					ret[newk]=mergebase(cdat,bdat[x],adat[x],k=k+[x],mlist=mlist,addmod=int(math.ceil(cdat["modindex"]/op["modindexproperties"][x]["fmult"])),lasttype=(bdat["type"] if isinstance(bdat,dict) and "type" in bdat else lasttype))
				else:
					ret[newk]=mergebase(cdat,bdat[x],adat[x],k=k+[x],mlist=mlist,lasttype=(bdat["type"] if isinstance(bdat,dict) and "type" in bdat else lasttype))
	if op.get("action","replace")=="elem_add_or_rec":
		for ai,ax in enumerate(adat):
			key=op.get("key",hasnotypestring)
			if not key in ax: continue
			fi=-1
			for bi,bx in enumerate(bdat):
				if not key in bx: continue
				if ax[key]==bx[key]:
					fi=bi
			if fi>=0:
				ret[fi]=mergebase(cdat,bdat[fi],adat[ai],k=k+[ai],mlist=mlist,lasttype=(bdat["type"] if isinstance(bdat,dict) and "type" in bdat else lasttype))
			else:
				ret.append(copy.deepcopy(adat[ai]))
	if op.get("action","replace")=="elem_add":
		for ai,ax in enumerate(adat):			
			ret.append(copy.deepcopy(adat[ai]))		
	if op.get("action","replace")=="replace":
		ret=copy.deepcopy(adat)
		if not addmod is None:
			ret+=addmod
	return ret
def extraspritemerge(bdat,adat,cdat):
	if "extraSprites" in bdat or "extraSprites" in adat:
		tmp=[]
		tmpk=[]
		tmpd={}
		lst=[(0,bdat.get("extraSprites",[])),(cdat["modindex"]	,adat.get("extraSprites",[]))]
		for l in lst:
			modindex=l[0]
			for x in l[1]:
				skey=[]
				for k in sorted(cdat["schema"]["definitions"]["extraSprite"]["properties"]):
					if k in ["files",linestring, formatdictname]: continue
					if k in x:
						skey.append((k,x[k]))
				skey=tuple(skey)				
				if not skey in tmpd:
					tmpd[skey]=len(tmp)
					tmpk.append(skey)
					tmp.append(dict(files={}))
				for fid in x.get("files",{}):
					if fid in ["files",linestring, formatdictname]: continue					
					if ("type","Projectiles") in skey:#ARGH! 
						newk=fid+35*int(math.ceil(modindex/35))
					elif ("type","TEXTURES.DAT") in skey:
						newk=fid
					else:
						newk=fid+modindex
					tmp[tmpd[skey]]["files"][newk]=x["files"][fid]
		
		for xi in range(len(tmp)):
			for sk in tmpk[xi]:
				tmp[xi][sk[0]]=sk[1]
		bdat["extraSprites"]=tmp

class NumList(list):
	pass

def numlist_rep(self, data):
#	return self.represent_sequence( 'tag:python/object/new:modules.validate.NumList', data, flow_style=True )
	return self.represent_sequence( 'tag:yaml.org,2002:seq', data, flow_style=True )

def make_represent_dict(neworder={}):
	def represent_dict(self, data):
	#	order={';b;ufopaedia;;': ['id', 'type_id', 'section', 'image_id', 'rect_stats', 'rect_text', 'text', 'requires', 'weapon', 'text_width'], ';b;research;;': ['name', 'cost', 'points', 'dependencies', 'needItem', 'unlocks', 'requires', 'lookup', 'getOneFree'], ';b;soldiers;;': ['type', 'minStats', 'maxStats', 'statCaps', 'armor', 'standHeight', 'kneelHeight', 'genderRatio'], ';b;soldiers;;maxStats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienMissions;;': ['type', 'points', 'raceWeights', 'waves'], ';b;ufoTrajectories;;': ['id', 'groundTimer', 'waypoints'], ';b;regions;;': ['type', 'cost', 'areas', 'cities', 'regionWeight', 'missionWeights', 'missionZones', 'missionRegion'], ';b;ufos;;battlescapeTerrainData;mapBlocks;;': ['name', 'width', 'length'], ';b;manufacture;;': ['name', 'category', 'requires', 'space', 'time', 'cost', 'requiredItems'], ';b;ufopaedia;;rect_stats;': ['x', 'y', 'width', 'height'], ';b;startingBase;crafts;;weapons;;': ['type', 'ammo'], ';b;ufos;;': ['type', 'size', 'sprite', 'damageMax', 'speedMax', 'accel', 'power', 'range', 'score', 'reload', 'breakOffTime', 'battlescapeTerrainData'], ';b;ufopaedia;;rect_text;': ['x', 'y', 'width', 'height'], ';b;MCDPatches;;data;;': ['MCDIndex', 'bigWall', 'LOFTS', 'TUSlide', 'terrainHeight', 'TUWalk', 'TUFly', 'deathTile', 'armor', 'HEBlock', 'flammability', 'fuel', 'noFloor'], ';b;terrains;;mapBlocks;;': ['name', 'width', 'length', 'type', 'subType', 'maxCount', 'frequency'], ';b;extraStrings;;': ['type', 'strings'], ';b;crafts;;battlescapeTerrainData;mapBlocks;;': ['name', 'width', 'length'], ';b;armors;;': ['type', 'spriteSheet', 'spriteInv', 'storeItem', 'corpseBattle', 'frontArmor', 'sideArmor', 'rearArmor', 'underArmor', 'damageModifier', 'loftempsSet', 'movementType', 'drawingRoutine', 'corpseGeo', 'size'], ';b;crafts;;battlescapeTerrainData;': ['name', 'mapDataSets', 'mapBlocks'], ';b;startingBase;facilities;;': ['type', 'x', 'y'], ';b;regions;;cities;;': ['name', 'lon', 'lat'], ';b;startingBase;crafts;;': ['type', 'id', 'fuel', 'damage', 'items', 'status', 'weapons'], ';b;startingBase;': ['facilities', 'randomSoldiers', 'crafts', 'items', 'scientists', 'engineers'], ';b;units;;': ['type', 'race', 'rank', 'armor', 'stats', 'standHeight', 'kneelHeight', 'value', 'deathSound', 'moveSound', 'energyRecovery', 'floatHeight', 'intelligence', 'aggression', 'specab', 'livingWeapon', 'aggroSound', 'spawnUnit'], ';b;crafts;;': ['type', 'sprite', 'fuelMax', 'damageMax', 'speedMax', 'accel', 'soldiers', 'vehicles', 'costBuy', 'costRent', 'refuelRate', 'transferTime', 'score', 'battlescapeTerrainData', 'weapons', 'requires', 'refuelItem', 'deployment', 'spacecraft'], ';b;alienRaces;;': ['id', 'members', 'retaliation'], ';b;invs;;': ['id', 'x', 'y', 'type', 'costs', 'slots'], ';b;items;;': ['type', 'name', 'bigSprite', 'floorSprite', 'handSprite', 'bulletSprite', 'size', 'costBuy', 'costSell', 'transferTime', 'clipSize', 'weight', 'fireSound', 'compatibleAmmo', 'accuracySnap', 'accuracyAimed', 'tuSnap', 'tuAimed', 'battleType', 'fixedWeapon', 'invWidth', 'invHeight', 'turretType', 'hitSound', 'hitAnimation', 'power', 'damageType', 'waypoint', 'blastRadius', 'armor', 'accuracyAuto', 'tuAuto', 'twoHanded', 'tuUse', 'painKiller', 'heal', 'stimulant', 'woundRecovery', 'healthRecovery', 'stunRecovery', 'energyRecovery', 'flatRate', 'requires', 'meleeSound', 'accuracyMelee', 'tuMelee', 'skillApplied', 'recover', 'recoveryPoints', 'strengthApplied', 'zombieUnit', 'arcingShot', 'liveAlien'], ';b;craftWeapons;;': ['type', 'sprite', 'sound', 'damage', 'range', 'accuracy', 'reloadCautious', 'reloadStandard', 'reloadAggressive', 'ammoMax', 'launcher', 'clip', 'projectileType', 'projectileSpeed', 'rearmRate'], ';b;startingTime;': ['second', 'minute', 'hour', 'weekday', 'day', 'month', 'year'], ';b;ufos;;battlescapeTerrainData;': ['name', 'mapDataSets', 'mapBlocks'], ';b;units;;stats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;extraSprites;;': ['type', 'files', 'width', 'height', 'subX', 'subY', 'singleImage'], ';b;facilities;;': ['type', 'spriteShape', 'spriteFacility', 'lift', 'buildCost', 'buildTime', 'monthlyCost', 'mapName', 'personnel', 'labs', 'workshops', 'radarRange', 'radarChance', 'defense', 'hitRatio', 'fireSound', 'hitSound', 'storage', 'aliens', 'requires', 'grav', 'mind', 'psiLabs', 'hyper', 'size', 'crafts'], ';b;MCDPatches;;': ['type', 'data'], ';b;extraSounds;;': ['type', 'files'], ';b;alienDeployments;;data;;': ['alienRank', 'lowQty', 'highQty', 'dQty', 'percentageOutsideUfo', 'itemSets'], ';b;terrains;;': ['name', 'mapDataSets', 'textures', 'largeBlockLimit', 'hemisphere', 'civilianTypes', 'roadTypeOdds', 'mapBlocks'], ';b;soldiers;;minStats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienMissions;;waves;;': ['ufo', 'count', 'trajectory', 'timer'], ';b;': ['countries', 'regions', 'facilities', 'crafts', 'craftWeapons', 'items', 'ufos', 'invs', 'terrains', 'armors', 'soldiers', 'units', 'alienRaces', 'alienDeployments', 'research', 'manufacture', 'ufopaedia', 'startingBase', 'startingTime', 'costSoldier', 'costEngineer', 'costScientist', 'timePersonnel', 'initialFunding', 'ufoTrajectories', 'alienMissions', 'alienItemLevels', 'MCDPatches', 'extraSprites', 'extraSounds', 'extraStrings'], ';b;countries;;': ['type', 'fundingBase', 'fundingCap', 'labelLon', 'labelLat', 'areas'], ';b;soldiers;;statCaps;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienDeployments;;': ['type', 'data', 'width', 'length', 'height', 'civilians', 'terrains', 'shade', 'nextStage']}
		order=neworder
		if formatdictname in data and data[formatdictname] in order:
			newitems=[]
			otheritems=[x for x in data]
			for o in order[data[formatdictname]]:
				if o in data:
					if not o in [linestring,formatdictname]:
						newitems.append((o,data[o]))
					otheritems.remove(o)
			otheritems=sorted(otheritems, key=lambda x: "%020d"%x if isinstance(x,int) else x)
			for o in otheritems:
	#			if o not in ["MCPdata","PREPoutput"]:				
				if not o in [linestring,formatdictname]:
					newitems.append((o,data[o]))
		else:
	#		items = [x for x in data.items()if x[0] not in ["MCPdata","PREPoutput"]]
			items = [x for x in data.items()if x[0] not in [formatdictname,linestring]]
			newitems=sorted(items,key=lambda x:"%020d"%x[0] if isinstance(x[0],int) else x[0])
		return self.represent_mapping('tag:yaml.org,2002:map', newitems)
	return represent_dict

def prepareoutput(mod,cdat):
	#if "MCPdata" in mod: del(mod["MCPdata"])
	#{';b;ufopaedia;;': ['id', 'type_id', 'section', 'image_id', 'rect_stats', 'rect_text', 'text', 'requires', 'weapon', 'text_width'], ';b;research;;': ['name', 'cost', 'points', 'dependencies', 'needItem', 'unlocks', 'requires', 'lookup', 'getOneFree'], ';b;soldiers;;': ['type', 'minStats', 'maxStats', 'statCaps', 'armor', 'standHeight', 'kneelHeight', 'genderRatio'], ';b;soldiers;;maxStats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienMissions;;': ['type', 'points', 'raceWeights', 'waves'], ';b;ufoTrajectories;;': ['id', 'groundTimer', 'waypoints'], ';b;regions;;': ['type', 'cost', 'areas', 'cities', 'regionWeight', 'missionWeights', 'missionZones', 'missionRegion'], ';b;ufos;;battlescapeTerrainData;mapBlocks;;': ['name', 'width', 'length'], ';b;manufacture;;': ['name', 'category', 'requires', 'space', 'time', 'cost', 'requiredItems'], ';b;ufopaedia;;rect_stats;': ['x', 'y', 'width', 'height'], ';b;startingBase;crafts;;weapons;;': ['type', 'ammo'], ';b;ufos;;': ['type', 'size', 'sprite', 'damageMax', 'speedMax', 'accel', 'power', 'range', 'score', 'reload', 'breakOffTime', 'battlescapeTerrainData'], ';b;ufopaedia;;rect_text;': ['x', 'y', 'width', 'height'], ';b;MCDPatches;;data;;': ['MCDIndex', 'bigWall', 'LOFTS', 'TUSlide', 'terrainHeight', 'TUWalk', 'TUFly', 'deathTile', 'armor', 'HEBlock', 'flammability', 'fuel', 'noFloor'], ';b;terrains;;mapBlocks;;': ['name', 'width', 'length', 'type', 'subType', 'maxCount', 'frequency'], ';b;extraStrings;;': ['type', 'strings'], ';b;crafts;;battlescapeTerrainData;mapBlocks;;': ['name', 'width', 'length'], ';b;armors;;': ['type', 'spriteSheet', 'spriteInv', 'storeItem', 'corpseBattle', 'frontArmor', 'sideArmor', 'rearArmor', 'underArmor', 'damageModifier', 'loftempsSet', 'movementType', 'drawingRoutine', 'corpseGeo', 'size'], ';b;crafts;;battlescapeTerrainData;': ['name', 'mapDataSets', 'mapBlocks'], ';b;startingBase;facilities;;': ['type', 'x', 'y'], ';b;regions;;cities;;': ['name', 'lon', 'lat'], ';b;startingBase;crafts;;': ['type', 'id', 'fuel', 'damage', 'items', 'status', 'weapons'], ';b;startingBase;': ['facilities', 'randomSoldiers', 'crafts', 'items', 'scientists', 'engineers'], ';b;units;;': ['type', 'race', 'rank', 'armor', 'stats', 'standHeight', 'kneelHeight', 'value', 'deathSound', 'moveSound', 'energyRecovery', 'floatHeight', 'intelligence', 'aggression', 'specab', 'livingWeapon', 'aggroSound', 'spawnUnit'], ';b;crafts;;': ['type', 'sprite', 'fuelMax', 'damageMax', 'speedMax', 'accel', 'soldiers', 'vehicles', 'costBuy', 'costRent', 'refuelRate', 'transferTime', 'score', 'battlescapeTerrainData', 'weapons', 'requires', 'refuelItem', 'deployment', 'spacecraft'], ';b;alienRaces;;': ['id', 'members', 'retaliation'], ';b;invs;;': ['id', 'x', 'y', 'type', 'costs', 'slots'], ';b;items;;': ['type', 'name', 'bigSprite', 'floorSprite', 'handSprite', 'bulletSprite', 'size', 'costBuy', 'costSell', 'transferTime', 'clipSize', 'weight', 'fireSound', 'compatibleAmmo', 'accuracySnap', 'accuracyAimed', 'tuSnap', 'tuAimed', 'battleType', 'fixedWeapon', 'invWidth', 'invHeight', 'turretType', 'hitSound', 'hitAnimation', 'power', 'damageType', 'waypoint', 'blastRadius', 'armor', 'accuracyAuto', 'tuAuto', 'twoHanded', 'tuUse', 'painKiller', 'heal', 'stimulant', 'woundRecovery', 'healthRecovery', 'stunRecovery', 'energyRecovery', 'flatRate', 'requires', 'meleeSound', 'accuracyMelee', 'tuMelee', 'skillApplied', 'recover', 'recoveryPoints', 'strengthApplied', 'zombieUnit', 'arcingShot', 'liveAlien'], ';b;craftWeapons;;': ['type', 'sprite', 'sound', 'damage', 'range', 'accuracy', 'reloadCautious', 'reloadStandard', 'reloadAggressive', 'ammoMax', 'launcher', 'clip', 'projectileType', 'projectileSpeed', 'rearmRate'], ';b;startingTime;': ['second', 'minute', 'hour', 'weekday', 'day', 'month', 'year'], ';b;ufos;;battlescapeTerrainData;': ['name', 'mapDataSets', 'mapBlocks'], ';b;units;;stats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;extraSprites;;': ['type', 'files', 'width', 'height', 'subX', 'subY', 'singleImage'], ';b;facilities;;': ['type', 'spriteShape', 'spriteFacility', 'lift', 'buildCost', 'buildTime', 'monthlyCost', 'mapName', 'personnel', 'labs', 'workshops', 'radarRange', 'radarChance', 'defense', 'hitRatio', 'fireSound', 'hitSound', 'storage', 'aliens', 'requires', 'grav', 'mind', 'psiLabs', 'hyper', 'size', 'crafts'], ';b;MCDPatches;;': ['type', 'data'], ';b;extraSounds;;': ['type', 'files'], ';b;alienDeployments;;data;;': ['alienRank', 'lowQty', 'highQty', 'dQty', 'percentageOutsideUfo', 'itemSets'], ';b;terrains;;': ['name', 'mapDataSets', 'textures', 'largeBlockLimit', 'hemisphere', 'civilianTypes', 'roadTypeOdds', 'mapBlocks'], ';b;soldiers;;minStats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienMissions;;waves;;': ['ufo', 'count', 'trajectory', 'timer'], ';b;': ['countries', 'regions', 'facilities', 'crafts', 'craftWeapons', 'items', 'ufos', 'invs', 'terrains', 'armors', 'soldiers', 'units', 'alienRaces', 'alienDeployments', 'research', 'manufacture', 'ufopaedia', 'startingBase', 'startingTime', 'costSoldier', 'costEngineer', 'costScientist', 'timePersonnel', 'initialFunding', 'ufoTrajectories', 'alienMissions', 'alienItemLevels', 'MCDPatches', 'extraSprites', 'extraSounds', 'extraStrings'], ';b;countries;;': ['type', 'fundingBase', 'fundingCap', 'labelLon', 'labelLat', 'areas'], ';b;soldiers;;statCaps;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienDeployments;;': ['type', 'data', 'width', 'length', 'height', 'civilians', 'terrains', 'shade', 'nextStage']}
	fDumper=yaml.SafeDumper
	fDumper.add_representer(dict, make_represent_dict(cdat["orderyaml"]))
	fDumper.add_representer(NumList, numlist_rep)
	t=yaml.dump(recprepareoutput(mod,";/;",cdat),Dumper=fDumper,default_flow_style=False,allow_unicode=True,width=100000)
	
	t=re.sub("(\ *)- - (.*)","\\1-\n\\1  - \\2",t)
	ls=t.split("\n")
	nl=[]
	o={}

	for lastpos in range (180,-1,-2):#moves list accordingly
		for li,l in enumerate(ls):
			if len(l)>lastpos:
				if l[lastpos]=="-":
					t=0
					while len(ls[li+t])>lastpos and ls[li+t][lastpos]in [" ","-"] and ls[li+t][0:max(0,lastpos-1)].strip()=="":
						ls[li+t]="  "+ls[li+t]
						t+=1
	for li,l in enumerate(ls): #fix itemSets missionZones
		if l.strip()=="-":
			lastpos=len(l)
			t=1
			while len(ls[li+t])>=lastpos and ls[li+t][0:lastpos].strip()=="" :
				ls[li+t]=ls[li+t][2:]
				t+=1
	return"\n".join(ls)

def recprepareoutput(elem,path,cdat):
	if isinstance(elem,dict):
		nonintfound=False
		for prop in elem:
			if not isinstance(prop,int): #elem[prop] for int does not work for some strrange reason
				elem[prop]=recprepareoutput(elem[prop],path+prop+";",cdat)
				nonintfound=True
		if nonintfound:elem[formatdictname]=path
	if isinstance(elem,list):
		testnrlist=True
		for l in elem:
			if not (isinstance(l,int) or isinstance(l,float)):testnrlist=False
		if testnrlist and not path in cdat["numlistexception"]: #TODO make exceptoin in schema
			tmp=NumList()
			for x in elem:
				tmp.append(x)
			elem=tmp
		for li,l in enumerate(elem):
			elem[li]=recprepareoutput(elem[li],path+";",cdat)
	return elem

def makecdata(dataname):
	cdata=dict(modindex=0,numlistexception=[],orderyaml={})
	getbase(dataname,cdata)
#	cdata["csprites"]=csprites
	cdata["schema"]=addschemalines(cdata["schema"])
	cdata["unlist"]={}
	cdata["dellist"]=[]
	for x in cdata["schema"]["oxcT_properties"]:
		for y in x:
			if "oxcV_key" in x[y]:
				cdata["unlist"][y]=x[y]["oxcV_key"]
				if x[y].get("oxcV_deletable",False):
					cdata["dellist"].append(y)
	
	cdata["adddefinitions"]=[]
	cdata["tmpcopy"]=copy.deepcopy(cdata["schema"])
	fixschema(cdata,cdata["tmpcopy"],cdata["schema"])
#	fixschema(cdata,cdata["schema"])
	for x in list(set(cdata["adddefinitions"])):
		cdata["schema"]["definitions"][x+nomergestring]=copy.deepcopy(cdata["schema"]["definitions"][x])
		del(cdata["schema"]["definitions"][x+nomergestring]["oxcML_mtype"])
	cdata["recschema"]=copy.deepcopy(cdata["schema"])
	makerecschema(cdata["recschema"],cdata)	
	del(cdata["recschema"]["definitions"])
	cdata["mergelist"]=[]
	#cdata["modindex"]=0#35*35*100000
	makerecschemaoptions(cdata["recschema"],cdata,p=[cdata["recschema"]],k=["/"])
	for orderkey in cdata["orderyaml"]:
		cdata["orderyaml"][orderkey]=[y[0] for y in sorted(cdata["orderyaml"][orderkey].items(),key=lambda x:x[1])]	
	#with open(staticpath+"static"+os.sep+"ruldata"+os.sep+'out.yml', 'w') as outfile:
	#	for p in cdata["orderyaml"]:									
	#		outfile.write( p+repr(cdata["orderyaml"][p])+"\n")			

	#print(cdata["mergelist"])
	
	#for x in cdata["mergelist"]:
	#	print(x)
	
	dodel(cdata["base"],cdata["add"],cdata)	
	removedel(cdata["add"],cdata)
	#makedeldict(cdata["base"],cdata)
	cdata["mbase"]=copy.deepcopy(cdata["base"])
	cdata["mbase"]=mergebase(cdata,cdata["base"],cdata["add"],k=["/"])
	extraspritemerge(cdata["mbase"],cdata["add"],cdata)
	cdata["modindex"]=1000
	cdata["base"]=cdata["mbase"]
	return cdata

def checks(allops,dataname,datastr,zip=None):
	edict={"_all_":[]}
	for elem in allops:
		edict[elem["name"]]=[]
	cdata=getcdata(dataname)
	#cdata=makecdata(dataname)
	cdata["modindex"]=1000

#	with open(staticpath+"static"+os.sep+"ruldata"+os.sep+'out.yml', 'w') as outfile:
#		outfile.write( yaml.dump(cdata["base"], Dumper=Dumper) )		
#		outfile.write( yaml.dump(cdata["mbase"], Dumper=Dumper) )		
#		outfile.write( yaml.dump(cdata["schema"], Dumper=Dumper) )
#		outfile.write( yaml.dump(cdata["deldict"], Dumper=Dumper) )
	cdata["datastr"]=datastr #.replace("\r","\n").replace("\n\n","\n").replace("\n\n","\n")	
	for elem in allops:
		ekey=elem["name"]
		for op in elem.get("ops",[]):
			if op.get("execpos","standard")=="puretext":
				if op.get("func","nofuncdeclared") in checklist:
					checklist[op["func"]](edict[ekey],cdata,op.get("params",{}))
				else:
					adderror(edict[ekey],"config","funcmissing",op.get("func","nofuncdeclared"),op.get("execpos","standard")) 				
	try:
		cdata["yamlloaderror"]=None
		loader = yaml.SafeLoader(datastr)
		def compose_node(parent, index):
			# the line number where the previous token has ended (plus empty lines)
			line = loader.line
			node = Composer.compose_node(loader, parent, index)
			node.__line__ = line + 1
			return node
		def construct_mapping(node, deep=False):
			mapping = Constructor.construct_mapping(loader, node, deep=deep)
			mapping[linestring] = node.__line__
			return mapping
		loader.compose_node = compose_node
		loader.construct_mapping = construct_mapping
		cdata["data"] = loader.get_single_data()		

	except yaml.YAMLError as exc:
		cdata["yamlloaderror"]=exc
		cdata["data"]={}
	except Exception as e:
		adderror(edict["_all_"],"checksfailed","yamlload", traceback.format_exc() if showtraceback else repr(e),"in code") 
		cdata["data"]={}
	#with open(staticpath+"static"+os.sep+"ruldata"+os.sep+'out.yml', 'w') as outfile:		
	#	outfile.write( yaml.dump(cdata["data"], Dumper=Dumper) )
	#	outfile.write( prepareoutput(cdata["data"],cdata) )
	
	for elem in allops:
		ekey=elem["name"]
		for op in elem.get("ops",[]):
			if op.get("execpos","standard")=="predelete":
				if op.get("func","nofuncdeclared") in checklist:
					checklist[op["func"]](edict[ekey],cdata,op.get("params",{}))
				else:
					adderror(edict[ekey],"config","funcmissing",op.get("func","nofuncdeclared"),op.get("execpos","standard")) 				

	try:
		dodel(cdata["base"],cdata["data"],cdata)
		removedel(cdata["data"],cdata)
	except Exception as e:
		adderror(edict["_all_"],"checksfailed","datahandledelete", traceback.format_exc() if showtraceback else repr(e),"in code") 
	cdata["alldata"]=copy.deepcopy(cdata["base"])		
	try:
		
		
		cdata["alldata"]=mergebase(cdata,cdata["alldata"],cdata["data"],k=["/"])
		extraspritemerge(cdata["alldata"],cdata["data"],cdata)
	except Exception as e:
		adderror(edict["_all_"],"checksfailed","datamergedata", traceback.format_exc() if showtraceback else repr(e),"in code") 
		cdata["alldata"]={}

	try:
		makelists(cdata)
	except Exception as e:
		adderror(edict["_all_"],"checksfailed","makelists", traceback.format_exc() if showtraceback else repr(e),"in code") 

	for elem in allops:
		ekey=elem["name"]
		for op in elem.get("ops",[]):
			if op.get("execpos","standard")=="standard":
				if op.get("func","nofuncdeclared") in checklist:					
					checklist[op["func"]](edict[ekey],cdata,op.get("params",{}))
				else:
					adderror(edict[ekey],"config","funcmissing",op.get("func","nofuncdeclared"),op.get("execpos","standard")) 
	
	try:
		for elem in allops:
			delerr=[]
			ekey=elem["name"]		
			igncateg=elem.get("ignoreerror",{}).get("categ",[])
			ignname=elem.get("ignoreerror",{}).get("name",[])
			for ei,e in enumerate(edict[ekey]):				
				ok=True				
				for x in igncateg:
					if x==e[0]:
						ok=False
						break
				if ok:					
					for x in ignname:
						if x==e[1]:
							ok=False
							break
				if not ok:
					delerr.append(ei)
				else:					
					el=list(e)
					if len(el)<5:
						el.append("")					
					if isinstance(e[3],list):
						if el[4]=="":
							el[4]=repr(e[3])
						el[3]=guessline(cdata["data"],e[3])
					edict[ekey][ei]=tuple(el)
			for i in range(len(delerr)-1,-1,-1):
				del (edict[ekey][delerr[i]])

	except Exception as e:
		adderror(edict["_all_"],"checksfailed","errorfilter", traceback.format_exc() if showtraceback else repr(e),"in code") 

#	with open(staticpath+"static"+os.sep+"ruldata"+os.sep+'out.yml', 'w') as outfile:
#		outfile.write( prepareoutput(cdata["alldata"],cdata) )
#		outfile.write( yaml.dump(cdata["lists"]["refall"], Dumper=Dumper) )
	return edict

	#zipstuff

# with open(staticpath+"static"+os.sep+"ruldata"+os.sep+"default"+os.sep+"test"+".yaml","r",encoding="utf-8-sig",errors="ignore") as fh:
# 	test=fh.read()


#with Timer() as t:
#	ign={"categ": ["schema-oxc"],"name":["pattern"]}
#	ign={}
#	checks(tops,"default",test,ign)
#print('check took %.03f sec.' % t.interval)

def format(dataname,datastr):
	cdata=getcdata(dataname)	
	return prepareoutput(yaml.load(datastr, Loader=Loader)	,cdata)

def merge(dataname,datastr1,datastr2,modindex,prepare):
	cdata=getcdata(dataname)	
	d1=yaml.load(datastr1, Loader=Loader)
	d2=yaml.load(datastr2, Loader=Loader)	
	#dodel(d1,d2,cdata)	
	#removedel(d2,cdata)
	
	d=copy.deepcopy(d1)
	d=mergebase(cdata,d1,d2,k=["/"])
	extraspritemerge(d,d2,cdata)
	cdata["modindex"]=int(modindex)
	if prepare:
		ret=prepareoutput(d	,cdata)
	else:
		ret=yaml.dump(d, Dumper=Dumper)
	return ret

def makejsontree1(cdata):
	return cdata

def makejsontree(cdata,name="Rulesettree"):
	defaults=dict(string="''",number=0.0,boolean=False,integer=0)
	tmp={}
	#print([x for x in cdata])		
	tmp["name"]=name
	if "oneOf" in cdata:
		tmp["children"]=[dict(name="oneOf",children=[])]
		for xi,x in enumerate(cdata["oneOf"]):
			tmp["children"][0]["children"].append(makejsontree(x,name="option: "+str(xi)))

	elif cdata.get("type",hasnotypestring)=="object":
		tmp["children"]=[]
		prop=cdata.get("properties",{})
		order=sorted([(x,prop[x].get("oxcF_poscounter",9999999))for x in prop],key=lambda x:x[1])
		for x in order:
			if x[0] in [linestring, formatdictname]: continue
			tmp["children"].append(makejsontree(prop[x[0]],name=x[0]))

	elif cdata.get("type",hasnotypestring) in ["string","number","boolean","integer"]:
		tmp["name"]=tmp["name"]+"|"+cdata.get("type",hasnotypestring)+"|default: "+str(cdata.get("default",defaults[cdata.get("type",hasnotypestring)]))
	elif cdata.get("type",hasnotypestring)=="array":
		if "type" in cdata["items"]:
			if cdata["items"]["type"]=="object":
				tmp["children"]=[makejsontree(cdata["items"],name="a list")]
			elif cdata["items"]["type"]=="array":
				tmp["children"]=[makejsontree(cdata["items"],name="a list")]
			else:
				print ((tmp["name"],cdata["items"]["type"]))
		else:
			print ((cdata["items"]))
			##elif isinstance(cdata["items"],list):
			#	print ((99,cdata["items"]["type"]=="array",cdata))
	else:
		print (cdata)


#			else:
#				print (cdata)
				#	print ([x for x in cdata["items"]])
		#print (cdata.get("items",hasnotypestring))
		#if "items" in cdata:
		#	tmp["children"]=[makejsontree(cdata["items"],name="a list")]
		
	return tmp
	

#def rulesettree():
#	pass