from django.contrib import admin
from django.utils.html import mark_safe
from .models import *
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.html import format_html
from .paginators import *

def convert_currency(f):
    return "{:0,.2f}".format(float(f))

###### FORM CKEDITOR
class SalesOffForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = SaleOff
        fields = '__all__'

class TourForm(forms.ModelForm):
    description_tour = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Tour
        fields = '__all__'

####### ------------ REGISTER:::: SALES_OFF
class SalesOffAdmin(admin.ModelAdmin):
    list_display = ['name_sales', 'description', 'price_value_sales', 'created_date']
    search_fields = ['name_sales','price_value_sales']
    list_filter = ['name_sales', 'price_value_sales', 'created_date']
    form = SalesOffForm

class TicketInlindAdmin(admin.TabularInline):
    model = Ticket

class ImageInlindAdmin(admin.TabularInline):
    model = TourImages

####### ------------ REGISTER:::: TOUR
class TourAdmin(admin.ModelAdmin):
    list_display = ['detail', 'name_tour', 'newPrice', 'amount_people_tour', 'remain_people', 'address_tour',
                  'amount_popular_tour', 'amount_like', 'date_begin_tour', 'user_id']
    search_fields = ['name_tour','price_tour','amount_like']
    list_filter = ['name_tour', 'price_tour','amount_like', 'created_date']
    form = TourForm
    inlines = [ImageInlindAdmin, TicketInlindAdmin]
    list_per_page = TourPaginator.page_size
    # paginator = [TourPaginator,]

    readonly_fields = ['avatar']

    def avatar(self, Tour):
        if Tour:
            return mark_safe(
                '<img src="/static/{url}" width="40%" />'.format(url=Tour.image_tour)
            )

    def detail(self, Tour):
        return mark_safe('<img src="/static/{url}" width="40%"/>'.format(url=Tour.image_tour))

    def newPrice(self, Tour):
        return mark_safe('<p>{pr} VND</p>'.format(pr=convert_currency(Tour.price_tour)))

class TicketAdmin(admin.ModelAdmin):
    list_display = ['tour', 'type_people', 'user', 'price_real', 'totals_minus_money', 'amount_ticket',
                  'status_ticket', 'bill']
    search_fields = ['tour','type_people','user','price_real']
    list_filter = ['tour', 'type_people','user', 'price_real']
    # form = TourForm

class BillAdmin(admin.ModelAdmin):
    list_display = ['code_bill', 'totals_bill', 'status_bill', 'user', 'method_pay']
    search_fields = ['code_bill','totals_bill','status_bill','user','method_pay']
    list_filter = ['totals_bill', 'status_bill','user', 'method_pay']

class CommentBlogAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'content_cmt', 'amount_like_cmt', 'created_date']
    search_fields = ['user','blog', 'content_cmt', 'amount_like_cmt','created_date']
    list_filter = ['user', 'blog', 'content_cmt','amount_like_cmt', 'created_date']
    list_per_page = CommentPaginator.page_size

    def get_user(self, CommentBlog):
        return CommentBlog.first_name


admin.site.register(SaleOff, SalesOffAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TypeCustomer)
admin.site.register(Bill, BillAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment)
admin.site.register(RatingVote)
admin.site.register(WishList)
admin.site.register(TourImages)
admin.site.register(Blog)
admin.site.register(CommentBlog, CommentBlogAdmin)
admin.site.register(LikeBlog)
admin.site.register(User)

