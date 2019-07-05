from django import template
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma

from ..models import Item

register = template.Library()

@register.simple_tag
def item_block(item):
    """
        문법 :
        {% item_block [item] %}

        하나의 item 인스턴스를 통해 기본 정보를 셋팅하여 item_list 중 하나의 블록이 셋팅됨

    """

    next_link = resolve_url('trade:item_detail', item.id)
    wishlist_link = resolve_url('mypage:wishlist_new', item.pk)
    user_link = resolve_url('store:store_sell_list', item.user.storeprofile.id)
    hit_count = item.hit_count.hits
    title = item.title
    amount = intcomma(item.amount)
    photo_url = item.photo.url
    item_status = item.get_item_status_display()
    pay_status = item.get_pay_status_display()
    updated_at = item.updated_at.strftime("%Y년 %m월 %d일 %H:%M")
    created_at = item.created_at.strftime("%Y년 %m월 %d일 %H:%M")

    html = """
        <div class="card" style="height: 450px; width: 20rem;">
          <a href="{next_link}"><img class="card-img-top" src="{photo_url}" alt="Card image cap">
          <div class="card-body">
            <h5 class="card-title">{title}</h5>
          </div>
          </a>
          <ul class="list-group list-group-flush">
            <li class="list-group-item"><b>{amount}</b>원</li>
            <li class="list-group-item">{pay_status}</li>
            <a href={user_link}><li class="list-group-item">{user}</li></a>
            <li class="list-group-item">{updated_at}</li>
          </ul>
          <div class="card-body">
            <a href="{wishlist_link}" class="card-link">찜하기</a>
            <a href="#" class="card-link">공유하기</a>
          </div>
        </div>
    """.format(hit_count=hit_count,
               title=title,
               amount=amount,
               next_link=next_link,
               photo_url=photo_url,
               item_status=item_status,
               pay_status=pay_status,
               updated_at=updated_at,
               created_at=created_at,
               user=item.user.profile.nick_name,
               user_link=user_link,
               wishlist_link=wishlist_link,
               )

    return mark_safe(html)
