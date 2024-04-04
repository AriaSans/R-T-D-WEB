from django.shortcuts import render

# Create your views here.
def yolo_main(request):
    return render(request, 'yolo_main.html')