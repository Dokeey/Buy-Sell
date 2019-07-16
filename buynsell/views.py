from operator import attrgetter

from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from category.models import Category
from trade.models import Item


class MainLV(ListView):
    model = Item
    template_name = 'base.html'
