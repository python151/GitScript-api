from django.http import JsonResponse
from django.contrib.auth import authenticate, login as log
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import shutil
from django.views.decorators.csrf import csrf_exempt

from api.models import Script
from pathlib import Path
import json
import os

def getSessionFromReq(request):
    data = request.GET.dict()
    sessKey = data.get('session-key')
    print(sessKey)
    obj = Session.objects.filter(session_key=sessKey).get()
    return obj.get_decoded()

def getSessionKey(request):
    return request.session.session_key

# Create your views here.
def login(request):
    ret = False
    if request.method != "GET":
        return JsonResponse({"data": {"success": ret}})
    else:
        data = request.GET.dict()

        username, password = data.get("username"), data.get("password")
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            log(request, user)
            request.session['userid'] = request.user.id
            request.session.modified = True
            print(request.session['userid'])
            ret = {
                "sessionKey": getSessionKey(request),
                "success": True,
            }
        else:
            ret = {
                "success": False,
            }

    print(ret)
    return JsonResponse({"data": ret}, safe=False)

@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({
            "data": {
                "success": False,
                "message": "Invalid method"
            }
        })
    
    foo = request.body
    body = json.loads(foo)

    username, password, email = body['username'], body['password'], body['email']
    
    user = User.objects.create_user(username=username, password=password, email=email)
    user.save()

    log(request, user)
    
    return JsonResponse({
        "data": {
            "success": True,
            "sessionKey": getSessionKey(request),
        }
    })

def getMyScripts(request):
    ''' 
        Will return all scripts of user
    '''
    if request.method == "GET":
        session = getSessionFromReq(request)
        print(session["_auth_user_id"])
        ret = []
        for i in Script.objects.filter(users__id=session.get("userid")).all():
            ret.append({
                "name": i.name,
                "description": i.description,
                "id": i.id,
            })
        print(ret)
        return JsonResponse({'data': ret})

def getScript(request, id):
    '''
        Will get id of script and return all the files in the script directory and there values
    '''
    session = getSessionFromReq(request)
    script = Script.objects.filter(users__id=session["_auth_user_id"], id=id)
    if script.exists():
        script = script.get()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dir = BASE_DIR+ "/code"+script.codeFolder
        try: files = os.listdir(dir)
        except FileNotFoundError: 
            try: os.mkdir(dir)
            except FileNotFoundError:
                d = dir.split("/")
                d.pop()
                os.mkdir("/".join(d))
                os.mkdir(dir)
            except FileExistsError:
                pass
            open(dir+"/README.md", "a").write("")
            files = os.listdir(dir)
        fileVals = []
        for file in files:
            try: fileVals.append({
                "name": file,
                "value": open(dir+"/"+file, "r").read()
            }) 
            except IsADirectoryError:
                pass
        return JsonResponse({
            "data": {
                "success": True,
                "name": script.name,
                "description": script.description,
                "id": script.id,
                "files": fileVals,
            }
        })
    else:
        return JsonResponse({"data": {"success": False}})

@csrf_exempt
def saveFile(request, scriptId, fileName):
    request.session = getSessionFromReq(request)
    if request.method != "POST" or not request.user.is_authenticated:
        return JsonResponse({"data": {"success": False}})
    

    foo = request.body
    body = json.loads(foo)

    code = body['code']
    print(code)

    script = Script.objects.filter(users__id=request.user.id, id=scriptId)
    if not script.exists:
        return JsonResponse({"data": {"success": False}})
    
    script = script.get()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code/"+script.codeFolder+"/"

    file = open(dir+fileName.replace("00000", "."), "w")
    file.write(code)

    return JsonResponse({"data": {
        "success": True,
        "saved": True,
    }})
    
@csrf_exempt
def createScript(request):
    request.session = getSessionFromReq(request)
    if not request.method == "POST":
        return JsonResponse({"data": {"success": False}})

    foo = request.body
    print(foo)
    data = json.loads(foo)

    name, description= data.get('name'), data.get('description')

    sObj = Script.objects.create(name=name, description=description)
    sObj.save()

    mDir = "/"+str(request.user.id)+"/"+str(sObj.id)

    sObj.codeFolder = mDir
    sObj.users.add(request.user)
    sObj.save()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code"+mDir

    try: os.mkdir(dir)
    except FileNotFoundError:
        d = dir.split("/")
        d.pop()
        os.mkdir("/".join(d))
        os.mkdir(dir)
    except FileExistsError:
        pass

    Path(dir+"/README.md").touch()

    return JsonResponse({"data": {"success": True, "scriptId": sObj.id}})


@csrf_exempt
def deleteFileFromScript(request, scriptId, fileName):
    fileName = fileName.replace("00000", ".")
    if request.method != "DELETE":
        return JsonResponse({
            "success": False
        })

    session = getSessionFromReq(request)
    userID = session["_auth_user_id"]

    script = Script.objects.filter(id=scriptId, users__id=userID)
    if script.exists():
        script = script.get()
    else:
        return JsonResponse({
            "success": False
        })
    dir = script.codeFolder

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code"+dir+"/"

    os.remove(dir+fileName)

    return JsonResponse({
        "data": {
            "success": True,
            "deleted": True
        }
    })

@csrf_exempt
def changeFileName(request):
    session = getSessionFromReq(request)
    if request.method != "PUT":
        return JsonResponse({
            "data": {
                "success": False
            }
        })
    
    foo = request.body
    print(foo)
    postData = json.loads(foo)

    scriptId = postData["scriptId"]
    
    userID = session["_auth_user_id"]
    script = Script.objects.filter(id=scriptId, users__id=userID)
    if script.exists():
        script = script.get()
    else:
        return JsonResponse({
            "success": False
        })
    dir = script.codeFolder

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code"+dir+"/"

    os.rename(dir+postData['oldName'], dir+postData['newName'])

    return JsonResponse({"data": {"success": True}})

@csrf_exempt
def deleteScript(request, id):
    if request.method != "DELETE":
        return JsonResponse({
            "success": False
        })

    session = getSessionFromReq(request)
    userID = session["_auth_user_id"]

    script = Script.objects.filter(id=id, users__id=userID)
    if script.exists():
        script = script.get()
    else:
        return JsonResponse({
            "success": False
        })
    dir = script.codeFolder

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code"+dir+"/"

    shutil.rmtree(dir)
    script.delete()

    return JsonResponse({
        "data": {
            "success": True,
            "deleted": True
        }
    })

def runScript(request, id):
    request.session = getSessionFromReq(request)
    
    script = Script.objects.filter(users__id=request.user.id, id=id)
    if not script.exists:
        return JsonResponse({"data": {"success": False, "output": "unknown error"}})
    
    script = script.get()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code/"+script.codeFolder+"/"

    try: file = open(dir+"main.py", "r")
    except FileNotFoundError:
        output = {
            "output": "must have file called main.py or Main.py",
            "success": False
        }
    finally:
        output = {"output": os.system("python3 "+dir+"main.py"), "success": True}

    return JsonResponse({
        "data": output
    })

def getPublicUserInfo(request, id):
    user = User.objects.filter(id=id)
    if not user.exists():
        return JsonResponse({"data": {"success": False}})
    user = user.get()

    scripts = []
    scriptObj = Script.objects.filter(users__id=user.id).all()
    for script in scriptObj:
        scripts.append({
            "name": script.name,
            "description": script.description,
            "id": script.id,
        })

    ret = {
        "success": True,
        "user": {
            "username": user.username,
            "scripts": scripts
        }
    }

    print(ret)

    return JsonResponse({"data": ret})