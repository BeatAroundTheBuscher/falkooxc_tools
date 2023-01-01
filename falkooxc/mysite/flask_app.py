#from __future__ import print_function
#from __future__ import unicode_literals
#from __future__ import division

#armor numbers
#ufopaedia crashes
#palette can be autofixed



import yaml,copy,glob,os,pickle,itertools,math,datetime,tempfile,base64
from PIL import Image

from oxcmodhelper1 import *
from specific import *



##if web!="web":
##    yaml.add_representer(dict,represent_dict) #NOWEB
##    yaml.add_representer( NumList, numlist_rep ) #NOWEB
yaml.add_representer(dict,represent_dict) #NOWEB
yaml.add_representer( NumList, numlist_rep ) #NOWEB



if web=="web":
    import shutil
    from zipfile import ZipFile
    from flask import Flask, request, session,  redirect, url_for, abort,render_template, flash ,send_file #WEB



#testmodfixes
#FIX basic weapons delted es/es-419  strings
#FIX tanks delted pl language
#TODO tidy up armout and hwp
#TODO dartrifle corpse unlock -> plasmaOR style
#elerium mace rename rulesets -> ruleset
#move GLOVE inte a new Resources folder

arguments=[]
#arguments.append("totest/fmp")
#arguments.append("totest/mib")
#arguments.append("totest/fmp0.5.5")

#arguments.append("totest/medigas")
#arguments.append("totest/0_pirates_73")


#arguments.append("totest")
#arguments.append("fixed")


fixme=dict(pathcaseextrafiles=False,removevanillavalues=True,langswitch=[('en-GB','en-US',1,''),('en-US','en-GB',1,''),('en-US','fi',0,'T:'),('en-US','es-419',0,'T:')])
fixme=dict(pathcaseextrafiles=True,removevanillavalues=True,langswitch=[('en-GB','en-US',1,''),('en-US','en-GB',1,'')])
#fixme=dict(pathcaseextrafiles=False,removevanillavalues=False,langswitch=[],test_lngs=['en-US','en-GB'])



options=dict(
saveres=True,
reloadorig=False,
showerror=True
)


#delete no change-values (copy/edit xcom1rul -> new mod?)
#combine images
#reset fileids



### END OF ARGUMENTS #############



#todo:
#('extrasprite/sound is not ruleset-referenced', 'extraSprites', 'sectoidInventoryImage', 0, 'Resources/AlienInventory/sectoid.png', 'totest/AlienInventoryMod/AlienInventoryMod/Ruleset/AlienInventory.rul')
#('references spritesheet does misses images', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'extraSprites', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
#('a sprite sheet is bigger than needed', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'extraSprites', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
#('no connected file entry found for ruleset-referenced', 'items', 'STR_TOXIGUN', 'bulletSprite', 'Projectiles', 'totest/Alien Armoury Expanded_1.3/Ruleset/AlienArmouryExpanded.rul')
#dir/files screwed in Combat-UniformArmors
#

def startmod(arguments,fixme,options):
    mods={}
    orig,lang=getorigdata(options.get("reloadorig",False))
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
        #if mfile.startswith("fixed/Dioxine_Piratez_Mod_0_69"):continue
       # if mfile.split("/")[1].startswith("0"):continue

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
        langmod,errors=checkmodlangs(mods[mfile],errors,fixme.get("test_lngs",[]),mfile)
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

        if options.get("saveres",False):
##            openparams={} if web=="web" else dict(encoding="ascii",errors="ignore")
##            openparams=dict(encoding="ascii",errors="ignore")
            openparams=dict(encoding="utf-8-sig",errors="ignore")
            with open(predir+"res.rul", 'w', **openparams) as fh:
                fh.write(prepareoutput(mods[mfile]))

    for x in allitems:
        if len(allitems[x])>1:
            errors.append(tuple(["an item reoccurs in another mod",x]+allitems[x]))

    if options.get("showerror",False):
        errshow=-9990
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


    ret={"errors":errors}
    return ret



if __name__ == "__main__":
    pass

    i=fixpalette(Image.open("tmp/MoriartyPlasmaCannonBasebits.png"),Image.open("orig/ufo-basescape.act.png"))
    i.save("tmp/MoriartyPlasmaCannonBasebits_fixed.png")
    #fixpalette(Image.open("tmp/C14Gauss.gif"),Image.open("orig/ufo-battlescape.act.png"))


####    ret=startmod(arguments,fixme,options)
##
####    makeconv("1,2,9,10,5,6,7,8,3,4,11,12,13,14,15,","cut.png","newconv.png")
####    im=convertpal(Image.open("newconv.png"),Image.open("out5a.png"),Image.open("out5a.png"),Image.open("out5a.png"),[0,0,0])
####    im.save("test11.png",optimize=False,transparency=0)
##
####    combinesprites("odata/ufo/tanks/*.gif",8,"out.png")
####    im=Image.open("out.png")
####    for y in range(im.size[1]):
####        if y%40!=0:continue
####        for x in range(im.size[0]):
####            im.putpixel((x,y),120)
####    im.save("test4.png",optimize=False,transparency=0)
##
####    combinesprites("odata/tftd/tdxcom_0/*.gif",16,"new8.png")
####    combinesprites("odata/tftd/tdxcom_1/*.gif",16,"new9.png")
####    combinesprites("odata/tftd/tdxcom_2/*.gif",16,"new10.png")
##
###TODO fix makegif standing, armor>10
##
####    combinesprites("odata/ufo/ethereal/*.gif",8,"new7.png")
###    combinesprites("odata/ufo/xcom_0/*.gif",8,"new6.png")
####    combinesprites("odata/ufo/tanks/*.gif",8,"new3.png")
####    combinesprites(r"C:\Users\fr\Desktop\oxcom\bbstoolkit\bb_tact\island*\*.gif",5,"new4.png")
######    combinesprites(r"C:\Users\fr\Desktop\oxcom\bbstoolkit\bb_tact\sea\*.gif",5,"new4.png")
####
####
####    im=convertpal(Image.open("ipconvC.png"),Image.open("new4.png"),Image.open("orig/ufo-battlescape.act.png"),Image.open("orig/tftd-depth0.act.png"),[0,0,0])
####    im.save("test1.png",optimize=False,transparency=0)
####    im=convertpal(Image.open("ipconvC.png"),Image.open("new4.png"),Image.open("orig/ufo-battlescape.act.png"),Image.open("orig/tftd-depth0B.act.png"),[0,0,0])
####    im.save("test2.png",optimize=False,transparency=0)
####    im=convertpal(Image.open("ipconvC.png"),Image.open("new4.png"),Image.open("orig/ufo-battlescape.act.png"),Image.open("orig/tftd-depth0C.act.png"),[0,0,0])
####    im.save("test3.png",optimize=False,transparency=0)
####    palstuff()
##
##
####    for a in ["man_"+str(i)+g+str(j) for i,g,j in itertools.product([0],["M","F"],range(4))]+["man_2","man_3"]:
#####    for a in ["man_"+str(i)+g+str(j) for i,g,j in itertools.product([1],["M","F"],range(4))]:
#####    for a in [1]:
####        for i in range(1,15):
#####            im=Image.open("new6.png")
####            im=Image.open("odata/ufo/inv/"+a+".gif")
####            tmp=bytearray(im.palette.palette)
####            tmp[0]=i
####            tmp[2]=i
####            im.save("tmp.png",optimize=False,transparency=0)
####            tmpim=Image.open("tmp.png")
####            tmpim.palette.palette=bytes(tmp)
####            tmpim.save("tmp.png",optimize=False,transparency=0)
####            im=convertpal(Image.open("ipconvCArmor.png"),Image.open("tmp.png"),Image.open("orig/ufo-battlescape.act.png"),Image.open("tmp.png"),[0,0,0])
####            im.save("abi"+a+str(i)+".png",optimize=False,transparency=0)
##
##
####    import struct
####    im=Image.open("orig/p_research_ufopaedia_WASPITE_AUTOPSY.gif")
####    a = bytearray()
####    for i in range(256):
####        for x in range(3):
####            a.extend(struct.pack("B",im.palette.palette[i*3+x]))
####    with open("test.act","wb") as fh:
####        fh.write(bytes(a))
##
##
##
##    #i2=Image.open("orig/p_research_ufopaedia_WASPITE_AUTOPSY.gif")
##   # im.palette.palette=i2.palette.palette
##    #im.save("orig/ufo-research.p.png")
####    combinesprites("tank01/*.gif",16,"out.png")
##    #
####    makeimages(dtype=2,spritepath="tmp/temp5b.png",baseimg="cut.png",rescomb="tmp/tempsp5.png",drout=5,colnr=16)
####    makeimages(dtype=2,spritepath="tmp/templ2.png",baseimg="cut.png",rescomb="tmp/tempsp2.png",drout=2)
####    makeimages(dtype=2,spritepath="tmp/temp3.png",baseimg="cut.png",rescomb="tmp/tempsp3.png",drout=3)
####
####    makeimages(dtype=2,spritepath="tmp/templ11.png",baseimg="cut.png",rescomb="tmp/tempsp11.png",drout=11)
####    makeimages(dtype=2,spritepath="tmp/templ12.png",baseimg="cut.png",rescomb="tmp/tempsp12.png",drout=12)
####    makeimages(dtype=2,spritepath="tmp/templ19.png",baseimg="cut.png",rescomb="tmp/tempsp19.png",drout=19,colnr=10)
####    makeimages(dtype=2,spritepath="tmp/templ20.png",baseimg="cut.png",rescomb="tmp/tempsp20.png",drout=20)
####
####    makeimages(dtype=2,spritepath="tmp/template2.png",baseimg="cut.png",rescomb="tmp/res2.png",drout=2)
####    makeimages(dtype=2,spritepath="tmp/template5a.png",baseimg="cut.png",rescomb="tmp/res5a.png",drout=5)
####    makeimages(dtype=2,spritepath="tmp/template5b.png",baseimg="cut.png",rescomb="tmp/res5b.png",drout=5)
####    makeimages(dtype=2,spritepath="tmp/template3.png",baseimg="cut.png",rescomb="tmp/res3.png",drout=3)
####    makeimages(dtype=2,spritepath="tmp/template11.png",baseimg="cut.png",rescomb="tmp/res11.png",drout=11)
####    makeimages(dtype=2,spritepath="tmp/template12.png",baseimg="cut.png",rescomb="tmp/res12.png",drout=12)
####    makeimages(dtype=2,spritepath="tmp/template20.png",baseimg="cut.png",rescomb="tmp/res20.png",drout=20)
####    makeimages(dtype=2,spritepath="tmp/template19.png",baseimg="cut.png",rescomb="tmp/res19.png",drout=19)
####
####    combinesprites("odata/ufo/x_reap/*.gif",8,"out5a.png")
####    combinesprites("odata/ufo/x_rob/*.gif",8,"out5b.png")
####
####
####    makeimages(dtype=1,spritepath="odata/ufo/tanks/*.gif",baseimg="cut.png",rescomb="tmp/template2.png",drout=2)
####    makeimages(dtype=1,spritepath="odata/ufo/x_reap/*.gif",baseimg="cut.png",rescomb="tmp/template5a.png",drout=5)
####    makeimages(dtype=1,spritepath="odata/ufo/x_rob/*.gif",baseimg="cut.png",rescomb="tmp/template5b.png",drout=5)
####    makeimages(dtype=1,spritepath="odata/ufo/cyber/*.gif",baseimg="cut.png",rescomb="tmp/template3.png",drout=3)
####    makeimages(dtype=1,spritepath="odata/tftd/tank01/*.gif",baseimg="cutb0.png",rescomb="tmp/template11.png",drout=11)
####    makeimages(dtype=1,spritepath="odata/tftd/hallucin/*.gif",baseimg="cutb0.png",rescomb="tmp/template12.png",drout=12)
####    makeimages(dtype=1,spritepath="odata/tftd/xarquid/*.gif",baseimg="cutb0.png",rescomb="tmp/template20.png",drout=20)
####    makeimages(dtype=1,spritepath="odata/tftd/triscen/*.gif",baseimg="cutb0.png",rescomb="tmp/template19.png",drout=19)
####
####
####    makeimages(dtype=1,spritepath="UNITS/PLASMA/*.gif",baseimg="cut.png",rescomb="tmp/temp5x1.png",drout=5)
####    makeimages(dtype=1,spritepath="UNITS/LASER/*.gif",baseimg="cut.png",rescomb="tmp/temp5x2.png",drout=5)
####    makeimages(spritepath="UNITS/PLASMA/*.gif",baseimg="cut.png",rescomb="tmp/x_s1.png",drout=5)
####    makeimages(spritepath="UNITS/LASER/*.gif",baseimg="cut.png",rescomb="tmp/x_s2.png",drout=5)
####
####
####    makeimages(spritepath="odata/tftd/tank01/*.gif",baseimg="cutb0.png",rescomb="tmp/tank01a.png",drout=11,uopt=dict(fly=True,turretType=4))
####    makeimages(spritepath="odata/tftd/tank01/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/tank01b.png",drout=11,uopt=dict(fly=False,turretType=1))
####    makeimages(spritepath="odata/tftd/triscen/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/triscen.png",drout=19)
####    makeimages(spritepath="odata/tftd/xarquid/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/xarquid.png",drout=20)
####    makeimages(spritepath="odata/tftd/hallucin/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/hallucin.png",drout=12)
####    makeimages(spritepath="odata/tftd/tentac/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/tentac.png",drout=18)
####    makeimages(spritepath="odata/tftd/biodron/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/biodron.png",drout=15)
####    makeimages(spritepath="odata/tftd/civil_1/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/civil_1a.png",drout=17)
####    makeimages(spritepath="odata/tftd/civil_2/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/civil_2a.png",drout=17)
####    makeimages(spritepath="odata/tftd/civil_1/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/civil_1b.png",drout=16)
####    makeimages(spritepath="odata/tftd/civil_2/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/civil_2b.png",drout=16)
####    makeimages(spritepath="odata/tftd/zombie/*.gif",baseimg="cutb0.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/tftdzombie.png",drout=16)
####    makeimages(spritepath="odata/ufo/silacoid/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/silacoid.png",drout=8)
####    makeimages(spritepath="odata/ufo/celatid/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/celatid.png",drout=9)
####    makeimages(spritepath="odata/ufo/civf/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/civf.png",drout=4)
####    makeimages(spritepath="odata/ufo/civm/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/civm.png",drout=4)
####    makeimages(spritepath="odata/ufo/ethereal/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/ethereal.png",drout=4)
####    makeimages(spritepath="odata/ufo/zombie/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/zombie.png",drout=4)
####    makeimages(spritepath="odata/ufo/tanks/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/tanksa.png",drout=2,uopt=dict(fly=True,turretType=4))
####    makeimages(spritepath="odata/ufo/tanks/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/tanksb.png",drout=2,uopt=dict(fly=False,turretType=1))
####    makeimages(spritepath="odata/ufo/cyber/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/cyber.png",drout=3)
####    makeimages(spritepath="odata/ufo/x_reap/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/x_reap.png",drout=5)
####    makeimages(spritepath="odata/ufo/x_rob/*.gif",baseimg="cut.png",combimg="new.gif",rescut="cutme2.png",rescomb="tmp/x_rob.png",drout=5)
##
##    #errors=ret["errors"]
##    #for e in preerrorlist: print ((len([x for x in errors if e[0]==x[0]]),e[0]))
##
####    allrulfiles=[]
####    allxrulfiles=[]
####    allfiles=[]
####    alldirs=[]
#####    for args in ["odata/tftd"]:
####    for args in ["odata/ufo/inv"]:
####        for root,dirs,files in os.walk(args):
####            for d in dirs:
####                alldirs.append(os.path.join(root,d).replace("\\","/"))
####            for f in files:
####                allfiles.append(os.path.join(root,f).replace("\\","/"))
####                if f.endswith(".rul"):
####                    allrulfiles.append(os.path.join(root,f).replace("\\","/"))
####                if f.endswith(".xrul"):
####                    allxrulfiles.append(os.path.join(root,f).replace("\\","/"))
######    for pfn in glob.glob("orig/*.act"):
######        b=Image.open("odata/tftd/triscen/triscen_000_0.gif")
######    #    with open("orig/Battlescape-Depth0.act","rb") as fh:
######
######        with open(pfn,"rb") as fh:
######            p=fh.read()
######            np=(5).to_bytes(1,byteorder="big")
######            for c in p:
######                #print ((c))
######                np+=c.to_bytes(1,byteorder="big")
######            print ((len(b.palette.palette),len(np[1:-4])))
######            b.palette.palette=np[1:-4]
######        b.save(pfn+"tftd.gif",optimize=False,transparency=0)
####    b=Image.open("cut.png")
####    for fn in allfiles:
####        if "99_unchanged" in fn :continue
####        if "dontfixmeiamold" in fn :continue
####
####        if fn.endswith("gif") and not  "tac01" in fn:
####
####            im=Image.open(fn)
####            print((fn,im.mode,))
####            im.palette.palette=b.palette.palette
####            im.save(fn,optimize=False,transparency=0)
##
##
####    b=Image.open("orig/ufo-battlescape.act.png")
####    for fn in glob.glob("tiletest/timg/*/*.gif"):
####        im=Image.open(fn)
####        im.palette.palette=b.palette.palette
####        im.save(fn,optimize=False,transparency=0)
####    combinesprites("tiletest/timg/*/*.gif",8,"tiletest/test1.png")
##
##
####udata=[]
####with open(r"C:\Users\fr\Desktop\oxcom\modtest\GEODATA\LOFTEMPS.DAT","rb") as fh:
####    for x in range(112):
####        a=struct.unpack("hhhhhhhhhhhhhhhh", fh.read(32))
####        #if a!= tdata[x]:
####        print (a,x,tdata[x])
####        udata.append(a)
##
####    for pdn in glob.glob(r"tiletest\TERRAIN\*.MCD"):
####        dn=os.sep.join(pdn.split(os.sep)[0:-2])+os.sep+pdn.split(os.sep)[-1][0:-4]
####        #if not os.path.isdir(dn):continue
####        rdn=dn.replace("tiletest"+os.sep,"").lower()
####
####        if not  (96<ord(rdn[0])<123):continue
####        if not os.path.isfile("tiletest/TERRAIN/"+rdn.upper()+".TAB"):continue
####        if not os.path.isfile("tiletest/TERRAIN/"+rdn.upper()+".PCK"):continue
####        if not os.path.isfile("tiletest/TERRAIN/"+rdn.upper()+".MCD"):continue
####        #if rdn=="lightnin":continue
####        #if rdn!="desert":continue
####        #if rdn!="avenger":continue
#####        if rdn!="blanks":continue
####        #if rdn!="u_bits":continue
####        mcdfn="tiletest/TERRAIN/"+rdn.upper()+".MCD"
####        with open(mcdfn,"rb") as fh:
####            mcd=fh.read()
####            nrelems=len(mcd)//62
####            print ((mcdfn,nrelems))
####            nrfiles=len([x for x in glob.glob("tiletest/timg/{0}/*.gif".format(rdn))])
####            im=None
####
####            breaknrlist=[1,nrelems]
####            for breaknr in [x for x in range(min(10,nrelems),1,-1)]+[x for x in range(min(10+1,nrelems),nrelems)]:
######                print ((nrelems%breaknr==0,nrelems,breaknr,nrelems%breaknr))
####                if nrelems%breaknr==0:
####                    breaknrlist.append(breaknr)
####            breaknrlist.sort(key=lambda x:(0.99*x)**2+(nrelems/x)**2)
####            breaknr=breaknrlist[0]
####
####
####            ix=iy=0
####            for ei in range(nrelems):
####                pnr=mcd[ei*62+0]
####                pfn=("tiletest/timg/{0}/{0}_{1:0"+str(math.floor(math.log(nrfiles,10))+1)+"d}_0.gif").format(rdn,pnr)
#####                ph=0 if mcd[ei*62+48]==0 else (255-mcd[ei*62+48])
####                ph=mcd[ei*62+49]
######                print ((ph))
####                #ph=min(max(ph,0),40)
####                if not os.path.isfile(pfn): print (("ARGL@",pfn))
####                if im is None:
####                    im=Image.open(pfn)
####                    for x in range(32):
####                        for y in range(40):
####                            im.putpixel((x,y),0)
####                    im=im.resize((32*breaknr,math.ceil(nrelems/breaknr)*80))#nrelems*32,80))
####                timg=Image.open(pfn)
######                print((pfn,timg,im.size,ix,iy,breaknr,ph))
####                for x in range(32):
####                    for y in range(40):
####                  #      if ix>=1792:print (((x+ix,y+40-ph+iy),im.size))
####                        im.putpixel((x+ix,y+40-ph+iy),timg.getpixel((x,y)))
####                if ei%breaknr==(breaknr-1):
####                    ix=0
####                    iy+=80
####                else:
####                    ix+=32
####                #print ((ei,pnr,ph,pfn,ix,iy,))
####
####            im.save("tiletest/timg/"+rdn+".png",optimize=False,transparency=0)
####
####            import base64
####            with open("tiletest/timg/"+rdn+".png","rb") as ifh:
####                bstr=base64.b64encode(ifh.read())
####                with open("tiletest/"+rdn+".tsx","w") as tsxfh:
####                    tsxfh.write("""<?xml version="1.0" encoding="UTF-8"?>
####<tileset name='"""+rdn+"""' tilewidth="32" tileheight="80">
####  <image format="png" width="256" height="720" ><data encoding="base64" >"""+bstr.decode("utf-8")+"""</data></image>
####</tileset>""")
##
##                #print ((bstr))
####        print ((dn,rdn[0]))
##
####from PIL import ImageDraw
####
####maxrmp=128
####breaknr=8
####
####
####im=Image.open(r"odata\ufo\ethereal\ethereal_00_0.gif")
#####im=Image.open(r"odata\ufo\civf\civf_00_0.gif")
####for x in range(32):
####    for y in range(40):
####        im.putpixel((x,y),0)
####im=im.resize((breaknr*32,(math.ceil(maxrmp/breaknr)*40)))
####txt = ImageDraw.Draw(im)
####ix=iy=0
####for i in range(maxrmp):
####    tim=Image.open(r"odata\ufo\ethereal\ethereal_0"+str(i%8)+"_0.gif")
#####    tim=Image.open(r"odata\ufo\civf\civf_0"+str(i%8)+"_0.gif")
####    for x in range(32):
####        for y in range(40):
####            c=tim.getpixel((x,y))
####            im.putpixel((ix+x,iy+y),0 if c==0 else (c+(i//8-1)*16))
####    txt.text((ix+8,iy+15),"{0:03d}".format(i),255)
####    if ix==(breaknr-1)*32:
####        ix=0
####        iy+=40
####    else:
####        ix+=32
####im.save("tiletest/routes.png",optimize=False,transparency=0)
##
##
####for fn,tw,th,w,h,ox,oy in [["types",65,57,325,114,4,9],["rank",24,34,192,35,1,1],["spawn",3,30,27,30,6,-7]]: #["routes",32,40,256,1280,0,0],
####    with open("tiletest/{0}.png".format(fn),"rb") as ifh:
####        bstr=base64.b64encode(ifh.read())
####        bstrtag='<image format="png" width="{0}" height="{1}" ><data encoding="base64" >'.format(w,h)+bstr.decode("utf-8")+'</data></image>'
####        with open("tiletest/{0}.tsx".format(fn),"w") as tsxfh:
####            tsxfh.write("""<?xml version="1.0" encoding="UTF-8"?>
####<tileset name='{4}' tilewidth="{0}" tileheight="{1}"><tileoffset x="{2}" y="{3}"/>
####  """.format(tw,th,ox,oy,fn)+bstrtag+"""
####</tileset>""")
##
##    """
##('tiletest/TERRAIN/AVENGER.MCD', 59)
##('tiletest/TERRAIN/BARN.MCD', 29)
##('tiletest/TERRAIN/BLANKS.MCD', 2)
##('tiletest/TERRAIN/BRAIN.MCD', 4)
##('tiletest/TERRAIN/CULTIVAT.MCD', 37)
##('tiletest/TERRAIN/DESERT.MCD', 66)
##('tiletest/TERRAIN/FOREST.MCD', 83)
##('tiletest/TERRAIN/FRNITURE.MCD', 26)
##('tiletest/TERRAIN/JUNGLE.MCD', 82)
##('tiletest/TERRAIN/LIGHTNIN.MCD', 42)
##('tiletest/TERRAIN/MARS.MCD', 36)
##('tiletest/TERRAIN/MOUNT.MCD', 78)
##('tiletest/TERRAIN/PLANE.MCD', 65)
##('tiletest/TERRAIN/POLAR.MCD', 81)
##('tiletest/TERRAIN/ROADS.MCD', 23)
##('tiletest/TERRAIN/UFO1.MCD', 20)
##('tiletest/TERRAIN/URBAN.MCD', 112)
##('tiletest/TERRAIN/URBITS.MCD', 25)
##('tiletest/TERRAIN/U_BASE.MCD', 67)
##('tiletest/TERRAIN/U_BITS.MCD', 8)
##('tiletest/TERRAIN/U_DISEC2.MCD', 17)
##('tiletest/TERRAIN/U_EXT02.MCD', 34)
##('tiletest/TERRAIN/U_OPER2.MCD', 15)
##('tiletest/TERRAIN/U_PODS.MCD', 11)
##('tiletest/TERRAIN/U_WALL02.MCD', 47)
##('tiletest/TERRAIN/XBASE1.MCD', 97)
##('tiletest/TERRAIN/XBASE2.MCD', 62)
##"""
##maps=[]
####maps.append(("UFO1A",[("BLANKS",2),("UFO1",20)],"ufo1a"))
####for x in ["UFO_160","UFO_150"]:
####    maps.append((x,[("BLANKS",2),("U_EXT02",34),("U_WALL02",47),("U_PODS",11),("U_BITS",8)],x.lower()))
####maps.append(("UFO_140",[("BLANKS",2),("U_EXT02",34),("U_WALL02",47),("U_OPER2",15),("U_BITS",8)],"ufo140"))
####for x in ["UFO_110","UFO_120"]:
####    maps.append((x,[("BLANKS",2),("U_EXT02",34),("U_WALL02",47),("U_BITS",8)],x.lower()))
####for x in ["TUFO_130","TUFO_130","UFO_170"]:
####    maps.append((x,[("BLANKS",2),("U_EXT02",34),("U_WALL02",47),("U_DISEC2",17),("U_BITS",8)],x.lower()))
####for x in range(19):
####    maps.append(("CULTA%02d"%x,[("BLANKS",2),("CULTIVAT",37),("BARN",29)],"culta%02d"%x))
####for x in range(12):
####    maps.append(("DESERT%02d"%x,[("BLANKS",2),("DESERT",66)],"desert%02d"%x))
####for x in range(12):
####    maps.append(("FOREST%02d"%x,[("BLANKS",2),("FOREST",83)],"forest%02d"%x))
####for x in range(12):
####    maps.append(("JUNGLE%02d"%x,[("BLANKS",2),("JUNGLE",82)],"jungle%02d"%x))
####for x in range(14):
####    maps.append(("POLAR%02d"%x,[("BLANKS",2),("POLAR",81)],"polar%02d"%x))
####for x in range(13):
####    maps.append(("MOUNT%02d"%x,[("BLANKS",2),("MOUNT",81)],"mount%02d"%x))
####for x in range(11):
####    maps.append(("MARS%02d"%x,[("BLANKS",2),("MARS",36),("U_WALL02",47)],"mars%02d"%x))
####for x in range(16):
####    if x in [12,13,14]:continue
####    maps.append(("UBASE_%02d"%x,[("BLANKS",2),("U_BASE",67),("U_WALL02",47),("U_PODS",11),("BRAIN",4)],"ubase%02d"%x))
####for x in range(16):
####    if 9<x<14 :continue
####    maps.append(("URBAN%02d"%x,[("BLANKS",2),("ROADS",23),("URBITS",25),("URBAN",112),("FRNITURE",26)],"urban%02d"%x))
####
####for x in range(21):
####    maps.append(("XBASE_%02d"%x,[("BLANKS",2),("XBASE1",97),("XBASE2",62)],"xbase%02d"%x))
####for x in [("PLANE",65),("AVENGER",59)]:#LIGHNIN
####    maps.append((x[0],[("BLANKS",2),x],x[0].lower()))
##
##
##for mn,tlist,ofn in maps:
##
##
##    rmpfn="tiletest/ROUTES/"+mn+".RMP"
##    rmpdata={}
##    rmplist=[]
##    if not os.path.isfile(rmpfn):
##        print ((rmpfn,"not found"))
##    else:
##        with open(rmpfn,"rb") as rmpfh:
##            rmpinfo=rmpfh.read()
##            for n in range(math.floor(len(rmpinfo)/24)):
##                rmpi=rmpinfo[n*24:(n+1)*24]
##                #print((n,[int(x) for x in rmpi]))
##                rmplist.append([rmpi[x] for x in [y for y in range(4,19) if y%3!=2]+[0,1,2,19,20,23]])
##                rmpdata[(rmpi[0],rmpi[1],rmpi[2])]=[n]+rmplist[-1]
##                #print (";".join([mn,str(n),""]+[str(x) for x in rmpi]))
##            if len(rmpdata)!=math.floor(len(rmpinfo)/24):
##                print ("RMP len error more than one rmp for one tile?")
##    mnfn="tiletest/MAPS/"+mn+".MAP"
##    if not os.path.isfile(mnfn):
##        print ((mnfn,"not found"))
##        continue
##    with open(mnfn,"rb") as mapfh:
##        mapinfo=mapfh.read(3)
##        maph=mapinfo[2]
##        mapw=mapinfo[1]
##        mapd=mapinfo[0]
##        mapdata=mapfh.read()
##        xmlstr="""<?xml version="1.0" encoding="UTF-8"?>
##<map version="1.0" orientation="isometric" width="{0:d}" height="{1:d}" tilewidth="32" tileheight="16">""".format(mapw,mapd)
##        fgid=1
##        for t in tlist+[("types",10),("rank",8),("spawn",11)]:
##            xmlstr+='<tileset firstgid="{0:d}" source="{1}.tsx"/>'.format(fgid,t[0].lower())
##            fgid+=t[1]
####        xmlstr+='<tileset firstgid="{0:d}"  name="routes" tilewidth="32" tileheight="40" >'.format(fgid,"routes")+bstrtag
####        for t in range(128):
####            xmlstr+='<tile id="'+str(t)+'">'
####            xmlstr+='<properties>'
####            for pi,p in enumerate(["go-1","gotype-1","go-2","gotype-2","go-3","gotype-3","go-4","gotype-4","go-5","gotype-5","size","rank","spawn"]):
####                if t<len(rmplist):
####                    if p.startswith("go-"):
####                        xmlstr+='<property  name="{0}" value="{1}"/>'.format(p,{255:"inactive",254:"N",253:"E",252:"S",251:"W"}.get(rmplist[t][pi],rmplist[t][pi]))
####                    else:
####                        xmlstr+='<property  name="{0}" value="{1}"/>'.format(p,rmplist[t][pi])
####                else:
####                    xmlstr+='<property  name="{0}" value="{1}"/>'.format(p,"-")
####            xmlstr+='</properties>'
####            xmlstr+='</tile>'
####
####
####
####        xmlstr+='</tileset>'
##        checkdouble=[]
##        for h in range(maph-1,-1,-1):
##            for li,l in [(0,"Ground"),(3,"Objects"),(1,"NW-Wall"),(2,"NE-Wall"),(-1,"Types"),(-2,"Rank"),(-3,"Spawn")]:
##                xmlstr+='<layer name="{0}" width="{1:d}" height="{2:d}"  visible="{3:d}">'.format(l+"-"+str(maph-h),mapw,mapd,1 if h==maph-1 else 0)
##                xmlstr+='<data encoding="csv">'
##                tmpstr=""
##                if li>=0:
##                    for x in range(0,mapw*mapd*4,4):
##                        if mapdata[h*mapw*mapd*4+x+li]==0:
##                            tmpstr+="0,"
##                        else:
##                            tmpstr+=str(mapdata[h*mapw*mapd*4+x+li]+1)+","
##
##                else:
##                    for x in range(0,mapw*mapd):
##                        w=x//mapw
##                        d=mapw-(x%mapw)
##                        if (w,mapw-d,h) in rmpdata:
##                            if li==-1:
##                                tmpstr+=str(fgid-29+rmpdata[(w,mapw-d,h)][-3]+(5 if rmpdata[(w,mapw-d,h)][-1]==0 else 0))+","
##                            elif li==-2:
##                                tmpstr+="0," if rmpdata[(w,mapw-d,h)][-2]==0 else (str(fgid-19+rmpdata[(w,mapw-d,h)][-2]-1)+",")#+(5 if rmpdata[(w,mapw-d,h)][-1]==0 else 0)
##                            elif li==-3:
##                                tmpstr+="0," if rmpdata[(w,mapw-d,h)][-1] <=1 else (str(fgid-11+rmpdata[(w,mapw-d,h)][-1]-1)+",")#+(5 if rmpdata[(w,mapw-d,h)][-1]==0 else 0)
##                            else:
##                                tmpstr+="0,"
##                        else:
##                            tmpstr+="0,"
###                        tmpstr+=str(rmpdata.get((w,mapw-d,h),[0-fgid])[0]+fgid+(128 if rmpdata.get((w,mapw-d,h),[0,0,0,0,0,0,0])[-3]==2 else 0))+","
##
##                xmlstr+=tmpstr[0:-1]
##                xmlstr+='</data>'
##                xmlstr+='</layer>'
##            for li,l in [(0,"Links")]:
##                xmlstr+='<objectgroup name="{0}" width="{1:d}" height="{2:d}"  visible="{3:d}">'.format(l+"-"+str(maph-h),mapw,mapd,1 if h==maph-1 else 0)
##                for ri,r in enumerate(rmplist):
##                    #print (r[-6:])
##                    if r[-4] == h :
##                        #print (1)
##                        #for c in range(5):
##                        x=(mapw-r[-5])*-1+mapw
##                        y=r[-6]
###                        xmlstr+='<object name="c:{8},{9},{10},{11},{12}" x="0" y="0"><polyline points="{0},{1} {2},{3} {4},{5} {6},{7}"/></object>'.format(x*16,y*16,x*16+16,y*16,x*16+16,y*16+16,x*16,y*16+16,ri,x,y,r[-5],r[-6])
##                        for c in range(5):
##                            edge={
##                                251:[r[x] if x-len(r)!=-5 else -9 for x in range(len(r))],
##                                252:[r[x] if x-len(r)!=-6 else 9+mapd for x in range(len(r))],
##                                253:[r[x] if x-len(r)!=-5 else 9+mapw for x in range(len(r))],
##                                254:[r[x] if x-len(r)!=-6 else -9 for x in range(len(r))]
##                                }
##                            if r[c*2]<len(rmplist):
##                                r2=rmplist[r[c*2]]
##                                x2=(mapw-r2[-5])*-1+mapw
##                                y2=r2[-6]
##                            elif r[c*2] in edge:
##                                r2=edge[r[c*2]]
##                                x2=(mapw-r2[-5])*-1+mapw
##                                y2=r2[-6]
##                            else:
##                                continue
##                            adddiff= 4 if (abs(x-x2)+abs(y-y2))==0 else 0
##                            if ((r[c*2],ri)) in checkdouble:
##                                checkdouble.append((ri,r[c*2]))
##                                continue
##                            checkdouble.append((ri,r[c*2]))
##                            if r2[-4]==r[-4]:
##                                xmlstr+='<object name="link:{4},{5},{6},{7}" x="0" y="0" ><polyline points="{0},{1} {2},{3} "/></object>'.format(x*16+8-adddiff,y*16+8+adddiff,x2*16+8+adddiff,y2*16+8-adddiff,ri,x,y,r[-5],r[-6])
##                            else:
##                                xmlstr+='<object name="c:{4},{5},{6},{7},{8}" x="0" y="0" type="{9:+}"><polyline points="{0},{1} {2},{3} "/></object>'.format(x*16+8-adddiff,y*16+8+adddiff,x2*16+8+adddiff,y2*16+8-adddiff,ri,x,y,r[-5],r[-6],r[-4]-r2[-4])
##
##
##                xmlstr+='</objectgroup>'
##        #print ((mnfn,len(checkdouble), [x for x in checkdouble if not (x[1],x[0]) in checkdouble]))
##        xmlstr+='</map>'
##        with open("tiletest/"+ofn+".tmx","w") as outfh:
##            outfh.write(xmlstr)
##        #print ((len(mninfo),len(mndata)))
##
##
##
####        im=Image.open(fn)
####        im.palette.palette=b.palette.palette
####        im.save(fn,optimize=False,transparency=0)
####    combinesprites("tiletest/*/*.gif",8,"tiletest/test1.png")
##


if web=="web":
    import os,shutil
    import tempfile
    from zipfile import ZipFile
    from flask import Flask, request, session,  redirect, url_for, abort,render_template, flash #WEB




    app = Flask(__name__)

    @app.route('/convpal', methods=['GET', 'POST'])
    def convpal():
        response = ""
        if request.method == 'POST' and "mfile" in request.files and request.files["mfile"]:
            directory_name = tempfile.mkdtemp()
            f = request.files['mfile']
            now=datetime.datetime.now()
            testdir="tesdH3454_%d_%d"%(now.day,random.randint(10**19,10**20-1))
            os.mkdir(directory_name+os.sep+testdir)
            fn=directory_name+os.sep+testdir+os.sep+'fn'+f.filename #werkzeug.secure_filename?
            f.save(fn)
            cfn=predir+"static/ipconvC.png"
            ffn=predir+"static/"+request.form.get("fromchoice","pal/tftd-depth0.png")
            pfn=predir+"static/"+request.form.get("tochoice","pal/ufo-battlescape.png")
            if request.form.get("fromchoice","")=="userdefined":
                ffn=fn
            if "pfile" in request.files and request.files["pfile"] and request.form.get("tochoice","")=="userdefined":
                pf=request.files['pfile']
                pfn=directory_name+os.sep+testdir+os.sep+'pfn'+pf.filename #werkzeug.secure_filename?
                pf.save(pfn)
            if "cfile" in request.files and request.files["cfile"].content_length>0:
                cf=request.files['cfile']
                cfn=directory_name+os.sep+testdir+os.sep+'cfn'+cf.filename #werkzeug.secure_filename?
                cf.save(cfn)
            if request.form.get("fromchoice","")=="mixcolours":
                ffn=fn
                pfn=fn
                cfn=directory_name+os.sep+testdir+os.sep+"newconv.png"
                makeconv(request.form.get("palorder",""),fn,cfn)
            #im1=Image.open(fn)
            #im2=Image.open(ffn)
            #im3=Image.open(pfn)
            #im4=Image.open(cfn)
            #response=repr([cfn,fn,pfn,ffn])
            resfn=directory_name+os.sep+testdir+os.sep+'res.png'
            if request.form.get("fixc15","0")=="doit":
                im=Image.open(fn)
                for x in range(im.size[0]):
                    for y in range(im.size[1]):
                        if im.getpixel((x,y))==15:
                            im.putpixel((x,y),14)
            else:
                if request.form.get("fixpal","0")=="doit":
                    im=fixpalette(Image.open(fn),Image.open(pfn))
                    im.save(fn,optimize=False,transparency=0)
                else:
                    im=convertpal(Image.open(cfn),Image.open(fn),Image.open(pfn),Image.open(ffn),[0,0,0])

            im.save(resfn,optimize=False,transparency=0)
            with open(resfn,"rb") as fh:
                response=send_file(resfn, as_attachment=True, attachment_filename='palconvsprite_%d.png'%random.randint(10**9,10**10-1))
            shutil.rmtree(directory_name,ignore_errors=True)
        return response


    @app.route('/palconvert', methods=['GET', 'POST'])
    def palconvert():
        return render_template('pal.html')


    @app.route('/getpngcomb', methods=['GET', 'POST'])
    def makesprites2png():
        response = ""
        if request.method == 'POST' and "mfile" in request.files and request.files["mfile"]:
            directory_name = tempfile.mkdtemp()
            f = request.files['mfile']
            now=datetime.datetime.now()
            testdir="test345dH3454_%d_%d"%(now.day,random.randint(10**19,10**20-1))
            os.mkdir(directory_name+os.sep+testdir)
            fn=directory_name+os.sep+testdir+os.sep+'test.zip'
            f.save(fn)
            zf=ZipFile(fn)
            zf.extractall(directory_name+os.sep+testdir)
            zf.close()
            os.remove(fn)

            #testfn=sorted([ofn for ofn in glob.glob(directory_name+os.sep+testdir+os.sep+"*.*") if ofn.lower().split(".")[-1]in allowedexts["extraSprites"] ])[0]
            testfn=directory_name+os.sep+testdir+os.sep+'newsprite_%d.png'%random.randint(10**9,10**10-1)
            combinesprites(directory_name+os.sep+testdir+"/*.*",int(request.form['nrcols']),testfn)
            with open(testfn,"rb") as fh:
                response=send_file(testfn, as_attachment=True, attachment_filename='newsprite_%d.png'%random.randint(10**9,10**10-1))
            shutil.rmtree(directory_name,ignore_errors=True)
#            for dn in [directory_name+os.sep+"test345dH345*" if dn.split("_")[1]!=str(now.day)]:
#                 shutil.rmtree(dn,ignore_errors=True)

        return response



    @app.route('/sprites2png', methods=['GET', 'POST'])
    def sprites2png():

        return render_template('sprites2png.html')


    @app.route('/gifcutter', methods=['GET', 'POST'])
    def gifcutter():
        response = ""+repr(request.form)
        if request.method == 'POST' and "gfile" in request.files and request.files["gfile"]:
            directory_name = tempfile.mkdtemp()
            f = request.files['gfile']
            now=datetime.datetime.now()
            testdir="tesdH3454_%d_%d"%(now.day,random.randint(10**19,10**20-1))
            os.mkdir(directory_name+os.sep+testdir)
            fn=directory_name+os.sep+testdir+os.sep+'fn'+f.filename #werkzeug.secure_filename?
            f.save(fn)
            resfn=directory_name+os.sep+testdir+os.sep+'res.png'
            #response=repr(int(request.form['dr']))
            makeimages(dtype=2,spritepath=fn,baseimg=predir+"static/cut.png",rescomb=resfn,drout=int(request.form['dr']))
            with open(resfn,"rb") as fh:
                response=send_file(resfn, as_attachment=True, attachment_filename='gifcutter_%d.png'%random.randint(10**9,10**10-1))
            shutil.rmtree(directory_name,ignore_errors=True)
        return response


    @app.route('/makegif', methods=['GET', 'POST'])
    def makegif():
        return render_template('gif.html')

    @app.route('/', methods=['GET', 'POST'])
    def hello_world():
        fixme=dict(pathcaseextrafiles=False,removevanillavalues=False,langswitch=[],test_lngs=['en-US','en-GB'])
        options=dict(
            saveres=True,
            reloadorig=False,
            showerror=False
        )
        arguments=[]
        files=[]
        ergerr=dict(errors=[])
        ziperrors=[]

        orig,lang=getorigdata(False)
        esel=[x[0] for x in preerrorlist]
        if "eselect[]" in request.form:
            esel=request.form.getlist("eselect[]")
        lsel=["en-GB","en-US"]
        if "lselect[]" in request.form:
            lsel=request.form.getlist("lselect[]")
        elist=[[x[0],x[1][1]]+newelevel[x[1][0] if x[1][0] in newelevel else -10]+['checked' if x[0] in esel else ""] for x in  preerrorlist]
        elist.sort(key=lambda x:x[0].lower())
        elist.sort(key=lambda x:x[2].lower())
        llist=sorted([[x,'checked' if x in lsel else ""] for x in lang],key=lambda z: z[1]+"zzzzz"+z[0])
        fopt=["Change case sensitive filepath entries","Remove unchanged vanilla properties/entries","if string only in en-XX add it to en-YY"]
        fsel=[fopt[2]]
        fsel=[]
        if "fselect[]" in request.form:
            fsel=request.form.getlist("fselect[]")
        flist=[[x,'checked' if x in fsel else ""] for x in fopt]
        if fopt[0] in fsel:fixme["pathcaseextrafiles"]=True
        if fopt[1] in fsel:fixme["removevanillavalues"]=True
        if fopt[2] in fsel:fixme["langswitch"]=[('en-GB','en-US',1,''),('en-US','en-GB',1,'')]
        fixme["test_lngs"]=lsel
        newrulstr=""
        if request.method == 'POST' and "mfile" in request.files and request.files["mfile"]:
            directory_name = tempfile.mkdtemp()
            try:
                f = request.files['mfile']
                testdir="test345dH345xd"
                os.mkdir(directory_name+os.sep+testdir)
                fn=directory_name+os.sep+testdir+os.sep+'test.zip'
                f.save(fn)
                zf=ZipFile(fn)
                zf.extractall(directory_name+os.sep+testdir)
                zf.close()
                arguments.append(directory_name+os.sep+testdir)
                os.remove(fn)
                #shutil.rmtree(fn,ignore_errors=True)
                #test_lngs=request.form.get('lang', 'en-GB,en-US').replace(" ","").split(",")
            except:
                ziperrors.append(("an error occured during the zipfile extraction","web"))
            else:

                try:
                    ergerr=startmod(arguments,fixme,options)
                    if fixme["pathcaseextrafiles"] or fixme["removevanillavalues"] or fixme["langswitch"]:
                        with open(predir+"res.rul","r") as fh:
                            newrulstr=fh.read()
                except yaml.reader.ReaderError:
                    ziperrors.append(("an error occured during modtest","web"))


            try:
                shutil.rmtree(directory_name,ignore_errors=True)
            except:
                pass
        selist=[[e[0],elevel.get(errorlist.get(e[0],[10])[0],"undefined")+":",errorlist.get(e[0],["","no description"])[1]]+list(e[1:-1])+[e[-1].split("/"+testdir+"/")[-1]] for e in ergerr["errors"]+ziperrors if e[0] in esel]
        selist.sort(key=lambda x:x[0])
        selist.sort(key=lambda x:dict([(elevel[x],x) for x in  elevel]).get(x[1][0:-1],-999),reverse=True)
        return render_template('layout.html', errorlist=elist,langlist=llist,fixlist=flist,
        errors=selist,
        langstr=""+repr((selist,elist[0:3],sorted([x for x in newelevel],reverse=True))),
        newrul=newrulstr,
        newelevel=newelevel,
        elevelsort=sorted([x for x in newelevel],reverse=True),

            )

###################################################
###################TODO############################
###################################################
#orig load -> checks new properties
#
#
#
#
#
#
#

