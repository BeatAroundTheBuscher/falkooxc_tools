from modules.config import staticpath
import glob, os

from flask import Flask, render_template
app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('empty.html')

@app.route('/rulcheck')
def rulcheck():
    return render_template('rulcheck.html', fns=[x.split(os.sep)[-1] for x in glob.glob(staticpath+"static/ruldata/*")])
@app.route('/rulformat')
def rulformat():
    return render_template('rulformat.html', fns=[x.split(os.sep)[-1] for x in glob.glob(staticpath+"static/ruldata/*")])
# @app.route('/rulmerge')
# def rulmerge():
#     return render_template('rulmerge.html', fns=[x.split(os.sep)[-1] for x in glob.glob(staticpath+"static/ruldata/*")])
@app.route('/langedit')
def langedit():
    return render_template('translate.html')
@app.route('/worldeditor')
def worldeditor():
    return render_template('worldeditor.html')
@app.route('/spritecomb')
def spritecomb():
    return render_template('spritecomb.html')
@app.route('/spritepalette')
def spritepalette():
    return render_template('spritepalette.html')
@app.route('/spriteconvert')
def spriteconvert():
    return render_template('spriteconvert.html')
@app.route('/hwpbuild')
def hwpbuild():
    return render_template('hwpbuild.html')

@app.route('/treerules')
def treerules():
    return render_template('treerules.html', fns=[x.split(os.sep)[-1] for x in glob.glob(staticpath+"static/ruldata/*")])


from flask import request, jsonify
import tempfile, os, shutil
import base64
from werkzeug import secure_filename
from modules.sprites import combinesprites


@app.route('/_spritecomb', methods = ['POST'])
def ajax_spritecomb():
    directory_name = tempfile.mkdtemp(prefix="spritecomb_")
    data=request.get_json(force=True)
    res={}
    res["idstring"]=data['idstring']
    files=data.get("files",[])
    for x in range(len(files)):
        fn=secure_filename(files[x]["fn"])
        with open(directory_name+os.sep+fn,"wb")as fh:
            fh.write(base64.b64decode(files[x]["cont"].split(",")[1]))
    resfn=directory_name+os.sep+secure_filename(data["name"]+'.png')
    combinesprites(directory_name+os.sep+"*.*",int(data['nrcols']),resfn)
    res["resimg"]="data:image/png;base64,{0}".format(str(base64.encodestring(open(resfn, "rb").read()) , "utf8").replace("\n", ""))
    shutil.rmtree(directory_name,ignore_errors=True)
    return jsonify(res)

from modules.sprites import paletteop

@app.route('/_spritepalette', methods = ['POST'])
def ajax_spritepalette():
    directory_name = tempfile.mkdtemp(prefix="spritepalette_")
    data=request.get_json(force=True)
    res={}
    res["idstring"]=data['idstring']
    files=data.get("files",[])
    for x in [0]:
        fn=secure_filename(files[x]["fn"])
        with open(directory_name+os.sep+fn,"wb")as fh:
            fh.write(base64.b64decode(files[x]["cont"].split(",")[1]))
            ifn=directory_name+os.sep+fn
            resfn=directory_name+os.sep+"res_"+fn+".png"
    paletteop(ifn,resfn,data["op"])    
    res["resimg"]="data:image/png;base64,{0}".format(str(base64.encodestring(open(resfn, "rb").read()) , "utf8").replace("\n", ""))
    shutil.rmtree(directory_name,ignore_errors=True)
    return jsonify(res)


from modules.sprites import spriteconv

@app.route('/_spriteconvert', methods = ['POST'])
def ajax_spriteconvert():
    directory_name = tempfile.mkdtemp(prefix="spriteconvert_")
    data=request.get_json(force=True)
    res={}
    res["idstring"]=data['idstring']
    files=data.get("files",[])
    fns=[]
    for x in range(len(files)):
        fn=secure_filename(files[x]["fn"])
        fns.append(directory_name+os.sep+fn)
        with open(directory_name+os.sep+fn,"wb")as fh:
            fh.write(base64.b64decode(files[x]["cont"].split(",")[1]))
    resdir=directory_name+os.sep+"res~"
    os.mkdir(resdir)    
    resfile=spriteconv(data,fns,secure_filename(secure_filename(data.get("fname","unknownname"))),resdir)
    ret='''data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAASCAIAAADdWck9AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAABl0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuNtCDrVoAAAB4SURBVDhPlZKBDsAwBES3//9os0pvRy1omqYaT3FuEblGSwEl3hMLpl54L4flaq8pcDwSwIHNL4uyAf7nJAkmAMwACPUUKQ265JpaGF6BBum7FACrAdo54VL5APAYfAJxpHD/BUIC9Q9hIhjY89YrmgL1ACpprMMDcmeAnZdVhCQAAAAASUVORK5CYII='''

    if resfile is None:
        raise Exception("no res file")
    else:
        if data.get("op",{}).get("out","UNKNOWNMODE")=="PNG":
            ret="data:image/png;base64,{0}".format(str(base64.encodestring(open(resfile, "rb").read()) , "utf8").replace("\n", ""))            
        else:
            ret="data:application/octet-stream;base64,{0}".format(str(base64.encodestring(open(resfile, "rb").read()) , "utf8").replace("\n", ""))
            
    res["resdata"]=ret
    res["out"]=data.get("op",{}).get("out","UNKNOWNMODE")

    #resfn=directory_name+os.sep+secure_filename(data["name"]+'.png')
    #combinesprites(directory_name+os.sep+"*.*",int(data['nrcols']),resfn)
    #res["resimg"]="data:image/png;base64,{0}".format(str(base64.encodestring(open(resfn, "rb").read()) , "utf8").replace("\n", ""))
    
    shutil.rmtree(directory_name,ignore_errors=True)
    return jsonify(res)

from modules.sprites import makeimages, getsize, splitspriteimg
@app.route('/_hwpbuild', methods=['POST'])
def ajax_hwpbuild():
    directory_name = tempfile.mkdtemp(prefix="hwpbuild_")
    data=request.get_json(force=True)
    res={}    
    fdata=data.get("fdata","")        
    fn=secure_filename(data.get("fn","TMP.png"))
    with open(directory_name+os.sep+fn,"wb")as fh:
        fh.write(base64.b64decode(fdata.split(",")[1]))
        ifn=directory_name+os.sep+fn
        resfn=directory_name+os.sep+"res_"+fn+".png"
        anifn=directory_name+os.sep+"anifn_"+fn+".png"
        tmpfn=directory_name+os.sep+"tmpfn_"+fn+".png"
    makeimages(dtype=2,spritepath=ifn,baseimg=staticpath+"static/img/hwp/cut.png",rescomb=resfn,drout=int(data.get("drawrout",5) ))        
    splitspriteimg(resfn,"{0}_images_{1:0>4d}_.png")    
    #makeimages(dtype=1,spritepath="{0}_images_*_.png".format(resfn),baseimg=staticpath+"static/img/hwp/cut.png",rescomb=tmpfn,drout=int(data.get("drawrout",5) ))        
    makeimages(dtype=0,spritepath="{0}_images_*_.png".format(resfn),baseimg=staticpath+"static/img/hwp/cut.png",rescomb=anifn,drout=int(data.get("drawrout",5) ))    
    res["resimg"]="data:image/png;base64,{0}".format(str(base64.encodestring(open(resfn, "rb").read()) , "utf8").replace("\n", ""))    
    res["aniimg"]="data:image/png;base64,{0}".format(str(base64.encodestring(open(anifn, "rb").read()) , "utf8").replace("\n", ""))    
    res["size"]=getsize(resfn)
    shutil.rmtree(directory_name,ignore_errors=True)
    return jsonify(res)

from modules.validate import newbase
@app.route('/_rulnewbase', methods = ['POST'])
def ajax_rulnewbase():
    data=request.get_json(force=True)
    res={}
    newbase(data)    
    return jsonify(res)

from modules.validate import checks
@app.route('/_rultest', methods = ['POST'])
def ajax_rultest():
    data=request.get_json(force=True)
    res={}
    res["errors"]=checks(data["allops"],data["basename"],data["rulstring"]) 
    return jsonify(res)

from modules.validate import format
@app.route('/_rulformat', methods = ['POST'])
def ajax_rulformat():
    data=request.get_json(force=True)
    res={}
    res["resrul"]=format(data["basename"],data["rulfile"]) 
    return jsonify(res)


from modules.validate import merge
@app.route('/_rulmerge', methods = ['POST'])
def ajax_rulmerge():
    data=request.get_json(force=True)
    res={}
    res["resrul"]=merge(data["dataname"],data["datastr1"],data["datastr2"],data["modindex"],data["prepare"]) 
    return jsonify(res)




if __name__ == '__main__':
    app.run(use_reloader=True, debug = True)