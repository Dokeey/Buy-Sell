from time import time

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from category.models import Category

# Create your models here.
# from imagekit.generatorlibrary import Thumbnail
from hitcount.models import HitCountMixin, HitCount
from imagekit.models import ProcessedImageField
from mptt.fields import TreeForeignKey
from pilkit.processors import ResizeToFill

from iamport import Iamport
from datetime import datetime
import pytz
from jsonfield import JSONField
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma
from django.http import Http404
from uuid import uuid4



def named_property(name):
    def wrap(fn):
        fn.short_description = name
        return property(fn)
    return wrap

def timestamp_to_datetime(timestamp):
    if timestamp:
        tz = pytz.timezone(settings.TIME_ZONE)
        return datetime.utcfromtimestamp(timestamp).replace(tzinfo=tz)
    return None


class Item(models.Model, HitCountMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    desc = models.TextField(blank=True)
    amount = models.PositiveIntegerField()
    photo = ProcessedImageField(
            blank=True,
            upload_to = 'item_img/{0}'.format(datetime.now().strftime("%Y-%m-%d")),
            processors = [ResizeToFill(100, 100)],
            format='PNG',
            options = {'quality': 60}
        )
    category = TreeForeignKey(Category, on_delete=models.CASCADE)
    item_status = models.CharField(
        max_length=3,
        choices=(
            ('c', 'C급 이하'),
            ('b', 'B급'),
            ('a', 'A급'),
            ('s', 'S급'),
        ),
        default='a',
    )
    pay_status = models.CharField(
        max_length=15,
        choices=(
            ('ready', '재고있음'),
            ('reservation', '예약'),
            ('sale_complete', '판매완료'),
        ),
        default='ready',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk', related_query_name='hit_count_generic_relation')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]



from django.contrib.auth import get_user_model
User = get_user_model()
user_pk = User.objects.get(username='deleteuser').id

class ItemComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=user_pk)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    message = models.TextField()
    secret = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        # sort comments in chronological order by default
        ordering = ('-created_at',)



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    buyer_email = models.EmailField()
    buyer_name = models.CharField(max_length=10)
    buyer_tel = models.CharField(max_length=11)
    buyer_addr = models.CharField(max_length=100)
    buyer_postcode = models.CharField(max_length=10)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    merchant_uid = models.UUIDField(default=uuid4, editable=False)
    imp_uid = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, verbose_name='상품명')
    amount = models.PositiveIntegerField(verbose_name='결제금액')
    status = models.CharField(
        max_length=9,
        choices=(
            ('ready', '미결제'),
            ('paid', '결제완료'),
            ('cancelled', '결제취소'),
            ('failed', '결제실패'),
            ('reserv', '구매예약'),
            ('success', '구매완료'),
        ),
        default='ready',
        db_index=True
    )
    meta = JSONField(blank=True, default={})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_ready = property(lambda self: self.status == 'ready')
    is_paid = property(lambda self: self.status == 'paid')
    is_paid_ok = property(lambda self: self.status == 'paid' and self.amount == self.meta.get('amount'))
    is_cancelled = property(lambda self: self.status == 'cancelled')
    is_failed = property(lambda self: self.status == 'failed')
    is_reserv = property(lambda self: self.status == 'reserv')
    is_success = property(lambda self: self.status == 'success')

    receipt_url = named_property('영수증')(lambda self: self.meta.get('receipt_url'))
    cancel_reason = named_property('취소이유')(lambda self: self.meta.get('cancel_reason'))
    fail_reason = named_property('실패이유')(lambda self: self.meta.get('fail_reason', ''))
    paid_at = named_property('결제일시')(lambda self: timestamp_to_datetime(self.meta.get('paid_at')))
    failed_at = named_property('실패일시')(lambda self: timestamp_to_datetime(self.meta.get('failed_at')))
    cancelled_at = named_property('취소일시')(lambda self: timestamp_to_datetime(self.meta.get('cancelled_at')))

    # @property
    # def is_ready(self):
    #     return self.status == 'ready'
    # is_ready = property(is_ready)

    # is_ready = property(lambda self: self.status == 'ready')

    # @property
    # def receipt_url(self):
    #     return self.meta.get('receipt_url')
    # receipt_url.short_description = '영수증'
    #아래와 같은 말

    # receipt_url = named_property('영수증')(lambda self: self.meta.get('receipt_url'))

    class Meta:
        ordering = ('-id',)

    @property
    def api(self):
        'Iamport Client 인스턴스'
        return Iamport(settings.IAMPORT_API_KEY, settings.IAMPORT_API_SECRET)

    @named_property('결제금액')
    def amount_html(self):
        return mark_safe('<div style="float: center;">{0}</div>'.format(intcomma(self.amount)))

    @named_property('처리결과')
    def status_html(self):
        cls, text_color = '', ''

        help_text = ''
        if self.is_ready:
            cls, text_color = 'fa fa-shopping-cart', '#ccc'
        elif self.is_paid_ok:
            cls, text_color = 'fas fa-dollar-sign', 'green'
        elif self.is_cancelled:
            cls, text_color = 'fa fa-times', 'gray'
            help_text = self.cancel_reason
        elif self.is_failed:
            cls, text_color = 'fa fa-ban', 'red'
            help_text = self.fail_reason
        elif self.is_reserv:
            cls, text_color = 'fas fa-dollar-sign', 'blue'
        elif self.is_success:
            cls, text_color = 'fa fa-check-circle', '#0fd9a6'
        html = '''
             <span style="color: {text_color};" title="this is title">
             <i class="{class_names}"></i>
             {label}
             </span>'''.format(class_names=cls, text_color=text_color, label=self.get_status_display())
        # if help_text:
        #     html += '<br/>' + help_text
        return mark_safe(html)

    @named_property('영수증 링크')
    def receipt_link(self):
        if self.is_paid_ok and self.receipt_url:
            return mark_safe('<a href="{0}" target="_blank">영수증</a>'.format(self.receipt_url))

    def update(self, commit=True, meta=None):
        '결재내역 갱신'
        if self.imp_uid:
            # self.meta = meta or self.api.find(imp_uid=self.imp_uid)
            try:
                self.meta = meta or self.api.find(imp_uid=self.imp_uid)
            except Iamport.HttpError:
                raise Http404('Not found {}'.format(self.imp_uid))

            # merchant_uid는 반드시 매칭되어야 합니다.
            assert str(self.merchant_uid) == self.meta['merchant_uid']

            # if self.amount != self.meta['amount']:
            #     pass
            self.status = self.meta['status']

        if self.status in ('reserv','paid'):
            self.item.pay_status = 'reservation'
            self.meta['paid_at'] = int(time())
        else:
            self.item.pay_status = 'ready'
        self.item.save()

        if commit:
            self.save()


    def cancel(self, reason=None, commit=True):
        '결제내역 취소'
        if self.status == 'reserv':
            self.status = 'cancelled'
            self.meta['cancelled_at'] = int(time())
        try:
            meta = self.api.cancel(reason, imp_uid=self.imp_uid)
            assert str(self.merchant_uid) == self.meta['merchant_uid']
            self.update(commit=commit, meta=meta)
        # except Iamport.ResponseError as e:  # 취소시 오류 예외처리(이미 취소된 결제는 에러가 발생함)
        except:  # 취소시 오류 예외처리(이미 취소된 결제는 에러가 발생함)
            self.update(commit=commit)
        if commit:
            self.save()
