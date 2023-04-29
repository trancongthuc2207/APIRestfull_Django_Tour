from rest_framework import serializers
from .models import *

baseUrl = "http://127.0.0.1:8000/static/"


class SaleOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOff
        fields = ['name_sales', 'description', 'price_value_sales', 'created_date']


######## TOUR
class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['name_tour', 'description_tour', 'image_tour', 'price_tour', 'amount_people_tour', 'remain_people',
                  'address_tour', 'amount_like', 'country_tour']


class TourBaseShow(serializers.ModelSerializer):
    image_tour = serializers.SerializerMethodField()

    def get_image_tour(self, Tour):
        return baseUrl + str(Tour.image_tour)

    class Meta:
        model = Tour
        fields = ['id', 'name_tour', 'description_tour', 'image_tour', 'date_begin_tour', 'price_tour',
                  'amount_people_tour', 'remain_people',
                  'address_tour', 'amount_like', 'country_tour', 'rating_count_tour']


class TourDetailSerializer(TourBaseShow):
    class Meta:
        model = TourBaseShow.Meta.model
        fields = TourBaseShow.Meta.fields + ['user_id', 'amount_popular_tour', 'created_date']


######## USER
class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, User):
        return baseUrl + str(User.avatar)

    def create(self, validated_data):
        data = validated_data.copy()

        u = User(**data)
        u.set_password(u.password)
        u.save()

        return u

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class TypeCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeCustomer
        fields = ['name_type_customer', 'description_customer', 'price_booked', 'sales_off', 'active', 'created_date']


class BillSerializer(serializers.ModelSerializer):
    ticket_of_bill = serializers.SerializerMethodField()

    def get_ticket_of_bill(self, Bill):
        ticket = Ticket.objects.filter(bill=Bill)
        return list(ticket.values('id', 'amount_ticket', 'active'))

    class Meta:
        model = Bill
        fields = ['id', 'code_bill', 'totals_bill', 'status_bill', 'active', 'created_date', 'ticket_of_bill']


class TicketSerializer(serializers.ModelSerializer):
    tour = serializers.SerializerMethodField()
    name_ticket = serializers.SerializerMethodField()

    def get_tour(self, Ticket):
        return {
            'id': Ticket.tour.id,
            'name_tour': Ticket.tour.name_tour,
            'image_tour': baseUrl + str(Ticket.tour.image_tour),
        }

    def get_name_ticket(self, Ticket):
        return {
            'name': Ticket.tour.name_tour + " --- " + Ticket.type_people.name_type_customer + "--- Số lượng: " + str(
                Ticket.amount_ticket),
            'code_bill': Ticket.bill.code_bill,
            'bill_active': Ticket.bill.active
        }

    class Meta:
        model = Ticket
        fields = ['name_ticket', 'tour', 'active', 'created_date']


class TicketDetailsSerializer(TicketSerializer):
    bill = serializers.SerializerMethodField()
    type_people = serializers.SerializerMethodField()
    tour = serializers.SerializerMethodField()

    def get_bill(self, Ticket):
        return {
            'code_bill': Ticket.bill.code_bill,
            'totals_bill': Ticket.bill.totals_bill,
            'bill_active': Ticket.bill.active
        }

    def get_type_people(self, Ticket):
        return {
            'name_type_customer': Ticket.type_people.name_type_customer,
            'price_booked': Ticket.type_people.price_booked,
        }

    def get_tour(self, Ticket):
        return {
            'id': Ticket.tour.id,
            'name_tour': Ticket.tour.name_tour,
            'image_tour': baseUrl + str(Ticket.tour.image_tour),
            'price_tour': Ticket.tour.price_tour,
        }

    class Meta:
        model = Ticket
        fields = ['tour', 'type_people', 'user', 'amount_ticket', 'price_real', 'totals_minus_money',
                  'status_ticket', 'bill']


class TourImagesSerializer(serializers.ModelSerializer):
    image_tour = serializers.SerializerMethodField()

    def get_image_tour(self, TourImages):
        return {
            baseUrl + str(TourImages.image_tour)
        }

    class Meta:
        model = TourImages
        fields = ['id', 'image_tour', 'active']


class WishListSerializer(serializers.ModelSerializer):
    tour = serializers.SerializerMethodField()

    def get_tour(self, WishList):
        return {
            'id': WishList.tour.id,
            'name_tour': WishList.tour.name_tour,
            'image_tour': baseUrl + str(WishList.tour.image_tour),
            'price_tour': WishList.tour.price_tour,
        }

    class Meta:
        model = WishList
        fields = ['tour', 'is_like', 'active']


class RatingVoteSerializer(serializers.ModelSerializer):
    tour = serializers.SerializerMethodField()

    def get_tour(self, WishList):
        return {
            'id': WishList.tour.id,
            'name_tour': WishList.tour.name_tour,
            'image_tour': baseUrl + str(WishList.tour.image_tour),
            'price_tour': WishList.tour.price_tour,
        }

    class Meta:
        model = RatingVote
        fields = ['tour', 'amount_star_voting', 'active']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'tour', 'content_cmt', 'amount_like_cmt', 'status_cmt', 'active']


class CommentShowSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, Comment):
        return {
            "id": Comment.user.id,
            "first_name": Comment.user.first_name,
            "last_name": Comment.user.last_name,
            "avatar": baseUrl + str(Comment.user.avatar)
        }

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content_cmt', 'amount_like_cmt', 'status_cmt', 'created_date']


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % obj.image.name) if request else ''


class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ['id', 'kw_blog', 'title_blog', 'content_blog', 'image_blog', 'image_content1_blog', 'image_content2_blog', 'count_like_blog', 'user', 'created_date']


class BlogBaseShow(BlogSerializer):
    image_blog = serializers.SerializerMethodField()

    def get_image_blog(self, Blog):
        return {
            baseUrl + str(Blog.image_blog)
        }

    class Meta:
        model = BlogSerializer.Meta.model
        fields = ['id', 'kw_blog', 'title_blog', 'image_blog', 'address_blog', 'country_blog', 'count_like_blog', 'created_date']


class BlogDetailsSerializer(BlogBaseShow):
    image1_blog = serializers.SerializerMethodField()
    image2_blog = serializers.SerializerMethodField()

    def get_image1_blog(self, Blog):
        if str(Blog.image_content1_blog) != '':
            return {
                baseUrl + str(Blog.image_content1_blog)
            }
        return {}

    def get_image2_blog(self, Blog):
        if str(Blog.image_content2_blog) != '':
            return {
                baseUrl + str(Blog.image_content2_blog)
            }
        return {}

    class Meta:
        model = BlogBaseShow.Meta.model
        fields = BlogBaseShow.Meta.fields + ['content_blog', 'image1_blog', 'image2_blog', 'user']


class CommentBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentBlog
        fields = ['id', 'blog', 'content_cmt', 'amount_like_cmt', 'status_cmt', 'active']


class CommentBlogShowSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, CommentBlog):
        return {
            "id": CommentBlog.user.id,
            "first_name": CommentBlog.user.first_name,
            "last_name": CommentBlog.user.last_name,
            "avatar": baseUrl + str(CommentBlog.user.avatar)
        }

    class Meta:
        model = CommentBlog
        fields = ['id', 'user', 'content_cmt', 'amount_like_cmt', 'status_cmt', 'created_date']


class LikeBlogSerializer(serializers.ModelSerializer):
    blog = serializers.SerializerMethodField()

    def get_blog(self, LikeBlog):
        return {
            'id': LikeBlog.blog.id,
            'title_blog': LikeBlog.blog.title_blog,
            'image_blog': baseUrl + str(LikeBlog.blog.image_blog),
        }

    class Meta:
        model = LikeBlog
        fields = ['blog', 'is_like', 'active']
#
#
# class CourseSerializer(ImageSerializer):
#     class Meta:
#         model = Course
#         fields = ['id', 'subject', 'created_date', 'category_id', 'image']
#
#
# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['id', 'name']
#
#
# class LessonSerializer(ImageSerializer):
#     class Meta:
#         model = Lesson
#         fields = ['id', 'subject', 'image']
#
#
# class LessonDetailSerializer(LessonSerializer):
#     tags = TagSerializer(many=True)
#
#     class Meta:
#         model = LessonSerializer.Meta.model
#         fields = LessonSerializer.Meta.fields + ['content', 'tags']
