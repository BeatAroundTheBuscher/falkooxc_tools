from deep_eq import deep_eq #https://gist.github.com/samuraisam/901117



import yaml,copy,glob,os,pickle,itertools,math
from deep_eq import deep_eq #https://gist.github.com/samuraisam/901117
from PIL import Image

arguments=[]
#arguments.append("totest")


fixme=dict(pathcaseextrafiles=False,removevanillavalues=False)
test_lngs=['en-GB']

reloadorig=0 #set to 1 if you have new game version/first start


elevel={1:"debug",10:"info",25:"warning",99:"error"}
errorlist=dict([
("is no list",(10,"happens if you mod non-list items like costScientist or you screw up a normal list property")),#found,info
("is no dict",(25,"all elements in listitems should be dict - fails with alienitemlevels")),#found,info
("contains delete!",(25,"mod combiner has no cencept of delete at the moment")),#founf,warning
("identifier missing",(99,"unique identifier is missing in list entries")),#found,warning
("changes original object",(10,"just an information")),#found,debug
("keeps original value",(10,"get rid of useless copying of data")),#found,debug
("an item occurs multiple time", (25,"same 'type' of item multiple times within the same list/mod")),#found, warning
("an item reoccurs in another mod",(25,"a new item is changed by multiple mods")),#found,info
("no string translation",(25,"a string that is referenced is missing")),#found,warning
("a language/translation is missing",(25,"one of the languages we test for is missing")),#found,warning
("a language is incomplete",(25,"a language misses strings that are found in other languagues")),#found, info
("rulfile is likely not UTF-8",(99,"rulfile is likely not UTF-8 but contains non-ascii characters")),#found,warning,fail
("some error during rulfile import",(99,"unknown error during rulfile import (e.g. contains non-utf8 chars in utf8 file, file contains TAB)")),#found,warning,fail
("rulfile not in Ruleset Folder",(99,"rul file needs to be in a Ruleset Folder (be aware of the uppercase R)")),#found,warning,fail
("non image in spritesheet directory",(10,"there is a non-image file in a spritesheet directory")),#found, info
("a sprite directory contain non-uniform filenames",(25,"to get an assured sorting order within a sprite sheet directory the file should only differ in digits that failed here")),#found,info
("the colour palette differ within a spride sheet",(25,"the palette is not the same for all images of an spritesheet")),#found,warning
("an image has the wrong mode",(99,"an image needs to use a indexed by a colour Palette to use ")),
("the image size differ within a spride sheet",(25,"the size is not the same for all images of an spritesheet")),
("the case sensitive test of dir/file path failed",(25,"to assure a workable mod on unix systems all file references are case sensitive")),#found,warning

("not referenced file found",(10,"a file is in the mod folder that is not use/wrongly referenced in the ruleset")),#found,info

("new sprite/sound is referenced multiple times",(10,"a sprite/sound is referenced multiple times in rulset")),#found,info
("extrasprite/sound is not ruleset-referenced",(25,"extrasprite is not ruleset-referenced but in file section (ok if you replace clicksound/alienturn-image/..)")),#found ,?
("no connected file entry found for ruleset-referenced",(25,"there is reference to a new file entry but this entry does not exist")),#found,warning

("the sub images are not fitting into the full image",(25,"the splitting of an combined image into subpixel is incomplete")),#found,info
("palette could use more colours",(10,"the image palette is only used in battlescape and likely can use the last 16 colours")),#found, info
("palette not correct",(25,"the assigned palette for an image is incorrect")),#found, warning
("image palette not complete",(25,"an image has an incomplete palette less than 256 colors")),#found,warning
("rul/real-size for single image does not match",(25,"size info in rul entry does not match real size")),
("single image needs fid 0",(25,"a single image needs to have a file entry of 0")),
("single imgae referenced without singleImage tag in file entry",(25,"a single image is referenced but has no singleImage:True entry in corresponding files section")),

("references spritesheet does misses images",(25,"a referenced spritesheet has less images than needed")),#found,?
("a sprite sheet is bigger than needed",(25,"a referenced spritesheet is bigger than necessary")),#found,?
("a reference is not for the first image spritesheet",(25,"a reference links to the middle of a sprite sheet")),

#specfile
("case sensitive path error for a file",(25,"the path to a file is wrong with case sensitve path settings")),#found,info
("spec file not found",(25,"missing map/terrain files")),
("spec file declared more than once",(10,"a map/terrain is used in more than one place .. by mistake?")),#found, info
("different case sensitive names for the same specfile",(25,"your map/terrain files have different casesensitive letters")),

#reorganize fileids
("file/dir not found",(25,"a extrasprite/sound entry is wrong")),#found,warning
("redefines original sprite/sound",(10,"warning that id is smaller than the biggest vanilla number and screws with existing sprites/sounds (works with some PCK entries not all)")),#found,info
("only ids up to 1000 save in extrasprite/sound",(25, "mods only have 1000 fileentries hihghe values can change fileentries in other mods")),#founf, warning
("more/less than one image with singleImage tag",(10,"referenced the same image multiple times .. by mistake?")),

#fixes
("fix: case sensitive path fixed",(-999,"a file reference was chasnged to fit the case sensetive path")),#found,fix
("fix: removes original value",(-999,"a property of an listelement is removed because its orignal value was not changed")),#found,fix

#TODO
("test",(999,"test"))
])

def getorigdata(reloadorig=0):

    if reloadorig==1:
        print ("load orig")
        with open('mysite/orig/Xcom1Ruleset.rul', 'r') as fh:
            orig=yaml.safe_load(fh)
        lang={}
        print ("load lang")
        for lfile in glob.glob("mysite/orig/Language/*.yml"):
            with open(lfile, 'rb') as fh:
                lfn=unicode(lfile.split(os.sep)[-1].split(".")[-2])
                print (lfile+":"+lfn)
                tmp=yaml.safe_load(fh)
                if [x for x in tmp][0]==lfn:
                    lang[lfn]=tmp
                else: print (lfn+" lang failed")
        print ("save orig")
        with open('mysite/orig.pickle', 'wb') as fh:
            pickle.dump((orig,lang),fh)
    else:
        with open('mysite/orig.pickle', 'rb') as fh:
            (orig,lang)=pickle.load(fh)
    return (orig,lang)

def mngextrafileelem(origspecfiles,cat,elem,origmaps,origterrain,unlist):

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



def testit(test_lngs,fixme,arguments,reloadorig):


    #unique identifier
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

    singleimages=[
        ["ufopaedia","image_id", 'research'],
        ["ufos","modSprite", 'geo',]
        ]
    #todo:
    #('extrasprite/sound is not ruleset-referenced', 'extraSprites', 'sectoidInventoryImage', 0, 'Resources/AlienInventory/sectoid.png', 'totest/AlienInventoryMod/AlienInventoryMod/Ruleset/AlienInventory.rul')
    #('references spritesheet does misses images', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'extraSprites', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
    #('a sprite sheet is bigger than needed', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'extraSprites', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
    #('no connected file entry found for ruleset-referenced', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
    #dir/files screwed in Combat-UniformArmors
    #

    #prepare id data for the hwp/armor sprite id chaos
    armorspace={1:99,2:32,3:56,5:160,6:131,7:227,8:9,9:28}
    armorspace[0]=lambda x:275+x.get("movementType",0)*8 if "storeItem" in x else 267
    armorspace[4]=lambda x:90 if x.get("type","") in armorsofspawners  else 75
    armorstart=dict([(x,0) for x in range(10)])
    armorstart[2]=lambda x:x.get("movementType",0)*32
    #hidden drawmethod 0++=10
    armorspace[10]=armorspace[0]
    armorstart[10]=armorstart[0]

    #get default palettes
    palettes={}
    for f in glob.glob("mysite/orig/p_*.gif"):
        with open(f,"rb") as fh:
            pim = Image.open(fh)
            pim.load()
            palettes[f.split(os.sep)[2].split("_")[1]]=[1,256,[[pim.palette.palette[3*i+g] for g in range(3)] for i in range(256)]]
    palettes["tactical2"][1]=256-16

    imageexts=["gif","png"]
    ignorelngcat=["armors", "ufoTrajectories", "MCDPatches","extraSprites","extraSounds","terrains","alienItemLevels","soldiers"]
    #['regions', 'items', 'ufos', 'invs', 'countries', 'units', 'alienDeployments', 'ufopaedia', 'craftWeapons', 'facilities', 'crafts', 'alienRaces', 'manufacture', 'alienMissions', 'research']


    mods={}
    orig,lang=getorigdata(reloadorig)
    cspritesc=0

    allrulfiles=[]
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


    errors=[]


    #for mfile in [x for x in glob.glob("notfmp/origmods/[a-z]dv*/ruleset/fu*.rul")]:
    for mfile in [x for x in allrulfiles]:
        if mfile.split("/")[-2]!="Ruleset":
            errors.append(("rulfile not in Ruleset Folder",mfile))
        else:
            with open(mfile, 'rb') as fh:
                print ("loading",mfile)
                try:
                    tmp=yaml.safe_load(fh)
                except yaml.reader.ReaderError:
                    errors.append(("rulfile is likely not UTF-8",mfile))
                except :
                    errors.append(("some error during rulfile import",mfile))
                else:
                    mods[mfile]=copy.deepcopy(tmp)
                    mods[mfile]["MCPdata"]=dict(base="/".join(mfile.split("/")[0:-2]),files=[],dirs=[])
                    mods[mfile]["MCPdata"]["dirs"]=[d for d in alldirs if d.startswith(mods[mfile]["MCPdata"]["base"])]
                    mods[mfile]["MCPdata"]["files"]=[f for f in allfiles if f.startswith(mods[mfile]["MCPdata"]["base"])]
                    mods[mfile]["MCPdata"]["rdirs"]=[d[len(mods[mfile]["MCPdata"]["base"])+1:] for d in alldirs if d.startswith(mods[mfile]["MCPdata"]["base"])]
                    mods[mfile]["MCPdata"]["rfiles"]=[f[len(mods[mfile]["MCPdata"]["base"])+1:] for f in allfiles if f.startswith(mods[mfile]["MCPdata"]["base"])]

    imagenames={}
    allmoddoublesearch={}


    origspecfiles={}

    for cat in ["crafts","ufos","terrains","facilities"]:
        for elem in orig[cat]:
            origspecfiles=mngextrafileelem(origspecfiles,cat,elem,[],[],unlist)
    origmaps=list(set([x[1] for x in origspecfiles if x[0]=="MAPS"]))
    origterrain=list(set([x[1] for x in origspecfiles if x[0]=="TERRAIN"]))


    for mfile in mods:
        mod=mods[mfile]
        getmallrefs=[]
        getmallfileids=[]
        #getmallxtrafileids=[]
        onemoddoublesearch={}
        modspecfiles={}
        deleteelemlist={}
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

        armorsofspawners=[x["armor"] for x in orig["units"]+mod.get("units",[]) if len(x.get("spawnUnit",""))>0]
        for cat in mod:
            if cat=="MCPdata":continue
            if not isinstance(mod[cat],list) and cat not in ["MCPdata"]:
                errors.append(("is no list",cat,mfile))
                continue
            for elemid,elem in enumerate(mod[cat]):
                if not isinstance(elem,dict):
                    errors.append(("is no dict",cat,mfile))
                    continue
                if elem.get("delete",False):
                    errors.append(("contains delete!",cat,elem,mfile))
                    continue
                if cat in unlist and not unlist[cat] in elem:
                    errors.append(("identifier missing",cat,unlist[cat],elem,mfile))
                    continue
                onemoddoublesearch[(cat,elem[unlist[cat]])]=onemoddoublesearch.get((cat,elem[unlist[cat]]),0)+1
                if (not cat in orig or elem[unlist[cat]] not in [x[unlist[cat]] for x in orig[cat]])and not cat in ["extraStrings","extraSprites","extraSounds"] :
                    allmoddoublesearch[(cat,elem[unlist[cat]])]=allmoddoublesearch.get((cat,elem[unlist[cat]]),[])
                    allmoddoublesearch[(cat,elem[unlist[cat]])].append((cat,elem[unlist[cat]],mfile))
                if cat in orig and not cat in ignorelngcat :

                    for test_lng in langmod:
                        testwords=[elem[unlist[cat]]]
                        if cat=="items" and not elem.get("recover",True):
                            testwords=[elem.get("name","STR_CORPSE_SHOULD_HAVE_A_NAMEENTRY")]
                        if cat=="ufopaedia" and "text" in elem:
                            testwords.append(elem["text"])
                        for testword in testwords:
                            #errors.append(("test no string translation",test_lng,cat,elem[unlist[cat]],testword,testwords,lang.get(test_lng,{}).get(test_lng,{}).get(testword,"") ,[x for x in lang], langmod.get(test_lng,{}).get(test_lng,{}).get(testword,""),mfile))
                            if not (lang.get(test_lng,{}).get(test_lng,{}).get(testword,"") or langmod.get(test_lng,{}).get(test_lng,{}).get(testword,"")):
                                errors.append(("no string translation",test_lng,cat,elem[unlist[cat]],testword,mfile))
    #TODO better orig-value recognition/fix
                if cat in orig :
                    if sum ([1 for x in orig[cat] if x[unlist[cat]]==elem[unlist[cat]] ] )>0:
                        errors.append(("changes original object",cat,elem[unlist[cat]],sum ([1 for x in orig[cat] if x[unlist[cat]]==elem[unlist[cat]] ] ),mfile))
                        oelem=[x for x in orig[cat] if x[unlist[cat]]==elem[unlist[cat]] ][0]
                        for prop in elem:
                            if not prop in oelem or prop==unlist[cat]:continue
                            if prop==unlist[cat]:continue
                            if deep_eq(elem[prop],oelem[prop]):
                                if fixme.get("removevanillavalues",False):
                                    deleteelemlist[(cat,elemid)]=deleteelemlist.get((cat,elemid),{"delprops":[],"o":oelem})
                                    deleteelemlist[(cat,elemid)]["delprops"].append(prop)
                                    errors.append(("fix: removes original value",cat,elem[unlist[cat]],prop,mfile))
                                else:
                                    errors.append(("keeps original value",cat,elem[unlist[cat]],prop,mfile))




                if cat in ["crafts","ufos","terrains","facilities"]:
                    modspecfiles=mngextrafileelem(modspecfiles,cat,elem,origmaps,origterrain,unlist)

                if cat in ["extraSprites","extraSounds"]:
                    for fid in elem.get("files",{}):

                        #####getmallfileids[(elem.get("type","missingtype"),fid)]=getmallfileids.get((elem.get("type","missingtype"),fid),[])
                        #####getmallfileids[(elem.get("type","missingtype"),fid)].append((elem.get("type","missingtype"),fid,mfile))
                        tmpimg=None
                        tocheckfile=mod["MCPdata"]["base"]+"/"+elem["files"][fid]
                        if fixme["pathcaseextrafiles"]:
                            if "/"==tocheckfile[-1]:
                                if not (tocheckfile in  [x+"/" for x in mod["MCPdata"]["dirs"]] and os.path.isdir(tocheckfile)):
                                    newfns=[mod["MCPdata"]["base"]+"/"+x for x in mod["MCPdata"]["rdirs"] if (mod["MCPdata"]["base"]+"/"+x).lower()==tocheckfile[0:-1].lower()]
                                    if len(newfns)>0:
                                        newfn=newfns[0]
                                        tocheckfile=newfn+"/"
                                        elem["files"][fid]=newfn.replace(mod["MCPdata"]["base"]+"/","")+"/"
                                        errors.append(("fix: case sensitive path fixed",cat,elem[unlist[cat]],elem["files"][fid],mfile))
                            else:
                                if not (tocheckfile in  [x for x in mod["MCPdata"]["files"]] and os.path.isfile(tocheckfile)):
                                    newfns=[x for x in mod["MCPdata"]["files"] if x.lower()==tocheckfile.lower()]
                                    if len(newfns)>0:
                                        newfn=newfns[0]
                                        tocheckfile=newfn
                                        elem["files"][fid]=newfn.replace(mod["MCPdata"]["base"]+"/","")
                                        errors.append(("fix: case sensitive path fixed",cat,elem[unlist[cat]],elem["files"][fid],mfile))
                        tmpentry=dict(cat=cat,lid=elem.get("type","missingtype"),fid=fid,fids=[fid],refids=[1],fpath=elem.get("files",{})[fid],img=[],modfile=mfile)
                        if not os.path.isfile(tocheckfile) and not os.path.isdir(tocheckfile):
                            errors.append(("file/dir not found",cat,elem[unlist[cat]],elem["files"][fid],mfile))
                        elif cat=="extraSprites":
                            tmpentry["fentry"]=dict(width=elem.get("width",320),height=elem.get("height",200),singleImage=elem.get("singleImage",False),subX=elem.get("subX",0),subY=elem.get("subY",0))
                            if os.path.isfile(tocheckfile) and tocheckfile.split(".")[-1].lower() in imageexts:
                                with open(tocheckfile,"rb") as fh:
                                    tmpimg=Image.open(fh)
                                    tmpimg.load()
                                    if elem.get("subX",0)+elem.get("subY",0)==0 or elem.get("singleImage",False):
                                        if elem.get("singleImage",False):
                                            if not tmpimg.size==(elem.get("width",320),elem.get("height",200)):
                                                errors.append(("rul/real-size for single image does not match",cat,elem[unlist[cat]],fid,elem["files"][fid],mfile))
                                            if fid!=0:
                                                errors.append(("single image needs fid 0",cat,elem[unlist[cat]],fid,elem["files"][fid],mfile))
                                        tmpentry["img"].append(tmpimg)
                                    else:
                                        imgsize=(elem.get("subX",0),elem.get("subY",0))
                                        newims=[]
                                        if tmpimg.size[1]%imgsize[1]!=0 or tmpimg.size[0]%imgsize[0] !=0:
                                            errors.append(("the sub images are not fitting into the full image",cat,elem[unlist[cat]],fid,elem["files"][fid],mfile))
                                        else:
                                            tmpentry["refids"]=[]
                                            for y in range(0,tmpimg.size[1]-imgsize[1]+1,imgsize[1]):
                                                for x in range(0,tmpimg.size[0]-imgsize[0]+1,imgsize[0]):
                                                    croptmp=tmpimg.crop((x,y,x+imgsize[0],y+imgsize[1]))
                                                    croptmp.save("tmp.gif",optimize=False,transparency=0) #TODO ARGH WTF why is crop / load combo not working?
                                                    croptmp=Image.open("tmp.gif")
                                                    croptmp.load()
                                                    newims.append(croptmp)
                                                    tmpentry["refids"].append(1 if x==0 else 0)
                                            tmpentry["img"]=newims
                                            tmpentry["fids"]=[fid+x for x in range(len(newims))]
                                            tmpentry["dfiles"]=["subimg" for x in range(len(newims))]
                            if os.path.isdir(tocheckfile):
                                tmpentry["dfiles"]=[]
                                for f in sorted(glob.glob(tocheckfile+"*")):
                                    if f.split(".")[-1].lower() in imageexts:
                                        if len(tmpentry["dfiles"])>0:
                                            tmpentry["fids"].append(tmpentry["fids"][-1]+1)
                                            tmpentry["refids"].append(0)
                                        with open(f,"rb") as fh:
                                            tmpimg=Image.open(fh)
                                            tmpimg.load()
                                            tmpentry["img"].append(tmpimg)
                                        tmpentry["dfiles"].append(f)
                                    else:
                                        errors.append(("non image in spritesheet directory",cat,elem[unlist[cat]],fid,elem["files"][fid],f,mfile))
                        getmallfileids.append(tmpentry)
                        #print(tmpentry)
                    if elem.get("singleImage",False) and len(elem["files"])!=1:
                        errors.append(("more/less than one image with singleImage tag",cat,elem[unlist[cat]],mfile))

                ################################ fix the rest


                for prop in elem:
                    if cat in propspdicts:
                        if prop in propspdicts[cat]:
                            for si,spfile in enumerate(propspdicts[cat][prop][0]):
                                newfileid=elem[prop]*propspdicts[cat][prop][3][si]+propspdicts[cat][prop][2][si]
                                if not csprites.get(spfile,[0,-99])[1]>newfileid: #vanilla references not added
                                    getmallrefs.append(dict(reftype="propid",ptype=csprites[spfile][3],cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=spfile,refid=[newfileid+x for x in range(propspdicts[cat][prop][1][si])],reftyp="spritesheet",modfile=mfile))
                                #['tactical2', 'tactical1', 'geo', 'base', 'research']

                            if cat=="items" and prop=="turretType":
                                tmparmors=[x.get("armor","") for x in orig["units"]+mod.get("units",[]) if x.get("type","")==elem.get("type","---")]
                                if tmparmors:
                                    tmparmorfiles=[x.get("spriteSheet","nosheet") for x in orig["armors"]+mod.get("armors",[]) if x.get("type","")==tmparmors[0]]
                                    if tmparmorfiles:
                                        getmallrefs.append(dict(reftype="turretid",ptype="tactical1",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=tmparmorfiles[0],refid=[elem[prop]*8+64+x for x in range(8)],reftyp="spritesheet",modfile=mfile))

                    if cat=="armors" and prop=="spriteSheet":
                        tmpspace=armorspace[elem.get("drawingRoutine",0)] if isinstance(armorspace[elem.get("drawingRoutine",0)],int) else armorspace[elem.get("drawingRoutine",0)](elem)
                        tmpstart=armorstart[elem.get("drawingRoutine",0)] if isinstance(armorstart[elem.get("drawingRoutine",0)],int) else armorstart[elem.get("drawingRoutine",0)](elem)
                        getmallrefs.append(dict(reftype="armor",ptype="tactical1",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=elem[prop],refid=[tmpstart+x for x in range(tmpspace)],reftyp="spritesheet",modfile=mfile))
                    if cat=="armors" and prop=="spriteInv":
                        getmallrefs.append(dict(reftype="armorinv",ptype="tactical2",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=elem[prop]+(".SPK" if elem.get("storeItem","") else ""),refid=[0],reftyp="sprite",modfile=mfile))
                        if len(elem.get("storeItem",""))>0:
                            for g in ["M","F"]:
                                for t in range(4):
                                    getmallrefs.append(dict(reftype="armorinv",ptype="tactical2",cat=cat,lid=elem[unlist[cat]],prop=prop,propid=elem[prop],refelem=elem[prop]+g+str(t)+".SPK",refid=[0],reftyp="sprite",modfile=mfile))
                    for si in  singleimages:
                        if not cat==si[0]:continue
                        if prop==si[1]:
                            getmallrefs.append(dict(reftype="image",ptype=si[2],cat=cat,lid=elem[unlist[cat]],prop=prop,propid=0,refelem=elem[prop],refid=[0],reftyp="sprite",modfile=mfile))




        tmpspecsumup={}
        for x in modspecfiles:
            tmpspecsumup[(x[0],x[1].lower())]=tmpspecsumup.get((x[0],x[1].lower()),[])
            tmpspecsumup[(x[0],x[1].lower())].append(x)
            if len(modspecfiles[x]["ref"])>1:
                errors.append(("spec file declared more than once",x,modspecfiles[x]["ref"],mfile))
        for x in tmpspecsumup:
            if len(tmpspecsumup[x])>1:
                errors.append(("different case sensitive names for the same specfile",x,tmpspecsumup[x],mfile))


    #errors.append(("image referenced more than once",cat,elem[unlist[cat]],imagenames[elem[si[1]]],mfile))
        filrev=dict(sum([[((x["lid"],y),xi) for y in x.get("fids",[])] for xi,x in enumerate(getmallfileids)],[]))
        refrev={}
        for revelem in [((x["refelem"],x["propid"]),xi) for xi,x in enumerate(getmallrefs)]:
            refrev[revelem[0]]=refrev.get(revelem[0],[])
            refrev[revelem[0]].append(revelem[1])
        for ref in refrev:
            #here one could check e.g. if mutliple references expect same palette ..
            if ref in filrev:
                refdata=getmallrefs[refrev[ref][0]]
                filedata=getmallfileids[filrev[ref]]
                if filedata["img"]:
                    if refdata.get("reftype","")=="image" and not filedata.get("fentry",{}).get("singleImage",False):
                        errors.append(("single imgae referenced without singleImage tag in file entry",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],refdata["ptype"],filedata["cat"],filedata["lid"],refdata["modfile"]))
                    if len(set(refdata["refid"])-set(filedata.get("fids",[])))>0:
                        errors.append(("references spritesheet does misses images",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],filedata["cat"],filedata["lid"],refdata["modfile"]))
                    if len(filedata.get("fids",[]))>len(refdata["refid"]):
                        errors.append(("a sprite sheet is bigger than needed",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],filedata["cat"],filedata["lid"],refdata["modfile"]))
                    #works for facilities/check reftype=="propid"?
                    if refdata.get("refid",[-99])[0] in filedata.get("fids",[]) and filedata["refids"][filedata.get("fids",[]).index(refdata.get("refid",[-99])[0])]!=1:
                        errors.append(("a reference is not for the first image spritesheet",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],filedata["cat"],filedata["lid"],refdata["modfile"]))
                    t=palettes[refdata["ptype"]][0]
                    f=palettes[refdata["ptype"]][1]
                    if filedata["img"][0].palette:
                        if len(filedata["img"][0].palette.palette)==768:
                            ipal=[[filedata["img"][0].palette.palette[3*i+g] for g in range(3)] for i in range(256)]
                            #if not refdata["refid"] in filedata.get("fids",[]): print ((refdata,filedata))
                            if not ipal[t:f]==palettes[refdata["ptype"]][2][t:f]:
                                if refdata["ptype"]=="tactical1" and ipal[t:f-16]==palettes[refdata["ptype"]][2][t:f-16]:
                                    errors.append(("palette could use more colours",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],refdata["ptype"],filedata.get("dfiles",[filedata["fpath"]])[0],refdata["modfile"]))
                                else:
                                    errors.append(("palette not correct",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],refdata["ptype"],filedata.get("dfiles",[filedata["fpath"]])[0],refdata["modfile"]))
                        else:
                            errors.append(("image palette not complete",refdata["cat"],refdata["lid"],refdata["prop"],refdata["refelem"],refdata["ptype"],filedata.get("dfiles",[filedata["fpath"]])[0],refdata["modfile"]))



        for rei,re in enumerate(getmallrefs):
            if not (re["refelem"],re["refid"][0])in filrev:
                errors.append(("no connected file entry found for ruleset-referenced",re["cat"],re["lid"],re["prop"],re["refelem"],re["modfile"]))
        unusedfiles=copy.deepcopy(mod["MCPdata"]["rfiles"])
        for fei,fe in enumerate(getmallfileids):
            if not (fe["lid"],fe["fid"])in refrev:
                errors.append(("extrasprite/sound is not ruleset-referenced",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            elif len(refrev[(fe["lid"],fe["fid"])])>1:
                errors.append(("new sprite/sound is referenced multiple times",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            if "dfiles" in fe:
                if len(set([''.join(c for c in y if not c.isdigit()) for y in fe["dfiles"]]))!=1:
                    errors.append(("a sprite directory contain non-uniform filenames",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            if len([x for x in fe.get("img",[]) if x.mode !="P"])>0:
                errors.append(("an image has the wrong mode",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            else:
                if "dfiles" in fe:
                    if len(set([img.palette.palette for img in fe["img"]]))!=1:
                        errors.append(("the colour palette differ within a spride sheet",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
                    if len(set([img.size for img in fe["img"]]))!=1:
                        errors.append(("the image size differ within a spride sheet",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            if fe["fpath"][0:-1] in  mod["MCPdata"]["rdirs"] if "/"==fe["fpath"][-1] else fe["fpath"] in mod["MCPdata"]["rfiles"]: #fileref-files are used
                if "/"==fe["fpath"][-1]:
                    getmallfileids[fei]["revdirref"]=mod["MCPdata"]["rdirs"].index(fe["fpath"][0:-1])
                    for x in copy.deepcopy(unusedfiles):
                        if "/".join(x.split("/")[0:-1])==fe["fpath"][0:-1]:
                            unusedfiles.remove(x)
                else:
                    getmallfileids[fei]["revfileref"]=mod["MCPdata"]["rfiles"].index(fe["fpath"])
                    if fe["fpath"] in unusedfiles:
                        unusedfiles.remove(fe["fpath"])
            else:
                errors.append(("the case sensitive test of dir/file path failed",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            if fe["lid"] in csprites and fe["fid"]<csprites[fe["lid"]][1]:
                errors.append(("redefines original sprite/sound",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
            if fe["fid"]>998:
                errors.append(("only ids up to 1000 save in extrasprite/sound",fe["cat"],fe["lid"],fe["fid"],fe["fpath"],fe["modfile"]))
        if mfile.replace(mod["MCPdata"]["base"]+"/","") in unusedfiles:#modfile  is used
            unusedfiles.remove(mfile.replace(mod["MCPdata"]["base"]+"/",""))
        for sx in modspecfiles:#spec file are used
            for fn in modspecfiles[sx]["files"]:
                tmpfn=mod["MCPdata"]["base"]+"/"+fn
                if os.path.isfile(tmpfn):
                    if  fn in unusedfiles:
                        unusedfiles.remove(fn)
                    if not fn in mod["MCPdata"]["rfiles"]:
                        newfns=[x for x in unusedfiles if fn.lower()==x.lower()]
                        if len(newfns)>0: unusedfiles.remove(newfns[0])
                        errors.append(("case sensitive path error for a file",sx,modspecfiles[sx]["ref"],fn,mfile))
                else:
                    errors.append(tuple(["spec file not found",sx,modspecfiles[sx]["ref"],fn,mfile]))
        for x in unusedfiles:#unused file => error
            errors.append(("not referenced file found",x,mfile))



        for ds in onemoddoublesearch:
            if onemoddoublesearch[ds]>1 :
                errors.append(("an item occurs multiple time",ds,onemoddoublesearch[ds],mfile))
    return errors
#    errshow=-999
#    for error in errors:
#        if not error[0] in errorlist:
#            print ("NO ENTRY FOR ERROR! "+error[0])
#        elif errorlist.get(error[0],[-1])[0]>=errshow:
#            print (error)



# A very simple Flask Hello World app for you to get started with...

import os,shutil
import tempfile
from zipfile import ZipFile
from flask import Flask, request, session,  redirect, url_for, abort,render_template, flash #,g

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    test_lngs=["en-GB","en-US"]
    files=[]
    ergerr=[]
    if request.method == 'POST' and "mfile" in request.files:
        directory_name = tempfile.mkdtemp()
        try:
            f = request.files['mfile']
            os.mkdir(directory_name+os.sep+'test')
            fn=directory_name+os.sep+'test'+os.sep+'test.zip'
            f.save(fn)
            zf=ZipFile(fn)
            zf.extractall(directory_name+os.sep+'test')
            zf.close()
            arguments.append(directory_name+os.sep+'test')
            os.remove(fn)
            #shutil.rmtree(fn,ignore_errors=True)
            test_lngs=request.form.get('lang', 'en-GB,en-US').replace(" ","").split(",")
            ergerr=testit(test_lngs,fixme,arguments,reloadorig)
            #files=[x for x in os.walk(directory_name)]
            # Clean up the directory yourself
            shutil.rmtree(directory_name,ignore_errors=True)
            #os.removedirs(directory_name)
        except:
            pass



    #return render_template('layout.html', errors=[request.form['lang']])
    #return render_template('layout.html', errors=[repr(request.form)])
    return render_template('layout.html', errors=[
        [e[0],elevel.get(errorlist.get(e[0],[10])[0],"undefined")+":",errorlist.get(e[0],["","no description"])[1]]+list(e[1:-1] )for e in ergerr],langstr=",".join(test_lngs))
    #test_lngs)#

