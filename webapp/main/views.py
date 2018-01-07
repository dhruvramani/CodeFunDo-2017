import os
from .models import File, Image
from django.http import HttpResponse
from django.views.static import serve
from django.shortcuts import render, redirect, get_object_or_404

BASE_DIR = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))

def index(request):
    if request.method == 'POST':
        num_files, paths = 2, list()
        imageName = ""
        for i in range(1, num_files + 1):
            fileObj = File()
            fileObj.file = request.FILES.get('file{}'.format(i) , False)
            fileObj.name = request.FILES['file{}'.format(i)].name
            if i==1:
                imageName += fileObj.name
                imageName += ","
            if i==2:
                imageName += fileObj.name
            paths.append("{}/data/{}".format(BASE_DIR, fileObj.name))
            fileObj.save()
        if(request.POST['filename'] == "ar"):
            from .weight2 import weight
        else:
            from .weights import weight
        weigh = weight(paths[0], paths[1])
        ''' 
        imageObj = Image()
        imageObj.name = imageName
        imageObj.weight = float("%.2f" % weigh)
        imageObj.save()
        '''
        if(request.POST['filename'] == "ar"):
            return render(request, 'main/ar.html', {"weight" : "%.2f" % weigh})
        return render(request,'main/results.html', {"weight" : "%.2f" % weigh})

    if request.method == 'GET':
        return render(request,'main/index.html', None)

def ar(request):
    if(request.method == 'GET'):
        return render(request, 'main/ar.html', {"weight" : "Click Me!"})