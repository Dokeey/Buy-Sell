from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .models import Item
from .forms import ItemForm


def item_new(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        # item = get_object_or_404(Item, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.photo = form.cleaned_data['photo']
            form.save()
            return redirect('trade:item_new')
    else:
        form = ItemForm
    return render(request, 'trade/item_new.html', {
        'form': form
    })