from django import template
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe

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
    hit_count = item.hit_count.hits
    title = item.title
    amount = item.amount
    photo_url = item.photo.url
    item_status = item.get_item_status_display()
    pay_status = item.get_pay_status_display()
    updated_at = item.updated_at.strftime("%Y년 %m월 %d일 %H:%M")
    created_at = item.created_at.strftime("%Y년 %m월 %d일 %H:%M")

    html = """
        <br>
        조회수 : {hit_count}<br>
        상품명 : {title}<br>
        가격 : {amount}<br>
        사진 : <a href="{next_link}"><img src="{photo_url}"/></a><br>
        등급 : {item_status}<br>
        재고 : {pay_status}<br>
        최근 업데이트 : {updated_at}<br>
        작성일 : {created_at}<br>
    """.format(hit_count=hit_count,
               title=title,
               amount=amount,
               next_link=next_link,
               photo_url=photo_url,
               item_status=item_status,
               pay_status=pay_status,
               updated_at=updated_at,
               created_at=created_at
               )

    return mark_safe(html)
