from datetime import datetime

from django import template
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma

from ..models import Item

register = template.Library()

def simple_time(time):
    delta_time = datetime.now() - time
    delta_time = delta_time.total_seconds()

    if delta_time < 60:
        time_str = "{}초 전".format(int(delta_time))
    elif 60 <= delta_time < 3600:
        time_str = "{}분 전".format(int(delta_time/60))
    elif 3600 <= delta_time < 86400:
        time_str = "{}시간 전".format(int(delta_time/3600))
    elif 86400 <= delta_time  < 2592000:
        time_str = "{}일 전".format(int(delta_time/86400))
    elif 2592000 <= delta_time < 31104000:
        time_str = "{}달 전".format(int(delta_time/2592000))
    else:
        time_str = "{}년 전".format(int(delta_time/31104000))

    return time_str

def status_check(status):
    if status == '재고있음':
        html = """<i class="far fa-handshake"></i> <span style="color:blue;"><b>{}</b></span>""".format(status)
    else:
        html = """<i class="far fa-handshake"></i> <span style="color:red;"><b>{}</b></span>""".format(status)
    return html


@register.simple_tag
def item_block(item):
    """
        문법 :
        {% item_block [item] %}

        하나의 item 인스턴스를 통해 기본 정보를 셋팅하여 item_list 중 하나의 블록이 셋팅됨

    """

    next_link = resolve_url('trade:item_detail', item.id)
    wishlist_link = resolve_url('mypage:wishlist_new', item.id)
    user_link = resolve_url('store:store_sell_list', item.user.storeprofile.id)
    hit_count = item.hit_count.hits
    title = item.title
    amount = intcomma(item.amount)
    photo_url = item.photo.url
    item_status = item.get_item_status_display()
    pay_status = status_check(item.get_pay_status_display())
    updated_at = item.updated_at.strftime("%Y년 %m월 %d일")
    created_at = item.created_at.strftime("%Y년 %m월 %d일 %H:%M")

    updated_str = simple_time(item.updated_at)

    html = """
        <div class="thumbnail">
          <div class="caption text-center" onclick="location.href='{next_link}'">
            <div class="position-relative">
              <img class="img-rounded img-thumbnail" src="{photo_url}" style="width:100px;height:100px;" />
            </div>
            <h5 id="thumbnail-label"><i class="fas fa-won-sign"></i>&nbsp;{amount}</h4>            
            <div class="thumbnail-description smaller text-center">
                <p><b>{title}</b></p>
                <hr>
                {pay_status}
            </div>
          </div>
          <div class="caption card-footer text-center">
            <ul class="list-inline">
              <li><a href="{user_link}"><i class="fas fa-user light-red lighter bigger-120"></i>&nbsp;{user}</a></li>
              <li></li>
              <li><i class="far fa-clock"></i>&nbsp;{updated_str}</li>
            </ul>
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
               updated_str=updated_str,
               user=item.user.profile.nick_name,
               user_link=user_link,
               wishlist_link=wishlist_link,
               )

    return mark_safe(html)
