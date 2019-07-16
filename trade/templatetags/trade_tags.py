from datetime import datetime

from django import template
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma

from ..models import Item

register = template.Library()

@register.simple_tag
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
        html = """<i class="far fa-handshake"></i> <span style="color:#368AFF;">{}</span>""".format(status)
    else:
        html = """<i class="far fa-handshake"></i> <span style="color:red;">{}</span>""".format(status)
    return html

def photos(item):

    html = """
            <div id="iteminfo" class="carousel slide" data-ride="carousel">
                <!--페이지-->
                <div class="carousel-inner">
                {}
                </div>
            </div> 
        """
    ht = ''
    for i, item_image in enumerate(item.itemimage_set.all()):
        if i == 0:
            ht += '<div class="item active">'
        else:
            ht += '<div class="item">'
        ht += """
                <a href="{0}">
                    <img class="img-responsive" style="margin:0 auth;height:auto; max-height:150px;border:1px solid #ededed;" src="{1}"/>
                </a>
            </div>
        """.format(resolve_url('trade:item_detail', item.id), item_image.photo.url)

    return html.format(ht)

@register.simple_tag
def item_block(item):
    """
        문법 :
        {% item_block [item] %}

        하나의 item 인스턴스를 통해 기본 정보를 셋팅하여 item_list 중 하나의 블록이 셋팅됨

    """

    next_link = resolve_url('trade:item_detail', item.id)
    wishlist_link = resolve_url('mypage:wishlist_action', item.id)
    user_link = resolve_url('store:store_sell_list', item.user.storeprofile.id)
    hit_count = item.hit_count.hits
    title = item.title
    amount = intcomma(item.amount)
    photo_url = item.itemimage_set.first().photo.url
    item_status = item.get_item_status_display()
    pay_status = status_check(item.get_pay_status_display())
    updated_at = item.updated_at.strftime("%Y년 %m월 %d일")
    created_at = item.created_at.strftime("%Y년 %m월 %d일 %H:%M")

    updated_str = simple_time(item.updated_at)
    created_str = simple_time(item.created_at)

    html = """
        <div class="thumbnail">
          <div class="caption text-center">
            <div class="position-relative">
              {photos}
            </div>
            <h4 id="thumbnail-label">{amount}<small> 원</small></h4><hr style="margin:5px">
            <div class="thumbnail-description smaller text-center">
                <b>{title}</b>
                <hr style="margin:5px">
                <i class="far fa-clock"></i>&nbsp;{time}<hr style="margin:5px">
                <ul class="list-inline">
                  <li class="col-sm-6 col-xs-12"><a href="{user_link}"><b><i class="fas fa-user light-red lighter bigger-120"></i>&nbsp;{user}</b></a></li>
                  <li class="pay-status col-sm-6 col-xs-12"><b>{pay_status}</b></li>
                </ul>
            </div>
          </div>
        </div>
    """.format(hit_count=hit_count,
               title=title,
               amount=amount,
               next_link=next_link,
               photo_url=photo_url,
               photos=photos(item),
               item_status=item_status,
               pay_status=pay_status,
               time=created_str,
               updated_at=updated_at,
               created_at=created_at,
               updated_str=updated_str,
               user=item.user.profile.nick_name,
               user_link=user_link,
               wishlist_link=wishlist_link,
               )

    return mark_safe(html)



@register.simple_tag
def order_time_check(order):
    if order.status == 'reserv':
        time = datetime.now() - order.created_at
        time = time.total_seconds()
        if time > 172800:
            order.status = 'ready'
            order.update()

    return ''