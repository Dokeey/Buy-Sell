from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import StoreProfile, QuestionComment
from .forms import StoreProfileForm, StoreQuestionForm

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
            sprofile.name = form.instance.name
            sprofile.save()
        return redirect('store:store_profile')
    else :

        form = form_cls(instance=profile)

    return render(request,'store/store_profile_edit.html',{
        'form': form,
    })


@login_required
def store_question(request, pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    comms = QuestionComment.objects.filter(store_profile_id=pk)
    form_cls = StoreQuestionForm
   # comm = get_object_or_404(StoreProfile, pk=pk)
    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.store_profile_id= pk
            comment.author=request.user
            comment.save()
        return redirect('store:store_question', pk)
    else:

        form = form_cls
    return render(request, 'store/store_question.html', {
        'comms':comms,
        'form': form,
        'stores': stores,
    })