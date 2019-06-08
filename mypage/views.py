from django.shortcuts import render

# Create your views here.

def mypage_main(request):
    return render(request, 'mypage/main.html')