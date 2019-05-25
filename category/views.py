from django.shortcuts import render, get_object_or_404
from .models import Category, SubCategory

# def print_category(request):
#     cates = Category.objects.all()
#     subcates = SubCategory.objects.all()
#
#     return render(request, 'category/print_category.html', {
#         'cates' : cates,
#         'subcates': subcates,
#     })


def categories(request, pk):
    category = get_object_or_404(Category, pk=pk)
    subcategory = SubCategory.objects.filter(category = pk)
    return render(request, 'category/categories.html', {
        'cate': category,
        'subcategory': subcategory
    })

def subcategories(request, cate_pk, pk):
    category = get_object_or_404(Category, pk=cate_pk)
    subcategory = get_object_or_404(SubCategory, pk=pk)

    return render(request, 'category/subcategories.html',{
        'cate' : category,
        'sub': subcategory
    })

def test(request):
    return render(request, 'category/test.html',{})