from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView, CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CustomerAskForm
from .models import CustomerFAQ, CustomerAsk, CustomerNotice


class CustomerFAQView(ListView):
    template_name = "customer/customer_faq.html"
    model = CustomerFAQ
    context_object_name = "faqs"


class CustomerFAQSearch(ListView):
    model = CustomerFAQ
    template_name = 'customer/customer_faq_search.html'
    context_object_name = 'faq_search'

    def get(self, request, *args, **kwargs):
        self.query = self.request.GET.get('query', '').strip()

        if self.query.replace(' ', '') == '':
            self.query = ''

        if self.query == '':
            messages.info(self.request, '검색어를 입력해주세요')
            if self.request.GET.get('next'):
                url = self.request.GET.get('next')
            else:
                url = "customer:customer_faq"
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


@method_decorator(login_required, name='dispatch')
class CustomerAskListView(ListView):
    model = CustomerAsk
    context_object_name = "asks"
    template_name = "customer/customer_ask.html"

    def get_queryset(self):
        self.queryset = CustomerAsk.objects.filter(author=self.request.user)
        return super().get_queryset()


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
