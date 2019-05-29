from django.shortcuts import render

# Create your views here.


def item_new(request):
    return render(request, 'trade/item_new.html')