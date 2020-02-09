from time import time

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.storage import FileSystemStorage
from django.db import models
from category.models import Category

# Create your models here.
# from imagekit.generatorlibrary import Thumbnail
from django.utils.crypto import get_random_string
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

def order_property(order):
    def wrap(fn):
        fn.admin_order_field = order
        return fn
    return wrap

def timestamp_to_datetime(timestamp):
    if timestamp:
        tz = pytz.timezone(settings.TIME_ZONE)
        return datetime.utcfromtimestamp(timestamp).replace(tzinfo=tz)
    return None


class Item(models.Model, HitCountMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="물품 주인", on_delete=models.CASCADE, db_index=True)
    title = models.CharField(verbose_name="물품명", max_length=50)
    desc = models.TextField(verbose_name="설명", blank=True)
    amount = models.PositiveIntegerField(verbose_name="가격")
    category = TreeForeignKey(Category, verbose_name="카테고리", on_delete=models.CASCADE, db_index=True)
    item_status = models.CharField(
        verbose_name="물품 상태",
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
        verbose_name="재고 상태",
        max_length=15,
        choices=(
            ('ready', '재고있음'),
            ('reservation', '예약'),
            ('sale_complete', '판매완료'),
        ),
        default='ready'
    )
    created_at = models.DateTimeField(verbose_name="등록일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)

    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk', related_query_name='hit_count_generic_relation')

    def __str__(self):
        return self.title

    class Meta:
        # ordering = ["-created_at"]
        verbose_name = "물품"
        verbose_name_plural = "물품"



def user_directory_path(instance, filename):
    """
    image upload directory setting
    e.g)
        item_img/{year}-{month}-{day}/{username}_{filename}_{randomstring}
        images/2016-7-12/user_file_xfiwefu.jpg
    """
    now = datetime.now()

    path = 'item_img/{year}-{month}-{day}/{username}_{randomstring}{filename}'.format(
        year=now.year,
        month=now.month,
        day=now.day,
        username=instance.item.user.username,
        filename=filename,
        randomstring=get_random_string(7),
    )
    return path



class ItemImage(models.Model):
    item = models.ForeignKey(Item, verbose_name="물품", on_delete=models.CASCADE, db_index=True)
    photo = ProcessedImageField(
            verbose_name="물품 사진",
            upload_to = user_directory_path,
            processors = [ResizeToFill(640, 640)],
            format='JPEG',
            options = {'quality': 70}
        )
    class Meta:
        verbose_name = "물품 사진"
        verbose_name_plural = "물품 사진"


from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user_pk = User.objects.get(username='deleteuser').id
except:
    user_pk = None

class ItemComment(models.Model):

    if user_pk:
        user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="작성자",
                                 on_delete=models.SET_DEFAULT, default=user_pk)
    else:
        user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="작성자", on_delete=models.CASCADE)

    item = models.ForeignKey(Item, verbose_name="물품", on_delete=models.CASCADE)
    message = models.TextField(verbose_name="내용")
    secret = models.BooleanField(verbose_name="비밀글", default=True)
    created_at = models.DateTimeField(verbose_name="작성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)
    parent = models.ForeignKey('self', verbose_name="상위 댓글", on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        # sort comments in chronological order by default
        ordering = ('-created_at',)
        verbose_name = "물품 문의"
        verbose_name_plural = "물품 문의"

    def __str__(self):
        return self.message

from accounts.validators import phone_validate

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="구매자", on_delete=models.CASCADE)

    email = models.EmailField(verbose_name="구매자 이메일", blank=True)
    username = models.CharField(verbose_name="구매자 성명", max_length=10)
    phone = models.CharField(verbose_name="구매자 연락처", max_length=11, validators=[phone_validate])
    post_code = models.CharField(verbose_name="구매자 우편번호", max_length=10)
    address = models.CharField(verbose_name="구매자 주소", max_length=100)
    detail_address = models.CharField(verbose_name="구매자 상세주소", max_length=20)
    requirement = models.TextField(verbose_name="배송 요청사항", max_length=30, blank=True)

    item = models.ForeignKey(Item, verbose_name="물품", on_delete=models.CASCADE)
    merchant_uid = models.UUIDField(default=uuid4, editable=False)
    imp_uid = models.CharField(verbose_name="이니페이 UID",max_length=100, blank=True)
    # name = models.CharField(max_length=100, verbose_name='상품명')
    amount = models.PositiveIntegerField(verbose_name='결제금액')
    pay_choice = models.CharField(
        verbose_name='결제 방식',
        max_length=15,
        default='import',
        choices=(
            ('import', '이니페이 카드결제'),
            ('bank_trans', '계좌이체'),
        )
    )
    status = models.CharField(
        verbose_name='처리 결과',
        max_length=9,
        choices=(
            ('ready', '미결제'),
            ('paid', '결제완료'),
            ('cancelled', '결제취소'),
            ('failed', '결제실패'),
            ('reserv', '거래예약'),
            ('success', '거래완료'),
        ),
        default='ready',
        db_index=True
    )
    meta = JSONField(blank=True, default={})
    created_at = models.DateTimeField(verbose_name="거래 일시", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)
    is_active = models.BooleanField(verbose_name="계좌 결제 여부", default=True)

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

    def __str__(self):
        return self.item.title

    class Meta:
        ordering = ('-id',)
        verbose_name = "주문 내역"
        verbose_name_plural = "주문 내역"

    @property
    def api(self):
        'Iamport Client 인스턴스'
        return Iamport(settings.IAMPORT_API_KEY, settings.IAMPORT_API_SECRET)

    @named_property('결제금액')
    def amount_html(self):
        return mark_safe('<div style="float: center;">{0} 원</div>'.format(intcomma(self.amount)))

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
        if self.is_success and self.receipt_url:
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
            if not commit:
                self.status = 'cancelled'
                self.meta['cancelled_at'] = int(time())

        commit = True
        if self.status in ('reserv','paid'):
            self.item.pay_status = 'reservation'
            self.meta['paid_at'] = int(time())
        elif self.status == 'success':
            self.item.pay_status = 'sale_complete'
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
            commit = False
            meta = self.api.cancel(reason, imp_uid=self.imp_uid)
            assert str(self.merchant_uid) == self.meta['merchant_uid']
            self.update(commit=commit, meta=meta)
        # except Iamport.ResponseError as e:  # 취소시 오류 예외처리(이미 취소된 결제는 에러가 발생함)
        except:  # 취소시 오류 예외처리(이미 취소된 결제는 에러가 발생함)
            self.update(commit=commit)
        if commit:
            self.save()


from category.models import Category

class ProxyCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"