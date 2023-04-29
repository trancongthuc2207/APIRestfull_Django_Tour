from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('sales-off', views.SalesOffViewSet)
r.register('tours', views.TourViewSet)
r.register('users', views.UserViewSet)
r.register('tickets', views.TicketViewSet)
r.register('bills', views.BillViewSet)
r.register('wishlist', views.WishListViewSet)
r.register('rating', views.RatingVoteViewSet)
r.register('comments', views.CommentViewSet)
r.register('tour-images', views.TourImagesViewSet)
r.register('blogs', views.BlogViewSet)
r.register('comments-blog', views.CommentBlogViewSet)
r.register('likes-blog', views.LikeBlogViewSet)

urlpatterns = [
    path('', include(r.urls))
]
