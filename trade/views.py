from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .models import Item
from .forms import ItemForm


@login_required
def item_new(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.photo = form.cleaned_data['photo']
            form.save()
            return redirect('trade:item_list')
    else:
        form = ItemForm
    return render(request, 'trade/item_new.html', {
        'form': form
    })

def item_list(request):
    items = Item.objects.all()
    return render(request, 'trade/item_list.html', {
        'items': items
    })

@login_required
def my_item_list(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'trade/item_list.html', {
        'items': items
    })

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'trade/item_detail.html', {
        'item': item
    })