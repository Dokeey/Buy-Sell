from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, ListView, TemplateView, DetailView, DeleteView, UpdateView, CreateView
from django.views.generic.edit import BaseUpdateView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from trade.models import Item
from .models import StoreProfile, QuestionComment, StoreGrade
from .forms import StoreProfileForm, StoreQuestionForm, StoreGradeForm

# @login_required
# def my_store_profile(request):
#     stores = get_object_or_404(StoreProfile, user=request.user)
#     return render(request, 'store/layout.html',{'stores': stores})

class StoreSellListView(TemplateView):
    model = StoreProfile
    template_name = 'store/store_sell_list.html'

    # context_object_name = 'stores'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = StoreProfile.objects.get(pk=self.kwargs['pk'])
        hit_count = HitCount.objects.get_for_object(context['stores'])
        context['hit_count_response'] = HitCountMixin.hit_count(self.request, hit_count)
        return context

class StoreProfileEditView(UpdateView):
    form_class = StoreProfileForm
    model = StoreProfile
    template_name = 'store/store_profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.storeprofile

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_sell_list", kwargs={'pk': self.request.user.storeprofile.pk})



class StoreQuestionLCView(CreateView):
    model = QuestionComment

    form_class = StoreQuestionForm
    template_name = 'store/store_question.html'

    def get(self, request, *args, **kwargs):
        stores = get_object_or_404(StoreProfile, pk=self.kwargs['pk'])
        comms =  QuestionComment.objects.filter(store_profile_id=self.kwargs['pk'], parent__isnull=True)
        return render(request, self.template_name, {'comms': comms, 'form':self.form_class, 'stores':stores})

    def form_valid(self, form):
        parent_obj = None

        try:
            parent_id = int(self.request.POST.get('parent_id'))
            #hidden으로 parent id 값 가져옴
        except:
            parent_id=None

        if parent_id:
            parent_obj = QuestionComment.objects.get(id=parent_id)
            if parent_obj:
                recomm = form.save(commit=False)
                recomm.parent = parent_obj
        comment = form.save(commit=False)
        comment.store_profile_id= self.kwargs['pk']
        comment.author=self.request.user
        comment.save()
        return redirect('store:store_question', self.kwargs['pk'])

class StoreQuestionEditView(UpdateView):
    form_class = StoreQuestionForm
    model = QuestionComment
    template_name = 'store/store_question_edit.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['cid'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_question", kwargs={'pk': self.kwargs['pk']})

class StoreQuestionDelView(DeleteView):
    model = QuestionComment

    # get method 일때 post mothod를 리턴하여 confirm template없이 삭제 가능하지만 추천하는 방법은 아님
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['cid'])

    def get_success_url(self):
        return reverse_lazy("store:store_question", kwargs={'pk': self.kwargs['pk']})



class StoreGradeListView(ListView):
    model = StoreGrade
    template_name = 'store/store_grade.html'
    context_object_name = 'grades'

    def get_context_data(self, **kwargs):
        context1 = super().get_context_data(**kwargs)
        context1['stores'] = StoreProfile.objects.get(pk=self.kwargs['pk'])
        return context1

class StoreGradeCreateView(CreateView):
    model = StoreGrade
    form_class = StoreGradeForm
    template_name = 'store/store_grade_new.html'
    def get(self, request, *args, **kwargs):
        try:
            StoreGrade.objects.get(store_item_id = kwargs['item_id'])
            messages.error(request, '이미 리뷰를 작성하셨습니다.')
            return redirect("trade:trade_history")
        except:
            items = get_object_or_404(Item, pk=self.kwargs['item_id'])
            return render(request, self.template_name,{'form':self.form_class, 'items': items})

    def form_valid(self, form):
        gradeform = form.save(commit=False)
        gradeform.author = self.request.user
        gradeform.store_profile_id = self.kwargs['pk']
        gradeform.store_item_id = self.kwargs['item_id']
        gradeform.save()
        return redirect('store:store_grade', self.kwargs['pk'])

class StoreGradeEditView(UpdateView):
    form_class = StoreGradeForm
    model = StoreGrade
    template_name = 'store/store_grade_new.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['gid'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_grade", kwargs={'pk': self.kwargs['pk']})

class StoreGradeDelView(DeleteView):
    model = StoreGrade

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['gid'])

    def get_success_url(self):
        return reverse_lazy("store:store_grade", kwargs={'pk': self.kwargs['pk']})

