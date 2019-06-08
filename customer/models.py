from django.conf import settings
from django.db import models

# Create your models here.

class CustomerCategory(models.Model):
    customer_category = models.CharField(max_length=40)

    def __str__(self):
        return self.customer_category

class CustomerFAQ(models.Model):
    faq_title = models.CharField(max_length=40)
    faq_category = models.ForeignKey(CustomerCategory, on_delete=models.CASCADE)
    faq_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CustomerAsk(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ask_category = models.ForeignKey(CustomerCategory, on_delete=models.CASCADE)
    ask_title = models.CharField(max_length=100)
    ask_post = models.TextField()
    ask_comment = models.TextField()
    ask_going = models.CharField(max_length=20,
        choices=(
            ('ready', '문의 중'),
            ('ok', '답변완료')
        ),
        default='ready',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

