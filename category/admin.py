from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from trade.models import Item
from .models import Category

# Register your models here.

class InlineItemAdmin(admin.StackedInline):
    model = Item
    extra = 0

    fields = ('user', 'title', 'desc', 'item_photos', 'get_edit_link')
    readonly_fields = ['user', 'item_photos', 'get_edit_link']

    def item_photos(self, obj=None):
        imageset = obj.itemimage_set.all()
        html = ''
        for image in imageset:
            ht = '<a href="{url}" style="padding:10px"><img style="border:1px solid #999999;" src="{url}" width="{width}" height={height} /></a>'.format(
                url=image.photo.url,
                width=100,
                height=100,
            )
            html = html + ht
        return mark_safe(html)
    item_photos.short_description = ("사진 자세히 보기")

    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[force_text(obj.pk)])
            return mark_safe("""<a href="{url}">{text}</a>""".format(
                url=url,
                text=("물품 상세 정보, 문의글 보러가기"),
            ))
        return "저장하시고 이용해주세요"
    get_edit_link.short_description = ("물품 자세히 보기")

    def has_add_permission(self, request, obj):
        return False


class CategoryFilter(SimpleListFilter):
    title = '최상위 카테고리' # or use _('country') for translated title
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        roots = Category.objects.root_nodes()
        return [(root.id, root) for root in roots]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.get(id=self.value()).get_descendants(include_self=True).annotate(_item_ctn=Count("item"))
        else:
            return queryset

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    # specify pixel amount for this ModelAdmin only:

    list_display = ('tree_actions', 'indented_title', 'item_count')  # Sane defaults.
    list_display_links = ('indented_title',)  # Sane defaults.
    inlines = [InlineItemAdmin]
    list_filter =(CategoryFilter,)
    # ordering = ['indented_title']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _item_ctn=Count("item"),
            # parent=
        )
        return qs

    def item_count(self, obj):
        return obj.item_set.all().count()
    item_count.short_description = '물품 개수'
    item_count.admin_order_field = '_item_ctn'





