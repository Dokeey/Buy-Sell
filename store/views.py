from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect


from .models import StoreProfile, QuestionComment, StoreGrade
from .forms import StoreProfileForm, StoreQuestionForm, StoreGradeForm

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
    comms = QuestionComment.objects.filter(store_profile_id=pk, parent__isnull=True)
    form_cls = StoreQuestionForm
    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES)
        if form.is_valid():
            parent_obj= None
            try:
                parent_id = int(request.POST.get('parent_id'))
                #hidden으로 parent id 값 가져옴
            except:
                parent_id=None

            if parent_id:
                parent_obj = QuestionComment.objects.get(id=parent_id)
                if parent_obj:
                    recomm = form.save(commit=False)
                    recomm.parent = parent_obj
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

@login_required
def store_question_edit(request, pk, cid):
    form_cls = StoreQuestionForm
    comment = get_object_or_404(QuestionComment, pk=cid)
    if request.method == "POST":
        forms = form_cls(request.POST, instance=comment)
        if forms.is_valid():
            forms.save()
        return redirect('store:store_question', pk)
    else:
        forms = form_cls(instance=comment)
    return render(request, 'store/store_question_edit.html',{
        'forms':forms
    })

@login_required
def store_question_del(request,pk, cid):
    comment = get_object_or_404(QuestionComment, pk=cid)
    comment.delete()
    return redirect('store:store_question', pk)

@login_required
def store_grade(request, pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    grades = StoreGrade.objects.filter(store_profile_id=pk)
    return render(request, 'store/store_grade.html', {
        'stores':stores,
        'grades':grades
    })

@login_required
def store_grade_new(request, pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    form_cls = StoreGradeForm
    if request.method == 'POST':
        form = form_cls(request.POST)
        if form.is_valid():
            gradeform = form.save(commit=False)
            gradeform.author = request.user
            gradeform.store_profile_id = pk
            gradeform.save()
        return redirect('store:store_grade', pk)
    else :
        form = form_cls

    return render(request, 'store/store_grade_new.html',{
        'form':form
    })

