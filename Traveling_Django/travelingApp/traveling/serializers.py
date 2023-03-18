from rest_framework import serializers
from .models import *


class SaleOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOff
        fields = ['name_sales', 'description', 'price_value_sales', 'created_date']


######## TOUR
class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['name_tour', 'description_tour', 'image_tour', 'price_tour', 'amount_people_tour', 'remain_people',
                  'address_tour', 'amount_like']


class TourDetailSerializer(TourSerializer):
    class Meta:
        model = TourSerializer.Meta.model
        fields = TourSerializer.Meta.fields + ['user_id', 'amount_popular_tour', 'created_date']


######## USER
class UserSerializer(serializers.ModelSerializer):

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

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['tour', 'type_people', 'user', 'amount_ticket', 'price_real', 'status_ticket']


# class ImageSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField(source='image')
#
#     def get_image(self, obj):
#         if obj.image:
#             request = self.context.get('request')
#             return request.build_absolute_uri('/static/%s' % obj.image.name) if request else ''
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
