from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response
from .models import *
from .serializers import (SaleOffSerializer, TourSerializer, TourDetailSerializer, UserSerializer, TicketSerializer,
                          TicketDetailsSerializer, TourBaseShow, TourImagesSerializer, RatingVoteSerializer, CommentShowSerializer)

from .paginators import TourPaginator, TicketPaginator, BillPaginator, WishListPaginator, RatingVotePaginator, CommentPaginator
from django.core.cache import cache
from datetime import datetime
import random
from .perms import *
from .condition import *
from urllib.parse import urlparse

baseCache = "Traveling:1:"
# + id Tour
nameKey_Tour_Redis = "local_details_tour_"


def GernerateCodeBill():
    code = datetime.now().strftime("D%m%d%Y-")
    num = ''
    for i in range(0, 7):
        n = random.randint(1, 9)
        num += str(n)
    code = code + num

    return code


#### SALES OFF
class SalesOffViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = SaleOff.objects.all()
    serializer_class = SaleOffSerializer


##### TOUR
class TourViewSet(viewsets.ViewSet, generics.ListAPIView):
    # queryset = Tour.objects.filter(active=True)
    serializer_class = TourBaseShow
    pagination_class = TourPaginator
    parser_classes = [parsers.MultiPartParser, ]
    queryset = Tour.objects.filter(active=True)

    # PERMISSION
    def get_permissions(self):
        if self.action in ['create_tour']:
            return [CanCRUD_Tour()]

        return [permissions.AllowAny()]

    ######## GET
    def filter_queryset(self, queryset):
        #########
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(name_tour__icontains=q)

        tour_id = self.request.query_params.get('tour_id')
        #########
        if tour_id:
            queryset = queryset.filter(id=tour_id)
        #########
        price_from = self.request.query_params.get('priceF')
        price_to = self.request.query_params.get('priceTo')

        if price_from and price_to:
            queryset = queryset.filter(price_tour__gte=(float(price_from)), price_tour__lte=(float(price_to)))
        elif price_from:
            queryset = queryset.filter(price_tour__gte=(float(price_from)))
        elif price_to:
            queryset = queryset.filter(price_tour__lte=(float(price_to)))

        ###########
        name_address = self.request.query_params.get('address')
        if name_address:
            queryset = queryset.filter(address_tour__icontains=name_address)

        print(self.request.query_params.get('message'))

        return queryset

    @action(methods=['get'], detail=True, url_path='details-tour')
    def details_tour(self, request, pk):
        if cache.get(nameKey_Tour_Redis + str(pk)):
            data_details = cache.get(nameKey_Tour_Redis + str(pk))
            # print(json.load(data_details))
            # data_re = ast.literal_eval(data_details)
            return Response(data_details)
        else:
            try:
                c = self.get_object()
                data = TourDetailSerializer(c).data
                t = len(TourImages.objects.filter(tour_id=c.id))
                if t > 0:
                    data['list_images'] = TourImagesSerializer(TourImages.objects.filter(tour_id=c.id), many=True).data


                l_cmt = len(Comment.objects.filter(tour_id=c.id))
                if l_cmt > 0:
                    data['list_comment'] = CommentShowSerializer(Comment.objects.filter(tour_id=c.id), many=True).data

                cache.set(nameKey_Tour_Redis + pk, str(data), 300)
                return Response(data)
            except:
                return Response('Have a problem')

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments_tour(self, request, pk):
            c = self.get_object()
            l_cmt = len(Comment.objects.filter(tour_id=c.id))
            data = []
            if l_cmt > 0:
                data = CommentShowSerializer(Comment.objects.filter(tour_id=c.id), many=True).data
            return Response(data)

    ####### POST Create New
    @action(methods=['post'], detail=False, url_path='create-tour')
    def create_tour(self, request):
        if CanCRUD_Tour.has_permission(self, request, request.user):
            try:
                tour = Tour(**TourSerializer(request.data).data)
                tour.image_tour = request.data['image_tour']
                tour.remain_people = tour.amount_people_tour
                tour.user = request.user
                tour.status_tour = "Run"
                tour.save()
                # Save List Image
                if len(request.FILES) > 1:
                    num = 0
                    for img in request.FILES.values():
                        if num > 0:
                            images_tour = TourImages(tour=tour, image_tour=img)
                            images_tour.save()
                            print(images_tour.image_tour)
                        num += 1

                return Response(TourBaseShow(tour).data)
            except:
                return Response("Data have a problem")
        return Response("You can't add this tour")

    @action(methods=['put'], detail=True, url_path='update-tour')
    def update_tour(self, request, pk):
        if CanCRUD_Tour.has_permission(self, request, request.user) == False:
            return Response("You don't have permission", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            try:
                tour_root = Tour.objects.get(id=pk)

                for key, value in request.data.items():
                    if "uploadedfile.InMemoryUploadedFile" in str(type(value)):
                        continue
                    setattr(tour_root, key, value)

                if "image_tour" in request.data:
                    tour_root.image_tour = request.data["image_tour"]

                tour_root.save()

                if len(request.FILES) > 1:
                    TourImages.objects.filter(tour=Tour.objects.get(id=pk)).delete()
                    num = 0
                    for img in request.FILES.values():
                        if num > 0:
                            images_tour = TourImages(tour=Tour.objects.get(id=pk), image_tour=img)
                            images_tour.save()
                        num += 1

                # Update Cache
                if cache.get(nameKey_Tour_Redis + str(pk)):
                    data = TourDetailSerializer(tour_root).data
                    t = len(TourImages.objects.filter(tour_id=pk))
                    if t > 0:
                        data['list_images'] = TourImagesSerializer(TourImages.objects.filter(tour_id=pk),
                                                                   many=True).data
                        data['isUpdate'] = True

                    l_cmt = len(Comment.objects.filter(tour_id=pk))
                    if l_cmt > 0:
                        data['list_comment'] = CommentShowSerializer(Comment.objects.filter(tour_id=pk),
                                                                     many=True).data
                    cache.set(nameKey_Tour_Redis + pk, str(data), 300)
                # Response
                data = TourDetailSerializer(tour_root).data
                t = len(TourImages.objects.filter(tour_id=tour_root.id))
                if t > 0:
                    data['list_images'] = TourImagesSerializer(TourImages.objects.filter(tour_id=tour_root.id),
                                                               many=True).data

                return Response(data)
            except:
                return Response("Lỗi cập nhật", status=status.HTTP_204_NO_CONTENT)


####### USER: Người dùng
class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current_user', 'update', 'partial_update', 'get_full_user']:
            return [CanGetUser()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)

    ####### FULL USER
    @action(methods=['get'], detail=False, url_path='all-users')
    def get_full_user(self, request):
        if request.user.is_superuser or request.user.is_staff:
            users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
            return Response(UserSerializer(users, many=True).data)
        else:
            return Response("You can not entry this data")


####### Ticket: Vé
class TicketViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    pagination_class = TicketPaginator

    def get_permissions(self):
        if self.action in ['create_ticket', 'update', 'partial_update', 'get_user_ticket']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=False, url_path='create-ticket')
    def create_ticket(self, request):
        if request.user.is_superuser or request.user.is_staff or request.user.is_staff == False:
            try:
                bill = Bill(code_bill=GernerateCodeBill(), status_bill="Pending")
                ##### Get Object
                tour_da = Tour.objects.get(id=int(request.data['tour']))

                if tour_da.remain_people == 0:
                    return Response("Tour is exhausted people")

                type_people_da = TypeCustomer.objects.get(id=int(request.data['type_people']))
                if check_can_book_ticket(request.user, tour_da, type_people_da):
                    ##### New Ticket
                    ticket = Ticket(tour=tour_da, type_people=type_people_da, user=request.user,
                                    amount_ticket=int(request.data['amount']))
                    ticket.price_real = (tour_da.price_tour + type_people_da.price_booked) * ticket.amount_ticket

                    ### SET PRICE DISCOUNT
                    if type_people_da.sales_off.id != 1:
                        if type_people_da.sales_off.price_value_sales != 0:
                            ticket.totals_minus_money = type_people_da.sales_off.price_value_sales * ticket.amount_ticket
                        elif type_people_da.sales_off.price_percent_sales != 0:
                            ticket.totals_minus_money = ((
                                                                 type_people_da.sales_off.price_percent_sales / 100) * type_people_da.price_booked) * ticket.amount_ticket
                    else:
                        ticket.totals_minus_money = 0
                    ticket.status_ticket = "Pending"

                    ## TOTALS BILL
                    bill.totals_bill = ticket.price_real - ticket.totals_minus_money
                    ticket.bill = bill

                    try:
                        bill.save()
                        ticket.save()
                        data = TicketSerializer(ticket).data
                        data['total-discount'] = ticket.totals_minus_money
                        data['bill-code'] = bill.code_bill
                        return Response(data, status=status.HTTP_201_CREATED)
                    except:
                        return Response("Some Thing Erro When Booking Ticket")
                else:
                    return Response("This tour that had ticket")
            except:
                return Response("Data have a problem")
        return Response("You can't add this ticket")

    @action(methods=['get'], detail=False, url_path='user-ticket')
    def get_user_ticket(self, request):
        queryset = Ticket.objects.all()
        stt = self.request.query_params.get("stt")
        if stt:
            queryset = queryset.filter(status_ticket__icontains=stt, user=request.user)

        bill_code = self.request.query_params.get("billcode")
        if bill_code:
            print(bill_code)
            bill = Bill.objects.get(code_bill__icontains=bill_code)
            queryset = queryset.filter(bill=bill, user=request.user)

        if bill_code:
            return Response(TicketDetailsSerializer(queryset, many=True).data)

        return Response(TicketSerializer(queryset, many=True).data)

    @action(methods=['patch'], detail=False, url_path='user-update-ticket')
    def user_update_ticket(self, request):
        queryset = Ticket.objects.all()

        bill_code = self.request.data['code_bill']
        try:
            bill = Bill.objects.get(code_bill__exact=bill_code)

            if bill:
                ticket = Ticket.objects.get(bill=bill)
                if TicketOwnerUser.has_permission(self, request, ticket):
                    try:
                        if request.data['status_ticket']:
                            ticket.status_ticket = request.data['status_ticket']
                            ticket.active = False
                            ticket.save()
                            bill.status_bill = "Cancle"
                            bill.active = False
                            bill.save()
                    except:
                        return Response("Lỗi trạng thái", status=status.HTTP_204_NO_CONTENT)
                    queryset = queryset.filter(bill=bill, user=request.user)
                    return Response(TicketDetailsSerializer(queryset, many=True).data)
                else:
                    return Response("Can't edit with your account", status=status.HTTP_204_NO_CONTENT)
        except:
            return Response("Không tìm thấy Bill code", status=status.HTTP_204_NO_CONTENT)


####### BILL: Hoá Đơn
class BillViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    pagination_class = BillPaginator

    def get_permissions(self):
        if self.action in ['get_user_bill']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='user-bill')
    def get_user_bill(self, request):
        queryset = Bill.objects.all()

        queryset = queryset.filter(user=request.user)
        #####
        stt = self.request.query_params.get("stt")
        if stt:
            queryset = queryset.filter(status_bill__icontains=stt,user=request.user)

        bill_code = self.request.query_params.get("billcode")
        if bill_code:
            queryset = queryset.filter(code_bill__icontains=bill_code,user=request.user)

        return Response(BillSerializer(queryset, many=True).data)

    @action(methods=['patch'], detail=True, url_path='update-bill')
    def update_user_bill(self, request, pk):
        bill = Bill.objects.get(id=pk)
        if BillOwnerUser.has_permission(self,request,bill) == False:
            return Response("You cant have permission")

        bill.status_bill = request.data['status_bill']
        bill.method_pay = request.data['method_pay']
        ticket = Ticket.objects.get(bill=bill)
        if request.data['status_bill'] == "Cancel":
            bill.active = 0
            bill.save()
            ticket.active = 0
            ticket.status_ticket = "Cancel"
            ticket.save()
            return Response(BillSerializer(bill).data)

        bill.save()
        ticket.status_ticket = request.data['status_bill']

        tour = Tour.objects.get(id=ticket.tour.id)
        tour.remain_people -= 1
        tour.save()

        return Response(BillSerializer(bill).data)


####### WishList
class WishListViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
    pagination_class = WishListPaginator

    def get_permissions(self):
        if self.action in ['get_user_wishlist', 'add_user_wishlist']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='my-wish-list')
    def get_user_wishlist(self, request):
        queryset = WishList.objects.all()
        queryset = queryset.filter(user=request.user, is_like=1)

        return Response(WishListSerializer(queryset, many=True).data)

    @action(methods=['post'], detail=True, url_path='add-wish-list')
    def add_user_wishlist(self, request, pk):
        try:
            wish = WishList.objects.filter(tour=Tour.objects.get(id=pk),user=request.user)
            if len(wish) > 0:
                oldwish = WishList.objects.get(tour=Tour.objects.get(id=pk),user=request.user)
                if oldwish.is_like == 0:
                    oldwish.is_like = 1
                else:
                    oldwish.is_like = 0
                oldwish.save()
                return Response(WishListSerializer(oldwish).data)
            else:
                newwish = WishList(tour=Tour.objects.get(id=pk),user=request.user)
                newwish.is_like = 1
                newwish.save()
                return Response(WishListSerializer(newwish).data)
        except:
            return Response("Error Add Wish List")


####### RatingVote
class RatingVoteViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = RatingVote.objects.all()
    serializer_class = RatingVoteSerializer
    pagination_class = RatingVotePaginator

    def get_permissions(self):
        if self.action in ['my-rating-list', 'add_user_rating']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='my-rating-list')
    def get_user_wishlist(self, request):
        queryset = RatingVote.objects.all()
        queryset = queryset.filter(user=request.user)

        return Response(RatingVoteSerializer(queryset, many=True).data)

    @action(methods=['post'], detail=True, url_path='add-rating-tour')
    def add_user_rating(self, request, pk):
        try:
            star = float(request.data['amount_star_voting'])
            rating = RatingVote.objects.filter(tour=Tour.objects.get(id=pk),user=request.user)
            if len(rating) > 0:
                oldrate = RatingVote.objects.get(tour=Tour.objects.get(id=pk),user=request.user)
                oldrate.amount_star_voting = star
                oldrate.save()
                return Response(RatingVoteSerializer(oldrate).data)
            else:
                newrate = RatingVote(tour=Tour.objects.get(id=pk),user=request.user)
                newrate.amount_star_voting = star
                newrate.save()
                return Response(RatingVoteSerializer(newrate).data)
        except:
            return Response("Error Rating Tour")


####### Comment:
class CommentViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPaginator

    def get_permissions(self):
        if self.action in ['add_user_comment']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='add-comment-tour')
    def add_user_comment(self, request, pk):
        try:
            content = request.data['content_cmt']
            add_comment = Comment(tour=Tour.objects.get(id=pk),user=request.user,content_cmt=content,amount_like_cmt=0,status_cmt="Run")
            add_comment.save()
            return Response(CommentSerializer(add_comment).data)
        except:
            return Response("Error Comment Comment")

    @action(methods=['delete'], detail=True, url_path='delete-comment-tour')
    def delete_user_comment(self, request, pk):
        try:
            cmt = Comment.objects.get(id=pk)
            if CommentOwnerUser.has_permission(self,request,cmt) == False:
                return Response("You cant have permission!!!")
            cmt.delete()
            return Response("Delete Successfully!!!")
        except:
            return Response("Error Delete Comment")

    @action(methods=['patch'], detail=True, url_path='edit-comment-tour')
    def edit_user_comment(self, request, pk):
        try:
            cmt = Comment.objects.get(id=pk)
            if CommentOwnerUser.has_permission(self,request,cmt) == False:
                return Response("You cant have permission!!!")
            cmt.content_cmt = request.data['content_cmt']
            cmt.save()
            data = CommentSerializer(cmt).data
            data["status_update"] = "Update Successfully!!!"
            return Response(data)
        except:
            return Response("Error Update Comment")