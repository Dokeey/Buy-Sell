
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DeleteView, UpdateView, CreateView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from rank import DenseRank

from buynsell import settings
from mypage.models import Follow
from trade.models import Item, Order
from .models import StoreProfile, QuestionComment, StoreGrade
from .forms import StoreProfileForm, StoreQuestionForm, StoreGradeForm

# @login_required
# def my_store_profile(request):
#     stores = get_object_or_404(StoreProfile, user=request.user)
#     return render(request, 'store/layout.html',{'stores': stores})







class StarStoreSearchList(ListView):
    model = StoreProfile
    template_name = 'store/star_store_search.html'
    context_object_name = 'star_search'
    paginate_by = 6
    def get_queryset(self):
        self.query = self.request.GET.get('query','')
        self.qs = super().get_queryset()
        if self.query:
            qs = self.qs.filter(name__icontains=self.query)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StarStoreSearchList, self).get_context_data()

        #페이지네이션
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

        context['ctn'] = self.get_queryset().count()
        if self.query:
            context['query'] = self.query

        return context

class StarStoreHitListView(ListView):
    template_name = 'store/star_store_hit.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ctype = ContentType.objects.get_for_model(StoreProfile)
        search_hit = HitCount.objects.filter(content_type=ctype).values('object_pk').annotate(rank=DenseRank('hits'))
        context['my_hit'] = ''
        for i in search_hit:
            if i['object_pk']:
                i['store_info'] = StoreProfile.objects.get(pk=i['object_pk'])
            if self.request.user.is_active:
                if i['object_pk'] == self.request.user.storeprofile.pk:
                    context['my_hit'] = i['rank']
        if context['my_hit'] == '':
            context['my_hit'] = '-'
        context['stores'] = search_hit

        return context

class StarStoreGradeListView(ListView):
    template_name = 'store/star_store_grade.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_grade = StoreGrade.objects.values('store_profile').annotate(rating_sum=Sum('rating') / Count('rating'),
                                                                           count=Count('rating'),
                                                                           rank=DenseRank('rating_sum',
                                                                                          'count')).order_by(
            '-rating_sum', '-count')
        context['my_grade'] = ''
        for i in search_grade:
            if i['store_profile']:
                i['store_info'] = StoreProfile.objects.get(pk=i['store_profile'])
            if self.request.user.is_active:
                if i['store_profile'] == self.request.user.storeprofile.pk:
                    context['my_grade'] = i['rank']

        if context['my_grade'] == '':
            context['my_grade'] = '-'

        context['stores'] = search_grade
        return context

class StarStoreSellListView(ListView):
    template_name = 'store/star_store_sell.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_sell = Order.objects.filter(status='success').values('item__user').annotate(count=Count('status'),
                                                                                           rank=DenseRank(
                                                                                               'count')).order_by(
            'user')
        context['my_sell'] = ''
        for i in search_sell:
            if i['rank']:
                i['store_info'] = StoreProfile.objects.get(user_id=i['item__user'])
            if self.request.user.is_active:
                if i['item__user'] == self.request.user:
                    context['my_sell'] = i['rank']

        if context['my_sell'] == '':
            context['my_sell'] = '-'
        context['stores'] = search_sell
        return context

class StarStoreFollowListView(ListView):
    template_name = 'store/star_store_follow.html'
    model = StoreProfile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_follow = Follow.objects.values('store').annotate(foll_count=Count('store'),
                                                                rank=DenseRank('foll_count')).order_by('-foll_count')
        print(search_follow)
        context['my_follow'] = ''
        for i in search_follow:
            if i['store']:
                i['store_info'] = StoreProfile.objects.get(pk=i['store'])

            if self.request.user.is_active:
                if self.request.user.storeprofile.pk == i['store']:
                    context['my_follow'] = i['rank']

        if context['my_follow'] == '':
            context['my_follow'] = '-'

        context['stores'] = search_follow
        # follow = Follow.objects.values_list('store',flat=True).annotate(foll_count=Count('store')).order_by('-foll_count')
        # print(follow)
        # follow_list = []
        # for i in range(0, follow.count()):
        #     follow_list.append(StoreProfile.objects.get(pk=(follow[i])))
        # context['follows'] = follow_list
        #
        # if self.request.user.is_active:
        #     if self.request.user.storeprofile.follow_set.all().count() != 0:
        #         context['my_follow'] = follow_list.index(self.request.user.storeprofile) + 1
        #     else:
        #         context['my_follow'] = '-'
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
        context['kakao_key'] = settings.KAKAO_KEY_JS
        context['stores'] = self.store
        hit_count = HitCount.objects.get_for_object(context['stores'])
        context['hit_count_response'] = HitCountMixin.hit_count(self.request, hit_count)
        return context

    def get_queryset(self):
        self.store = StoreProfile.objects.get(pk=self.kwargs['pk'])
        self.queryset = self.store.user.item_set.all()
        return super().get_queryset()


@method_decorator(login_required, name='dispatch')
class StoreProfileEditView(UpdateView):
    form_class = StoreProfileForm
    model = StoreProfile
    template_name = 'store/store_profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.storeprofile

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_sell_list", kwargs={'pk': self.request.user.storeprofile.pk})

@method_decorator(login_required, name='dispatch')
class StoreQuestionLCView(CreateView):

    model = QuestionComment
    form_class = StoreQuestionForm
    template_name = 'store/store_question.html'
    ordering = '-created_at'

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
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StoreQuestionLCView, self).get_context_data(**kwargs)
        self.sort = self.request.GET.get('sort', '')

        context['sort'] = self.sort
        context['form'] = self.form_class
        context['comms'] = self.model.objects.filter(store_profile_id=self.kwargs['pk'], parent__isnull=True)
        if self.sort == 'all':
            context['comms'] = self.model.objects.filter(store_profile_id=self.kwargs['pk'], parent__isnull=True)
        elif self.sort == 'my':
            context['comms'] = self.model.objects.filter(author=self.request.user, parent__isnull=True)

        context['stores'] = get_object_or_404(StoreProfile, pk=self.kwargs['pk'])

        return context
        
@method_decorator(login_required, name='dispatch')
class StoreQuestionEditView(UpdateView):
    form_class = StoreQuestionForm
    model = QuestionComment
    template_name = 'store/store_question_edit.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['cid'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_question", kwargs={'pk': self.kwargs['pk']})

@method_decorator(login_required, name='dispatch')
class StoreQuestionDelView(DeleteView):
    model = QuestionComment
    template_name = 'store/store_question_delete.html'
    pk_url_kwarg = 'cid'
    # get method 일때 post mothod를 리턴하여 confirm template없이 삭제 가능하지만 추천하는 방법은 아님
    # def get(self, request, *args, **kwargs):
    #     return self.post(request, *args, **kwargs)
    #
    # def get_object(self, queryset=None):
    #     return self.model.objects.get(pk=self.kwargs['cid'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        print(self.object)
        if self.request.user != self.object.author:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('store:store_question', self.kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("store:store_question", kwargs={'pk': self.kwargs['pk']})


class StoreGradeListView(ListView):
    model = StoreGrade
    template_name = 'store/store_grade.html'
    ordering = '-created_at'
    context_object_name = 'grades'
    paginate_by = 10
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

        context['stores'] = StoreProfile.objects.get(pk=self.kwargs['pk'])
        context['sort'] = self.request.GET.get('sort','recent')
        return context

@method_decorator(login_required, name='dispatch')
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

@method_decorator(login_required, name='dispatch')
class StoreGradeEditView(UpdateView):
    form_class = StoreGradeForm
    model = StoreGrade
    template_name = 'store/store_grade_new.html'
    pk_url_kwarg = 'gid'
    # def get_object(self, queryset=None):
    #     return self.model.objects.get(pk=self.kwargs['gid'])

    def get_context_data(self, **kwargs):
        context = super(StoreGradeEditView, self).get_context_data()
        grade = self.model.objects.get(pk=self.kwargs['gid'])
        context['items'] = get_object_or_404(Item, pk=grade.store_item_id)
        return context
    def get_success_url(self, **kwargs):
        return reverse_lazy("store:store_grade", kwargs={'pk': self.kwargs['pk']})

@method_decorator(login_required, name='dispatch')
class StoreGradeDelView(DeleteView):
    model = StoreGrade
    template_name = 'store/store_question_delete.html'
    pk_url_kwarg = 'gid'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.author:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('store:store_grade', self.kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("store:store_grade", kwargs={'pk': self.kwargs['pk']})

