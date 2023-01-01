from PIL import Image
import glob, math, itertools, copy, re , os, struct, zipfile
from werkzeug import secure_filename
#from config import 
from modules.config import staticpath
from functools import partial


relpos=[(16,0),(32,8),(0,8),(16,16)]

def combinesprites(pathglob,nrcols,outfn):
    ifns=[fn for fn in glob.glob(pathglob) if fn.lower().endswith(".gif") or fn.lower().endswith(".png")]
    ifns.sort()
    if ifns:
        ifiles=[]
        first=Image.open(ifns[0])
        out=Image.open(ifns[0])
        for x in range(first.size[0]):
            for y in range(first.size[1]):
                out.putpixel((x,y),0)
        for fn in ifns:
            ifiles.append(Image.open(fn))
            ifiles[-1].palette=first.palette
        out=out.resize((first.size[0]*nrcols,first.size[1]*int(math.ceil(len(ifns)/nrcols))))
        addx=0
        addy=0
        for i,im in enumerate(ifiles):
            for x in range(first.size[0]):
                for y in range(first.size[1]):
                    out.putpixel((addx+x,addy+y),im.getpixel((x,y)))
            if addx+first.size[0] < out.size[0]:
                addx+=first.size[0]
            else:
                addx=0
                addy+=first.size[1]
        out.save(outfn,optimize=False,transparency=0)

def fixpalette(ifn,imp):
    mim=Image.open(ifn)    
    opal=[tuple([y for y in imp.palette.palette[x*3:x*3+3]]) for x in range(len(imp.palette.palette)//3)]    
    fpal=[]
    if (mim.mode in ["RGB","RGBA"]):
        im=mim.convert(mode="P")        
    else:
        im=Image.open(ifn)    
        fpal=[tuple([y for y in im.palette.palette[x*3:x*3+3]]) for x in range(len(im.palette.palette)//3)]
    im.palette.palette=imp.palette.palette
    for x in range(mim.size[0]):
        for y in range(mim.size[1]):
            c=mim.getpixel((x,y))
            if (mim.mode in ["RGBA"] and c[3]==0) :
                im.putpixel((x,y),0)     
            elif mim.mode in ["RGB","RGBA"] and c[0:3] in opal:
                im.putpixel((x,y),opal.index(c[0:3]))
            elif mim.mode in ["P"] and fpal[c] in opal:
                im.putpixel((x,y),opal.index(fpal[c]))
            else:
                im.putpixel((x,y),0)                
    return im

def paletteop(ifn,resfn,op):    
    imp=Image.open(staticpath+"static/img/pal/"+secure_filename(op["pal"])+".mini.png")

    if (op["op"]=="fix"):
        im=fixpalette(ifn,imp)        
    else:
        im=Image.open(ifn)    
    if (op["op"]=="transform"):
        transdict={}
        for l in op.get("cols",{}):
            for i in range(int(op["cols"][l][1])):
                transdict[int(l)+i]=int(op["cols"][l][0])+i
        for x in range(im.size[0]):
            for y in range(im.size[1]):
                c=im.getpixel((x,y))
                if c in transdict:
                    im.putpixel((x,y),transdict[c])

    im.putpalette([imp.palette.palette[x] for x in range(len(imp.palette.palette))])
    if op.get("maketrans",True):
        im.save(resfn,optimize=False,transparency=0)
    else:
        tim=Image.open(staticpath+"static/img/pal/notrans.png")
        tim=tim.resize(im.size)
        for x in range(im.size[0]):
            for y in range(im.size[1]):
                c=im.getpixel((x,y))
                tim.putpixel((x,y),c)
        tim.putpalette([imp.palette.palette[x] for x in range(len(imp.palette.palette))])
        tim.save(resfn,optimize=False)


def spriteconv(data,fns,fname,resdir):
    mode=data.get("op",{}).get("mode","UNKNOWNMODE")
    out=data.get("op",{}).get("out","PNG")
    maxcolnr=max(1,data.get("op",{}).get("maxcolnr",1))
    width=max(1,data.get("op",{}).get("width",320))
    height=max(1,data.get("op",{}).get("height",200))
    pal=data.get("pal","ufo-battlescape")
    if mode=="magic":
        for k in data.get("op",{}).get("files",{}):
            if re.sub('[^A-Za-z0-9-_]', '_', k)==data.get("fname",""):
                mode=data["op"]["files"][k][0]
                width=data["op"]["files"][k][1]
                height=data["op"]["files"][k][2]
    ims=[]
    if mode=="DAT":
        img_size=width*height
        with open(fns[0],"rb")as fh:
            while True:                
                buf=fh.read(img_size)  
                if not buf: break                            
                ims.append([int(x) for x in buf])
    if mode=="SPK":
        im=[]
        with open(fns[0],"rb")as fh:
            while True:                
                buf=fh.read(2)
                if int(buf[0])==255 and int(buf[1])==255:
                    buf=fh.read(2)
                    for x in range(2*(int(buf[0])+int(buf[1])*256)):
                        im.append(0)
                if int(buf[0])==254 and int(buf[1])==255:
                    buf=fh.read(2)
                    buf=fh.read((int(buf[0])+int(buf[1])*256)*2)
                    for x in range(len(buf)):
                        im.append(int(buf[x]))
                if not buf: 
                    break            
                if int(buf[0])==253 and int(buf[1])==255: break
            ims.append(im)
    if mode=="BDY":
        im=[]        
        rpos=0
        with open(fns[0],"rb")as fh:
            while True:                
                buf=fh.read(1)
                if not buf: break
                if (int(buf[0])>=129):
                    c=int(fh.read(1)[0])
                    for x in range(min(width-rpos,257-int(buf[0]))):
                        im.append(c)
                    rpos+=257-int(buf[0])
                else:
                    buf=fh.read(int(buf[0])+1)
                    for x in range(min(width-rpos,len(buf))):
                        im.append(int(buf[x]))
                    rpos+=len(buf)
                if (rpos>=width): rpos=0                
            ims.append(im)
    if mode=="PCK":
        tfile=[fn for fn in fns if fn.upper().endswith(".TAB")][0]
        pfile=[fn for fn in fns if fn.upper().endswith(".PCK")][0]
        #print(tfile)
        #print(pfile)
        im=[]        
        framesize="H"
        with open(tfile,"rb")as fh:
            buf=fh.read(4)
            if struct.unpack("I",buf)[0]==0: framesize="I"
        ppos=[]
        with open(tfile,"rb")as fh:
            while True:                
                buf=fh.read( struct.calcsize(framesize))
                if not buf: break
                ppos.append(struct.unpack(framesize,buf)[0])
        with open(pfile,"rb")as fh:
            for pos in ppos:
                im=[]
                fh.seek(pos)
                buf=fh.read(1)
                for x in range(int(buf[0])*width):
                    im.append(0)
                while True:   
                    buf=fh.read(1)
                    if int(buf[0])==255:
                        break
                    elif int(buf[0])==254:
                        buf=fh.read(1)
                        for x in range(int(buf[0])):
                            im.append(0)
                    else:
                        im.append(int(buf[0]))
                ims.append(im)
    if mode in ["PNG2PCK","PNG2ZIP"]:
        bim=Image.open(fns[0])
        for iy in range(bim.size[1]//height):
            for ix in range(bim.size[0]//width):
                im=[]
                firstc=bim.getpixel((ix*width,iy*height))
                checkempty=True
                for y in range(height):        
                    for x in range(width):
                        c=bim.getpixel((ix*width+x,iy*height+y))
                        if checkempty:
                            checkempty = (c==(firstc if x%2==0 or y%2==0 else 0))
                        im.append(c)
                #print (ix,iy,firstc,checkempty)
                if not checkempty:
                    ims.append(im)



    resfile=None
    newfns=[]
    #print([len(x) for x in ims])
    inr=0
    for idat in ims:
        im=Image.open(staticpath+"static/img/pal/"+secure_filename(pal)+".mini.png")
        im=im.resize((width,height))
        for x in range(width):
            for y in range(height):
                if x+y*width<len(idat):
                    im.putpixel((x,y),idat[x+y*width])
                else:
                    im.putpixel((x,y),0)
        newfns.append(resdir+os.sep+fname+"_%04d.png"%inr)
        im.save((newfns[-1]),optimize=False,transparency=0)
        inr+=1
    if mode=="PNG2ZIP":
        resfile=resdir+os.sep+"png~result.zip"
        with zipfile.ZipFile(resfile,mode='w',compression=zipfile.ZIP_DEFLATED) as zf:
            for nfn in newfns:
                zf.write(nfn,nfn.split(os.sep)[-1])
    if mode=="PNG2PCK":
        tabdata=bytearray([])
        pckdata=bytearray([])
        warntxt=""
        for inr,im in enumerate(ims):
            emptylines=0
            if len(pckdata)>=256**2:
                warntxt+="the pck format can not contain unlimited images the exact number depends on the amount of transparent pixel in the source image we stopped with image {} \r\n".format(inr)
                break            
            tabdata.append(len(pckdata)%256)
            tabdata.append(len(pckdata)//256)
            for ln in range(height):
                #if inr==0: print(ln,[im[ln*width+x] for x in range(width)])
                if sum([im[ln*width+x] for x in range(width)])==0:
                    emptylines+=1
                else:
                    break
            pckdata.append(emptylines) 
            pos=emptylines*width
            while pos<len(im):
                if (im[pos]==0):
                    if sum([im[x] for x in range(pos,len(im))])==0:
                        break
                    epix=0
                    for ec in range(255):
                        if pos+ec<len(im) and (im[pos+ec]==0):
                            epix+=1
                        else:
                            break
                    pckdata.append(254) 
                    pckdata.append(epix) 
                    pos+=epix
                elif (im[pos]in [254,255]):
                    pckdata.append(254) 
                    pckdata.append(1) 
                    warntxt+="image nr: {} - the source image contained a pixel with color index {} that is not allowed in PCK and was replaced with transparent pixel at {} {}\r\n".format(inr,im[pos],pos%width,pos//width)
                    pos+=1
                else:
                    pckdata.append(im[pos]) 
                    pos+=1  
            pckdata.append(255) 
            #print (inr,len(im),emptylines,height)
        pckfns=[]
        pckfns.append(resdir+os.sep+fname+".PCK")
        pckfns.append(resdir+os.sep+fname+".TAB")
        if warntxt:
            pckfns.append(resdir+os.sep+"WARNING.txt")
            with open(pckfns[-1],"w") as fh:
                fh.write(warntxt)
        with open(pckfns[0],"wb") as fh:
            fh.write(pckdata)
        with open(pckfns[1],"wb") as fh:
            fh.write(tabdata)


        resfile=resdir+os.sep+"png~resultpck.zip"        
        with zipfile.ZipFile(resfile,mode='w',compression=zipfile.ZIP_DEFLATED) as zf:
            for pnfn in pckfns:
                zf.write(pnfn,pnfn.split(os.sep)[-1])



            #if inr==0: print (inr,len(im),emptylines,height)


    if out=="PNG":
        maxcolnr=min(maxcolnr,len(ims))        
        if len(ims)%maxcolnr != 0:
            for z in range(maxcolnr-len(ims)%maxcolnr):
                im=Image.open(staticpath+"static/img/pal/"+secure_filename(pal)+".mini.png")
                im=im.resize((width,height))
                for x in range(width):
                    for y in range(height):
                        im.putpixel((x,y),96 if x%2==0 or y%2==0 else 0)
                im.save(resdir+os.sep+fname+("_%04d.png"%inr),optimize=False,transparency=0)
                inr+=1
        resfile=resdir+os.sep+"png~result.png"
        combinesprites(resdir+os.sep+"*.png",maxcolnr,resfile)

    return resfile


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
            20:dict(animcount=4,blocks=[0,1,2,3],
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
    dsdict[21]=copy.deepcopy(dsdict[5])
    del(dsdict[21]["standing"])
    dsdict[21]["walking"]["spritein"]=[x-8*4 for x in dsdict[21]["walking"]["spritein"]]
    dsdict[21]["backspriting"]=[(i,d,[0,1,2,3],[a+d*16+y*4 for y in range(4)]) for i,(a,d) in enumerate(itertools.product(range(4),range(8)))]
    dsdict[20]["backspriting"]=[(i,d,[0,1,2,3],[a+d*20+y*5 for y in range(4)]) for i,(a,d) in enumerate(itertools.product(range(5),range(8)))]

    for x in dsdict:
        dsdict[x]["animcount"]=dsdict[x].get("animcount",8)
        dsdict[x]["directions"]=dsdict[x].get("directions",8)
        dsdict[x]["blocks"]=dsdict[x].get("blocks",[3])
    return dsdict


def makeimages(dtype=0,spritepath="",baseimg="",rescomb="",drout=0,uopt={},colnr=8):
    """dtype=0 -> makes im list to animations
    dtype=1 -> makes im list to hwp template
    dtype=2 -> hwp template to hwp sprites
    """
    #print ((spritepath))
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
def splitspriteimg(fn,name):    
    fni=Image.open(fn)
    i=0
    for y in range(0,fni.size[1],40):
        for x in range(0,fni.size[0],32):
            sprite=fni.crop((x,y,x+32,y+40))
            sprite.save(name.format(fn,i),optimize=False,transparency=0)
            i+=1
def getsize(resfn):
    return Image.open(resfn).size    