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
    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = SaleOff
        fields = '__all__'


class TourForm(forms.ModelForm):
    description_tour = forms.CharField(widget=forms.Textarea(attrs={'cols': 750, 'rows': 25}))

    class Meta:
        model = Tour
        fields = '__all__'


class TypeCustomerForm(forms.ModelForm):
    description_customer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = TypeCustomer
        fields = '__all__'


class TypeCustomerAdmin(admin.ModelAdmin):
    form = TypeCustomerForm


##### ------------ REGISTER:::: BLOG
class CommentBlogShowReadInlindAdmin(admin.TabularInline):
    model = CommentBlog
    fields = ['get_image_user', 'get_user', 'custom_content_cmt']
    readonly_fields = ['get_image_user', 'get_user', 'custom_content_cmt']
    max_num = 1

    def get_image_user(self, CommentBlog):

        if str(CommentBlog.user.avatar) == '':
            return mark_safe(
                '<a href="/admin/traveling/user/{id}/"> <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAPEBAQBxARDhAPDxANDQ8NDQ8ODQ8PFREWFhURFRMYHSggGBolGxUVITEhJSkrLi4uFx8zODcsNygtOisBCgoKBQUFDgUFDisZExkrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrK//AABEIAOEA4QMBIgACEQEDEQH/xAAbAAEBAAMBAQEAAAAAAAAAAAAABQEEBgMCB//EADAQAQACAAQDBgUFAQEBAAAAAAABAgMEESEFMVESIjJBYXFCcoGhsWKRwdHhovAz/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AP2sAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYmerRzHEqxtgx2p6/D/oN9iZ6oWLnMS3itMeldoeEz1B0kTHlLLmo9Hrh5q9fBafad4+4OgE7L8TidseNP1Ry+sKFbRMa1nWJ5THIGQAAAAAAAAAAAAAAAAAAAGLWiI1ttEbzLKTxTM6z2Kco8XrPQHlnc5OJOlNq9OvrLUAAAAABsZTNWw523r51/prgOjwsSLRFqTrEvtE4dmexbS3httPpPVbAAAAAAAAAAAAAAAAAAB54+J2K2t0jX6uemdd55zvPur8XtpSI62j9uaOAAAAAAAAAvZHF7eHEzzjuz7wgqnBreOPaQUgAAAAAAAAAAAAAAAAATuM8qe8/hKWOLV1w4mPhtH32RwAAAAAAAAFDg3it8sflPVODU2vPrEApAAAAAAAAAAAAAAAAAA88bD7VZrPnGn1c9aNJmLc42n3dKlcVy2k9unKfF6T1BOAAAAAAAAX8lg9ikRPPxT7ym8Ny3bt2reGs/vPRZAAAAAAAAAAAAAAAAAAAYtETtbeJ5sXvFY1vMRHWXhg52l7dmk7+Wsaa+wJ+dyU03w96/evv6NJ0zRzHDq23w+5P/P7AjjZxcjiV+HWOtd2vasx4omPeNAYGYiZ8MTPtD3w8niW5VmPW20A12zk8pOJPSvnb+m7l+GRG+NPa9I2r/rfiNNo2BjDpFYiKRpEcn018xm6YcxF53nyjeYjrL1wsWto1w5iY9AfYAAAAAAAAAAAAAAMAy0s3n602w+9b7R7tfPZ/XWuBOkcptHn7JwPTGxrXnXEnX8R7Q8wBv5biU12xu9HX4o/tSwcet//AJzE+nn+znmYnoDpRBw87iV5Wmfm3e0cUv5xWfpILAjzxS/lFY+kvK+exJ520+WNAWsTFrWNcSYj3lOzPE/LL7fqnn9ITpmZ3tOs9ZnWWAZmdd53mecyzh3ms64c6T6PkBWynEYttj92evwz/Sg5lu5LPTTu4u9fvX/AWRisxMa13id4mGQAAAAAAAAAAEriOc17mFO3xT19GxxLNdiOzTxW+0dUYAAAAAAAAAAAAAAAAG7w/OdiezieCf8AmeqxDmlThea17mJPyz/AKQAAAAAAAD5xLxWJtblEavpN4vjcqR5963t5AnY2JN7Ta3Oft6PgAAAAAAAAAAAAAAAAAGa2mJia7TE6xLADoctjResWjz5x0nzeqRwnG0tNJ5W3j3hXAAAAAAAc9msTt3tPrt7RyW83fs0tP6Z0952c+AAAAAAAAAAAAAAAAAAAAD6w79mYmPKYl0dbaxEx5xEuaXOG31w49Na/++kg2gAAAAAaXFbaYenW0R/P8Iytxme7X5v4SQAAAAAAAAAAAAAAAAAAAAFXg1trx6xP7x/iUo8GnvX9o/IKoAAAAAJ3GeVPefwlAAAAAAAAAAAAAAAAAAAAAAocG8V/lj8gCsAAAD//2Q==" width="40px" /></a>'.format(
                    img=CommentBlog.user.avatar, id=CommentBlog.user.id))

        return mark_safe('<a href="/admin/traveling/user/{id}/"> <img src="/static/{img}" width="40px" /></a>'.format(
            img=CommentBlog.user.avatar, id=CommentBlog.user.id))

    def get_user(self, CommentBlog):
        return "{first} {last}".format(first=CommentBlog.user.first_name, last=CommentBlog.user.last_name)

    def custom_content_cmt(self, CommentBlog):
        return '{cmt}'.format(cmt=CommentBlog.content_cmt)


class BlogForm(forms.ModelForm):
    title_blog = forms.CharField(widget=forms.Textarea(attrs={'cols': 750, 'rows': 2}))
    content_blog = forms.CharField(widget=forms.Textarea(attrs={'cols': 750, 'rows': 25}))

    class Meta:
        model = Blog
        fields = '__all__'


class BlogAdmin(admin.ModelAdmin):
    list_display = ['show_image_blog', 'kw_blog', 'title_blog', 'address_blog', 'country_blog', 'count_like_blog',
                    'user']
    search_fields = ['kw_blog', 'title_blog', 'address_blog', 'country_blog', 'count_like_blog']
    list_filter = ['kw_blog', 'address_blog', 'country_blog', 'created_date']
    inlines = [CommentBlogShowReadInlindAdmin, ]
    list_per_page = TourPaginator.page_size
    form = BlogForm

    def show_image_blog(self, Blog):
        return mark_safe(
            '<img src="/static/{url}" width="50px" />'.format(url=Blog.image_blog)
        )


####### ------------ REGISTER:::: SALES_OFF
class SalesOffAdmin(admin.ModelAdmin):
    list_display = ['name_sales', 'description', 'price_value_sales', 'created_date']
    search_fields = ['name_sales', 'price_value_sales']
    list_filter = ['name_sales', 'price_value_sales', 'created_date']
    form = SalesOffForm


class TicketInlindAdmin(admin.TabularInline):
    readonly_fields = ['bill', 'tour', 'type_people', 'user', 'price_real', 'totals_minus_money', 'amount_ticket',
                       'status_ticket']
    model = Ticket
    max_num = 1

class ImageInlindAdmin(admin.TabularInline):
    model = TourImages


####### ------------ REGISTER:::: TOUR
class TourAdmin(admin.ModelAdmin):
    list_display = ['detail', 'name_tour', 'newPrice', 'amount_people_tour', 'remain_people', 'address_tour',
                    'amount_popular_tour', 'amount_like', 'date_begin_tour', 'user_id']
    search_fields = ['name_tour', 'price_tour', 'amount_like']
    list_filter = ['name_tour', 'price_tour', 'amount_like', 'created_date']
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


class BillTicketInlinđAmin(admin.TabularInline):
    readonly_fields = ['tour','type_people','user','price_real','totals_minus_money','amount_ticket','status_ticket']
    model = Ticket
    max_num = 0
    extra = 0

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['tour','type_people','user','price_real','totals_minus_money','amount_ticket','status_ticket']


class TicketAdmin(admin.ModelAdmin):
    list_display = ['tour', 'type_people', 'user', 'price_real', 'totals_minus_money', 'amount_ticket',
                    'status_ticket']
    search_fields = ['price_real']
    list_filter = ['tour', 'type_people', 'user', 'price_real']
    readonly_fields = ['get_bill']
    list_per_page = TicketPaginator.page_size
    form = TicketForm

    def get_bill(self, Ticket):
        return mark_safe('<a href="/admin/traveling/bill/{id}/">{codebill}</a>'.format(id=Ticket.bill.id,
                                                                                       codebill=Ticket.bill.code_bill))


class BillAdmin(admin.ModelAdmin):
    list_display = ['code_bill', 'totals_bill', 'status_bill', 'user', 'method_pay']
    search_fields = ['code_bill', 'totals_bill', 'status_bill', 'user', 'method_pay']
    list_filter = ['totals_bill', 'status_bill', 'user', 'method_pay']
    inlines = [BillTicketInlinđAmin]


class CommentBlogForm(forms.ModelForm):
    content_cmt = forms.CharField(widget=forms.Textarea(attrs={'cols': 750, 'rows': 2}))

    class Meta:
        model = CommentBlog
        fields = '__all__'


class CommentBlogAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_blogg', 'content_cmt', 'amount_like_cmt', 'created_date']
    search_fields = ['user', 'blog', 'content_cmt', 'amount_like_cmt', 'created_date']
    list_filter = ['user', 'blog', 'content_cmt', 'amount_like_cmt', 'created_date']
    list_per_page = CommentPaginator.page_size
    form = CommentBlogForm

    def get_user(self, CommentBlog):
        return CommentBlog.first_name

    def get_blogg(self, CommentBlog):
        return mark_safe('<a href="/admin/traveling/blog/{id}/">{blog}</a>'.format(id=CommentBlog.blog.id,
                                                                                       blog=CommentBlog.blog.title_blog))


class CommentForm(forms.ModelForm):
    content_cmt = forms.CharField(widget=forms.Textarea(attrs={'cols': 750, 'rows': 2}))

    class Meta:
        model = Comment
        fields = '__all__'


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour', 'content_cmt', 'amount_like_cmt', 'created_date']
    search_fields = ['user', 'tour', 'content_cmt', 'amount_like_cmt', 'created_date']
    list_filter = ['user', 'tour', 'content_cmt', 'amount_like_cmt', 'created_date']
    list_per_page = CommentPaginator.page_size
    form = CommentForm

    def get_user(self, Comment):
        return Comment.first_name


class WishListAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_tour_wish', 'is_like', 'created_date']
    search_fields = ['user', 'tour', 'is_like', 'created_date']
    list_filter = ['user', 'tour', 'is_like', 'created_date']
    list_per_page = CommentPaginator.page_size

    def get_tour_wish(self, WishList):
        return mark_safe('<a href="/admin/traveling/tour/{id}/">{tour}</a>'.format(id=WishList.tour.id,
                                                                                   tour=WishList.tour.name_tour))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class UserAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'get_staff']
    list_per_page = TourPaginator.page_size
    form = UserForm
    inlines = [TicketInlindAdmin]

    def get_username(self, User):
        return User.username

    def get_staff(self, User):
        return User.is_staff


class RatingVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_tour_rate','get_amount_star', ]
    list_per_page = RatingVotePaginator.page_size
    form = UserForm

    def get_amount_star(self, RatingVote):
        data = ''
        icon = '❤️'
        for star in range(int(RatingVote.amount_star_voting)):
            data += icon
        return data

    def get_tour_rate(self, RatingVote):
        return mark_safe('<a href="/admin/traveling/tour/{id}/">{tour}</a>'.format(id=RatingVote.tour.id,
                                                                                   tour=RatingVote.tour.name_tour))


class TourImagesAdmin(admin.ModelAdmin):
    list_display = ['get_tour', 'get_image', 'active']
    list_per_page = TourPaginator.page_size

    def get_tour(self, TourImages):
        return mark_safe('<a href="/admin/traveling/tour/{id}/">{tour}</a>'.format(id=TourImages.tour.id,
                                                                                   tour=TourImages.tour.name_tour))
    def get_image(self, TourImages):
        return mark_safe('<img src="/static/{url}" width="50px" height="50px"/>'.format(url=TourImages.image_tour))


class LikeBlogAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_blog_wish', 'is_like', 'created_date']
    search_fields = ['user', 'blog', 'is_like', 'created_date']
    list_filter = ['user', 'blog', 'is_like', 'created_date']
    list_per_page = CommentPaginator.page_size

    def get_blog_wish(self, LikeBlog):
        return mark_safe('<a href="/admin/traveling/blog/{id}/">{blog}</a>'.format(id=LikeBlog.blog.id,
                                                                                   blog=LikeBlog.blog.title_blog))


admin.site.register(SaleOff, SalesOffAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TypeCustomer, TypeCustomerAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(RatingVote, RatingVoteAdmin)
admin.site.register(WishList, WishListAdmin)
admin.site.register(TourImages, TourImagesAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(CommentBlog, CommentBlogAdmin)
admin.site.register(LikeBlog, LikeBlogAdmin)
admin.site.register(User,UserAdmin)
