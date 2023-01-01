from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import yaml,copy,glob,os,pickle,itertools,math
from PIL import Image
from oxcmodhelper1 import *

yaml.add_representer(dict,represent_dict)
yaml.add_representer( NumList, numlist_rep )


#testmodfixes
#FIX basic weapons delted es/es-419  strings
#FIX tanks delted pl language
#TODO tidy up armout and hwp
#TODO dartrifle corpse unlock -> plasmaOR style
#elerium mace rename rulesets -> ruleset
#move GLOVE inte a new Resources folder

arguments=[]
#arguments.append("totest")
arguments.append(".")


fixme=dict(pathcaseextrafiles=False,removevanillavalues=True,langswitch=[('en-GB','en-US',1,''),('en-US','en-GB',1,''),('en-US','fi',0,'T:'),('en-US','es-419',0,'T:')])
fixme=dict(pathcaseextrafiles=True,removevanillavalues=True,langswitch=[('en-GB','en-US',1,''),('en-US','en-GB',1,'')])
fixme=dict(pathcaseextrafiles=False,removevanillavalues=False,langswitch=[])


#delete no change-values (copy/edit xcom1rul -> new mod?)
#combine images
#reset fileids

test_lngs=['en-US','en-GB']

reloadorig=1 #set to 1 if you have new game version/first start

### END OF ARGUMENTS #############



#todo:
#('extrasprite/sound is not ruleset-referenced', 'extraSprites', 'sectoidInventoryImage', 0, 'Resources/AlienInventory/sectoid.png', 'totest/AlienInventoryMod/AlienInventoryMod/Ruleset/AlienInventory.rul')
#('references spritesheet does misses images', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'extraSprites', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
#('a sprite sheet is bigger than needed', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'extraSprites', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
#('no connected file entry found for ruleset-referenced', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
#dir/files screwed in Combat-UniformArmors
#
elevel={1:"debug",10:"info",25:"warning",99:"error"}
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



#checkmodsall (atm no method)
("an item reoccurs in another mod",(25,"a new item is changed by multiple mods")),#found,info

#TODO
 #fix palette

#old
  #("single image referenced without singleImage tag in file entry",(25,"a single image is referenced but has no singleImage:True entry in corresponding files section")),
#  ("a reference is not for the first image spritesheet",(25,"a reference links to the middle of a sprite sheet")),#found





#TODO
("test",(999,"test"))
]
errorlist=dict(preerrorlist)



mods={}
orig,lang=getorigdata(reloadorig)
del (orig["extraSprites"]) #else one gets missleading "change original value" errors while adding new bullets
cspritesc=0

allrulfiles,allxrulfiles,allfiles,alldirs=getfilelists(arguments)

errors=[]


origspecfiles={}
for cat in ["crafts","ufos","terrains","facilities"]:
    for elem in orig[cat]:
        origspecfiles=mngextrafileelem(origspecfiles,cat,elem,[],[])
origmaps=list(set([x[1] for x in origspecfiles if x[0]=="MAPS"]))
origterrain=list(set([x[1] for x in origspecfiles if x[0]=="TERRAIN"]))

for mfile in [x for x in allrulfiles]:
    if mfile.startswith("fixed/Dioxine_Piratez_Mod_0_69"):continue
    if mfile.split("/")[1].startswith("0"):continue
    tmp,errors=loadamod(mfile,errors,alldirs,allfiles)

    if tmp:
        mods[mfile],errors=fixorigvalue(orig,tmp,errors,"orig",mfile,fixme.get("removevanillavalues",False))

        todoxrulfile=[]
        for xfile in allxrulfiles:
            if xfile.split("/")[-1].split(".")[0:-2]==mfile.split("/")[-1].split(".")[0:-1]:
                todoxrulfile.append(xfile)
        todoxrulfile.sort(key=lambda x:x.lower().split("/")[-1].split(".")[-2])
        xrules=[]
        for xrulefile in todoxrulfile:
            tmp,errors=loadamod(xrulefile,errors,alldirs,allfiles)
            if tmp:
                tmp,errors=fixorigvalue(mods[mfile],tmp,errors,mfile,xrulefile,False)
                xrules.append(tmp)
                mods[mfile],errors=add2mod(mods[mfile],tmp,errors,mfile,xrulefile)
        mods[mfile],errors=fixmodlanguage(mods[mfile],errors,fixme.get("langswitch",[]),mfile)
        errors=checkmodstuff(mods[mfile],errors,mfile)
        mods[mfile],errors=makerefs(mods[mfile],errors,orig,mfile)
        mods[mfile],errors=fixfilepaths(mods[mfile],errors,mfile,fixme.get("pathcaseextrafiles",False),True)

allitems={}
testsublevel=dict(extraStrings="strings",extraSounds="files",extraSprites="files")
for mfile in mods:
    langmod,errors=checkmodlangs(mods[mfile],errors,test_lngs,mfile)
    for cat in mods[mfile]:
        ret,errors=checkmodtrivial(mods[mfile][cat],cat,0,mfile,errors)
        if ret and cat in unlist:
            for elem in mods[mfile][cat]:
                ret,errors=checkmodtrivial(elem,cat,1,mfile,errors)
                if ret:

                    if cat not in testsublevel:
                        allitems[(cat,elem[unlist[cat]])]=allitems.get((cat,elem[unlist[cat]]),[])
                        allitems[(cat,elem[unlist[cat]])].append(mfile)
                    else:
                        for lelem in elem.get(testsublevel[cat],[]):
                            allitems[(cat,elem[unlist[cat]],lelem)]=allitems.get((cat,elem[unlist[cat]]),[])
                            allitems[(cat,elem[unlist[cat]],lelem)].append(mfile)

                    if cat in lngcat:
                        errors=checkelemlangs(cat,elem,langmod,lang,errors,mfile)
                    if cat in ["crafts","ufos","terrains","facilities"]:
                        mods[mfile]["MCPdata"]["modspecfiles"]=mngextrafileelem(mods[mfile]["MCPdata"]["modspecfiles"],cat,elem,origmaps,origterrain)

    mods[mfile],errors=checkspecfilepaths(mods[mfile],errors,mfile,True)
    if mfile.replace(mods[mfile]["MCPdata"]["base"]+"/","") in mods[mfile]["MCPdata"]["unusedfiles"]:#modfile  is used
        mods[mfile]["MCPdata"]["unusedfiles"].remove(mfile.replace(mods[mfile]["MCPdata"]["base"]+"/",""))
    for x in mods[mfile]["MCPdata"]["unusedfiles"]:#unused file => error
        errors.append(("not referenced file found",x,mfile))

    errors=checkref(mods[mfile],errors,mfile)
    errors=checkmodlogic(mods[mfile],orig,errors,mfile)
    #errors=checkmodlogic(orig,orig,errors,"orig")

    with open("res.rul", 'w', encoding='utf_8_sig') as fh:
        fh.write(prepareoutput(mods[mfile]))

for x in allitems:
    if len(allitems[x])>1:
        errors.append(tuple(["an item reoccurs in another mod",x]+allitems[x]))


errshow=999
for error in errors:
    if not error[0] in errorlist:
        print ("NO ENTRY FOR ERROR! "+error[0])
    elif errorlist.get(error[0],[-1])[0]>=errshow:
        print (error)
for e in preerrorlist: print ((len([x for x in errors if e[0]==x[0]]),e[0]))
#for e in [x for x in errors if x[0]=="extrasprite/sound is not ruleset-referenced"]:print ((e))
#for e in [x for x in errors if x[0]=="file/dir not found"]:print ((e))
#for e in [x for x in errors if x[0]=="no connected file entry found for ruleset-referenced"]:print ((e))
#for e in [x for x in errors if x[0]=="new sprite/sound is referenced multiple times"]:print ((e))
#for e in [x for x in errors if x[0]=="redefines original sprite/sound"]:print ((e))
#for e in [x for x in errors if x[0]=="an item reoccurs in another mod"]:print ((e))
#for e in [x for x in errors if x[0]=="missing research referenced"]:print ((e))
#for e in [x for x in errors if x[0]=="missing item referenced"]:print ((e))








