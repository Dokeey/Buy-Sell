from django import forms

from category.models import Category, SubCategory
from .models import Item


class ItemForm(forms.ModelForm):
    CHOICESES = (
        ('Debt', (
            (11, 'Credit Card'),
            (12, 'Student Loans'),
            (13, 'Taxes'),
        )),
        ('Entertainment', (
            (21, 'Books'),
            (22, 'Games'),
        )),
        ('Everyday', (
            (31, 'Groceries'),
            (32, 'Restaurants'),
        )),
    )
    CHOICES = []
    for cate in Category.objects.all():
        category = []
        category.append(cate)
        sub_category_group = []
        for subcate in SubCategory.objects.filter(category=cate):
            sub_category = []
            sub_category.append(subcate.id)
            sub_category.append(subcate)
            sub_category_group.append(sub_category)

        category.append(sub_category_group)
        CHOICES.append(category)

    tmp = forms.ChoiceField(choices=CHOICES)
    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category','sub_category','status','is_public', 'tmp']