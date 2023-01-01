#from __future__ import print_function
#from __future__ import unicode_literals
#from __future__ import division

from deep_eq import deep_eq #https://gist.github.com/samuraisam/901117
import yaml
import glob,os,pickle,copy,re,random,struct,math,itertools
from PIL import Image

from specific import *



elevel={1:"debug",10:"info",25:"warning",99:"error"}
newelevel={1:["debug","gray"],10:["info","gray"],25:["warning","#9BA013;"],99:["error","red"],-10:["unknown","blue"]}
preerrorlist=[
#loadmod:
# (1) load yamlfile->dict
("rulfile is likely not UTF-8",(99,"rulfile is likely not UTF-8 but contains non-ascii characters")),#found,warning,fail
("some error during rulfile import",(99,"unknown error during rulfile import (e.g. contains non-utf8 chars in utf8 file, file contains TAB)")),#found,warning,fail
("rulfile not in Ruleset Folder",(99,"rul file needs to be in a Ruleset Folder (be aware of the uppercase R)")),#found,warning,fail
("the mod .rul is not a map/dict",(99,"the rulefile is not a map/dict e.g. empty .rul file")),
#check multikeys in map/dict
("list not same length",(99,"this should not happen!")),
("a property doubled in map/dict",(25,"a listelement contains a property element twice")),#found
("an error during key duplicate check",(99,"there was an error?")),

#add2mod
("problem during adding of xrul file",(99,"a problem while adding a xrul file occured")),
("xrul wants to delete non existing object",(25,"the xrul file wants to delete an item but it does not exist in original mod")),

#fixorigvalues mod->mod
("changes original object",(10,"just an information")),#found,debug
("keeps original value",(10,"get rid of useless copying of data")),#found,debug
("fix: removes original value",(1,"a property of an listelement is removed because its orignal value was not changed")),#found,fix
("fix: removes original object",(1,"all properties of rule object are of the same original value deleted from mod")),#found,fix
("unknown/strange type in rul file",(99,"unknown type or data structure in rulfile")),
("problem during check/fix of original values",(99,"unknown problem")),
#TODO filemangment copy to new mod

#checkmodtrivial
("is no list",(10,"happens if you mod object is not a list if it should")),#,info
("is no dict",(25,"all elements in listitems should be dict")),#found,info
("contains delete!",(25,"an item contains a delete command")),#founf,warning
("identifier missing",(99,"unique identifier is missing in list entries")),#found,warning
("is wrong type",(25,"an item uses a wrong datatype")),#,info

#checkmodlangs/checkelemlangs
("no string translation",(25,"a string that is referenced is missing")),#found,warning
("a language/translation is missing",(25,"one of the languages we test for is missing")),#found,warning
("a language is incomplete",(25,"a language misses strings that are found in other languagues")),#found, info

#fixmodlanguage
("fix: failed - base language not found",(25,"the filling of language strings failed because the base language is missing")),#,fix
("fix: added new language",(10,"a missing languiage was added and filled based on an existing one")),#,fix
("language string differs in similar languages",(10,"for the string differs in two languages")),#,fix
("fix: added new string",(1,"yeah new string")),#,fix

#checkmodstuff
("an item occurs multiple time", (25,"same 'type' of item multiple times within the same list/mod")),#found, warning
("single image needs fid 0",(25,"a single image needs to have a file entry of 0")),
("more/less than one image with singleImage tag",(10,"referenced the same image multiple times .. by mistake?")),
("only ids up to 1000 save in extrasprite/sound",(25, "mods only have 1000 fileentries hihghe values can change fileentries in other mods")),#founf, warning
("fileid is not an integer",(25,"all file ids should be integers")),

#fixfilepaths mod->mod
("image/sound file should be in Resources/modname/... ",(10,"a file reference should reference files/dirs in a subdirectory in Resources")),
("a file is available in 2 casesensitive versions",(25,"on a filesystem that is case sensitive we have 2 files that the same case insensetive name")),
("fix: case sensitive path fixed",(1,"a file reference was changed to fit the case sensetive path")),#found,fix
("file/dir not found",(25,"a extrasprite/sound entry is wrong")),#found,warning
("the case sensitive test of dir/file path failed",(25,"to assure a workable mod on unix systems all file references are case sensitive")),#found,warning

("two sprites overlap in their file ids",(25,"the file ids of images of one spritesheets are reused by another image")),

("extrasprite/sound is not ruleset-referenced",(25,"extrasprite is not ruleset-referenced but in file section (ok if you replace clicksound/alienturn-image/..)")),#found ,?
("redefines original sprite/sound",(10,"warning that id is smaller than the biggest vanilla number and screws with existing sprites/sounds (works with some PCK entries not all)")),#found,info
("new sprite/sound is referenced multiple times",(10,"a sprite/sound is referenced multiple times in rulset")),#found,info


("non-ASCII char in path",(25,"only use ascii letter in path/file/map/terrain names")),
#checkspecfilepaths ...
("case sensitive path error for a file",(25,"the path to a file is wrong with case sensitve path settings")),#found,info
("spec file not found",(25,"missing map/terrain files")),
("different case sensitive names for the same specfile",(25,"your map/terrain files have different casesensitive letters")),
("spec file declared more than once",(10,"a map/terrain is used in more than one place .. by mistake?")),#found, info

#unused files (atm no method)
("not referenced file found",(10,"a file is in the mod folder and is not used/wrongly referenced in the ruleset")),#found,info

#loadfiles
("non image in spritesheet directory",(10,"there is a non-image file in a spritesheet directory")),#found, info
("a sprite directory contain non-uniform filenames",(25,"to get an assured sorting order within a sprite sheet directory the file should only differ in digits that failed here")),#found,info
("the colour palette differ within a spride sheet",(25,"the palette is not the same for all images of an spritesheet")),#found,warning
("an image has the wrong mode",(99,"an image needs to use a indexed by a colour Palette to use ")),
("the image size differ within a spride sheet",(25,"the size is not the same for all images of an spritesheet")),
("the sub images are not fitting into the full image",(25,"the splitting of an combined image into subpixel is incomplete")),#found,info
("image palette not complete",(25,"an image has an incomplete palette less than 256 colors")),#found,warning
("rul/real-size for single image does not match",(25,"size info in rul entry does not match real size")),
("fileextension not allowed",(25,"only specific file extensioen are allowed for images/maps/sounds")),
("an error occured during filereading",(25,"while reading a image/sound/map/terrain an unexpected error occured")),


("no connected file entry found for ruleset-referenced",(25,"there is reference to a new file entry but this entry does not exist")),#found,warning
("palette could use more colours",(10,"the image palette is only used in battlescape and likely can use the last 16 colours")),#found, info
("palette not correct",(25,"the assigned palette for an image is incorrect")),#found, warning, #http://imgur.com/kPn3C3W
("references spritesheet does misses images",(25,"a referenced spritesheet has less images than needed")),#found,?
("a sprite sheet is bigger than needed",(25,"a referenced spritesheet is bigger than necessary")),#found,?

#checkmodlogic
("missing research referenced",(25,"there is a research object referenced but it does not exist within rulset")),#
("missing item referenced",(25,"there is a item referenced but it does not exist within rulset ; craft production produces craft not item - ok ; needItem:true is used to block alienraces/autopsy/ufo/mission research - ok)")),#
("no listorder for new objects",(10,"new object should get a listOrder property to place them within their lists correctly")),#
("logicproblem",(10,"some logic problem occured")),#



#checkmodsall (atm no method)
("an item reoccurs in another mod",(25,"a new item is changed by multiple mods")),#found,info




#TODO
#fix palette

#old
#("single image referenced without singleImage tag in file entry",(25,"a single image is referenced but has no singleImage:True entry in corresponding files section")),
#  ("a reference is not for the first image spritesheet",(25,"a reference links to the middle of a sprite sheet")),#found



#online test errors
("an error occured during the zipfile extraction",(99,"the extraction or upload of the zipfile failed")),
("an error occured during modtest",(99,"an unknown error occured while testing a mod")),

#TODO
("test",(999,"internal use"))
]
errorlist=dict(preerrorlist)



#unique identifier what mod category has list->dict->unique property name
unlist=dict([
('invs', 'id'),
('research', 'name'),
('ufoTrajectories', 'id'),
('terrains', 'name'),
('items', 'type'),
('ufos', 'type'),
('alienMissions', 'type'),
('regions', 'type'),
('units', 'type'),
('facilities', 'type'),
('crafts', 'type'),
('manufacture', 'name'),
('ufopaedia', 'id'),
('MCDPatches', 'type'),
('extraSprites', 'type'),
('soldiers', 'type'),
('alienRaces', 'id'),
('countries', 'type'),
('alienDeployments', 'type'),
('craftWeapons', 'type'),
('armors', 'type')
])
unlist["extraSounds"]="type"
unlist["extraStrings"]="type"
unlist["statStrings"]="string"


#todo fix for new 2x2    ,3x3,.. facilities [1]=lambda x,[2*x.get("size",1)**2] / [1]() if hasattr([1], '__call__') else [1]
#what property in what object creates a reference to what internal file(s)
propsprites=[["facilities","spriteShape",["BASEBITS.PCK"]],
["facilities","spriteFacility",["BASEBITS.PCK"]],
["crafts","sprite",["BASEBITS.PCK","INTICON.PCK","INTICON.PCK"]],
["craftWeapons","sprite",["BASEBITS.PCK","INTICON.PCK"]],
["craftWeapons","sound",["GEO.CAT"]],
["items","bigSprite",["BIGOBS.PCK"]],
["items","floorSprite",["FLOOROB.PCK"]],
["items","handSprite",["HANDOB.PCK"]],
["items","fireSound",["BATTLE.CAT"]],
["items","hitSound",["BATTLE.CAT"]],
["items","meleeSound",["BATTLE.CAT"]],
["items","meleeHitSound",["BATTLE.CAT"]],
["items","hitAnimation",["SMOKE.PCK"]],
["items","meleeAnimation",["HIT.PCK"]],
#["ufos","sprite",["INTERWIN.DAT"]], #DO NOT USE->headache
["units","deathSound",["BATTLE.CAT"]],
["units","aggroSound",["BATTLE.CAT"]],
["units","moveSound",["BATTLE.CAT"]],
["units","moveSound",["BATTLE.CAT"]],
["items","bulletSprite",["Projectiles"]]
]
#0=first filename determines startid
#1=add to counter
#2=relative fileid add 1 to counter as lang as relative id is used
#3=multiplier for spriteid
propspdicts={}
for x in propsprites:
    propspdicts[x[0]]=propspdicts.get(x[0],{})
    propspdicts[x[0]][x[1]]=[x[2],[1 for y in x[2]],[0 for y in x[2]],[1 for y in x[2]]]
propspdicts["items"]["hitAnimation"][1]=[10]
propspdicts["items"]["meleeAnimation"][1]=[4]
propspdicts["items"]["handSprite"][1]=[8]
propspdicts["items"]["bulletSprite"][3]=[35]
propspdicts["crafts"]["sprite"][2]=[33,11,0]
propspdicts["craftWeapons"]["sprite"][2]=[48,5]

#min id,min fileid,(is sprite/sound)
#vanilla use - ids/palette for some internal files
csprites=dict([
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
sptest=[x for x in csprites]
#where to find referenced sprites (not sprite sheet)
singleimages=[["ufopaedia","image_id", 'research'],["ufos","modSprite", 'geo',]]


#get default palettes
palettes={}
for f in glob.glob(predir+"orig/p_*.gif"):
    with open(f,"rb") as fh:
        pim = Image.open(fh)
        pim.load()
        palettes[f.split("orig")[-1].split("_")[1]]=[1,256,[[pim.palette.palette[3*i+g] for g in range(3)] for i in range(256)]]

palettes["tactical2"][1]=256-16

allowedexts=dict(extraSounds=["ogg","wav"],extraSprites=["gif","png"],MAPS=["map","rmp"],TERRAIN=["mcd","pck","tab"])
ignorelngcat=["armors", "ufoTrajectories", "MCDPatches","extraSprites","extraSounds","terrains","alienItemLevels","soldiers"]
lngcat=['regions', 'items', 'ufos', 'invs', 'countries', 'units', 'alienDeployments', 'ufopaedia', 'craftWeapons', 'facilities', 'crafts', 'alienRaces', 'manufacture', 'alienMissions', 'research']

add2txtlistdata=dict(
items=["requires","compatibleAmmo"],
armors=["corpseBattle"],
#alienRaces=["members"],
research=["dependencies","unlocks","requires","getOneFree"],
crafts=["requires"],
ufopaedia=["requires"],
manufacture=["requires"]
)

relpos=[(16,0),(32,8),(0,8),(16,16)]

##12:32
##15:11
##
##19:160
##20:128
def getarmordata(mod,orig):
    #prepare id data for the hwp/armor sprite id chaos
    armorsofspawners=[x["armor"] for x in orig["units"]+mod.get("units",[]) if len(x.get("spawnUnit",""))>0]
    armorspace={1:99,2:32,3:56,5:160,6:131,7:227,8:9,9:28}
    armorspace[0]=lambda x:275+x.get("movementType",0)*8 if "storeItem" in x else 267
    armorspace[4]=lambda x:90 if x.get("type","") in armorsofspawners  else 75
    armorstart=dict([(x,0) for x in range(21)])
    armorstart[2]=lambda x:x.get("movementType",0)*32
    #hidden drawmethod 0++=10
    armorspace[10]=armorspace[0]
    for x in range(11,21):
        armorstart[x]=armorstart[0]
        armorspace[x]=armorstart[0]

    return armorspace,armorstart,armorsofspawners


def getorigdata(reloadorig):
    #mkdir orig
    #cd orig
    #mkdir Language
    #cd Language
    #wget http://openxcom.org/translations/latest.zip
    #wget https://github.com/SupSuper/OpenXcom/raw/master/bin/data/Language/en-GB.yml
    #wget https://github.com/SupSuper/OpenXcom/raw/master/bin/data/Language/en-US.yml
    #cd ..
    #wget http://github.com/SupSuper/OpenXcom/raw/master/bin/data/Ruleset/Xcom1Ruleset.rul
    #paletteimages
    #deep_eq
    if reloadorig:
        print ("load orig")
        with open(predir+'orig/Xcom1Ruleset.rul', 'r') as fh:
            orig=yaml.safe_load(fh)
        lang={}
        print ("load lang")
        for lfile in glob.glob(predir+"orig/Language/*.yml"):
            lfn=lfile.split(os.sep)[-1].split(".")[-2]
            with open(lfile, 'rb') as fh:
                print (lfile+":"+(lfn))
                tmp=yaml.safe_load(fh)
                if len(tmp)==1 and (True in tmp or False in tmp):
                    ltmp=tmp[[x for x in tmp][0]]
                    del(tmp[[x for x in tmp][0]])
                    tmp[lfn]=ltmp

                if [x for x in tmp][0]==lfn:
                    lang[lfn]=tmp
                else: print (lfn+" lang failed")
        print ("save orig")
        with open(predir+'orig.pickle', 'wb') as fh:
            pickle.dump((orig,lang),fh)
    else:
        with open(predir+'orig.pickle', 'rb') as fh:
            (orig,lang)=pickle.load(fh)
    return (orig,lang)


def getfilelists(arguments):
    allrulfiles=[]
    allxrulfiles=[]
    allfiles=[]
    alldirs=[]
    for args in arguments:
        for root,dirs,files in os.walk(args):
            for d in dirs:
                alldirs.append(os.path.join(root,d).replace("\\","/"))
            for f in files:
                allfiles.append(os.path.join(root,f).replace("\\","/"))
                if f.endswith(".rul"):
                    allrulfiles.append(os.path.join(root,f).replace("\\","/"))
                if f.endswith(".xrul"):
                    allxrulfiles.append(os.path.join(root,f).replace("\\","/"))
    return allrulfiles,allxrulfiles,allfiles,alldirs


def compmodlen(mod1,mod2,errors,path=[],mfile="undefined"):
    if isinstance(mod1,list) and len (mod1)!=len(mod2):
        errors.append(("list not same length",path,mfile))
        return errors
    if isinstance(mod1,dict) and len (mod1)!=len(mod2):
            xinfo=[]
            if len(path)>0 and path[0]  in unlist:
                xinfo=[unlist[path[0]]+": "+mod2.get(unlist[path[0]],"no identifier")]
            xdiff=[int(str(x)[20:]) if isinstance(x,int) else x[20:] for x in mod1]
            errors.append(tuple(["a property doubled in map/dict"]+path+xinfo+[list(set([x for x in xdiff if xdiff.count(x)>1]))]+[mfile]))
            return errors
    if isinstance(mod1,list):
        for ei,elem in enumerate(mod1):
            errors=compmodlen(mod1[ei],mod2[ei],errors,path=path+["[%d]"%ei],mfile=mfile)
    elif isinstance(mod1,dict):
        for elem in mod1:
            if isinstance(elem,int) :#or (web=="web" and isinstance(elem,long)):
                ekey=elem
                eskey=int(str(ekey)[20:])
            else:
                ekey=elem
                eskey=ekey[20:]
            errors=compmodlen(mod1[ekey],mod2[eskey],errors,path=path+[eskey],mfile=mfile)
    return errors

def loadamod(mfile,errors,alldirs,allfiles):
    mod={}
    if mfile.split("/")[-2]!="Ruleset":
        errors.append(("rulfile not in Ruleset Folder",mfile))
    else:
        with open(mfile, 'rb') as fh:
            print ("loading",mfile)
            try:
                t=fh.read()
                t=t.decode("utf-8")

                tmp=yaml.safe_load(t)
#                tmp=yaml.safe_load(fh)
            except yaml.reader.ReaderError:
                errors.append(("rulfile is likely not UTF-8",mfile))
            except :
                errors.append(("some error during rulfile import",mfile))
            else:
                mod=copy.deepcopy(tmp)
                if isinstance(mod,dict):
                    mod["MCPdata"]=dict(base="/".join(mfile.split("/")[0:-2]),files=[],dirs=[])
                    mod["MCPdata"]["dirs"]=[d for d in alldirs if d.startswith(mod["MCPdata"]["base"])]
                    mod["MCPdata"]["files"]=[f for f in allfiles if f.startswith(mod["MCPdata"]["base"])]
                    mod["MCPdata"]["rdirs"]=[d[len(mod["MCPdata"]["base"])+1:] for d in alldirs if d.startswith(mod["MCPdata"]["base"])]
                    mod["MCPdata"]["rfiles"]=[f[len(mod["MCPdata"]["base"])+1:] for f in allfiles if f.startswith(mod["MCPdata"]["base"])]
                    mod["MCPdata"]["unusedfiles"]=copy.deepcopy(mod["MCPdata"]["rfiles"])
                    mod["MCPdata"]["fdata"]={}
                    mod["MCPdata"]["fdataref"]={}
                    mod["MCPdata"]["modspecfiles"]={}
                    mod["MCPdata"]["getmallrefs"]=[]


                    try:
##                        openparams={} if web=="web" else dict(encoding="ascii",errors="ignore")
##                        openparams={} if web=="web" else dict(encoding="utf-8-sig",errors="ignore")
                        openparams=dict(encoding="utf-8-sig",errors="ignore")
                        with open(mfile, 'r',**openparams) as fh:
                            kcteststr=fh.read()
##                            if web=="web":
##                                if len(kcteststr)>3:
##                                    if ord(kcteststr[0])==239 and ord(kcteststr[1])==187 and ord(kcteststr[2])==191:
##                                        kcteststr = kcteststr[3:]
                            kcteststr=re.sub(r'[^\x00-\x7F]', 'x', kcteststr)
                            kclines=[]
                            for x in kcteststr.split("\n"):
                                kclines.append(x+"\n")
                            kctestnewstr=""
                            p=re.compile('[A-Z0-9a-z_-]+:')
                            for kcl in kclines:
                                for x in p.findall(kcl):
                                    kcl=kcl.replace(x,"%d"%random.randint(10**19,10**20-1)+x)
                                kctestnewstr+=kcl
                            with open(predir+"grr.rul","w") as fh2:
                                fh2.write(kctestnewstr)
                            with open(predir+"grr.rul","rb") as fh2:
                                kctmp=yaml.safe_load(fh2)
                            errors=compmodlen(kctmp,tmp,errors,mfile=mfile)
                    except yaml.reader.ReaderError:
                        errors.append(("an error during key duplicate check",mfile))
                else:
                    errors.append(("the mod .rul is not a map/dict",mfile))
                    mod={}
    return mod,errors

def fixorigvalue(orig,mod,errors,oname,mfile,fixit):
    try:
        deletecat=[]
        for cat in orig:
            if cat in mod:
                if cat=="MCPdata":continue
                if isinstance(orig[cat],list) and isinstance(mod[cat],list) and cat !="alienItemLevels":
                    deleteelem=[]
                    for ei,elem in enumerate(mod[cat]):
                        if not unlist.get(cat,"identifier unknown") in elem: continue
                        elemshow=[unlist[cat],elem.get(unlist[cat],"no unique id declared")]
                        testlist=[(xi,x) for xi,x in enumerate(orig[cat]) if x[unlist[cat]]==elem[unlist[cat]] ]
                        if len( testlist )>0:
                            oelem=orig[cat][testlist[0][0]]
                            if sum ([1 for prop in elem if prop!=unlist[cat] and prop in oelem and deep_eq(elem[prop],oelem[prop]) ] )>0:
                                if fixit:
                                    preerror=tuple(["fix: removes original value",cat]+elemshow+[[prop for prop in elem if prop!=unlist[cat] and prop in oelem and deep_eq(elem[prop],oelem[prop])]]+[oname,mfile])
                                    #errors.append(tuple(["fix: removes original value",cat]+elemshow+[[prop for prop in elem if prop!=unlist[cat] and prop in oelem and deep_eq(elem[prop],oelem[prop])]]+[oname,mfile]))
                                    delprops=[]
                                    for prop in elem:
                                        if prop==unlist[cat]:continue
                                        if prop in oelem and deep_eq(elem[prop],oelem[prop]):
                                            delprops.append(prop)
                                    for dprop in delprops:
                                        del(mod[cat][ei][dprop])
                                    if len(elem)==1:
                                        errors.append(tuple(["fix: removes original object",cat]+elemshow+[[prop for prop in elem if prop!=unlist[cat] and prop in oelem and deep_eq(elem[prop],oelem[prop])]]+[oname,mfile]))
                                        deleteelem.append(ei)
                                    else:
                                        errors.append(preerror)
                                else:
                                    errors.append(tuple(["keeps original value",cat]+elemshow+[[prop for prop in elem if prop!=unlist[cat] and prop in oelem and deep_eq(elem[prop],oelem[prop])]]+[oname,mfile]))
                            testlist2=[prop for prop in elem if prop!=unlist[cat] and prop in oelem and not deep_eq(elem[prop],oelem[prop])]
                            #testlist2=[prop for prop in elem if prop!=unlist[cat] and not (cat,prop) in ignorechangeprop and prop in oelem and not deep_eq(elem[prop],oelem[prop])]
                            if len (testlist2 )>0:
                                errors.append(tuple(["changes original object",cat]+elemshow+[testlist2]+[oname,mfile]))
                    deleteelem.sort(reverse=True)
                    for delelem in deleteelem:
                        del(mod[cat][delelem])
                    if len(mod[cat])==0:
                        errors.append(tuple(["fix: removes original object","whole object",cat]+[oname,mfile]))
                        deletecat.append(cat)
                elif isinstance(orig[cat],dict) and isinstance(mod[cat],dict):
                    if sum ([1 for prop in mod[cat] if prop in orig[cat] and deep_eq(mod[cat][prop],orig[cat][prop]) ] )>0:
                        if fixit:
                            preerror=tuple(["fix: removes original value",cat]+[[prop for prop in mod[cat] if prop in orig[cat] and deep_eq(mod[cat][prop],orig[cat][prop])]]+[oname,mfile])
                            #errors.append(tuple(["fix: removes original value",cat]+[[prop for prop in mod[cat] if prop in orig[cat] and deep_eq(mod[cat][prop],orig[cat][prop])]]+[oname,mfile]))
                            delprops=[]
                            for prop in mod[cat]:
                                if prop in orig[cat] and deep_eq(mod[cat][prop],orig[cat][prop]):
                                    delprops.append(prop)
                            for dprop in delprops:
                                del(mod[cat][dprop])
                            if len(mod[cat])==0:
                                errors.append(tuple(["fix: removes original object",cat]+[[prop for prop in mod[cat] if prop in orig[cat] and deep_eq(mod[cat][prop],orig[cat][prop])]]+[oname,mfile]))
                                deletecat.append(cat)
                            else:
                                errors.append(preerror)
                        else:
                            errors.append(tuple(["keeps original value",cat]+[[prop for prop in mod[cat] if prop in orig[cat] and deep_eq(mod[cat][prop],orig[cat][prop])]]+[oname,mfile]))
                    if sum ([1 for prop in mod[cat] if prop in orig[cat] and not deep_eq(mod[cat][prop],orig[cat][prop]) ] )>0:
                        errors.append(tuple(["changes original object",cat]+[[prop for prop in mod[cat] if prop in orig[cat] and not deep_eq(mod[cat][prop],orig[cat][prop])]]+[oname,mfile]))
                elif (isinstance(orig[cat],int) and isinstance(mod[cat],int)) or (isinstance(orig[cat],list) and isinstance(mod[cat],list) and cat =="alienItemLevels"):
                    if deep_eq(mod[cat],orig[cat]):
                        if fixit:
                            errors.append(tuple(["fix: removes original value",cat]+[oname,mfile]))
                            deletecat.append(cat)
                        else:
                            errors.append(tuple(["keeps original value",cat]+[oname,mfile]))
                    else:
                        errors.append(tuple(["changes original object",cat]+[oname,mfile]))
                else:
                    errors.append(tuple(["unknown/strange type in rul file",cat]+[oname,mfile]))
        for delcat in deletecat:
            del(mod[delcat])

    except:
        errors.append(tuple(["problem during check/fix of original values"]+[oname,mfile]))
    return mod,errors


"""


[16:30] <SupSuper> what do you mean a "add2list"?
[16:31] <falko_> i command like "delete" that does not delete an element but adds to lists within objects like compatible ammo, getonefree, requires,...
[16:32] <falko_> if you are interested i could post some thought about it in the forum - i use it for my "xrul" (extrarul -file) that "copies" the mod mechanics of a normal rulfile
[16:33] <falko_> as soon as i am finished with this tool yopu guys could get some feedback if such command is appriciated/flexible enough/easy to use/... - the implementation would be in ine file the template where the delete operation is also coded
[16:34] <falko_> if there is a  chance for implementation i would add more thoughts/info to that thing than just describing what it does
[16:35] <SupSuper> sure
[16:35] <SupSuper> it's not a problem of "how to do it", more "how to do it without it becoming a tremendous mess" :)
[16:36] <falko_> yeah :)
[16:36] <falko_>  i hope i can give you a usable suggestion how one can do it
[16:37] <falko_> do you have a online help for c++ where i can get information about lists (vectors?)
[16:41] <SupSuper> hmmm well i usually just check this reference: http://www.cplusplus.com/
[16:41] <falko_> ok i will take a look thx
  - add2txtlist:
      - elemid: STR_SOMEELEM
      - requires: STR_SOME_TECH
      - requires: STR_SOME_OLD_TECH
        op: delete
      - requires: STR_SOME_OLD_TECH
        pos: start
  - add2txtlist:
      - elemid: STR_SOMEOTHERELEM
      - getonefree: STR_SOME_GIVEAWAY_TECH

add2txtlistdata=dict(
items=["requires","compatibleAmmo"],
armors=["corpseBattle"],
#alienRaces=["members"],
research=["dependencies","unlocks","requires","getOneFree"],
crafts=["requires"],
ufopaedia=["requires"],
manufacture=["requires"],
)

items: requires, compatibleAmmo
armors: corpseBattle
alienRaces: members !
research: dependencies, unlocks, requires, getOneFree
crafts,ufopaedia,manufacture: requires

regions: missionWeights int
invs: costs int
soldiers: minStats,maxStats,statCaps int
units: stats int
manufacture: requiredItems,producedItems int
ufopaedia: rect_stats, rect_text int
alienMissions: raceWeights NO



ufoTrajectories:
    waypoints:
      - [5, 4, 100]
manufacture:
    requires:
      - STR_FUSION_MISSILE
alienDeployments:
    data:
      - alienRank: 5
        lowQty: 1
        highQty: 1
        dQty: 0
        percentageOutsideUfo: 50
        itemSets:
          -
            - STR_PLASMA_PISTOL
            - STR_PLASMA_PISTOL_CLIP
            - STR_PLASMA_PISTOL_CLIP
            - STR_MIND_PROBE
          -
            - STR_PLASMA_RIFLE
            - STR_PLASMA_RIFLE_CLIP
            - STR_PLASMA_RIFLE_CLIP
            - STR_MIND_PROBE
          -
            - STR_HEAVY_PLASMA
            - STR_HEAVY_PLASMA_CLIP
            - STR_MIND_PROBE
terrains:
    textures: [1, 2, 3, 4]
    mapBlocks:
      - name: CULTA00
        width: 10
        length: 10
        type: 1
        subType: 0
        maxCount: 3

crafts:
    deployment:
      - [10, 5, 1, 2]
      - [10, 6, 1, 2]

regions:
    areas:
      - [195, 305, -70, -55]
    cities:
      - name: STR_NEW_YORK
        lon: 286.125
        lat: -40.75
    missionZones:
      -
        - [200, 220, -65, -60]
        - [230, 260, -65, -55]
        - [280, 290, -50, -40]
        - [230, 250, -50, -40]
        - [260, 280, -50, -40]

countries:
    areas:
      - [235, 255, -49, -32]
      - [255, 277.5, -49, -29]
"""

def add2mod(orig,mod,errors,oname,mfile):
    xchangeprop=[("alienMissions","raceWeights")]
    try:
        deletecat=[]
        for cat in mod:
            if cat=="MCPdata":continue #TODO
            if not cat in orig:
                orig[cat]=copy.deepcopy(mod[cat])
            else:
                if isinstance(orig[cat],list) and isinstance(mod[cat],list) and cat !="alienItemLevels":
                    deleteelem=[]
                    for ei,elem in enumerate(mod[cat]):
                        if not unlist.get(cat,"identifier unknown") in elem and not "delete" in elem : continue
                        elemshow=[unlist[cat],elem.get(unlist[cat],"no unique id declared")]
                        if not elem.get("delete",False):
                            testlist=[(xi,x) for xi,x in enumerate(orig[cat]) if x[unlist[cat]]==elem[unlist[cat]] ]
                        else:
                            testlist=[(xi,x) for xi,x in enumerate(orig[cat]) if x[unlist[cat]]==elem["delete"] ]
                        if elem.get("delete",False):
                            if len(testlist)>0:
                                deleteelem.append(testlist[0][0])
                            else:
                                errors.append(tuple(["xrul wants to delete non existing object",cat,elem["delete"]]+[oname,mfile]))
##                        if elem.get("add2txtlist",False) and cat in add2txtlistdata:
##
##
##
##
##
                        elif len( testlist )==0:
                            orig[cat].append(copy.deepcopy(elem))
                        else:
                            oelem=orig[cat][testlist[0][0]]
                            for prop in elem:
                                if (cat,prop) in xchangeprop and prop in oelem:
                                    for m in elem[prop]:
                                        if not m in oelem[prop]:
                                            orig[cat][testlist[0][0]][prop][m]=copy.deepcopy(elem[prop][m])
                                        else:
                                            for r in elem[prop][m]:
                                                orig[cat][testlist[0][0]][prop][m][r]=copy.deepcopy(elem[prop][m][r])
                                    pass
                                else:
                                    orig[cat][testlist[0][0]][prop]=copy.deepcopy(elem[prop])
                    deleteelem.sort(reverse=True)
                    for delelem in deleteelem:
                        del(orig[cat][delelem])
                elif isinstance(orig[cat],dict) and isinstance(mod[cat],dict):
                    for prop in mod[cat]:
                        orig[cat][prop]=copy.deepcopy(elem[prop])
                elif (isinstance(orig[cat],int) and isinstance(mod[cat],int)) or (isinstance(orig[cat],list) and isinstance(mod[cat],list) and cat =="alienItemLevels"):
                    orig[cat]=copy.deepcopy(mod[cat])

    except:
        errors.append(tuple(["problem during adding of xrul file"]+[oname,mfile]))
    return orig,errors

def checkmodtrivial(elem,cat,lvl,mfile,terrors):
    ret=True
    if lvl==0:
        if cat in unlist and not isinstance(elem,list):
            ret=False
            terrors.append(("is no list",cat,mfile))
        if not cat in unlist and not cat in ["startingBase","startingTime","alienItemLevels","MCPdata"] and not isinstance(elem,int):
            ret=False
            terrors.append(("is wrong type",cat,mfile))
        if cat=="alienItemLevels":
            ret=isinstance(elem,list) and len(elem)>0
            if ret:
                for ail in elem:
                    ret=ret and isinstance(ail,list) and len(ail)==10
            if not ret:
                terrors.append(("is wrong type",cat,mfile))
        if cat in ["startingBase","startingTime"] and not isinstance(elem,dict):
            ret=False
            terrors.append(("is wrong type",cat,mfile))
    if lvl==1:
        if cat in unlist:
            if not isinstance(elem,dict):
                ret=False
                errors.append(("is no dict",cat,mfile))
            else:
                if elem.get("delete",False):
                    terrors.append(("contains delete!",cat,repr(elem)[0:150],mfile))
                    ret=False
                if not unlist[cat] in elem:
                    terrors.append(("identifier missing",cat,unlist[cat],repr(elem)[0:150],mfile))
                    ret=False
    return ret,terrors





def checkmodlangs(mod,errors,test_lngs,mfile):
    for l1 in mod.get("extraStrings",[]):
        tmpmissing={}
        l1name=l1.get("type","NOTTHERE")
        l1strings=l1.get("strings",{})
        for l2 in mod.get("extraStrings",[]):
            if l1!=l2:
                l2name=l2.get("type","NOTTHERE")
                l2strings=l2.get("strings",{})
                if len(set(l2strings)-set(l1strings))>0:
                    tmpmissing[l2name]=list(set(l2strings)-set(l1strings))
        if tmpmissing:
            errors.append(("a language is incomplete",l1name,tmpmissing,mfile))
    langmod={}
    for test_lng in test_lngs:
        langmod[test_lng]={test_lng:{}}
        for l in mod.get("extraStrings",[]):
            if isinstance(l,dict) and test_lng == l.get("type"):
                langmod[test_lng][test_lng]=l.get("strings",{})
        if langmod[test_lng][test_lng]=={} and len(mod.get("extraStrings",[]))>0:
            del langmod[test_lng]
            errors.append(("a language/translation is missing",test_lng,mfile))
    return langmod,errors

def checkelemlangs(cat,elem,langmod,lang,errors,mfile):

    for test_lng in langmod:
        testwords=[elem[unlist[cat]]]
        if cat=="items" and not elem.get("recover",True):
            testwords=[elem.get("name","STR_CORPSE_SHOULD_HAVE_A_NAMEENTRY")]
        if cat=="ufopaedia" and "text" in elem:
            testwords.append(elem["text"])
        for testword in testwords:
            if not (lang.get(test_lng,{}).get(test_lng,{}).get(testword,"") or langmod.get(test_lng,{}).get(test_lng,{}).get(testword,"")):
                errors.append(("no string translation",test_lng,cat,elem[unlist[cat]],testword,mfile))
    return errors

def fixmodlanguage(mod,errors,langswitch,mfile):
    cat="extraStrings"
    for ltype in langswitch:
        f1=-1
        f2=-1
        if cat in mod:
            for i in range(len(mod[cat])):
                elem=mod[cat][i]
                if checkmodtrivial(elem,cat,1,mfile,[])[0]:
                    if elem[unlist[cat]]==ltype[0]:f1=i
                    if elem[unlist[cat]]==ltype[1]:f2=i
            if f1<0:
                errors.append (("fix: failed - base language not found",cat,ltype,mfile))
            else:
                if f2<0:
                    errors.append (("fix: added new language",cat,ltype[1],mfile))
                    mod[cat].append(dict(type=ltype[1],strings={}))
                    f2=len(mod[cat])-1
                mod[cat][f1]["strings"]=mod[cat][f1].get("strings",{})
                mod[cat][f2]["strings"]=mod[cat][f2].get("strings",{})
                for string in mod[cat][f1]["strings"]:
                    if string in mod[cat][f2]["strings"]:
                        if ltype[2]==1 and mod[cat][f1]["strings"][string]!=mod[cat][f2]["strings"][string]:
                            errors.append (("language string differs in similar languages",cat,ltype,string,mfile))
                    else:
                        errors.append (("fix: added new string",cat,ltype,string,mfile))
                        mod[cat][f2]["strings"][string]=ltype[3]+mod[cat][f1]["strings"][string]
    return mod,errors

def checkmodstuff(mod,errors,mfile):
    checkallelem={}
    for cat in unlist:
        if cat in mod:
            if not checkmodtrivial(mod[cat],cat,0,mfile,[])[0]: continue
            for elem in mod[cat]:
                if not checkmodtrivial(elem,cat,1,mfile,[])[0]: continue
                checkallelem[(cat,elem[unlist[cat]])]=checkallelem.get((cat,elem[unlist[cat]]),0)+1
                for testsprite in [
                    [[x for x in elem.get("files",{}) if cat in ["extraSprites","extraSounds"] and not isinstance(x,int)],"fileid is not an integer"],
                    [[x for x in elem.get("files",{}) if cat in ["extraSprites","extraSounds"] and isinstance(x,int) and x>999],"only ids up to 1000 save in extrasprite/sound"],
                    [[x for x in elem.get("files",{}) if cat=="extraSprites" and elem.get("singleImage",False) and len(elem["files"])!=1 ],"more/less than one image with singleImage tag"],
                    [[x for x in elem.get("files",{}) if cat=="extraSprites" and elem.get("singleImage",False) and not 0 in elem["files"]!=0],"single image needs fid 0"]
                ]:
                    if len(testsprite[0])>0:
                        errors.append((testsprite[1],cat,elem[unlist[cat]],testsprite[0],mfile))
    for celem in checkallelem:
        if checkallelem[celem]>1:
            errors.append(("an item occurs multiple time",celem[0],celem[1],checkallelem[celem],mfile))
    return errors


def mngextrafileelem(origspecfiles,cat,elem,origmaps,origterrain):

    if cat in ["crafts","ufos"]:
        for mobj in elem.get("battlescapeTerrainData",{}).get("mapBlocks",[]):
            if not mobj.get("name","NONONOMAPNAME") in origmaps:
                n=("MAPS",mobj.get("name","NONONOMAPNAME"))
                origspecfiles[n]=origspecfiles.get(n,dict(ref=[],files=["MAPS/"+mobj.get("name","NONONOMAPNAME")+".MAP","ROUTES/"+mobj.get("name","NONONOMAPNAME")+".RMP"]))
                origspecfiles[n]["ref"].append((cat,elem[unlist[cat]],mobj.get("name","NONONOMAPNAME")))
        for tname in elem.get("battlescapeTerrainData",{}).get("mapDataSets",[]):
            if not tname in origterrain:
                n=("TERRAIN",tname)
                origspecfiles[n]=origspecfiles.get(n,dict(ref=[],files=["TERRAIN/"+tname+"."+x for x in ["MCD","PCK","TAB"]]))
                origspecfiles[n]["ref"].append((cat,elem[unlist[cat]],tname))
    if cat in ["facilities"] and "mapName" in elem:
        if not elem.get("name","NONONOMAPNAME") in origmaps:
            n=("MAPS",elem.get("mapName","NONONOMAPNAME"))
            origspecfiles[n]=origspecfiles.get(n,dict(ref=[],files=["MAPS/"+elem.get("name","NONONOMAPNAME")+".MAP","ROUTES/"+elem.get("name","NONONOMAPNAME")+".RMP"]))
            origspecfiles[n]["ref"].append(("MAPS",cat,elem[unlist[cat]],elem.get("mapName","NONONOMAPNAME")))
    if cat in ["terrains"]:
        for mobj in elem.get("mapBlocks",[]):
            if not mobj.get("name","NONONOMAPNAME") in origmaps:
                n=("MAPS",mobj.get("name","NONONOMAPNAME"))
                origspecfiles[n]=origspecfiles.get(n,dict(ref=[],files=["MAPS/"+mobj.get("name","NONONOMAPNAME")+".MAP","ROUTES/"+mobj.get("name","NONONOMAPNAME")+".RMP"]))
                origspecfiles[n]["ref"].append((cat,elem[unlist[cat]],mobj.get("name","NONONOMAPNAME")))
        for tname in elem.get("mapDataSets",[]):
            if not tname in origterrain:
                n=("TERRAIN",tname)
                origspecfiles[n]=origspecfiles.get(n,dict(ref=[],files=["TERRAIN/"+tname+"."+x for x in ["MCD","PCK","TAB"]]))
                origspecfiles[n]["ref"].append((cat,elem[unlist[cat]],tname))
    return origspecfiles





def loadfiles(ref,fpath,elem,mfile,flist,errors,mod):
    try:
        if fpath[-1]!="/" and not fpath.split(".")[-1].lower() in allowedexts.get(ref[0],[]):
            errors.append(("fileextension not allowed",ref,fpath,allowedexts.get(ref[0],[]),mfile))
        else:
            if ref[0] in ["extraSounds","MAPS","TERRAIN"]:
                with open (fpath,"rb") as fh:
                    data=fh.read()
                    flist[ref]=(fpath.split(".")[-1],data)
            if ref[0] in ["extraSprites"]:
                img=[]
                imgn=[]

                if fpath[-1]!="/":
                    with open(fpath,"rb") as fh:
                        tmpimg=Image.open(fh)
                        if elem.get("subX",0)+elem.get("subY",0)==0 or elem.get("singleImage",False):
                            imgn.append(fpath)
                            img.append(tmpimg)
                            if elem.get("singleImage",False):
                                if not tmpimg.size==(elem.get("width",320),elem.get("height",200)):
                                    errors.append(("rul/real-size for single image does not match",ref,fpath,mfile))
                        else:
                            imgsize=(elem.get("subX",0),elem.get("subY",0))
                            if tmpimg.size[1]%imgsize[1]!=0 or tmpimg.size[0]%imgsize[0] !=0:
                                errors.append(("the sub images are not fitting into the full image",ref,fpath,mfile))
                            else:
                                for y in range(0,tmpimg.size[1]-imgsize[1]+1,imgsize[1]):
                                    for x in range(0,tmpimg.size[0]-imgsize[0]+1,imgsize[0]):
                                        croptmp=tmpimg.crop((x,y,x+imgsize[0],y+imgsize[1]))
                                        croptmp.save("tmp.gif",optimize=False,transparency=0) #TODO ARGH WTF why is crop / load combo not working?
                                        croptmp=Image.open("tmp.gif")
                                        croptmp.load()
                                        img.append(croptmp)
                                        imgn.append(fpath)

                else:
                    filelist=[x for x in glob.glob(fpath+"*")]
                    wrongfiles=[ x.replace("\\","/").replace(mod["MCPdata"]["base"]+"/","") for x in filelist if not x.split(".")[-1].lower() in allowedexts.get(ref[0],[])]
                    imagefiles=[ x for x in filelist if x.split(".")[-1].lower() in allowedexts.get(ref[0],[])]
                    imagenamefiles=list(set([ re.sub(r'[0-9]',"_",x.replace("\\","/").replace(mod["MCPdata"]["base"]+"/","")) for x in filelist if x.split(".")[-1].lower() in allowedexts.get(ref[0],[])]))
                    if len(wrongfiles)>0:
                        errors.append(("non image in spritesheet directory",ref,fpath,wrongfiles,mfile))
                    if len(imagenamefiles)>1:
                        errors.append(("a sprite directory contain non-uniform filenames",ref,fpath,imagenamefiles,mfile))
                    for f in sorted(imagefiles):
                        with open(f,"rb") as fh:
                            tmpimg=Image.open(fh)
                            tmpimg.load()
                            img.append(tmpimg)
                            imgn.append(f)
                imgn=[x.replace("\\","/").replace(mod["MCPdata"]["base"]+"/","") for x in imgn]
                rbgmodelist=[ifile for i,ifile in enumerate(imgn) if not img[i].mode=="P"]
                shortpallist=[ifile for i,ifile in enumerate(imgn) if img[i].mode=="P" and not len(img[i].palette.palette)==768]
                paldifflist=[ifile for i,ifile in enumerate(imgn) if img[i].mode=="P" and img[0].mode=="P" and  img[i].palette.palette!=img[0].palette.palette]
                sizedifflist=[ifile for i,ifile in enumerate(imgn) if img[i].size!=img[0].size]
                if len(rbgmodelist)>0:
                    errors.append(("an image has the wrong mode",ref,fpath,rbgmodelist,mfile))
                if len(shortpallist)>0:
                    errors.append(("image palette not complete",ref,fpath,shortpallist,mfile))
                if len(paldifflist)>0:
                    errors.append(("the colour palette differ within a spride sheet",ref,fpath,paldifflist,mfile))
                if len(sizedifflist)>0:
                    errors.append(("the image size differ within a spride sheet",ref,fpath,sizedifflist,mfile))
                flist[ref]=img
    except:
        errors.append(("an error occured during filereading",ref,fpath,mfile))
    return flist,errors
def fixfilepaths(mod,errors,mfile,fixit,getfiles):
    for cat in unlist:
        if cat in mod:
            if not cat in ["extraSprites","extraSounds"]:continue
            if not checkmodtrivial(mod[cat],cat,0,mfile,[])[0]: continue
            for ei,elem in enumerate(mod[cat]):
                if not checkmodtrivial(elem,cat,1,mfile,[])[0]: continue
                for fid in elem.get("files",{}):
                    tocheckfile=elem["files"][fid]
                    if len(re.sub(r'[\x00-\x7F]',"",tocheckfile))>0:
                        errors.append(("non-ASCII char in path",cat,elem[unlist[cat]],fid,tocheckfile,mfile))
                    if len(tocheckfile.split("/"))<3 or tocheckfile.split("/")[0]!="Resources":
                        errors.append(("image/sound file should be in Resources/modname/... ",cat,elem[unlist[cat]],fid,tocheckfile,mfile))
                    if "/"==tocheckfile[-1]:
                        checkfunc=os.path.isdir
                        rlist=[x+"/" for x in mod["MCPdata"]["rdirs"]]
                        alist=[x+"/" for x in mod["MCPdata"]["dirs"]]
                    else:
                        checkfunc=os.path.isfile
                        rlist=mod["MCPdata"]["rfiles"]
                        alist=mod["MCPdata"]["files"]
                    newfns=[x for x in rlist if x.lower()==tocheckfile.lower()]
                    if len(newfns)==0 or (len(newfns)==1 and not checkfunc(mod["MCPdata"]["base"]+"/"+newfns[0])):
                        errors.append(("file/dir not found",cat,elem[unlist[cat]],fid,newfns,tocheckfile,mfile))
                    elif len(newfns)>1:
                        errors.append(("a file is available in 2 casesensitive versions",cat,elem[unlist[cat]],fid,newfns,tocheckfile,mfile))
                    elif newfns[0]!=tocheckfile:
                        if getfiles: mod["MCPdata"]["fdata"],errors=loadfiles((cat,elem[unlist[cat]],fid),mod["MCPdata"]["base"]+"/"+newfns[0],elem,mfile,mod["MCPdata"]["fdata"],errors,mod)
                        if "/"!=tocheckfile[-1]:
                            if newfns[0] in mod["MCPdata"]["unusedfiles"]: mod["MCPdata"]["unusedfiles"].remove(newfns[0])
                        else:
                            for usedfile in [x.replace("\\","/").replace(mod["MCPdata"]["base"]+"/","") for x in glob.glob(mod["MCPdata"]["base"]+"/"+newfns[0]+"*")]:
                                if os.path.isfile(mod["MCPdata"]["base"]+"/"+usedfile):
                                    if usedfile in mod["MCPdata"]["unusedfiles"]: mod["MCPdata"]["unusedfiles"].remove(usedfile)
                        if fixit:
                            errors.append(("fix: case sensitive path fixed",cat,elem[unlist[cat]],fid,tocheckfile,newfns[0],mfile))
                            mod[cat][ei]["files"][fid]=newfns[0]
                        else:
                            errors.append(("the case sensitive test of dir/file path failed",cat,elem[unlist[cat]],fid,tocheckfile,newfns[0],mfile))
                    elif newfns[0]==tocheckfile:
                        if getfiles: mod["MCPdata"]["fdata"],errors=loadfiles((cat,elem[unlist[cat]],fid),mod["MCPdata"]["base"]+"/"+newfns[0],elem,mfile,mod["MCPdata"]["fdata"],errors,mod)
                        if "/"!=tocheckfile[-1]:
                            if newfns[0] in mod["MCPdata"]["unusedfiles"]: mod["MCPdata"]["unusedfiles"].remove(newfns[0])
                        else:
                            for usedfile in [x.replace("\\","/").replace(mod["MCPdata"]["base"]+"/","") for x in glob.glob(mod["MCPdata"]["base"]+"/"+newfns[0]+"*")]:
                                if os.path.isfile(mod["MCPdata"]["base"]+"/"+usedfile):
                                    if usedfile in mod["MCPdata"]["unusedfiles"]: mod["MCPdata"]["unusedfiles"].remove(usedfile)
    testimg={}
    testfiles={}
    for f in mod["MCPdata"]["fdata"]:
        if f[0]=="extraSprites":
            ele=mod["MCPdata"]["fdata"][f]
            testfiles[f[1]]=1
            testimg[f[1]]=testimg.get(f[1],{})
            testimg[f[1]][tuple([x for x in range(f[2],f[2]+len(ele))])]=f
    for fi in testfiles:
        for ei,e in enumerate(testimg[fi]):
            for ei2,e2 in enumerate(testimg[fi]):
                if ei>=ei2:continue
                if len(set(e)&set(e2))>0:
                    errors.append(("two sprites overlap in their file ids","extraSprites",testimg[fi][e][1:],testimg[fi][e2][1:],mfile))

    for  x in mod["MCPdata"]["fdata"]:
        if x[0].startswith("e"):
            mod["MCPdata"]["fdataref"][x]=mod["MCPdata"]["fdataref"].get(x,[])
            for ri,ref in enumerate(mod["MCPdata"]["getmallrefs"]):
                if x[1]== ref.get("refelem","noreffound"):
                    if x[2] in ref.get("refid",[]):
                        mod["MCPdata"]["fdataref"][x].append(ri)
                        #print ((x,mod["MCPdata"]["getmallrefs"]["filebackref"]))
                        mod["MCPdata"]["getmallrefs"][ri]["filebackref"].append(x)
            if len(mod["MCPdata"]["fdataref"][x])==0:
                errors.append(("extrasprite/sound is not ruleset-referenced",x,mfile))
    for  x in mod["MCPdata"]["fdata"]:
        if x[0].startswith("e"):
            if x[1] in csprites and x[2]<csprites[x[1]][1]:
                errors.append(("redefines original sprite/sound",x,mfile))
            if len(mod["MCPdata"]["fdataref"][x])>1:
                errors.append(("new sprite/sound is referenced multiple times",x,[[mod["MCPdata"]["getmallrefs"][y][z] for z in ["cat","lid","prop"]] for y in mod["MCPdata"]["fdataref"][x]],mfile))
    return mod,errors

def checkspecfilepaths(mod,errors,mfile,getfiles):
    modspecfiles=mod["MCPdata"]["modspecfiles"]
    tmpspecsumup={}
    for x in modspecfiles:
        tmpspecsumup[(x[0],x[1].lower())]=tmpspecsumup.get((x[0],x[1].lower()),[])
        tmpspecsumup[(x[0],x[1].lower())].append((x,modspecfiles[x]["ref"]))
        if len(modspecfiles[x]["ref"])>1:
            errors.append(("spec file declared more than once",x,modspecfiles[x]["ref"],mfile))
        if len(re.sub(r'[\x00-\x7F]',"",x[1]))>0:
            errors.append(("non-ASCII char in path",x,modspecfiles[x]["ref"],mfile))
        for sfile in modspecfiles[x]["files"]:
            newfns=[y for y in mod["MCPdata"]["rfiles"] if y.lower()==sfile.lower()]
            if len(newfns)==0 or (len(newfns)==1 and not os.path.isfile(mod["MCPdata"]["base"]+"/"+newfns[0])):
                errors.append(("spec file not found",x,modspecfiles[x]["ref"],sfile,mfile))
            elif len(newfns)>1:
                errors.append(("a file is available in 2 casesensitive versions",x,modspecfiles[x]["ref"],sfile,newfns,mfile))
            elif newfns[0]!=sfile:
                if getfiles: mod["MCPdata"]["fdata"],errors=loadfiles(tuple(list(x)+[sfile.split(".")[-1]]),mod["MCPdata"]["base"]+"/"+newfns[0],None,mfile,mod["MCPdata"]["fdata"],errors,mod)
                if newfns[0] in mod["MCPdata"]["unusedfiles"]: mod["MCPdata"]["unusedfiles"].remove(newfns[0])
                #TODO fixing?
                errors.append(("case sensitive path error for a file",x,modspecfiles[x]["ref"],sfile,newfns[0],mfile))
            elif newfns[0]==sfile:
                if getfiles: mod["MCPdata"]["fdata"],errors=loadfiles(tuple(list(x)+[sfile.split(".")[-1]]),mod["MCPdata"]["base"]+"/"+newfns[0],None,mfile,mod["MCPdata"]["fdata"],errors,mod)
                if newfns[0] in mod["MCPdata"]["unusedfiles"]: mod["MCPdata"]["unusedfiles"].remove(newfns[0])
    for x in tmpspecsumup:
        if len(tmpspecsumup[x])>1:
            errors.append(("different case sensitive names for the same specfile",tmpspecsumup[x],mfile))
    return mod,errors


def makerefs(mod,errors,orig,mfile):
    armorspace,armorstart,armorsofspawners=getarmordata(mod,orig)
    getmallrefs=[]
    for cat in unlist:
        if cat in mod:
            if not checkmodtrivial(mod[cat],cat,0,mfile,[])[0]: continue
            for elem in mod[cat]:
                if not checkmodtrivial(elem,cat,1,mfile,[])[0]: continue
                for prop in elem:
                    if cat in propspdicts:
                        if prop in propspdicts[cat]:
                            for si,spfile in enumerate(propspdicts[cat][prop][0]):
                                newfileid=elem[prop]*propspdicts[cat][prop][3][si]+propspdicts[cat][prop][2][si]
                                if not csprites.get(spfile,[0,-99])[1]>newfileid: #vanilla references not added
                                    getmallrefs.append(dict(reftype="propid",filebackref=[],ptype=csprites[spfile][3],cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=spfile,refid=[newfileid+x for x in range(propspdicts[cat][prop][1][si])],reftyp="spritesheet",modfile=mfile))
                                #['tactical2', 'tactical1', 'geo', 'base', 'research']

                            if cat=="items" and prop=="turretType":
                                tmparmors=[x.get("armor","") for x in orig["units"]+mod.get("units",[]) if x.get("type","")==elem.get("type","---")]
                                if tmparmors:
                                    tmparmorfiles=[x.get("spriteSheet","nosheet") for x in orig["armors"]+mod.get("armors",[]) if x.get("type","")==tmparmors[0]]
                                    if tmparmorfiles:
                                        getmallrefs.append(dict(reftype="turretid",filebackref=[],ptype="tactical1",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=tmparmorfiles[0],refid=[elem[prop]*8+64+x for x in range(8)],reftyp="spritesheet",modfile=mfile))

                    if cat=="armors" and prop=="spriteSheet":
                        if not elem[prop] in [x.get(prop,"") for x in orig[cat]]:#vanilla references not added
                            tmpspace=armorspace[elem.get("drawingRoutine",0)] if isinstance(armorspace[elem.get("drawingRoutine",0)],int) else armorspace[elem.get("drawingRoutine",0)](elem)
                            tmpstart=armorstart[elem.get("drawingRoutine",0)] if isinstance(armorstart[elem.get("drawingRoutine",0)],int) else armorstart[elem.get("drawingRoutine",0)](elem)
                            getmallrefs.append(dict(reftype="armor",filebackref=[],ptype="tactical1",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=elem[prop],refid=[tmpstart+x for x in range(tmpspace)],reftyp="spritesheet",modfile=mfile))
                    if cat=="armors" and prop=="spriteInv":
                        if not elem[prop] in [x.get(prop,"") for x in orig[cat]]:#vanilla references not added
                            getmallrefs.append(dict(reftype="armorinv",filebackref=[],ptype="tactical2",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=elem[prop]+(".SPK" if elem.get("storeItem","") else ""),refid=[0],reftyp="sprite",modfile=mfile))
                            if len(elem.get("storeItem",""))>0:
                                for g in ["M","F"]:
                                    for t in range(4):
                                        getmallrefs.append(dict(reftype="armorinvauto",filebackref=[],ptype="tactical2",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=elem[prop]+g+str(t)+".SPK",refid=[0],reftyp="sprite",modfile=mfile))
                    for si in  singleimages:
                        if not cat==si[0]:continue
                        if prop==si[1]:
                            getmallrefs.append(dict(reftype="image",filebackref=[],ptype=si[2],cat=cat,lid=elem[unlist[cat]],prop=prop,propid=0,refelem=elem[prop],refid=[0],reftyp="sprite",modfile=mfile))
    mod["MCPdata"]["getmallrefs"]=getmallrefs


    return mod,errors



def checkref(mod,errors,mfile):
    alist={}
    for x in mod["MCPdata"]["getmallrefs"]:
        if x.get("reftype","edgf")=="armorinv":
            alist[x["refelem"]]=alist.get(x["refelem"],[0,[]])
            alist[x["refelem"]][0]=len(x.get("filebackref"))
        elif x.get("reftype","edgf")=="armorinvauto":
            invref=x["refelem"][0:-6]+".SPK"
            if len(x.get("filebackref"))==1:
                alist[invref]=alist.get(invref,[0,[]])
                alist[invref][1].append(x["refelem"])
        elif len(x.get("filebackref"))==0:
            errors.append(("no connected file entry found for ruleset-referenced",x,mfile))

###  ("single image referenced without singleImage tag in file entry",(25,"a single image is referenced but has no singleImage:True entry in corresponding files section")),

##        if x["reftype"] in ["image","armorinv","armorinvauto"]:
##            for felem in mod.get("extraSprites",[]):
##                if felem.get("type","")==x["refelem"]:
##                    if felem.get("singleImage",False):
##                        print ((felem.get("singleImage",False),felem.get("type",""),x["refelem"],mfile))

    for a in alist:
        testset=set([a[0:-4]+"MF"[x%2]+str(x//2)+".SPK" for x in range(8)])-set(alist[a][1])
        if len(alist[a][1])>0 and len(testset)>0 :
            errors.append(("no connected file entry found for ruleset-referenced","armor",a,list(testset),mfile))
        elif len(alist[a][1])==0 and alist[a][0]==0:
            errors.append(("no connected file entry found for ruleset-referenced","armor",a,mfile))
    for ref in mod["MCPdata"]["getmallrefs"]:
        for fref in ref["filebackref"]:
            if fref[0]!="extraSprites": continue
            if len(mod["MCPdata"]["fdata"][fref])>0:
                fimg=mod["MCPdata"]["fdata"][fref][0]
                t=palettes[ref["ptype"]][0]
                f=palettes[ref["ptype"]][1]
                if fimg.palette:
                    if len(fimg.palette.palette)==768:
                        ipal=[[fimg.palette.palette[3*i+g] for g in range(3)] for i in range(256)]
                        #if not refdata["refid"] in filedata.get("fids",[]): print ((refdata,filedata))
                        if not ipal[t:f]==palettes[ref["ptype"]][2][t:f]:
                            if ref["ptype"]=="tactical1" and ipal[t:f-16]==palettes[ref["ptype"]][2][t:f-16]:
                                errors.append(("palette could use more colours",ref["cat"],ref["lid"],ref["prop"],ref["refelem"],ref["ptype"],fref,mfile))
                            else:
                                errors.append(("palette not correct",ref["cat"],ref["lid"],ref["prop"],ref["refelem"],ref["ptype"],fref,mfile))

            if len(ref["refid"])>len(mod["MCPdata"]["fdata"][fref]):
                errors.append(("references spritesheet does misses images",fref,[ref[z] for z in ["cat","lid","prop"]],len(ref["refid"]),len(mod["MCPdata"]["fdata"][fref]),mfile))
            if len(ref["refid"])<len(mod["MCPdata"]["fdata"][fref]):
                errors.append(("a sprite sheet is bigger than needed",fref,[ref[z] for z in ["cat","lid","prop"]],len(ref["refid"]),len(mod["MCPdata"]["fdata"][fref]),mfile))
    return errors



def checkmodlogic(mod,orig,errors,mfile):
    itemlist=[x.get("type","no type defined") for x in orig.get("items",[])+mod.get("items",[]) if isinstance(x,dict)]
    reselist=[x.get("name","no name defined") for x in orig.get("research",[])+mod.get("research",[])if isinstance(x,dict)]
#    corpselist=sum([x.get("corpseBattle",[]) for x in orig.get("armors",[])+mod.get("armors",[]) if isinstance(x,dict)]+[[x.get("corpseGeo",[])] for x in orig.get("armors",[])+mod.get("armors",[]) if isinstance(x,dict) and isinstance(x.get("corpseGeo",[]),str)])
    corpselist=sum([x.get("corpseBattle",[]) for x in orig.get("armors",[])+mod.get("armors",[]) if isinstance(x,dict)],[x.get("corpseGeo",[]) for x in orig.get("armors",[])+mod.get("armors",[]) if isinstance(x,dict) and isinstance(x.get("corpseGeo",[]),str)])
    alienlist=sum([x.get("members",[]) for x in orig.get("alienRaces",[])+mod.get("alienRaces",[]) if isinstance(x,dict)],[])
    alienarmor=[x.get("armor") for x in orig.get("units",[])+mod.get("units",[]) if isinstance(x,dict) and "armor" in x]
    recoveritems=[x.get("type","no type defined") for x in orig.get("items",[])+mod.get("items",[]) if isinstance(x,dict) and x.get("recover",True)]
    testlistorder=dict(
        items=[x.get("type","no type defined") for x in orig.get("items",[])],
        research=[x.get("name","no name defined") for x in orig.get("research",[])],
        manufacture=[x.get("name","no name defined") for x in orig.get("manufacture",[])],
        ufopaedia=[x.get("id","no name defined") for x in orig.get("ufopaedia",[])]
    )
    ressearch=dict(facilities=[["requires"]],crafts=[["requires"]],items=[["requires"]],research=[["dependencies"],["unlocks"],["requires"],"lookup",["getOneFree"]],manufacture=[["requires"]],ufopaedia=[["requires"]])
    itemsearch=dict(craftWeapons=["clip","launcher"],crafts=["refuelItem"],items=[["compatibleAmmo"]],armors=[["corpseBattle"],"corpseGeo"])
    for cat in mod:
        if checkmodtrivial(mod[cat],cat,0,mfile,[])[0]:
            if cat in unlist:
                for elem in mod[cat]:
                    missedrese=[]
                    misseditem=[]
                    logicprob=[]
                    if checkmodtrivial(elem,cat,1,mfile,[])[0]:
                        if cat in testlistorder:
                           if not elem[unlist[cat]] in testlistorder[cat] and not "listOrder" in elem and (cat!="items" or elem.get("recover",True)) and (cat!="research" or elem.get("cost",0)>0)and (cat!="ufopaedia" or elem.get("section","NOSECTION")!="STR_NOT_AVAILABLE"):
                               errors.append(("no listorder for new objects",cat,elem[unlist[cat]],mfile))
                        for prop in ressearch.get(cat,[]):
                            if isinstance(prop,list):
                                if prop[0] in elem:
                                    if isinstance(elem[prop[0]],list):
                                        for reselem in elem[prop[0]]:
                                            if not reselem in reselist:
                                                missedrese.append((prop[0],reselem))
                                    else:
                                        errors.append(("is no list",cat,elem[unlist[cat]],prop,mfile))

                            else:
                                if prop in elem:
                                    if not elem[prop] in reselist:
                                        missedrese.append((prop,elem[prop]))
                        if cat=="armors" and elem["type"] in alienarmor:
                            if "corpseGeo" in elem:
                                if isinstance(elem.get("corpseGeo",""),str):
                                    if not elem["corpseGeo"] in recoveritems:
                                        logicprob.append(("corpseGeo not in itemlist/ or recover: False",elem["corpseGeo"],elem["type"]))
                                else:
                                    errors.append(("unknown/strange type in rul file",cat,elem[unlist[cat]],"corpseGeo",mfile))
                            else:
                                if isinstance(elem.get("corpseBattle",[]),list):
                                    for tmpcorpse in elem.get("corpseBattle",[]):
                                        if not tmpcorpse in recoveritems:
                                            logicprob.append(("corpseBattle not in itemlist/ or recover: False",tmpcorpse,elem["type"]))
                                else:
                                    errors.append(("is no list",cat,elem[unlist[cat]],prop,mfile))

                        if cat=="items":
                            if elem["type"] in  alienlist:
                              if not elem.get("liveAlien",False):
                                    logicprob.append(("alien cant be recovered/no liveAlien: True",elem["type"]))
                              if not elem.get("recover",False):
                                    logicprob.append(("alien cant be recovered/no recover: True",elem["type"]))
                              if not elem["type"] in reselist:
                                    logicprob.append(("alien cant be recovered/no research object",elem["type"]))
                            if elem["type"] in corpselist:
                                if elem.get("battleType",-1)!=11:
                                    logicprob.append(("wrong battletype for corpse",elem["type"],elem.get("type","no type for corpse")))
                                if elem.get("recover",False) and not elem.get("recoveryPoints",0)>0:
                                    logicprob.append(("recoverable corpse need recoverypoints",elem["type"],elem.get("type","no type for corpse")))
                                if elem.get("recover",False) and "name" in elem and not elem["name"] in corpselist:
                                    logicprob.append(("corpse-name is no item",elem["type"],elem.get("name","no item for corpse")))
                        if cat=="research" and elem.get("needItem",False) and not elem.get("name","no name for researchobject") in itemlist:
                            misseditem.append(("needItem->Item",elem.get("name","no name for researchobject")))
                        if cat=="manufacture":
                            for x in elem.get("producedItems",[elem.get("name","no name for manufactureobject")]):
                                if not x in itemlist:
                                    misseditem.append(("producedItems",x))
                            for x in elem.get("requiredItems",[]):
                                if not x in itemlist:
                                    misseditem.append(("requiredItems",x))
                        if cat=="alienDeployments":
                            testelem=[]
                            for d in elem.get("data",[]):
                                for iset in d.get("itemSets",[]):
                                    if isinstance(iset,list):
                                        for weapon in iset:
                                            testelem.append(weapon)
                            for w in set(testelem):
                                if not w in itemlist:
                                    misseditem.append(("itemSets",w))
                        for prop in itemsearch.get(cat,[]):
                            if isinstance(prop,list):
                                if prop[0] in elem:
                                    for iteelem in elem[prop[0]]:
                                        if not iteelem in itemlist:
                                            misseditem.append((prop[0],iteelem))
                            else:
                                if prop in elem:
                                    if not elem[prop] in itemlist:
                                        misseditem.append((prop,elem[prop]))
                    if missedrese: errors.append(("missing research referenced",cat,elem[unlist[cat]],missedrese,mfile))
                    if misseditem: errors.append(("missing item referenced",cat,elem[unlist[cat]],misseditem,mfile))
                    if logicprob:  errors.append(("logicproblem",cat,elem[unlist[cat]],logicprob,mfile))
            elif cat=="startingBase" and cat in mod and isinstance(mod[cat],dict):
                missedrese=[]
                misseditem=[]
                for i in mod[cat].get("items",[]):
                    if not i in itemlist: misseditem.append(("items",i))
                for c in mod[cat].get("crafts",{}):
                    for i in c.get("items",[]):
                        if not i in itemlist: misseditem.append(("crafts->items",i))
                    #for i in c.get("weapons",[]): #weapons != items
                    #    if not i.get("type","no weapon type") in itemlist: misseditem.append(("crafts->weapons",i.get("type","no weapon type")))
                if missedrese: errors.append(("missing research referenced",cat,missedrese,mfile))
                if misseditem: errors.append(("missing item referenced",cat,misseditem,mfile))

    return errors



##if web=="noweb":
if 1==1:
    class NumList(list):
        pass

    def numlist_rep(self, data):
        return self.represent_sequence( u'tag:yaml.org,2002:seq', data, flow_style=True )


    def represent_dict(self, data):
        order={';b;ufopaedia;;': ['id', 'type_id', 'section', 'image_id', 'rect_stats', 'rect_text', 'text', 'requires', 'weapon', 'text_width'], ';b;research;;': ['name', 'cost', 'points', 'dependencies', 'needItem', 'unlocks', 'requires', 'lookup', 'getOneFree'], ';b;soldiers;;': ['type', 'minStats', 'maxStats', 'statCaps', 'armor', 'standHeight', 'kneelHeight', 'genderRatio'], ';b;soldiers;;maxStats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienMissions;;': ['type', 'points', 'raceWeights', 'waves'], ';b;ufoTrajectories;;': ['id', 'groundTimer', 'waypoints'], ';b;regions;;': ['type', 'cost', 'areas', 'cities', 'regionWeight', 'missionWeights', 'missionZones', 'missionRegion'], ';b;ufos;;battlescapeTerrainData;mapBlocks;;': ['name', 'width', 'length'], ';b;manufacture;;': ['name', 'category', 'requires', 'space', 'time', 'cost', 'requiredItems'], ';b;ufopaedia;;rect_stats;': ['x', 'y', 'width', 'height'], ';b;startingBase;crafts;;weapons;;': ['type', 'ammo'], ';b;ufos;;': ['type', 'size', 'sprite', 'damageMax', 'speedMax', 'accel', 'power', 'range', 'score', 'reload', 'breakOffTime', 'battlescapeTerrainData'], ';b;ufopaedia;;rect_text;': ['x', 'y', 'width', 'height'], ';b;MCDPatches;;data;;': ['MCDIndex', 'bigWall', 'LOFTS', 'TUSlide', 'terrainHeight', 'TUWalk', 'TUFly', 'deathTile', 'armor', 'HEBlock', 'flammability', 'fuel', 'noFloor'], ';b;terrains;;mapBlocks;;': ['name', 'width', 'length', 'type', 'subType', 'maxCount', 'frequency'], ';b;extraStrings;;': ['type', 'strings'], ';b;crafts;;battlescapeTerrainData;mapBlocks;;': ['name', 'width', 'length'], ';b;armors;;': ['type', 'spriteSheet', 'spriteInv', 'storeItem', 'corpseBattle', 'frontArmor', 'sideArmor', 'rearArmor', 'underArmor', 'damageModifier', 'loftempsSet', 'movementType', 'drawingRoutine', 'corpseGeo', 'size'], ';b;crafts;;battlescapeTerrainData;': ['name', 'mapDataSets', 'mapBlocks'], ';b;startingBase;facilities;;': ['type', 'x', 'y'], ';b;regions;;cities;;': ['name', 'lon', 'lat'], ';b;startingBase;crafts;;': ['type', 'id', 'fuel', 'damage', 'items', 'status', 'weapons'], ';b;startingBase;': ['facilities', 'randomSoldiers', 'crafts', 'items', 'scientists', 'engineers'], ';b;units;;': ['type', 'race', 'rank', 'armor', 'stats', 'standHeight', 'kneelHeight', 'value', 'deathSound', 'moveSound', 'energyRecovery', 'floatHeight', 'intelligence', 'aggression', 'specab', 'livingWeapon', 'aggroSound', 'spawnUnit'], ';b;crafts;;': ['type', 'sprite', 'fuelMax', 'damageMax', 'speedMax', 'accel', 'soldiers', 'vehicles', 'costBuy', 'costRent', 'refuelRate', 'transferTime', 'score', 'battlescapeTerrainData', 'weapons', 'requires', 'refuelItem', 'deployment', 'spacecraft'], ';b;alienRaces;;': ['id', 'members', 'retaliation'], ';b;invs;;': ['id', 'x', 'y', 'type', 'costs', 'slots'], ';b;items;;': ['type', 'name', 'bigSprite', 'floorSprite', 'handSprite', 'bulletSprite', 'size', 'costBuy', 'costSell', 'transferTime', 'clipSize', 'weight', 'fireSound', 'compatibleAmmo', 'accuracySnap', 'accuracyAimed', 'tuSnap', 'tuAimed', 'battleType', 'fixedWeapon', 'invWidth', 'invHeight', 'turretType', 'hitSound', 'hitAnimation', 'power', 'damageType', 'waypoint', 'blastRadius', 'armor', 'accuracyAuto', 'tuAuto', 'twoHanded', 'tuUse', 'painKiller', 'heal', 'stimulant', 'woundRecovery', 'healthRecovery', 'stunRecovery', 'energyRecovery', 'flatRate', 'requires', 'meleeSound', 'accuracyMelee', 'tuMelee', 'skillApplied', 'recover', 'recoveryPoints', 'strengthApplied', 'zombieUnit', 'arcingShot', 'liveAlien'], ';b;craftWeapons;;': ['type', 'sprite', 'sound', 'damage', 'range', 'accuracy', 'reloadCautious', 'reloadStandard', 'reloadAggressive', 'ammoMax', 'launcher', 'clip', 'projectileType', 'projectileSpeed', 'rearmRate'], ';b;startingTime;': ['second', 'minute', 'hour', 'weekday', 'day', 'month', 'year'], ';b;ufos;;battlescapeTerrainData;': ['name', 'mapDataSets', 'mapBlocks'], ';b;units;;stats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;extraSprites;;': ['type', 'files', 'width', 'height', 'subX', 'subY', 'singleImage'], ';b;facilities;;': ['type', 'spriteShape', 'spriteFacility', 'lift', 'buildCost', 'buildTime', 'monthlyCost', 'mapName', 'personnel', 'labs', 'workshops', 'radarRange', 'radarChance', 'defense', 'hitRatio', 'fireSound', 'hitSound', 'storage', 'aliens', 'requires', 'grav', 'mind', 'psiLabs', 'hyper', 'size', 'crafts'], ';b;MCDPatches;;': ['type', 'data'], ';b;extraSounds;;': ['type', 'files'], ';b;alienDeployments;;data;;': ['alienRank', 'lowQty', 'highQty', 'dQty', 'percentageOutsideUfo', 'itemSets'], ';b;terrains;;': ['name', 'mapDataSets', 'textures', 'largeBlockLimit', 'hemisphere', 'civilianTypes', 'roadTypeOdds', 'mapBlocks'], ';b;soldiers;;minStats;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienMissions;;waves;;': ['ufo', 'count', 'trajectory', 'timer'], ';b;': ['countries', 'regions', 'facilities', 'crafts', 'craftWeapons', 'items', 'ufos', 'invs', 'terrains', 'armors', 'soldiers', 'units', 'alienRaces', 'alienDeployments', 'research', 'manufacture', 'ufopaedia', 'startingBase', 'startingTime', 'costSoldier', 'costEngineer', 'costScientist', 'timePersonnel', 'initialFunding', 'ufoTrajectories', 'alienMissions', 'alienItemLevels', 'MCDPatches', 'extraSprites', 'extraSounds', 'extraStrings'], ';b;countries;;': ['type', 'fundingBase', 'fundingCap', 'labelLon', 'labelLat', 'areas'], ';b;soldiers;;statCaps;': ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee'], ';b;alienDeployments;;': ['type', 'data', 'width', 'length', 'height', 'civilians', 'terrains', 'shade', 'nextStage']}
        if "PREPoutput" in data and data["PREPoutput"] in order:
            newitems=[]
            otheritems=[x for x in data]
            for o in order[data["PREPoutput"]]:
                if o in data:
                    newitems.append((o,data[o]))
                    otheritems.remove(o)
            otheritems=sorted(otheritems)
            for o in otheritems:
                if o not in ["MCPdata","PREPoutput"]:
                    newitems.append((o,data[o]))
        else:
            items = [x for x in data.items()if x[0] not in ["MCPdata","PREPoutput"]]
            newitems=sorted(items,key=lambda x:x[0])
        return self.represent_mapping(u'tag:yaml.org,2002:map', newitems)


def prepareoutput(mod):
    if "MCPdata" in mod: del(mod["MCPdata"])
    t=yaml.dump(recprepareoutput(mod,";b;"),default_flow_style=False,allow_unicode=True,width=1000)
    t=re.sub("(\ *)- - (.*)","\\1-\n\\1  - \\2",t)
    ls=t.split("\n")
    nl=[]
    o={}

    for lastpos in range (18,-1,-2):#moves list accordingly
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

def recprepareoutput(elem,path):
    if isinstance(elem,dict):
        nonintfound=False
        for prop in elem:
            if not isinstance(prop,int): #elem[prop] for int does not work for some strrange reason
                elem[prop]=recprepareoutput(elem[prop],path+prop+";")
                nonintfound=True
        if nonintfound:elem["PREPoutput"]=path
    if isinstance(elem,list):
        testnrlist=True
        for l in elem:
            if not (isinstance(l,int) or isinstance(l,float)):testnrlist=False
        if testnrlist and not "damageModifier" in path:
            tmp=NumList()
            for x in elem:
                tmp.append(x)
            elem=tmp
        for li,l in enumerate(elem):
            elem[li]=recprepareoutput(elem[li],path+";")
    return elem




















##### make order txt, edit txt, read txt -> order dict
##
##with open("orig/Xcom1Ruleset.rul","r") as fh:
##    plines=fh.readlines()
##    plines=[re.sub(r':.*', '', l).replace("-"," ").replace("\n","") for l in plines if ":" in l and l.strip()[0]not in ["#"]]
##    #plines=[l for l in plines if ":" in l]
##    lines=[]
##    #for l in plines:
##    #    if not l.replace("\n","") in lines:
##    #        lines.append(l.replace("\n",""))
##    for l in plines:
##        lines.append(l.replace("\n",""))
##    print(len(lines))
##    lnr=dict([(x,[])for x in range (50,-1,-1)])
##    lastdict=dict([(x-20,"") for x in range(50)])
##    lastdict[-2]="b"
##
##
##    for l in lines:
##        found=False
##        for x in range (50,-1,-1):
##            testspace=True and not found
##            for y in range (x):
##                testspace=testspace and l[y]==" "
##            if testspace:
##                tmp=l.strip()
##                for i in range(1,20):
##                    tmp=lastdict[x-i]+";"+tmp
##                lnr[x].append(str(x)+";"+tmp)
##                found=True
##                lastdict[x]=l.strip()
##                continue
##    orderme=["type","id","name"]
##    for ln in lnr:
##        for l in lnr[ln]:
##            if not l in orderme:
##                orderme.append(l)
##    for l in orderme:
##        print (l)
##
##
##
##
##
##txt=""";;;;;;;;;;;;;;;;;;b;;countries
##;;;;;;;;;;;;;;;;;;b;;regions
##;;;;;;;;;;;;;;;;;;b;;facilities
##;;;;;;;;;;;;;;;;;;b;;crafts
##;;;;;;;;;;;;;;;;;;b;;craftWeapons
##;;;;;;;;;;;;;;;;;;b;;items
##;;;;;;;;;;;;;;;;;;b;;ufos
##;;;;;;;;;;;;;;;;;;b;;invs
##;;;;;;;;;;;;;;;;;;b;;terrains
##;;;;;;;;;;;;;;;;;;b;;armors
##;;;;;;;;;;;;;;;;;;b;;soldiers
##;;;;;;;;;;;;;;;;;;b;;units
##;;;;;;;;;;;;;;;;;;b;;alienRaces
##;;;;;;;;;;;;;;;;;;b;;alienDeployments
##;;;;;;;;;;;;;;;;;;b;;research
##;;;;;;;;;;;;;;;;;;b;;manufacture
##;;;;;;;;;;;;;;;;;;b;;ufopaedia
##;;;;;;;;;;;;;;;;;;b;;startingBase
##;;;;;;;;;;;;;;;;;;b;;startingTime
##;;;;;;;;;;;;;;;;;;b;;costSoldier
##;;;;;;;;;;;;;;;;;;b;;costEngineer
##;;;;;;;;;;;;;;;;;;b;;costScientist
##;;;;;;;;;;;;;;;;;;b;;timePersonnel
##;;;;;;;;;;;;;;;;;;b;;initialFunding
##;;;;;;;;;;;;;;;;;;b;;ufoTrajectories
##;;;;;;;;;;;;;;;;;;b;;alienMissions
##;;;;;;;;;;;;;;;;;;b;;alienItemLevels
##;;;;;;;;;;;;;;;;;;b;;MCDPatches
##;;;;;;;;;;;;;;;;;;b;;extraSprites
##;;;;;;;;;;;;;;;;;;b;;extraSounds
##;;;;;;;;;;;;;;;;;;b;;extraStrings
##
##;;;;;;;;;;;;;;;;b;;startingBase;;facilities
##;;;;;;;;;;;;;;;;b;;startingBase;;randomSoldiers
##;;;;;;;;;;;;;;;;b;;startingBase;;crafts
##;;;;;;;;;;;;;;;;b;;startingBase;;items
##;;;;;;;;;;;;;;;;b;;startingBase;;scientists
##;;;;;;;;;;;;;;;;b;;startingBase;;engineers
##
##;;;;;;;;;;;;;;;;b;;startingTime;;second
##;;;;;;;;;;;;;;;;b;;startingTime;;minute
##;;;;;;;;;;;;;;;;b;;startingTime;;hour
##;;;;;;;;;;;;;;;;b;;startingTime;;weekday
##;;;;;;;;;;;;;;;;b;;startingTime;;day
##;;;;;;;;;;;;;;;;b;;startingTime;;month
##;;;;;;;;;;;;;;;;b;;startingTime;;year
##
##;;;;;;;;;;;;;;b;;countries;;;;type
##;;;;;;;;;;;;;;b;;countries;;;;fundingBase
##;;;;;;;;;;;;;;b;;countries;;;;fundingCap
##;;;;;;;;;;;;;;b;;countries;;;;labelLon
##;;;;;;;;;;;;;;b;;countries;;;;labelLat
##;;;;;;;;;;;;;;b;;countries;;;;areas
##
##;;;;;;;;;;;;;;b;;regions;;;;type
##;;;;;;;;;;;;;;b;;regions;;;;cost
##;;;;;;;;;;;;;;b;;regions;;;;areas
##;;;;;;;;;;;;;;b;;regions;;;;cities
##;;;;;;;;;;;;;;b;;regions;;;;regionWeight
##;;;;;;;;;;;;;;b;;regions;;;;missionWeights
##;;;;;;;;;;;;;;b;;regions;;;;missionZones
##;;;;;;;;;;;;;;b;;regions;;;;missionRegion
##
##;;;;;;;;;;;;;;b;;facilities;;;;type
##;;;;;;;;;;;;;;b;;facilities;;;;spriteShape
##;;;;;;;;;;;;;;b;;facilities;;;;spriteFacility
##;;;;;;;;;;;;;;b;;facilities;;;;lift
##;;;;;;;;;;;;;;b;;facilities;;;;buildCost
##;;;;;;;;;;;;;;b;;facilities;;;;buildTime
##;;;;;;;;;;;;;;b;;facilities;;;;monthlyCost
##;;;;;;;;;;;;;;b;;facilities;;;;mapName
##;;;;;;;;;;;;;;b;;facilities;;;;personnel
##;;;;;;;;;;;;;;b;;facilities;;;;labs
##;;;;;;;;;;;;;;b;;facilities;;;;workshops
##;;;;;;;;;;;;;;b;;facilities;;;;radarRange
##;;;;;;;;;;;;;;b;;facilities;;;;radarChance
##;;;;;;;;;;;;;;b;;facilities;;;;defense
##;;;;;;;;;;;;;;b;;facilities;;;;hitRatio
##;;;;;;;;;;;;;;b;;facilities;;;;fireSound
##;;;;;;;;;;;;;;b;;facilities;;;;hitSound
##;;;;;;;;;;;;;;b;;facilities;;;;storage
##;;;;;;;;;;;;;;b;;facilities;;;;aliens
##;;;;;;;;;;;;;;b;;facilities;;;;requires
##;;;;;;;;;;;;;;b;;facilities;;;;grav
##;;;;;;;;;;;;;;b;;facilities;;;;mind
##;;;;;;;;;;;;;;b;;facilities;;;;psiLabs
##;;;;;;;;;;;;;;b;;facilities;;;;hyper
##;;;;;;;;;;;;;;b;;facilities;;;;size
##;;;;;;;;;;;;;;b;;facilities;;;;crafts
##
##;;;;;;;;;;;;;;b;;crafts;;;;type
##;;;;;;;;;;;;;;b;;crafts;;;;sprite
##;;;;;;;;;;;;;;b;;crafts;;;;fuelMax
##;;;;;;;;;;;;;;b;;crafts;;;;damageMax
##;;;;;;;;;;;;;;b;;crafts;;;;speedMax
##;;;;;;;;;;;;;;b;;crafts;;;;accel
##;;;;;;;;;;;;;;b;;crafts;;;;soldiers
##;;;;;;;;;;;;;;b;;crafts;;;;vehicles
##;;;;;;;;;;;;;;b;;crafts;;;;costBuy
##;;;;;;;;;;;;;;b;;crafts;;;;costRent
##;;;;;;;;;;;;;;b;;crafts;;;;refuelRate
##;;;;;;;;;;;;;;b;;crafts;;;;transferTime
##;;;;;;;;;;;;;;b;;crafts;;;;score
##;;;;;;;;;;;;;;b;;crafts;;;;battlescapeTerrainData
##;;;;;;;;;;;;;;b;;crafts;;;;weapons
##;;;;;;;;;;;;;;b;;crafts;;;;requires
##;;;;;;;;;;;;;;b;;crafts;;;;refuelItem
##;;;;;;;;;;;;;;b;;crafts;;;;deployment
##;;;;;;;;;;;;;;b;;crafts;;;;spacecraft
##
##;;;;;;;;;;;;;;b;;craftWeapons;;;;type
##;;;;;;;;;;;;;;b;;craftWeapons;;;;sprite
##;;;;;;;;;;;;;;b;;craftWeapons;;;;sound
##;;;;;;;;;;;;;;b;;craftWeapons;;;;damage
##;;;;;;;;;;;;;;b;;craftWeapons;;;;range
##;;;;;;;;;;;;;;b;;craftWeapons;;;;accuracy
##;;;;;;;;;;;;;;b;;craftWeapons;;;;reloadCautious
##;;;;;;;;;;;;;;b;;craftWeapons;;;;reloadStandard
##;;;;;;;;;;;;;;b;;craftWeapons;;;;reloadAggressive
##;;;;;;;;;;;;;;b;;craftWeapons;;;;ammoMax
##;;;;;;;;;;;;;;b;;craftWeapons;;;;launcher
##;;;;;;;;;;;;;;b;;craftWeapons;;;;clip
##;;;;;;;;;;;;;;b;;craftWeapons;;;;projectileType
##;;;;;;;;;;;;;;b;;craftWeapons;;;;projectileSpeed
##;;;;;;;;;;;;;;b;;craftWeapons;;;;rearmRate
##
##;;;;;;;;;;;;;;b;;items;;;;type
##;;;;;;;;;;;;;;b;;items;;;;name
##;;;;;;;;;;;;;;b;;items;;;;bigSprite
##;;;;;;;;;;;;;;b;;items;;;;floorSprite
##;;;;;;;;;;;;;;b;;items;;;;handSprite
##;;;;;;;;;;;;;;b;;items;;;;bulletSprite
##;;;;;;;;;;;;;;b;;items;;;;size
##;;;;;;;;;;;;;;b;;items;;;;costBuy
##;;;;;;;;;;;;;;b;;items;;;;costSell
##;;;;;;;;;;;;;;b;;items;;;;transferTime
##;;;;;;;;;;;;;;b;;items;;;;clipSize
##;;;;;;;;;;;;;;b;;items;;;;weight
##;;;;;;;;;;;;;;b;;items;;;;fireSound
##;;;;;;;;;;;;;;b;;items;;;;compatibleAmmo
##;;;;;;;;;;;;;;b;;items;;;;accuracySnap
##;;;;;;;;;;;;;;b;;items;;;;accuracyAimed
##;;;;;;;;;;;;;;b;;items;;;;tuSnap
##;;;;;;;;;;;;;;b;;items;;;;tuAimed
##;;;;;;;;;;;;;;b;;items;;;;battleType
##;;;;;;;;;;;;;;b;;items;;;;fixedWeapon
##;;;;;;;;;;;;;;b;;items;;;;invWidth
##;;;;;;;;;;;;;;b;;items;;;;invHeight
##;;;;;;;;;;;;;;b;;items;;;;turretType
##;;;;;;;;;;;;;;b;;items;;;;hitSound
##;;;;;;;;;;;;;;b;;items;;;;hitAnimation
##;;;;;;;;;;;;;;b;;items;;;;power
##;;;;;;;;;;;;;;b;;items;;;;damageType
##;;;;;;;;;;;;;;b;;items;;;;waypoint
##;;;;;;;;;;;;;;b;;items;;;;blastRadius
##;;;;;;;;;;;;;;b;;items;;;;armor
##;;;;;;;;;;;;;;b;;items;;;;accuracyAuto
##;;;;;;;;;;;;;;b;;items;;;;tuAuto
##;;;;;;;;;;;;;;b;;items;;;;twoHanded
##;;;;;;;;;;;;;;b;;items;;;;tuUse
##;;;;;;;;;;;;;;b;;items;;;;painKiller
##;;;;;;;;;;;;;;b;;items;;;;heal
##;;;;;;;;;;;;;;b;;items;;;;stimulant
##;;;;;;;;;;;;;;b;;items;;;;woundRecovery
##;;;;;;;;;;;;;;b;;items;;;;healthRecovery
##;;;;;;;;;;;;;;b;;items;;;;stunRecovery
##;;;;;;;;;;;;;;b;;items;;;;energyRecovery
##;;;;;;;;;;;;;;b;;items;;;;flatRate
##;;;;;;;;;;;;;;b;;items;;;;requires
##;;;;;;;;;;;;;;b;;items;;;;meleeSound
##;;;;;;;;;;;;;;b;;items;;;;accuracyMelee
##;;;;;;;;;;;;;;b;;items;;;;tuMelee
##;;;;;;;;;;;;;;b;;items;;;;skillApplied
##;;;;;;;;;;;;;;b;;items;;;;recover
##;;;;;;;;;;;;;;b;;items;;;;recoveryPoints
##;;;;;;;;;;;;;;b;;items;;;;strengthApplied
##;;;;;;;;;;;;;;b;;items;;;;zombieUnit
##;;;;;;;;;;;;;;b;;items;;;;arcingShot
##;;;;;;;;;;;;;;b;;items;;;;liveAlien
##
##;;;;;;;;;;;;;;b;;ufos;;;;type
##;;;;;;;;;;;;;;b;;ufos;;;;size
##;;;;;;;;;;;;;;b;;ufos;;;;sprite
##;;;;;;;;;;;;;;b;;ufos;;;;damageMax
##;;;;;;;;;;;;;;b;;ufos;;;;speedMax
##;;;;;;;;;;;;;;b;;ufos;;;;accel
##;;;;;;;;;;;;;;b;;ufos;;;;power
##;;;;;;;;;;;;;;b;;ufos;;;;range
##;;;;;;;;;;;;;;b;;ufos;;;;score
##;;;;;;;;;;;;;;b;;ufos;;;;reload
##;;;;;;;;;;;;;;b;;ufos;;;;breakOffTime
##;;;;;;;;;;;;;;b;;ufos;;;;battlescapeTerrainData
##
##;;;;;;;;;;;;;;b;;invs;;;;id
##;;;;;;;;;;;;;;b;;invs;;;;x
##;;;;;;;;;;;;;;b;;invs;;;;y
##;;;;;;;;;;;;;;b;;invs;;;;type
##;;;;;;;;;;;;;;b;;invs;;;;costs
##;;;;;;;;;;;;;;b;;invs;;;;slots
##
##;;;;;;;;;;;;;;b;;terrains;;;;name
##;;;;;;;;;;;;;;b;;terrains;;;;mapDataSets
##;;;;;;;;;;;;;;b;;terrains;;;;textures
##;;;;;;;;;;;;;;b;;terrains;;;;largeBlockLimit
##;;;;;;;;;;;;;;b;;terrains;;;;hemisphere
##;;;;;;;;;;;;;;b;;terrains;;;;civilianTypes
##;;;;;;;;;;;;;;b;;terrains;;;;roadTypeOdds
##;;;;;;;;;;;;;;b;;terrains;;;;mapBlocks
##
##;;;;;;;;;;;;;;b;;armors;;;;type
##;;;;;;;;;;;;;;b;;armors;;;;spriteSheet
##;;;;;;;;;;;;;;b;;armors;;;;spriteInv
##;;;;;;;;;;;;;;b;;armors;;;;storeItem
##;;;;;;;;;;;;;;b;;armors;;;;corpseBattle
##;;;;;;;;;;;;;;b;;armors;;;;frontArmor
##;;;;;;;;;;;;;;b;;armors;;;;sideArmor
##;;;;;;;;;;;;;;b;;armors;;;;rearArmor
##;;;;;;;;;;;;;;b;;armors;;;;underArmor
##;;;;;;;;;;;;;;b;;armors;;;;damageModifier
##;;;;;;;;;;;;;;b;;armors;;;;loftempsSet
##;;;;;;;;;;;;;;b;;armors;;;;movementType
##;;;;;;;;;;;;;;b;;armors;;;;drawingRoutine
##;;;;;;;;;;;;;;b;;armors;;;;corpseGeo
##;;;;;;;;;;;;;;b;;armors;;;;size
##
##;;;;;;;;;;;;;;b;;soldiers;;;;type
##;;;;;;;;;;;;;;b;;soldiers;;;;minStats
##;;;;;;;;;;;;;;b;;soldiers;;;;maxStats
##;;;;;;;;;;;;;;b;;soldiers;;;;statCaps
##;;;;;;;;;;;;;;b;;soldiers;;;;armor
##;;;;;;;;;;;;;;b;;soldiers;;;;standHeight
##;;;;;;;;;;;;;;b;;soldiers;;;;kneelHeight
##;;;;;;;;;;;;;;b;;soldiers;;;;genderRatio
##
##;;;;;;;;;;;;;;b;;units;;;;type
##;;;;;;;;;;;;;;b;;units;;;;race
##;;;;;;;;;;;;;;b;;units;;;;rank
##;;;;;;;;;;;;;;b;;units;;;;armor
##;;;;;;;;;;;;;;b;;units;;;;stats
##;;;;;;;;;;;;;;b;;units;;;;standHeight
##;;;;;;;;;;;;;;b;;units;;;;kneelHeight
##;;;;;;;;;;;;;;b;;units;;;;value
##;;;;;;;;;;;;;;b;;units;;;;deathSound
##;;;;;;;;;;;;;;b;;units;;;;moveSound
##;;;;;;;;;;;;;;b;;units;;;;energyRecovery
##;;;;;;;;;;;;;;b;;units;;;;floatHeight
##;;;;;;;;;;;;;;b;;units;;;;intelligence
##;;;;;;;;;;;;;;b;;units;;;;aggression
##;;;;;;;;;;;;;;b;;units;;;;specab
##;;;;;;;;;;;;;;b;;units;;;;livingWeapon
##;;;;;;;;;;;;;;b;;units;;;;aggroSound
##;;;;;;;;;;;;;;b;;units;;;;spawnUnit
##
##;;;;;;;;;;;;;;b;;alienRaces;;;;id
##;;;;;;;;;;;;;;b;;alienRaces;;;;members
##;;;;;;;;;;;;;;b;;alienRaces;;;;retaliation
##
##;;;;;;;;;;;;;;b;;alienDeployments;;;;type
##;;;;;;;;;;;;;;b;;alienDeployments;;;;data
##;;;;;;;;;;;;;;b;;alienDeployments;;;;width
##;;;;;;;;;;;;;;b;;alienDeployments;;;;length
##;;;;;;;;;;;;;;b;;alienDeployments;;;;height
##;;;;;;;;;;;;;;b;;alienDeployments;;;;civilians
##;;;;;;;;;;;;;;b;;alienDeployments;;;;terrains
##;;;;;;;;;;;;;;b;;alienDeployments;;;;shade
##;;;;;;;;;;;;;;b;;alienDeployments;;;;nextStage
##
##;;;;;;;;;;;;;;b;;research;;;;name
##;;;;;;;;;;;;;;b;;research;;;;cost
##;;;;;;;;;;;;;;b;;research;;;;points
##;;;;;;;;;;;;;;b;;research;;;;dependencies
##;;;;;;;;;;;;;;b;;research;;;;needItem
##;;;;;;;;;;;;;;b;;research;;;;unlocks
##;;;;;;;;;;;;;;b;;research;;;;requires
##;;;;;;;;;;;;;;b;;research;;;;lookup
##;;;;;;;;;;;;;;b;;research;;;;getOneFree
##
##;;;;;;;;;;;;;;b;;manufacture;;;;name
##;;;;;;;;;;;;;;b;;manufacture;;;;category
##;;;;;;;;;;;;;;b;;manufacture;;;;requires
##;;;;;;;;;;;;;;b;;manufacture;;;;space
##;;;;;;;;;;;;;;b;;manufacture;;;;time
##;;;;;;;;;;;;;;b;;manufacture;;;;cost
##;;;;;;;;;;;;;;b;;manufacture;;;;requiredItems
##
##;;;;;;;;;;;;;;b;;ufopaedia;;;;id
##;;;;;;;;;;;;;;b;;ufopaedia;;;;type_id
##;;;;;;;;;;;;;;b;;ufopaedia;;;;section
##;;;;;;;;;;;;;;b;;ufopaedia;;;;image_id
##;;;;;;;;;;;;;;b;;ufopaedia;;;;rect_stats
##;;;;;;;;;;;;;;b;;ufopaedia;;;;rect_text
##;;;;;;;;;;;;;;b;;ufopaedia;;;;text
##;;;;;;;;;;;;;;b;;ufopaedia;;;;requires
##;;;;;;;;;;;;;;b;;ufopaedia;;;;weapon
##;;;;;;;;;;;;;;b;;ufopaedia;;;;text_width
##
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_AC_AP_AMMO
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_AUTO_CANNON
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_AVALANCHE_LAUNCHER
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_AVALANCHE_MISSILES
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_CANNON
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_CANNON_ROUNDS_X50
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_GRENADE
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_HC_AP_AMMO
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_HEAVY_CANNON
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_PISTOL
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_PISTOL_CLIP
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_RIFLE
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_RIFLE_CLIP
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_ROCKET_LAUNCHER
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_SMALL_ROCKET
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_SMOKE_GRENADE
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_STINGRAY_LAUNCHER
##// ;;;;;;;;;;;;;;b;;startingBase;;items;;STR_STINGRAY_MISSILES
##
##;;;;;;;;;;;;;;b;;ufoTrajectories;;;;id
##;;;;;;;;;;;;;;b;;ufoTrajectories;;;;groundTimer
##;;;;;;;;;;;;;;b;;ufoTrajectories;;;;waypoints
##
##;;;;;;;;;;;;;;b;;alienMissions;;;;type
##;;;;;;;;;;;;;;b;;alienMissions;;;;points
##;;;;;;;;;;;;;;b;;alienMissions;;;;raceWeights
##;;;;;;;;;;;;;;b;;alienMissions;;;;waves
##
##;;;;;;;;;;;;;;b;;MCDPatches;;;;type
##;;;;;;;;;;;;;;b;;MCDPatches;;;;data
##
##;;;;;;;;;;;;;;b;;extraSprites;;;;type
##;;;;;;;;;;;;;;b;;extraSprites;;;;files
##;;;;;;;;;;;;;;b;;extraSprites;;;;width
##;;;;;;;;;;;;;;b;;extraSprites;;;;height
##;;;;;;;;;;;;;;b;;extraSprites;;;;subX
##;;;;;;;;;;;;;;b;;extraSprites;;;;subY
##;;;;;;;;;;;;;;b;;extraSprites;;;;singleImage
##
##;;;;;;;;;;;;;;b;;extraSounds;;;;type
##;;;;;;;;;;;;;;b;;extraSounds;;;;files
##
##;;;;;;;;;;;;;;b;;extraStrings;;;;type
##;;;;;;;;;;;;;;b;;extraStrings;;;;strings
##
##// ;;;;;;;;;;;;b;;regions;;;;missionWeights;;STR_ALIEN_RESEARCH
##// ;;;;;;;;;;;;b;;regions;;;;missionWeights;;STR_ALIEN_HARVEST
##// ;;;;;;;;;;;;b;;regions;;;;missionWeights;;STR_ALIEN_ABDUCTION
##// ;;;;;;;;;;;;b;;regions;;;;missionWeights;;STR_ALIEN_INFILTRATION
##// ;;;;;;;;;;;;b;;regions;;;;missionWeights;;STR_ALIEN_BASE
##
##;;;;;;;;;;;;b;;crafts;;;;battlescapeTerrainData;;name
##;;;;;;;;;;;;b;;crafts;;;;battlescapeTerrainData;;mapDataSets
##;;;;;;;;;;;;b;;crafts;;;;battlescapeTerrainData;;mapBlocks
##
##;;;;;;;;;;;;b;;ufos;;;;battlescapeTerrainData;;name
##;;;;;;;;;;;;b;;ufos;;;;battlescapeTerrainData;;mapDataSets
##;;;;;;;;;;;;b;;ufos;;;;battlescapeTerrainData;;mapBlocks
##
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_BACK_PACK
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_BELT
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_LEFT_HAND
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_LEFT_LEG
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_LEFT_SHOULDER
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_RIGHT_HAND
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_RIGHT_LEG
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_RIGHT_SHOULDER
##// ;;;;;;;;;;;;b;;invs;;;;costs;;STR_GROUND
##
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;tu
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;stamina
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;health
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;bravery
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;reactions
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;firing
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;throwing
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;strength
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;psiStrength
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;psiSkill
##;;;;;;;;;;;;b;;soldiers;;;;minStats;;melee
##
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;tu
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;stamina
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;health
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;bravery
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;reactions
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;firing
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;throwing
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;strength
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;psiStrength
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;psiSkill
##;;;;;;;;;;;;b;;soldiers;;;;maxStats;;melee
##
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;tu
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;stamina
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;health
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;bravery
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;reactions
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;firing
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;throwing
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;strength
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;psiStrength
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;psiSkill
##;;;;;;;;;;;;b;;soldiers;;;;statCaps;;melee
##
##;;;;;;;;;;;;b;;units;;;;stats;;tu
##;;;;;;;;;;;;b;;units;;;;stats;;stamina
##;;;;;;;;;;;;b;;units;;;;stats;;health
##;;;;;;;;;;;;b;;units;;;;stats;;bravery
##;;;;;;;;;;;;b;;units;;;;stats;;reactions
##;;;;;;;;;;;;b;;units;;;;stats;;firing
##;;;;;;;;;;;;b;;units;;;;stats;;throwing
##;;;;;;;;;;;;b;;units;;;;stats;;strength
##;;;;;;;;;;;;b;;units;;;;stats;;psiStrength
##;;;;;;;;;;;;b;;units;;;;stats;;psiSkill
##;;;;;;;;;;;;b;;units;;;;stats;;melee
##
##// ;;;;;;;;;;;;b;;manufacture;;;;requiredItems;;STR_ALIEN_ALLOYS
##// ;;;;;;;;;;;;b;;manufacture;;;;requiredItems;;STR_ELERIUM_115
##// ;;;;;;;;;;;;b;;manufacture;;;;requiredItems;;STR_UFO_POWER_SOURCE
##// ;;;;;;;;;;;;b;;manufacture;;;;requiredItems;;STR_UFO_NAVIGATION
##
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_stats;;x
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_stats;;y
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_stats;;width
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_stats;;height
##
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_text;;x
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_text;;y
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_text;;width
##;;;;;;;;;;;;b;;ufopaedia;;;;rect_text;;height
##
##;;;;;;;;;;;;b;;startingBase;;facilities;;;;type
##;;;;;;;;;;;;b;;startingBase;;facilities;;;;x
##;;;;;;;;;;;;b;;startingBase;;facilities;;;;y
##
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;type
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;id
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;fuel
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;damage
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;items
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;status
##;;;;;;;;;;;;b;;startingBase;;crafts;;;;weapons
##
##// ;;;;;;;;;;;;b;;alienMissions;;year;;raceWeights;;0
##// ;;;;;;;;;;;;b;;alienMissions;;year;;raceWeights;;1
##// ;;;;;;;;;;;;b;;alienMissions;;year;;raceWeights;;3
##// ;;;;;;;;;;;;b;;alienMissions;;year;;raceWeights;;5
##// ;;;;;;;;;;;;b;;alienMissions;;year;;raceWeights;;7
##
##// ;;;;;;;;;;;;b;;extraSprites;;year;;files;;0
##// ;;;;;;;;;;;b;;extraSprites;;year;;files;;0;4
##
##;;;;;;;;;;b;;regions;;;;cities;;;;name
##;;;;;;;;;;b;;regions;;;;cities;;;;lon
##;;;;;;;;;;b;;regions;;;;cities;;;;lat
##
##// ;;;;;;;;;;b;;regions;;;;cities;;STR_ALIEN_BASE;;name
##// ;;;;;;;;;;b;;regions;;;;cities;;STR_ALIEN_BASE;;lon
##// ;;;;;;;;;;b;;regions;;;;cities;;STR_ALIEN_BASE;;lat
##
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;name
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;width
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;length
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;type
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;subType
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;maxCount
##;;;;;;;;;;b;;terrains;;;;mapBlocks;;;;frequency
##
##;;;;;;;;;;b;;alienDeployments;;;;data;;;;alienRank
##;;;;;;;;;;b;;alienDeployments;;;;data;;;;lowQty
##;;;;;;;;;;b;;alienDeployments;;;;data;;;;highQty
##;;;;;;;;;;b;;alienDeployments;;;;data;;;;dQty
##;;;;;;;;;;b;;alienDeployments;;;;data;;;;percentageOutsideUfo
##;;;;;;;;;;b;;alienDeployments;;;;data;;;;itemSets
##
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_GRENADE
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_HC_AP_AMMO
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_HC_HE_AMMO
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_HEAVY_CANNON
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_PISTOL
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_PISTOL_CLIP
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_RIFLE
##// ;;;;;;;;;;b;;startingBase;;crafts;;text;;items;;STR_RIFLE_CLIP
##
##;;;;;;;;;;b;;alienMissions;;;;waves;;;;ufo
##;;;;;;;;;;b;;alienMissions;;;;waves;;;;count
##;;;;;;;;;;b;;alienMissions;;;;waves;;;;trajectory
##;;;;;;;;;;b;;alienMissions;;;;waves;;;;timer
##
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;MCDIndex
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;bigWall
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;LOFTS
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;TUSlide
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;terrainHeight
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;TUWalk
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;TUFly
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;deathTile
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;armor
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;HEBlock
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;flammability
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;fuel
##;;;;;;;;;;b;;MCDPatches;;;;data;;;;noFloor
##
##;;;;;;;;b;;crafts;;;;battlescapeTerrainData;;mapBlocks;;;;name
##;;;;;;;;b;;crafts;;;;battlescapeTerrainData;;mapBlocks;;;;width
##;;;;;;;;b;;crafts;;;;battlescapeTerrainData;;mapBlocks;;;;length
##
##;;;;;;;;b;;ufos;;;;battlescapeTerrainData;;mapBlocks;;;;name
##;;;;;;;;b;;ufos;;;;battlescapeTerrainData;;mapBlocks;;;;width
##;;;;;;;;b;;ufos;;;;battlescapeTerrainData;;mapBlocks;;;;length
##
##;;;;;;;;b;;startingBase;;crafts;;;;weapons;;;;type
##;;;;;;;;b;;startingBase;;crafts;;;;weapons;;;;ammo
##
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;0;;STR_RIFLE_CLIP;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;0;;STR_RIFLE_CLIP;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;0;;STR_RIFLE_CLIP;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;1;;STR_RIFLE_CLIP;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;1;;STR_RIFLE_CLIP;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;1;;STR_RIFLE_CLIP;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;STR_RIFLE_CLIP;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;STR_RIFLE_CLIP;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;STR_RIFLE_CLIP;;STR_MUTON
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;STR_RIFLE_CLIP;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;STR_RIFLE_CLIP;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;STR_RIFLE_CLIP;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;STR_RIFLE_CLIP;;STR_MUTON
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;STR_RIFLE_CLIP;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;STR_RIFLE_CLIP;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;STR_RIFLE_CLIP;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;STR_RIFLE_CLIP;;STR_MUTON
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;STR_RIFLE_CLIP;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;0;;timer;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;0;;timer;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;0;;timer;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;1;;timer;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;1;;timer;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;timer;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;timer;;STR_MUTON
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;timer;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;timer;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;timer;;STR_MUTON
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;timer;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;timer;;STR_SECTOID
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;timer;;STR_MUTON
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;timer;;STR_FLOATER
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;1;;timer;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;3;;timer;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;timer;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;5;;timer;;STR_ETHEREAL
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;timer;;STR_SNAKEMAN
##// ;;;;;;;;b;;alienMissions;;year;;raceWeights;;7;;timer;;STR_ETHEREAL"""
##
##order={}
##
##for gi,g in enumerate(txt.split("\n\n")):
##    o=[]
##    foundline=False
##    for li,l in enumerate(g.split("\n")):
##        if l.startswith(";"):
##            o.append(l.split(";;")[-1])#]=dict(order=li,uniq=False)
##            foundline=True
##    #if foundline:order[tuple(l.split(";;")[0:-1])]=o
##    if foundline:order[";"+re.sub("^;*","",";".join(l.split(";;")[0:-1]))+";"]=o
##print (order)



def combinesprites(pathglob,nrcols,outfn):
    ifns=[fn for fn in glob.glob(pathglob) if fn.lower().endswith(".gif") or fn.lower().endswith(".png")]
    ifns.sort()
    if ifns:
        ifiles=[]
        pre=Image.open(ifns[0])
        out=Image.open(ifns[0])
        for x in range(pre.size[0]):
            for y in range(pre.size[1]):
                pre.putpixel((x,y),0)
                out.putpixel((x,y),0)
        for fn in ifns:
            ifiles.append(Image.open(fn))
            ifiles[-1].palette=pre.palette
        out=out.resize((pre.size[0]*nrcols,pre.size[1]*int(math.ceil(len(ifns)/nrcols))))
        addx=0
        addy=0
        for i,im in enumerate(ifiles):
            for x in range(pre.size[0]):
                for y in range(pre.size[1]):
                    out.putpixel((addx+x,addy+y),im.getpixel((x,y)))
            if addx+pre.size[0] < out.size[0]:
                addx+=pre.size[0]
            else:
                addx=0
                addy+=pre.size[1]
        out.save(outfn,optimize=False,transparency=0)


def getdsdict(uopt,cut):
##* Drawing routine for XCom soldiers in overalls, sectoids (routine 0),
##* mutons (routine 10),
##* aquanauts (routine 13),
##* aquatoids, calcinites, deep ones, gill men, lobster men, tasoths (routine 14).
##* Drawing routine for floaters. (1)
##* Drawing routine for XCom tanks. (2)
##* Drawing routine for cyberdiscs. (3)
##* Drawing routine for civilians, ethereals, zombies (routine 4),
##* Drawing routine for sectopods and reapers. (5)
##* Drawing routine for snakemen. (6)
##* Drawing routine for chryssalid. (7)
##* Drawing routine for silacoids. (8)
##* Drawing routine for celatids. (9)

##* tftd civilians, tftd zombies (routine 16), more tftd civilians (routine 17).
##*   Very easy: first 8 is standing positions, then 8 walking sequences of 8, finally death sequence of 3
##* Drawing routine for terror tanks. (11)
##* Drawing routine for hallucinoids (routine 12) and biodrones (routine 15).
##* Drawing routine for tentaculats. (18)
##* Drawing routine for triscenes. (19)
##* Drawing routine for xarquids. (20)

    #QUESTIONS:
    #19 is the cutimage wide enough is there a useful limit (cursorbox) ?
    turretoffsets =   [ (-2,-1), (-7,-3), (-5,-4), (0,-5), (5,-4), (7,-3), (2,-1), ( 0,-1) ]
    tftdturretoffsets=[(-3,-3), (-2,-5), (0,-4), (0,-2), (0,-4), (2,-5), (3,-3), (0,-3)]
    tftdturretoffsets=[(-3,3), (-2,-4), (0,0), (0,-1), (0,0), (2,-4), (3,3), (0,-2)]  # + coelacanth offset? worse for both?

    silacoidloop = [ 0, 1, 2, 3, 4, 3, 2, 1 ]
    standConvert = [ 3, 2, 1, 0, 7, 6, 5, 4 ] #array for converting stand frames for some tftd civilians

    dsdict={5:dict(animcount=4,blocks=[0,1,2,3],
            backspriting=[(x,x,[0,1,2,3],[x+y*8 for y in range(4)]) for x in range(8)]+[(i+4*8,d,[0,1,2,3],[4*8+a+d*16+y*4 for y in range(4)]) for i,(a,d) in enumerate(itertools.product(range(4),range(8)))],
            standing=dict(
                          spritein=[d+block*8 for block,d in itertools.product(range(4),range(8))],
                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product(range(4),range(8))],
                       ),
            walking=dict(spritein=[8*4+a+block*4+d*(4*4) for a,block,d in itertools.product(range(4),range(4),range(8))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for a,block,d in itertools.product(range(4),range(4),range(8))],
                       ),
            ),
            3:dict(blocks=[0,1,2,3],
            backspriting=[(x,0,[0,1,2,3],[x+y*8 for y in range(4)]) for x in range(8)]+[(8+x,1,[1,2,3],[32+x+y*8 for y in range(3)]) for x in range(8)],
            standing=dict(spritein=[d+block*8 for block,d in itertools.product(range(4),range(8))],
                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product(range(4),range(8))],
                       ),
            walking=dict(spritein=[8*4+a+block*8 for a,block,d in itertools.product(range(8),range(3),range(8))] + [d+block*8 for block,d in itertools.product(range(4),range(8))]*8,
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for a,block,d in itertools.product(range(8),[1,2,3],range(8))] + [((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for a,block,d in itertools.product(range(8),range(4),range(8))],
                       ),
            ),
            2:dict(blocks=[0,1,2,3],
            backspriting=[(i,i//8,[0,1,2,3],[(i//8)*32+i%8+x*8 for x in range(4)])if i<16 else ((i,2,[1,2,3],[104+(i-56)+x*8 for x in range(3)])if (5*8+16)<=i<(5*8+16+8) else (i,i//8+(1 if i<(5*8+16+8) else 0 ),[-1],[i+48+(16 if i>63 else 0)]))  for i in range(64+20*8)],
            standing=dict(spritein=[d+block*8 + (32 if uopt.get("fly",False) else 0)for block,d in itertools.product(range(4),range(8))] + ([d + 64 + 8*uopt.get("turretType",-1) for d in range(8)] if uopt.get("turretType",-1)>=0 else []),
                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product(range(4),range(8))] + ([((turretoffsets[d][0] if uopt.get("fly",False) else 0)+relpos[block][0],(turretoffsets[d][1] if uopt.get("fly",False) else 0)-4+d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product([3],range(8))] if uopt.get("turretType",-1)>=0 else []),
                       ),
            walking=dict(spritein=([104+a+block*8 for a,block,d in itertools.product(range(8),range(3),range(8))] if uopt.get("fly",False) else [])                                                                + [d+block*8 + (32 if uopt.get("fly",False) else 0)for block,a,d in itertools.product(range(4),range(8),range(8))]                              + ([a + 64 + 8*uopt.get("turretType",-1) for block,a,d in itertools.product([3],range(8),range(8))] if uopt.get("turretType",-1)>=0 else []),
                          spritepos=([((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for a,block,d in itertools.product(range(8),[1,2,3],range(8))] if uopt.get("fly",False) else []) + [ ((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product(range(4),range(8),range(8))] + ([((a+1)*(cut.size[0]+1)+(turretoffsets[d][0] if uopt.get("fly",False) else 0)+relpos[block][0],(turretoffsets[d][1] if uopt.get("fly",False) else 0)-4+d*(cut.size[1]+1)+relpos[block][1])  for block,a,d in itertools.product([3],range(8),range(8))] if uopt.get("turretType",-1)>=0 else []),
                       ),
            ),
            11:dict(blocks=[0,1,2,3],
                    backspriting=[(i,d,[0,1,2,3],[a+d*16+y*4 for y in range(4)]) for i,(a,d) in enumerate(itertools.product(range(4),range(16)))]+[(i+4*16,16+i//8,[-1],[i+4*4*16]) for i in range(8*25)],
                    standing=dict(spritein=[] if uopt.get("fly",False) else [a%4+block*4+d*16 + 0 for block,a,d in itertools.product(range(4),range(1),range(8))],
                          spritepos=[]if uopt.get("fly",False) else [ ((a)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product(range(4),range(1),range(8))]
                       ),
                    walking=dict(spritein=[(a%4)+block*4+d*16 + (128 if uopt.get("fly",False) else 0)for block,a,d in itertools.product(range(4),range(8),range(8))]                         + ([a + 256 + 8*uopt.get("turretType",-1) for block,a,d in itertools.product([3],range(8),range(8))] if uopt.get("turretType",-1)>=0 else []),
                          spritepos=[ ((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product(range(4),range(8),range(8))] + ([((a+1)*(cut.size[0]+1)+tftdturretoffsets[d][0] + relpos[block][0],tftdturretoffsets[d][1] - 16+d*(cut.size[1]+1)+relpos[block][1])  for block,a,d in itertools.product([3],range(8),range(8))] if uopt.get("turretType",-1)>=0 else []),
                       ),
            ),
            4:dict(
            standing=dict(
                          spritein=[d for block,d in itertools.product([3],range(8))],
                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product([3],range(8))],
                       ),
            walking=dict(spritein=[8+a+d*8 for block,a,d in itertools.product([3],range(8),range(8))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product([3],range(8),range(8))],
                       ),
            ),
            8:dict(directions=1,
            hit=dict(
                          spritein=[5],
                          spritepos=[(relpos[block][0],relpos[block][1]) for block,d in itertools.product([3],range(1))],
                       ),
            walking=dict(spritein=[silacoidloop[a] for block,a,d in itertools.product([3],range(8),range(1))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product([3],range(8),range(1))],
                       ),
            ),
            9:dict(directions=1,
##            standing=dict(
##                          spritein=[0],
##                          spritepos=[(relpos[block][0],relpos[block][1]) for block,d in itertools.product([3],range(1))],
##                       ),
            walking=dict(spritein=[a+d*8 for block,a,d in itertools.product([3],range(8),range(1))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product([3],range(8),range(1))],
                       ),
            ),
            18:dict(animcount=1,
            standing=dict(
                          spritein=[d for block,d in itertools.product([3],range(8))],
                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product([3],range(8))],
                       ),
            walking=dict(spritein=[8+d for block,a,d in itertools.product([3],range(1),range(8))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product([3],range(1),range(8))],
                       ),
            ),
            19:dict(animcount=4,blocks=[0,1,2,3],
            standing=dict(
                          spritein=[block*5+d*5*4 for block,d in itertools.product([0,1,2,3],range(8))],
                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product([0,1,2,3],range(8))],
                       ),
            walking=dict(spritein=[block*5+d*5*4+a+1 for block,a,d in itertools.product([0,1,2,3],range(4),range(8))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product([0,1,2,3],range(4),range(8))],
                       ),
            ),
            12:dict(blocks=[0,1,2,3],directions=1,
                    backspriting=[(x,0,[0,1,2,3],[x+y*8 for y in range(4)]) for x in range(8)],
##            standing=dict(
##                          spritein=,
##                          spritepos=[(relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,d in itertools.product([0,1,2,3],range(8))],
##                       ),
            walking=dict(spritein=[d+block*8 for block,d in itertools.product([0,1,2,3],range(8))],#[8+d for block,a,d in itertools.product([3],range(1),range(8))],
                          spritepos=[((a+1)*(cut.size[0]+1)+relpos[block][0],d*(cut.size[1]+1)+relpos[block][1]) for block,a,d in itertools.product([0,1,2,3],range(8),range(1))],
                       ),
            ),               }
    dsdict[16]=copy.deepcopy(dsdict[4])
    dsdict[16]["standing"]["spritein"]=[64+standConvert[d] for block,d in itertools.product([3],range(8))]
    dsdict[16]["walking"]["spritein"]=[a+d*8 for block,a,d in itertools.product([3],range(8),range(8))]
    dsdict[17]=copy.deepcopy(dsdict[16])
    dsdict[16]["standing"]["spritein"]=[64+d for block,d in itertools.product([3],range(8))]
    for key in ["walking","standing"]:dsdict[17][key]["spritein"]=[x+76 for x in dsdict[17][key]["spritein"]]
    dsdict[15]=copy.deepcopy(dsdict[9])
    dsdict[20]=copy.deepcopy(dsdict[5])
    del(dsdict[20]["standing"])
    dsdict[20]["walking"]["spritein"]=[x-8*4 for x in dsdict[20]["walking"]["spritein"]]
    dsdict[20]["backspriting"]=[(i,d,[0,1,2,3],[a+d*16+y*4 for y in range(4)]) for i,(a,d) in enumerate(itertools.product(range(4),range(8)))]
    dsdict[19]["backspriting"]=[(i,d,[0,1,2,3],[a+d*20+y*5 for y in range(4)]) for i,(a,d) in enumerate(itertools.product(range(5),range(8)))]

    for x in dsdict:
        dsdict[x]["animcount"]=dsdict[x].get("animcount",8)
        dsdict[x]["directions"]=dsdict[x].get("directions",8)
        dsdict[x]["blocks"]=dsdict[x].get("blocks",[3])
    return dsdict



def makeimages(dtype=0,spritepath="",baseimg="",rescomb="",drout=0,uopt={},colnr=8):
    """dtype=0 -> makes im list to animations
    dtype=1 -> makes im list to hwp tamplate
    dtype=2 -> hwp tamplate to hwp sprites
    """
    print ((spritepath))
    cut=Image.open(baseimg)
    ifns=[fn for fn in glob.glob(spritepath)]

    ifns.sort()
    ifiles=[]
    for fn in ifns:
        ifiles.append(Image.open(fn))

    new=Image.open(ifns[0])
    for x in range(new.size[0]):
        for y in range(new.size[1]):
            new.putpixel((x,y),0)
    dsdict=getdsdict(uopt,cut)
    animcount=dsdict[drout]["animcount"]
    directions=dsdict[drout]["directions"]
    blocks=dsdict[drout]["blocks"]
    if dtype==0: new=new.resize(((cut.size[0]+1)*(1+animcount),(cut.size[1]+1)*directions))
    if dtype in [1,2]:
        tmpw={}
        tmph={}
        tmppos={}
        tmpmember={}
        tmpblocks={}
        for bs in dsdict[drout]["backspriting"]:
            tmpw[bs[1]]=max(tmpw.get(bs[1],0),(65 if bs[2][0]>=0 else 33))
            tmph[bs[1]]=max(tmph.get(bs[1],0),(57 if bs[2][0]>=0 else 41))
            tmpmember[bs[1]]=tmpmember.get(bs[1],[])
            tmpmember[bs[1]].append(bs[0])
            tmpblocks[bs[1]]=tmpmember.get(bs[1],[])
            tmpblocks[bs[1]]=bs[2]+tmpblocks[bs[1]]
        rows=sorted(list(set([bs[1] for bs in dsdict[drout]["backspriting"]])))
        rows.reverse()
        for r in rows:
            tmppos[r]=sum([tmph[x] for x in range(r)])
        rows.reverse()

        pw=max([(len(tmpmember[r])*tmpw[r]) for r in rows])
        ph=sum([tmph[r] for r in rows])

        if dtype==2:
            tmpm=max(sum([bs[3] for bs in dsdict[drout]["backspriting"]],[]))
            pw=colnr*32
            ph=(1+math.ceil((tmpm+1)/colnr))*40

        new=new.resize((pw,ph))


    blockcolor=[168,184,176,192]
    jump=8*4
    spposdict={}

    count=0
    if dtype==0:
        for d in range(directions):
            for k in range(-1,animcount):
                addx=1*(cut.size[0]+1)+k*(cut.size[0]+1)
                addy=d*(cut.size[1]+1)
                for x in range(cut.size[0]):
                    for y in range(cut.size[1]):
                        c=cut.getpixel((x,y))
                        if k==-2 or not c in [bc for bi,bc in enumerate(blockcolor) if bi in blocks]:
                            new.putpixel((addx+x,addy+y),120)
                    new.putpixel((addx+x,addy+cut.size[1]),240)
                for y in range(cut.size[1]):
                    new.putpixel((addx+cut.size[0],addy+y),240)
    if dtype in [1,2]:
        for r in rows:
            for ci,mem in enumerate(tmpmember[r]):
                addx=ci*tmpw[r]
                addy=tmppos[r]
                if dtype==1:
                    for x in range(tmpw[r]):
                        new.putpixel((addx+x,addy+tmph[r]-1),240)
                    for y in range(tmph[r]):
                        new.putpixel((addx+tmpw[r]-1,addy+y),240)
                    if tmpw[r]==65 and dtype==1:
                        for x in range(cut.size[0]):
                            for y in range(cut.size[1]):
                                c=cut.getpixel((x,y))
                                if not c in [bc for bi,bc in enumerate(blockcolor) if bi in tmpblocks[r]]:
                                    new.putpixel((addx+x,addy+y),120)
                for bs in dsdict[drout]["backspriting"]:
                    if bs[3][0]>=len(ifiles) and dtype==1:continue

                    if bs[0]==mem:
#                        print ((bs))
                        for b in range(len(bs[3])):
#                            print ((b,bs))
                            if dtype==1:
                                im=ifiles[bs[3][b]]
                                for x in range(im.size[0]):
                                    for y in range(im.size[1]):
                                        c=im.getpixel((x,y))
                                        if c!=0:
                                                if bs[2][b]>=0:
                                                    new.putpixel((addx+x+relpos[bs[2][b]][0],addy+y+relpos[bs[2][b]][1]),c)
                                                else:
                                                    new.putpixel((addx+x,addy+y),c)
                            if dtype==2:
                                im=ifiles[0]
                                tmpw2=32
                                tmph2=40
                                if bs[2][b]>=0:tmpw2,tmph2=cut.size
                                nx=bs[3][b]%colnr
                                ny=math.floor(bs[3][b]/colnr)
##                                print ((bs,nx,ny,new.size,colnr))
                                for x in range(tmpw2):
                                    for y in range(tmph2):
                                        c=cut.getpixel((x,y))
                                        if c!=0 or bs[2][b]<0:
                                            if bs[2][b]>=0:
                                                if blockcolor[bs[2][b]]==c:
                                                    c2=im.getpixel((addx+x,addy+y))
                                                    dx=nx*32+x-relpos[bs[2][b]][0]
                                                    dy=ny*40+y-relpos[bs[2][b]][1]
    #                                                print (((dx,dy),new.size))
                                                    if c2!=0:
                                                        if dx>=0 and dy>=0 and dx<new.size[0] and dy<new.size[1] :
                                                            new.putpixel((nx*32+x-relpos[bs[2][b]][0],ny*40+y-relpos[bs[2][b]][1]),c2)
                                                        else:
                                                            print (((dx,dy),new.size,ny*40+y,c2))
                                            else:
                                                c2=im.getpixel((addx+x,addy+y))
                                                new.putpixel((nx*32+x,ny*40+y),c2)

    if dtype==0:
        ds=dsdict[drout]
        for anim in dsdict[drout]:
                if not isinstance(dsdict[drout][anim],dict):continue
                ds=dsdict[drout][anim]
                for i,ifpos in enumerate(ds["spritein"]):
                    im=ifiles[ifpos]
                    for x in range(im.size[0]):
                        for y in range(im.size[1]):
                            c=im.getpixel((x,y))
                            if c!=0:
                                new.putpixel((x+ds["spritepos"][i][0],y+ds["spritepos"][i][1]),c)
    new.save(rescomb,optimize=False,transparency=0)




def palstuff(makepal=True,makeconv=True,palbase="cut.png",convout="ipconv.png"):
    convdict={
        ("orig/tftd-depth0.act","orig/ufo-battlescape.act"):"""0,255,81,225,229,116,116,139,0,36,37,38,40,42,38,0
144,48,49,50,51,52,53,54,55,56,57,58,76,77,79,254
255,81,82,83,84,85,86,87,87,88,89,9,10,11,12,14
255,1,81,82,3,4,5,240,241,243,8,9,10,11,12,13
160,161,162,163,164,165,166,167,168,168,169,170,171,173,174,175
64,65,66,67,68,69,70,71,72,73,74,75,76,77,79,254
208,208,209,52,53,53,54,55,56,57,58,60,76,77,78,173
31,79,0,0,0,0,0,0,0,0,0,0,0,0,0,0
16,16,17,18,18,19,20,149,150,72,73,74,75,76,77,79
144,144,145,146,68,69,70,72,73,75,19,23,167,195,198,235
17,18,18,19,19,20,21,22,103,165,166,167,167,168,171,79
20,20,21,21,22,22,23,24,24,25,26,168,169,170,171,172
80,224,3,227,240,242,244,246,247,248,249,12,13,14,253,79
179,179,180,160,160,161,162,163,89,90,91,92,93,168,169,170
178,178,179,180,181,181,182,183,89,90,91,92,93,236,237,252
208,208,209,209,210,211,212,212,213,58,59,60,62,63,77,255"""
        }
    convdict={
        ("orig/tftd-depth0.act","orig/ufo-battlescape.act"):"""0,255,81,225,229,116,116,139,0,36,37,38,40,42,38,0
144,144,145,145,146,147,148,149,150,151,152,153,154,155,156,157
255,81,82,83,84,85,86,87,87,88,89,9,10,11,12,14
255,1,81,82,3,4,5,240,241,243,8,9,10,11,12,13
160,161,162,163,164,165,166,167,168,168,169,170,171,173,174,175
64,65,66,67,68,69,70,71,72,73,74,75,76,77,79,254
208,208,209,52,53,53,54,55,56,57,58,60,76,77,78,173
31,79,0,0,0,0,0,0,0,0,0,0,0,0,0,0
16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,24
144,144,145,146,68,69,70,72,73,75,19,23,167,195,198,235
17,18,18,19,19,20,21,22,103,165,166,167,167,168,171,79
20,20,21,21,22,22,23,24,24,25,26,168,169,170,171,172
80,224,3,227,240,242,244,246,247,248,249,12,13,14,253,79
179,179,180,160,160,161,162,163,89,90,91,92,93,168,169,170
178,178,179,180,181,181,182,183,89,90,91,92,93,236,237,252
208,208,209,209,210,211,212,212,213,58,59,60,62,63,77,255"""
        }




    pallist=[ #testagainst,actfile,replace color 0
#("cut.png","orig/ufo-battlescape.act"),

##("orig/p_tactical1_floorob_CYBERMITE_CORPSE.gif","orig/ufo-battlescape.act",(0,255,0)),
##("orig/p_geo_guardian_dogfight.gif","orig/ufo-geo.act",(32,255,32)),
##("orig/p_base_Sentinel_base.gif","orig/ufo-basescape.act",(64,255,64)),
##("orig/p_research_ufopaedia_WASPITE_AUTOPSY.gif","orig/ufo-research.act",(96,255,96)),

("orig/ufo-battlescape.act.png","orig/ufo-battlescape.act",(0,255,0)),
("orig/ufo-geo.act.png","orig/ufo-geo.act",(32,255,32)),
("orig/ufo-basescape.act.png","orig/ufo-basescape.act",(64,255,64)),
("orig/ufo-research.act.png","orig/ufo-research.act",(96,255,96)),



("orig/tftd-depth0.act.png","orig/tftd-depth0.act",(255,0,255)),
("orig/tftd-depth1.act.png","orig/tftd-depth1.act",(255,32,255)),
("orig/tftd-depth2.act.png","orig/tftd-depth2.act",(255,64,255)),
("orig/tftd-depth3.act.png","orig/tftd-depth3.act",(255,96,255)),
("orig/tftd-geoscape.act.png","orig/tftd-geoscape.act",(255,128,255)),
("orig/tftd-ufopaedia.act.png","orig/tftd-ufopaedia.act",(255,160,255)),

        ]
    ipconv = Image.new("RGBA", (259, 113), (0,0,0,0))
    ipconvln=0
    pcopy={}
    for pimg,pdat,pc in pallist:
        im=Image.open(pimg)
        if makepal:im2=Image.open(palbase)
        with open(pdat,"rb") as fh:
            s=fh.read()
            a = bytearray()
            for i in range(256):
            #    im3.putpixel((i%16,int(i/16)),i)
                rcol=[s[i*3+x] for x in range(3) ]
                icol=[im.palette.palette[i*3+x] for x in range(3) ]
                dcol=[abs(rcol[x]-icol[x]) for x in range(3) ]
                if max(dcol)>0: print ((pdat,i,rcol,icol,dcol))
                c=[]
                for x in range(3):
                    a.extend(struct.pack("B",s[i*3+x]))
                    c.append(s[i*3+x])

                if tuple(c)==pc and i>0 :print ((pdat,i,pc))
            a[0]=pc[0]
            a[1]=pc[1]
            a[2]=pc[2]

            if makeconv:
                for i in range(256):
                    ipconv.putpixel((i+3,ipconvln),tuple(list(a[i*3:i*3+3])+[255]))
                ipconv.putpixel((0,ipconvln),tuple(list(a[197*3:197*3+3])+[255]))
                ipconvln+=1
            pcopy[pdat]=copy.deepcopy(a)
        if makepal:
            im2.palette.palette=bytes(a)
            #im3.palette.palette=bytes(a)
            im2.save(pdat+".png",optimize=False,transparency=0)
            i1=Image.open(pdat+".png")
            s=8
            w=h=16
##            s=1
##            w=256
##            h=1
            plist=[]
            i1=i1.resize((w*s,h*s*2))
            for i in [0,1]:
                for x in range(w):
                    for y in range(h):
                        c=tuple([x for x in i1.palette.palette[(y*w+x)*3:(y*w+x+1)*3]])
                        for sx in range(s):
                            for sy in range(s):
                                #print ((x*s+sx,i*h*s+y*s+sy,i1.size))
                                if i==1 and (sx==0 or sx ==7 or sy==0 or sy==7) and c in plist:
                                    i1.putpixel((x*s+sx,i*h*s+y*s+sy),0)
                                else:
                                    i1.putpixel((x*s+sx,i*h*s+y*s+sy),y*w+x)
                        if i==1:plist.append(c)
            i1.save(pdat+".p.png",optimize=False,transparency=0)
    if makeconv:
        ipconvln+=1
        for pimg,pdat,pc in pallist:
            for pimg2,pdat2,pc2 in pallist:
                t=convdict.get((pdat,pdat2),"")
                if t and pdat in pcopy:
                    clist=[[] for x in range(256)]
                    tclist=sum([[int(y) for y in x.split(",")] for x in t.strip().split("\n")],[])
                    for ci,c in enumerate(tclist):
                        if ci==0: continue
                        clist[c].append(ci)
                    lenc=max([len(x)  for x in clist])
                    for xi in range(len(clist)):
                        for yi,y in enumerate(clist[xi]):
                            ipconv.putpixel((xi+3,ipconvln+yi),tuple(list(pcopy[pdat][y*3:y*3+3])+[255]))
                    for y in range(lenc):
                        ipconv.putpixel((1,ipconvln),tuple(list(dict([(x[1],x[2])for x in pallist])[pdat])+[255]))
                        ipconv.putpixel((2,ipconvln),tuple(list(dict([(x[1],x[2])for x in pallist])[pdat2])+[255]))
                        ipconvln+=1
        ipconv.save(convout)


def convertpal(pconv,im,topim,frompim,firstcol):
##    if web=="web":
##        cpal=ord
##    else:
##        cpal=lambda x:x
    cpal=lambda x:x
    fromcolor=tuple([cpal(x) for x in frompim.palette.palette[0:3]]+[255])
    tocolor=tuple([cpal(x) for x in topim.palette.palette[0:3]]+[255])
    colors={}
    topcollist=False
    nacolor=False
    for lnr in range(pconv.size[1]):
        if pconv.getpixel((3,lnr))==tocolor and pconv.getpixel((1,lnr))[3]==0 and pconv.getpixel((2,lnr))[3]==0:
            topcollist=[pconv.getpixel((x,lnr)) for x in range(4,259)]
            nacolor=topcollist.index(pconv.getpixel((0,lnr)))
    for lnr in range(pconv.size[1]):
        if fromcolor==pconv.getpixel((1,lnr)) and tocolor==pconv.getpixel((2,lnr)) and pconv.getpixel((0,lnr))[3]==0 :
            for ci in range(1,256):
                c=pconv.getpixel((3+ci,lnr))
                if c[3]==255:
                    colors[c]=ci
    opcol={}
    for lnr in range(pconv.size[1]):
        if pconv.getpixel((3,lnr))==fromcolor and pconv.getpixel((1,lnr))[3]==0 and pconv.getpixel((2,lnr))[3]==0:
            opcol=dict([(ci,pconv.getpixel((3+ci,lnr))) for ci in range(1,256)])
    #with open("outstuff.txt","w")as fgfg:
    #    fgfg.write(repr(opcol)+"\n"+repr(colors))
    topim=topim.resize(im.size)
    for x in range(topim.size[0]):
        for y in range(topim.size[1]):
            c=im.getpixel((x,y))
            if c==0:
                topim.putpixel((x,y),0)
            else:
                if opcol.get(c,-1) in colors:
                    topim.putpixel((x,y),colors[opcol[c]])
                elif not nacolor is None:
                    topim.putpixel((x,y),nacolor)
    if not firstcol is None:
        tmp=bytearray(topim.palette.palette)
        tmp[0]=firstcol[0]
        tmp[1]=firstcol[1]
        tmp[2]=firstcol[2]
        topim.save("tmp.png",optimize=False,transparency=0)
        tmpim=Image.open("tmp.png")
        tmpim.palette.palette=bytes(tmp)
        topim=tmpim
    return topim


def makeconv(sl,pfn,cfn):
    l=[int(x) for x in sl.split(",") if len(x)>0][0:15]
    pim=Image.open(pfn)
    pcol=[x for x in bytearray(pim.palette.palette)[0:3]]
    del(pim)
    rows=max([l.count(x) for x in l])
    im=Image.new("RGBA",(259,1+rows),(0,0,0,0) )
    im.putpixel((0,0),(197,197,197,255))
    for c in range(3):
        im.putpixel((3,0),tuple(pcol+[255]))
        for r in range(rows):
            im.putpixel((1,r+1),tuple(pcol+[255]))
            im.putpixel((2,r+1),tuple(pcol+[255]))

    for x in range(1,256):
        im.putpixel((3+x,0),(x,x,x,255))
    for x in range(1,16):
        im.putpixel((3+x,1),(x,x,x,255))
    npc=[[x if y==0 else -1 for x in range(16)]+[-1 for x in range(256-16)] for y in range(rows)]
    for xi,x in enumerate(l):
        for y in range(rows):
            if npc[y][x*16]==-1:
                for z in range(16):
                    c=(xi+1)*16+z
                    npc[y][x*16+z]=c
                    im.putpixel((3+x*16+z,1+y),(c,c,c,255))
                break

    print ((l))
    print ((npc,))
    for y in npc:
        for x in range(16):
            print ((y[x*16:x*16+16]))
    im.save(cfn)

def fixpalette(im,imp):
    opal=[[y for y in imp.palette.palette[x*3:x*3+3]] for x in range(len(imp.palette.palette)//3)]
    fpal=[[y for y in im.palette.palette[x*3:x*3+3]] for x in range(len(im.palette.palette)//3)]
    transform=dict([(x,x) for x in range(len(im.palette.palette)//3)])
    for xi,x in enumerate(fpal):
        transform[xi]=opal.index(x) if x in opal else 0
    im.palette.palette=imp.palette.palette
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            im.putpixel((x,y),transform[im.getpixel((x,y))])
    return im
