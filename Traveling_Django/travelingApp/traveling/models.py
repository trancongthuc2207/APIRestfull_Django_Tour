from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


class User(AbstractUser):
    avatar = models.ImageField(upload_to='user/%Y/%m', null=True)
    phone_number = models.CharField(max_length=12, null=True, default="")
    citizen_id = models.CharField(max_length=12, null=True, default="")
    date_of_birth = models.DateTimeField(null=True)
    gender = models.CharField(max_length=50, null=True, default="")
    address = models.CharField(max_length=255, null=True, default="")

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


## Tour
class SaleOff(BaseModel):
    name_sales = models.CharField(max_length=255)
    image_sales = models.ImageField(upload_to='sales/%Y/%m', null=True)
    description = RichTextField()
    price_value_sales = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    price_percent_sales = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    dated_begin_sales = models.DateTimeField()
    dated_finish_sales = models.DateTimeField()
    type_sales = models.IntegerField()
    status_sales = models.CharField(max_length=25)

    def __str__(self):
        return self.name_sales


class Tour(BaseModel):
    name_tour = models.CharField(max_length=255, unique=True)
    description_tour = RichTextField()
    price_tour = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    date_begin_tour = models.DateTimeField(null=True)
    image_tour = models.ImageField(upload_to='travel/tour/%Y/%m', null=True)
    amount_people_tour = models.IntegerField(null=True, default=1)
    remain_people = models.IntegerField(null=True)
    address_tour = models.CharField(max_length=255, null=True)
    amount_popular_tour = models.IntegerField(default=1,  null=True)
    amount_like = models.IntegerField(default=1)
    status_tour = models.CharField(max_length=25, null=True)
    country_tour = models.CharField(max_length=255, null=True)
    rating_count_tour = models.DecimalField(null=True, max_digits=10, decimal_places=2, default=5)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name_tour


class TypeCustomer(BaseModel):
    name_type_customer = models.CharField(max_length=255, unique=True)
    description_customer = RichTextField()
    price_booked = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    sales_off = models.ForeignKey(SaleOff, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name_type_customer


class Bill(BaseModel):
    code_bill = models.CharField(max_length=25, null=True, unique=True, db_index=True)
    totals_bill = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    status_bill = models.CharField(max_length=25)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    method_pay = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.code_bill


class Ticket(BaseModel):
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True)
    type_people = models.ForeignKey(TypeCustomer, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    price_real = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    totals_minus_money = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)
    amount_ticket = models.SmallIntegerField(default=1)
    status_ticket = models.CharField(max_length=25)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.status_ticket


class Comment(BaseModel):
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_cmt = RichTextField()
    amount_like_cmt = models.IntegerField(null=True)
    status_cmt = models.CharField(max_length=25)

    def __str__(self):
        return self.content_cmt


class RatingVote(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True)
    amount_star_voting = models.DecimalField(null=True, default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.amount_star_voting)


class WishList(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True)
    is_like = models.BooleanField()

    def __str__(self):
        return str(self.is_like)


class TourImages(BaseModel):
    tour = models.ForeignKey(Tour, on_delete=models.SET_NULL, null=True)
    image_tour = models.ImageField(upload_to='travel/tour/%Y/%m', null=True)

    def __str__(self):
        return str(self.image_tour)


class Blog(BaseModel):
    kw_blog = models.CharField(max_length=25, db_index=True)
    title_blog = models.CharField(max_length=255, null=False)
    content_blog = RichTextField()
    image_blog = models.ImageField(upload_to='blog/%Y/%m', null=True)
    image_content1_blog = models.ImageField(upload_to='blog/%Y/%m', null=True)
    image_content2_blog = models.ImageField(upload_to='blog/%Y/%m', null=True)
    address_blog = models.CharField(max_length=255, null=True)
    country_blog = models.CharField(max_length=255, null=True)
    count_like_blog = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.kw_blog


class CommentBlog(BaseModel):
    blog = models.ForeignKey(Blog, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_cmt = RichTextField()
    amount_like_cmt = models.IntegerField(null=True)
    status_cmt = models.CharField(max_length=25)

    def __str__(self):
        return self.content_cmt


class LikeBlog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    blog = models.ForeignKey(Blog, on_delete=models.SET_NULL, null=True)
    is_like = models.BooleanField()

    def __str__(self):
        return str(self.is_like)