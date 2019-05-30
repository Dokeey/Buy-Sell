from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import StoreProfile
from .forms import StoreProfileForm

@login_required
def store_profile(request):
    stores = get_object_or_404(StoreProfile, user=request.user)
    return render(request, 'store/layout.html',{
        'stores': stores,
    })


@login_required #로그인시에만 접속할 수 있다.
def store_profile_edit(request):
    form_cls = StoreProfileForm
    profile = get_object_or_404(StoreProfile, user=request.user)
    if request.method == 'POST' :
        form = form_cls(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            sprofile = form.save(commit=False)
            sprofile.name = form.instance.name +'의 가게'
            sprofile.save()
        return redirect('store:store_profile')
    else :

        form = form_cls

    return render(request,'store/store_profile_edit.html',{
        'form': form,
    })


