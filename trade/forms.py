from django import forms

from category.models import Category, SubCategory
from .models import Item, ItemComment


class ItemForm(forms.ModelForm):
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

    category_tmp = forms.ChoiceField(choices=CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_tmp'].label = '카테고리'


    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category_tmp', 'status','is_public']


class ItemCommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':50}))
    class Meta:
        model = ItemComment
        fields = ['message']