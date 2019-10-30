from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.


class CustomerCategory(MPTTModel):
    name = models.CharField(verbose_name="카테고리 명", max_length=50, unique=True)
    parent = TreeForeignKey('self',verbose_name="상위 카테고리 명", on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']


    class Meta:
        verbose_name = "1:1 카테고리"
        verbose_name_plural = "1:1 카테고리"

class CustomerFAQ(models.Model):
    faq_title = models.CharField(verbose_name="FAQ 제목", max_length=40)
    faq_category = TreeForeignKey(CustomerCategory, verbose_name="FAQ 카테고리", on_delete=models.CASCADE)
    faq_content = models.TextField(verbose_name="설명" )
    created_at = models.DateTimeField(verbose_name="작성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ['faq_title']


class CustomerAsk(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="작성자", on_delete=models.CASCADE)
    ask_category = TreeForeignKey(CustomerCategory, verbose_name="문의 카테고리", on_delete=models.CASCADE)
    ask_title = models.CharField(verbose_name="제목", max_length=100)
    ask_post = models.TextField(verbose_name="문의내용" )
    ask_comment = models.TextField(verbose_name="답변" )
    ask_going = models.CharField(verbose_name="답변 상태", max_length=20,
        choices=(
            ('ready', '문의 중'),
            ('ok', '답변완료')
        ),
        default='ready',
        db_index=True
    )
    created_at = models.DateTimeField(verbose_name="작성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)

    class Meta:
        verbose_name = "1:1 문의"
        verbose_name_plural = "1:1 문의"
        ordering = ('-created_at',)
        
class CustomerNotice(models.Model):
    notice_title = models.CharField(verbose_name="제목", max_length=40)
    notice_content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(verbose_name="작성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)

    class Meta:
        verbose_name = "공지사항"
        verbose_name_plural = "공지사항"