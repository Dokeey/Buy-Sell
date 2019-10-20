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
    ordering = '-id'
    paginate_by = 5

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
        context['prev'] = start_index - 4
        context['next'] = end_index + 1
        context['last_page'] = max_index
        context['page_range'] = page_range

        return context

customer_notice = CustomerNoticeList.as_view()

# class CustomerNoticeDetail(HitCountDetailView):
#     model = CustomerNotice
#     template_name = 'customer/notice_detail.html'
#     count_hit = True
#
# notice_detail = CustomerNoticeDetail.as_view()