import os
from .models import File
from .weights import weight
from django.http import HttpResponse
from django.views.static import serve
from django.shortcuts import render, redirect, get_object_or_404

BASE_DIR = os.path.dirname((os.path.dirname(os.path.abspath(__file__))))

def index(request):
    if request.method == 'POST':
        num_files, paths = 2, list()
        for i in range(1, num_files + 1):
            fileObj = File()
            fileObj.file = request.FILES.get('file{}'.format(i) , False)
            fileObj.name = request.FILES['file{}'.format(i)].name
            paths.append("{}/data/{}".format(BASE_DIR, fileObj.name))
            fileObj.save()
        weigh = weight(paths[0], paths[1])
        return render(request,'main/results.html', {"weight" : "%.2f" % weigh})

    if request.method == 'GET':
        return render(request,'main/index.html', None)