from django.contrib import admin
from django.utils.html import mark_safe
from .models import *

from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

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


####### ------------ REGISTER:::: TOUR
class TourAdmin(admin.ModelAdmin):
    list_display = ['name_tour', 'description_tour', 'price_tour', 'amount_people_tour', 'remain_people', 'address_tour',
                  'amount_popular_tour', 'amount_like', 'created_date', 'user_id']
    search_fields = ['name_tour','price_tour','amount_like']
    list_filter = ['name_tour', 'price_tour','amount_like', 'created_date']
    form = TourForm


admin.site.register(SaleOff, SalesOffAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TypeCustomer)
admin.site.register(Bill)
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(RatingVote)
admin.site.register(WishList)
admin.site.register(User)