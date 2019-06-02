from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .models import Item, ItemComment
from .forms import ItemForm, ItemCommentForm


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
    comments = ItemComment.objects.filter(item=item, parent=None)
    form = ItemCommentForm
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        form = ItemCommentForm(request.POST)
        if form.is_valid():
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = ItemComment.objects.get(id=parent_id)
                if parent_obj:
                    replay_comment = form.save(commit=False)
                    replay_comment.parent = parent_obj
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.item = item
            new_comment.save()
        return redirect('trade:item_detail', pk)
    return render(request, 'trade/item_detail.html', {
        'item': item,
        'comments': comments,
        'form': form,
    })

def test(request):
    return render(request, 'trade/test.html')