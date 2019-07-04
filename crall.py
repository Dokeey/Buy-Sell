import os

from django.core.files.base import ContentFile
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buynsell.settings')

import django
django.setup()

import sys
import requests
from bs4 import BeautifulSoup

from trade.models import Item

from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from random import randint

User = get_user_model()


def main(query):
    url = 'https://search.shopping.naver.com/search/all.nhn'
    params = {'query': query}
    res = requests.get(url, params=params)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    ctn = 0
    userlist = User.objects.filter(is_active=True)
    count = User.objects.filter(is_active=True).aggregate(count=Count('id'))['count']
    item_status = ['a', 'b', 'c', 's']

    def trim(s):
        return ' '.join(s.split())

    for item_tag in soup.select('#_search_list ._itemSection'):
        user = userlist[randint(0, count - 1)]  # Index of User
        status = item_status[randint(0, 3)] # item_status
        name = trim(item_tag.select('a.tit')[0].text)  # title
        price = trim(item_tag.select('.price .num')[0].text).replace(',', '').replace('$','').replace('.','')  # amount
        img_url = item_tag.select('img[data-original]')[0]['data-original']

        try:
            detest = item_tag.select('.detail')[0].text
        except:
            detest = ''

        res = requests.get(img_url, stream=True)
        img_name = os.path.basename(img_url.split('?', 1)[0])

        print(name, price, detest, img_name, img_url)
        print('')
        print(user, status)
        print('')

        item = Item(user=user, title=name, amount=price, desc=detest, category=query, item_status=status)
        item.photo.save(img_name, ContentFile(res.content))
        item.save()

        ctn += 1
        if ctn > 10:
            break


from category.models import Category

cate = Category.objects.all()
for cat in cate:
    main(cat)