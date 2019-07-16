import operator

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView, ListView, TemplateView, DetailView, DeleteView, UpdateView, CreateView
from django.views.generic.edit import BaseUpdateView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from mypage.models import Follow
from trade.models import Item, Order
from .models import StoreProfile, QuestionComment, StoreGrade
from .forms import StoreProfileForm, StoreQuestionForm, StoreGradeForm

# @login_required
# def my_store_profile(request):
#     stores = get_object_or_404(StoreProfile, user=request.user)
#     return render(request, 'store/layout.html',{'stores': stores})

class StarStoreHitListView(ListView):
    template_name = 'store/star_store_hit.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_all = StoreProfile.objects.all()
        hit_list = []
        for store in store_all :
            hit_count = HitCount.objects.get_for_object(store)
            hit_list.append(hit_count)

        hit_list.sort(key=operator.attrgetter('hits'), reverse=True)
        context['hit_lists'] = hit_list
        if self.request.user.is_active:
            context['my_hit'] = hit_list.index(HitCount.objects.get_for_object(self.request.user.storeprofile))+1
        return context

class StarStoreGradeListView(ListView):
    template_name = 'store/star_store_grade.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = StoreGrade.objects.values_list('store_profile', flat=True).annotate(rating_sum=Sum('rating')/Count('rating'),count=Count('rating')).order_by('-rating_sum','-count')
        store_list = []
        for i in range(0, context['grades'].count()):
            store_list.append(StoreProfile.objects.get(pk=(context['grades'][i])))
        context['stores'] = store_list

        if self.request.user.is_active:
            if self.request.user.storeprofile.storegrade_set.all().count() != 0:
                context['my_grade'] = context['stores'].index(self.request.user.storeprofile)+1
            else:
                context['my_grade'] = '-'
        return context

class StarStoreSellListView(ListView):
    template_name = 'store/star_store_sell.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sell_list = {}
        store_all = StoreProfile.objects.all()
        for store in store_all:
            orders = Order.objects.filter(item__user=store.user, status='success')
            sell_list[store] = orders.count()

        context['sells'] = sorted(sell_list, key=sell_list.get, reverse=True)
        if self.request.user.is_active:
            context['my_sell'] = context['sells'].index(self.request.user.storeprofile) + 1
        return context

class StarStoreFollowListView(ListView):
    template_name = 'store/star_store_follow.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        follow = Follow.objects.values_list('store',flat=True).annotate(foll_count=Count('store')).order_by('-foll_count')
        print(follow)
        follow_list = []
        for i in range(0, follow.count()):
            follow_list.append(StoreProfile.objects.get(pk=(follow[i])))
        context['follows'] = follow_list

        if self.request.user.is_active:
            if self.request.user.storeprofile.follow_set.all().count() != 0:
                context['my_follow'] = follow_list.index(self.request.user.storeprofile) + 1
            else:
                context['my_follow'] = '-'
        return context

class StoreSellListView(ListView):
    model = Item
    template_name = 'store/store_sell_list.html'
    paginate_by = 20
    context_object_name = 'items'

    # context_object_name = 'stores'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5  # Display only 5 page numbers
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        context['stores'] = self.store
        hit_count = HitCount.objects.get_for_object(context['stores'])
        context['hit_count_response'] = HitCountMixin.hit_count(self.request, hit_count)
        return context

    def get_queryset(self):
        self.store = StoreProfile.objects.get(pk=self.kwargs['pk'])
        self.queryset = self.store.user.item_set.all()
        return super().get_queryset()


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
    ordering = '-created_at'
    context_object_name = 'grades'
    def get_ordering(self):
        self.sort = self.request.GET.get('sort','recent')

        if self.sort == 'recent':
            sort = '-created_at'
        elif self.sort == 'past':
            sort = 'created_at'
        elif self.sort == 'hgrade':
            sort = '-rating'
        elif self.sort == 'rgrade':
            sort = 'rating'
        return sort

    def get_queryset(self):
        self.gsort = self.request.GET.get('gsort', '')
        self.queryset = self.model.objects.filter(store_profile=self.kwargs['pk'])
        if self.gsort == 'five':
            self.queryset = self.model.objects.filter(store_profile=self.kwargs['pk'], rating=5)
        elif self.gsort == 'four':
            self.queryset = self.model.objects.filter(store_profile=self.kwargs['pk'], rating=4)
        elif self.gsort == 'three':
            self.queryset = self.model.objects.filter(store_profile=self.kwargs['pk'], rating=3)
        elif self.gsort == 'two':
            self.queryset = self.model.objects.filter(store_profile=self.kwargs['pk'], rating=2)
        elif self.gsort == 'one':
            self.queryset = self.model.objects.filter(store_profile=self.kwargs['pk'], rating=1)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stores'] = StoreProfile.objects.get(pk=self.kwargs['pk'])
        context['sort'] = self.request.GET.get('sort','recent')
        return context

class StoreGradeCreateView(CreateView):
    model = StoreGrade
    form_class = StoreGradeForm
    template_name = 'store/store_grade_new.html'

    def get(self, request, *args, **kwargs):
        try:
            self.model.objects.get(store_item_id = kwargs['item_id'])
            messages.error(request, '이미 리뷰를 작성하셨습니다.')
            return redirect("trade:order_history")
        except:
            items = get_object_or_404(Item, pk=self.kwargs['item_id'])
            return render(request, self.template_name,{'form':self.form_class, 'items': items})

    def form_valid(self, form):
        gradeform = form.save(commit=False)
        gradeform.author = self.request.user
        gradeform.store_profile_id = self.kwargs['pk']
        gradeform.store_item_id = self.kwargs['item_id']
        gradeform.rating = self.request.POST.get('rating')
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

