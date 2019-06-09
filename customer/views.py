from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView
from hitcount.views import HitCountDetailView

from .forms import CustomerAskForm
from .models import CustomerFAQ, CustomerAsk, CustomerNotice


def customer(request):
    return render(request, 'customer/customer.html')

def customer_faq(request):
    faqs = CustomerFAQ.objects.all()

    return render(request, 'customer/customer_faq.html', {
        'faqs': faqs
    })

@login_required
def customer_ask(request):

    asks = CustomerAsk.objects.filter(author=request.user)

    return render(request, 'customer/customer_ask.html', {
        'asks': asks
    })

@login_required
def customer_ask_new(request):
    form_cls = CustomerAskForm

    if request.method == 'POST':
        form = form_cls(request.POST)

        if form.is_valid():
            ask_form = form.save(commit=False)
            ask_form.author = request.user
            ask_form.save()
        return redirect('customer:customer_ask')
    else :
        form = form_cls
    return render(request, 'customer/customer_ask_new.html', {
        'form':form
    })

@login_required
def customer_ask_edit(request, ask_id):
    form_cls = CustomerAskForm
    ask_post = get_object_or_404(CustomerAsk, pk=ask_id)
    if request.method == 'POST':
        form = form_cls(request.POST, instance=ask_post)

        if form.is_valid():
            ask_form = form.save(commit=False)
            ask_form.author = request.user
            ask_form.save()
        return redirect('customer:customer_ask')
    else :
        form = form_cls(instance=ask_post)
    return render(request, 'customer/customer_ask_new.html', {
        'form': form
    })

@login_required
def customer_ask_detail(request, ask_id):
    ask_post = get_object_or_404(CustomerAsk, pk=ask_id)
    return render(request, 'customer/customer_ask_detail.html', {
        'ask': ask_post,
    })

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