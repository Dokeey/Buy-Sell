from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView, CreateView
from hitcount.views import HitCountDetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CustomerAskForm
from .models import CustomerFAQ, CustomerAsk, CustomerNotice
# def customer(request):
#     return render(request, 'customer/customer.html')

# def customer_faq(request):
#     faqs = CustomerFAQ.objects.all()

#     return render(request, 'customer/customer_faq.html', {
#         'faqs': faqs
#     })

class CustomerFAQView(ListView):
    template_name = "customer/customer_faq.html"
    model = CustomerFAQ
    context_object_name = "faqs"

class CustomerFAQSearch(ListView):
    model = CustomerFAQ
    template_name = 'customer/customer_faq_search.html'
    context_object_name = 'faq_search'

    def get(self, request, *args, **kwargs):
        self.query = self.request.GET.get('query', '')

        if self.query == '':
            messages.info(self.request, '검색어를 입력해주세요')
            url = self.request.GET.get('next')
            return redirect(url)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.qs = super().get_queryset()
        
        if self.query:
            qs = self.qs.filter(faq_title__icontains=self.query)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        if self.query:
            context['query'] = self.query

        return context


# @login_required
# def customer_ask(request):

#     asks = CustomerAsk.objects.filter(author=request.user)

#     return render(request, 'customer/customer_ask.html', {
#         'asks': asks
#     })

@method_decorator(login_required, name='dispatch')
class CustomerAskListView(ListView):
    model = CustomerAsk
    context_object_name = "asks"
    template_name = "customer/customer_ask.html"

# @login_required
# def customer_ask_new(request):
#     form_cls = CustomerAskForm

#     if request.method == 'POST':
#         form = form_cls(request.POST)

#         if form.is_valid():
#             ask_form = form.save(commit=False)
#             ask_form.author = request.user
#             ask_form.save()
#         return redirect('customer:customer_ask')
#     else :
#         form = form_cls
#     return render(request, 'customer/customer_ask_new.html', {
#         'form':form
#     })

@method_decorator(login_required, name='dispatch')
class CustomerAskCreateView(CreateView):
    template_name = "customer/customer_ask_new.html"
    model = CustomerAsk
    form_class = CustomerAskForm

    def form_valid(self, form):
        ask_form = form.save(commit=False)
        ask_form.author = self.request.user
        ask_form.save()
        return redirect('customer:customer_ask')

# @login_required
# def customer_ask_edit(request, ask_id):
#     form_cls = CustomerAskForm
#     ask_post = get_object_or_404(CustomerAsk, pk=ask_id)
#     if request.method == 'POST':
#         form = form_cls(request.POST, instance=ask_post)

#         if form.is_valid():
#             ask_form = form.save(commit=False)
#             ask_form.author = request.user
#             ask_form.save()
#         return redirect('customer:customer_ask')
#     else :
#         form = form_cls(instance=ask_post)
#     return render(request, 'customer/customer_ask_new.html', {
#         'form': form
#     })

@method_decorator(login_required, name='dispatch')
class CustomerAskEditView(UpdateView):
    model = CustomerAsk
    form_class = CustomerAskForm
    template_name = "customer/customer_ask_new.html"
    pk_url_kwarg = 'ask_id'
    context_object_name = "ask"

    def get(self, request, *args, **kwargs):
        self.objects = self.get_object()
        status = self.model.objects.get(pk=kwargs['ask_id'])
        if status.ask_going == "ok":
            return redirect("customer:customer_ask")
        else:
            return super().get(request, *args, **kwargs)
    def form_valid(self, form):
        ask_form = form.save(commit=False)
        ask_form.author = self.request.user
        ask_form.save()
        return redirect('customer:customer_ask')

# @login_required
# def customer_ask_detail(request, ask_id):
    # ask_post = get_object_or_404(CustomerAsk, pk=ask_id)
    # return render(request, 'customer/customer_ask_detail.html', {
    #     'ask': ask_post,
    # })

@method_decorator(login_required, name='dispatch')
class CustomerAskDetailView(DetailView):
    template_name = "customer/customer_ask_detail.html"
    model = CustomerAsk
    pk_url_kwarg = 'ask_id'
    context_object_name = "ask"



class CustomerNoticeList(ListView):
    model = CustomerNotice
    template_name = 'customer/notice_list.html'
    context_object_name = 'notice_list'
customer_notice = CustomerNoticeList.as_view()

class CustomerNoticeDetail(HitCountDetailView):
    model = CustomerNotice
    template_name = 'customer/notice_detail.html'
    count_hit = True

notice_detail = CustomerNoticeDetail.as_view()