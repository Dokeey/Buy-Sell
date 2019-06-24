from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, ListView, TemplateView, DetailView, DeleteView, UpdateView
from django.views.generic.edit import BaseUpdateView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from trade.models import Item
from .models import StoreProfile, QuestionComment, StoreGrade
from .forms import StoreProfileForm, StoreQuestionForm, StoreGradeForm


# def store_sell_list(request, pk):
#     stores = get_object_or_404(StoreProfile, pk=pk)
#
#     return render(request, 'store/store_sell_list.html', {
#         'stores': stores
#     })

class StoreSellListView(TemplateView):
    model = StoreProfile
    template_name = 'store/store_sell_list.html'
    # context_object_name = 'stores'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = StoreProfile.objects.get(pk=self.kwargs['pk'])
        return context
store_sell_list = StoreSellListView.as_view()


# @login_required #로그인시에만 접속할 수 있다.
# def store_profile_edit(request):
#     form_cls = StoreProfileForm
#     profile = get_object_or_404(StoreProfile, user=request.user)
#     if request.method == 'POST' :
#         form = form_cls(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             sprofile = form.save(commit=False)
#             sprofile.name = form.instance.name
#             sprofile.save()
#         return redirect('store:store_sell_list', profile.pk)
#     else :
#
#         form = form_cls(instance=profile)
#
#     return render(request,'store/store_profile_edit.html',{
#         'form': form,
#     })

class StoreProfileEditView(UpdateView):
    form_class = StoreProfileForm
    model = StoreProfile
    template_name = 'store/store_profile_edit.html'

    def get_object(self, queryset=None):
        print(self.request.user.storeprofile)
        return self.request.user.storeprofile

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_sell_list", kwargs={'pk': self.request.user.storeprofile.pk})

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

# @login_required
# def store_question_edit(request, pk, cid):
#     form_cls = StoreQuestionForm
#     comment = get_object_or_404(QuestionComment, pk=cid)
#     if request.method == "POST":
#         forms = form_cls(request.POST, instance=comment)
#         if forms.is_valid():
#             forms.save()
#         return redirect('store:store_question', pk)
#     else:
#         forms = form_cls(instance=comment)
#         print(comment)
#     return render(request, 'store/store_question_edit.html',{
#         'forms':forms
#     })

class StoreQuestionEditView(UpdateView):
    form_class = StoreQuestionForm
    model = QuestionComment
    template_name = 'store/store_question_edit.html'

    def get_object(self, **kwargs):
        print(self.kwargs['cid'])
        print(QuestionComment.objects.get(pk=self.kwargs['cid']))
        return QuestionComment.objects.get(pk=self.kwargs['cid'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_sell_list", kwargs={'pk': self.kwargs['pk']})


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
        'grades':grades,
    })

@login_required
def store_grade_new(request, pk, item_id):
    items = get_object_or_404(Item, pk=item_id)
    try:
        StoreGrade.objects.get(store_item_id = items.pk)
        messages.error(request, '이미 리뷰를 작성하셨습니다.')
        return redirect("accounts:profile")
    except:
        form_cls = StoreGradeForm
        if request.method == 'POST':
            form = form_cls(request.POST)
            if form.is_valid():
                gradeform = form.save(commit=False)
                gradeform.author = request.user
                gradeform.store_profile_id = pk
                gradeform.store_item = items
                gradeform.save()
            return redirect('store:store_grade', pk)
        else :
            form = form_cls()

        return render(request, 'store/store_grade_new.html',{
            'form':form,
            'items':items,
        })


@login_required
def store_grade_edit(request, pk, gid):
    stores = get_object_or_404(StoreProfile, pk=pk)
    grade = get_object_or_404(StoreGrade, pk=gid)
    form_cls = StoreGradeForm
    if request.method == 'POST':
        form = form_cls(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            return redirect('store:store_grade',pk)
    else :
        form = form_cls(instance=grade)
    return render(request, 'store/store_grade_new.html',{
        'form':form,
        'stores':stores
    })

def store_grade_del(request, pk, gid):
    grade = get_object_or_404(StoreGrade, pk= gid)
    grade.delete()
    return redirect('store:store_grade',pk)

# class StoreGradeDelView(DeleteView):
#     model = StoreGrade
#     success_url = reverse_lazy('root')

