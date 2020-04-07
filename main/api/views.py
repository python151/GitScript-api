from django.http import JsonResponse
from django.contrib.auth import authenticate, login as log
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from django.views.decorators.csrf import csrf_exempt

from api.models import Script
from pathlib import Path

import os

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
        print(user.username)
        if user is not None:
            log(request, user)
            ret = {
                "id": user.id,
                "success": True,
            }
        else:
            ret = {
                "success": False,
            }

    print(ret)
    return JsonResponse({"data": ret}, safe=False)

def signup(request):
    return False

def getMyScripts(request):
    ''' 
        Will return all scripts of user
    '''
    if request.method == "GET":
        if request.user.is_authenticated:
            ret = []
            for i in Script.objects.filter(users__id=request.user.id).all():
                ret.append({
                    "name": i.name,
                    "description": i.description,
                    "id": i.id,
                })
            return JsonResponse({'data': ret})

def getScript(request, id):
    '''
        Will get id of script and return all the files in the script directory and there values
    '''
    if request.user.is_authenticated:
        script = Script.objects.filter(users__id=request.user.id, id=id)
        if script.exists():
            script = script.get()
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dir = BASE_DIR+ "/code"+script.codeFolder
            files = os.listdir(dir)
            fileVals = []
            for file in files:
               fileVals.append({
                   "name": file,
                   "value": open(dir+"/"+file, "r").read()
               }) 
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
    else:
        return JsonResponse({"data": {"success": False}})

@csrf_exempt
def saveFile(request, scriptId, fileName):
    if request.method != "POST" or not request.user.is_authenticated:
        return JsonResponse({"data": {"success": False}})
    
    data = request.POST.dict()
    code = data.get('code')

    script = Script.objects.filter(users__id=request.user.id, id=scriptId)
    if not script.exists:
        return JsonResponse({"data": {"success": False}})
    
    script = script.get()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code"+script.codeFolder

    file = open(dir+filename.replace("00000", "."), "w")
    file.write(code)

    return JsonResponse({"data": {
        "success": True,
        "saved": True,
    }})
    
def createScript(request):
    if not request.user.is_authenticated and request.method == "GET":
        return JsonResponse({"data": {"success": False}})
    
    data = request.GET.dict()

    name, description= data.get('name'),data.get('description')

    sObj = Script.objects.create(name=name, description=description)
    sObj.save()

    mDir = "/"+str(request.user.id)+"/"+str(sObj.id)

    sObj.codeFolder = mDir
    sObj.users.add(request.user)
    sObj.save()
    

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir = BASE_DIR+ "/code"+mDir

    os.mkdir(dir)

    Path(dir+"/README.md").touch()

    return JsonResponse({"data": {"success": True}})