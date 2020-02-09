import os
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from django.core.files.base import ContentFile
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buynsell.settings')

import django
django.setup()

import requests
from bs4 import BeautifulSoup

from trade.models import Item, ItemImage

from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from random import randint

from category.models import Category
User = get_user_model()
cate_cnt = 0

def main(query):
    url = 'https://search.shopping.naver.com/search/all.nhn'
    params = {'query': query}
    res = requests.get(url, params=params)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    ctn = 0
    userlist = User.objects.filter(is_active=True)
    count = userlist.aggregate(count=Count('id'))['count']
    item_status = ['a', 'b', 'c', 's']
    item_list = []
    item_image_list = []

    def trim(s):
        return ' '.join(s.split())

    global cate_cnt
    cate_cnt += 1
    print("{} 카테고리 크롤링 진행중..".format(query))
    print("     남은 카테고리 : {}".format(Category.objects.all().count()-cate_cnt))

    for item_tag in soup.select('#_search_list ._itemSection'):
        try:
            user = userlist[randint(0, count - 1)]  # Index of User
            status = item_status[randint(0, 3)] # item_status
            name = trim(item_tag.select('.tit a')[0].text)[0:50]  # title
            price = trim(item_tag.select('.price .num')[0].text).replace(',', '').replace('$','').replace('.','')  # amount
            img_url = item_tag.select('img[data-original]')[0]['data-original']
            res = requests.get(img_url, stream=True)
            img_name = os.path.basename(img_url.split('?', 1)[0])
        except:
            continue

        try:
            detest = item_tag.select('.detail')[0].text
        except:
            detest = ''


        # print(name, price, detest, img_name,img_url)
        # print('')
        # print(user, status)
        # print('')

        item = Item(user=user, title=name, amount=price, desc=detest, category=query, item_status=status)
        item.save()
        item_image = ItemImage(item=item)
        item_image.photo.save(img_name, ContentFile(res.content))
        item_image.save()

        # item = Item()
        # item.user = user
        # item.title = name
        # item.amount = price
        # item.desc = detest
        # item.category = query
        # item.item_status = status
        # item_list.append(item)
        #
        # item_image = ItemImage(item=item)
        # item_image.photo.save(img_name, ContentFile(res.content))
        # item_image_list.append(item_image)

        ctn += 1
        if ctn > 20:
            break

if __name__ == '__main__':
    cate = Category.objects.all()
    for cat in cate:
        main(cat)