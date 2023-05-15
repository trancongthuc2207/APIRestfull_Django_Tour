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

from django.core.mail import send_mail
from django.conf import settings

from .test_Momo import set_paramater_url

import json

baseCache = "Traveling:1:"
# + id Tour
nameKey_Tour_Redis = "local_details_tour_"
nameKey_Blog_Redis = "local_details_blog"

def GernerateCodeBill():
    code = datetime.now().strftime("D%m%d%Y-")
    num = ''
    for i in range(0, 7):
        n = random.randint(1, 9)
        num += str(n)
    code = code + num

    return code

def convert_currency(f):
    return "{:0,.2f}".format(float(f))

def update_cache_details_tour(pk):
    c = Tour.objects.get(pk=pk)
    data = TourDetailSerializer(c).data
    t = len(TourImages.objects.filter(tour_id=c.id,active=True))
    if t > 0:
        data['list_images'] = TourImagesSerializer(TourImages.objects.filter(tour_id=c.id,active=True), many=True).data

    rating_vote = {}
    for star in range(1, 6):
        rating_vote["Star " + str(star)] = len(RatingVote.objects.filter(amount_star_voting=star, tour=c))
    data['num_rating'] = rating_vote

    l_cmt = len(Comment.objects.filter(tour_id=c.id))
    if l_cmt > 0:
        data['list_comment'] = CommentShowSerializer(Comment.objects.filter(tour_id=c.id), many=True).data

    return cache.set(nameKey_Tour_Redis + pk, str(data), 300)

def update_cache_details_blog(pk):
    c = Blog.objects.get(pk=pk)
    data = BlogDetailsSerializer(c).data

    l_cmt = len(CommentBlog.objects.filter(blog_id=c.id))
    if l_cmt > 0:
        data['list_comment'] = CommentShowSerializer(CommentBlog.objects.filter(blog_id=c.id), many=True).data

    return cache.set(nameKey_Blog_Redis + pk, str(data), 300)

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
    queryset = Tour.objects.filter(active=True, remain_people__gt = 0).order_by('-rating_count_tour')

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
            queryset = queryset.filter(name_tour__icontains=q) | queryset.filter(address_tour__icontains=q) | queryset.filter(country_tour__icontains=q)

        tour_id = self.request.query_params.get('tour_id')
        #########
        if tour_id:
            queryset = queryset.filter(id=tour_id)
        ######### FILTER PRICE
        price_from = self.request.query_params.get('priceF')
        price_to = self.request.query_params.get('priceTo')
        if price_from and price_to:
            queryset = queryset.filter(price_tour__gte=(float(price_from)), price_tour__lte=(float(price_to)))
        elif price_from:
            queryset = queryset.filter(price_tour__gte=(float(price_from)))
        elif price_to:
            queryset = queryset.filter(price_tour__lte=(float(price_to)))

        ########### FILTER ADDRESS
        # name_address = self.request.query_params.get('address')
        # if name_address:
        #     queryset = queryset.filter(address_tour__icontains=name_address)

        ########### FILTER SORT
        sort_by = self.request.query_params.get('sort_by')
        match sort_by:
            case 'newest':
                queryset = queryset.order_by('-date_begin_tour')
            case 'high_price':
                queryset = queryset.order_by('-price_tour')
            case 'low_price':
                queryset = queryset.order_by('price_tour')

        ########### FILTER REMAIN
        remain = self.request.query_params.get('remain')
        if remain:
            queryset = queryset.filter(remain_people__gte=int(remain)).order_by('-remain_people')

        ########### FILTER DATE
        date_sr = self.request.query_params.get('date')
        if date_sr:
            queryset = queryset.filter(date_begin_tour__gte=date_sr)

        print(self.request.query_params.get('message'))
        return queryset

    @action(methods=['get'], detail=True, url_path='details-tour')
    def details_tour(self, request, pk):
        if cache.get(nameKey_Tour_Redis + str(pk)):
            data_details = cache.get(nameKey_Tour_Redis + str(pk))
            # print(json.load(data_details))
            # data_re = ast.literal_eval(data_details)
            # print(json.loads(data_details))

            return Response(data_details)
        else:
            try:
                c = self.get_object()
                data = TourDetailSerializer(c).data
                t = len(TourImages.objects.filter(tour_id=c.id,active=True))
                if t > 0:
                    data['list_images'] = TourImagesSerializer(TourImages.objects.filter(tour_id=c.id,active=True), many=True).data

                rating_vote = {}
                for star in range(1,6):
                    rating_vote["Star " + str(star)] = len(RatingVote.objects.filter(amount_star_voting=star, tour=c))
                data['num_rating'] = rating_vote

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


    @action(methods=['post'], detail=False, url_path='create-10-tour')
    def create_10_tour(self, request):
        if CanCRUD_Tour.has_permission(self, request, request.user):
            try:
                for i in range(10):
                    tour = Tour(**TourSerializer(request.data).data)
                    tour.name_tour += " V" + str(i)
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
                            num += 1

                return Response(TourBaseShow(tour).data)
            except:
                return Response("Data have a problem")
        return Response("You can't add this tour")

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
                        num += 1

                return Response(TourBaseShow(tour).data)
            except:
                return Response("Data have a problem")
        return Response("You can't add this tour")


    @action(methods=['put'], detail=True, url_path='update-tour')
    def update_tour(self, request, pk):
        if CanCRUD_Tour.has_permission(self, request, request.user) == False:
            return Response("You don't have permission", status=status.HTTP_204_NO_CONTENT)
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
                    update_cache_details_tour(pk)
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
        if self.action in ['update', 'partial_update', 'get_full_user']:
            return [CanUpdateUser()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)

    ####### FULL USER
    @action(methods=['get'], detail=False, url_path='all-users')
    def get_full_user(self, request):
        if request.user.is_staff and request.user.is_superuser == False:
            users = User.objects.filter(is_staff=False, is_superuser=False)
            return Response(UserSerializer(users, many=True).data)
        elif request.user.is_superuser:
            users = User.objects.filter(is_superuser=False)
            return Response(UserSerializer(users, many=True).data)
        else:
            return Response("You can not entry this data", status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        user = User()

        if 'avatar' in request.data:
            user.avatar = request.data['avatar']
        for key, value in request.data.items():
            if "uploadedfile.InMemoryUploadedFile" in str(type(value)):
                continue
            setattr(user, key, value)
        user.set_password(request.data['password'])
        user.save()

        return Response(UserSerializer(user).data)

    def put(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)

        if 'avatar' in request.data:
            user.avatar = request.data['avatar']
        for key, value in request.data.items():
            if "uploadedfile.InMemoryUploadedFile" in str(type(value)):
                continue
            setattr(user, key, value)

        if 're_password' in request.data:
            u = User()
            u.set_password(request.data['re_password'])
            if u.password != user.password:
                return Response("Your old password is not corrected!!")

        if 'password' in request.data:
            user.set_password(request.data['password'])

        user.save()

        return Response(UserSerializer(user).data)

    def partial_update(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)

        if 'avatar' in request.data:
            user.avatar = request.data['avatar']
        for key, value in request.data.items():
            if "uploadedfile.InMemoryUploadedFile" in str(type(value)):
                continue
            setattr(user, key, value)

        if 're_password' in request.data:
            u = User()
            u.set_password(request.data['re_password'])
            if u.password != user.password:
                return Response("Your old password is not corrected!!")

        if 'password' in request.data:
            user.set_password(request.data['password'])

        user.save()

        return Response(UserSerializer(user).data)

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

                if not check_can_book_more_ticket(request.user):
                    return Response({'message':"Sorry about that you have booked more than 10 ticket's pending, You must pay it!!"}, status=status.HTTP_204_NO_CONTENT)

                if not check_amount_to_book(int(request.data['amount']), tour_da.remain_people):
                    return Response({'message':"Your booked amounting that is bigger than tour have, only {} remain".format(tour_da.remain_people)}, status=status.HTTP_204_NO_CONTENT)

                if tour_da.remain_people == 0:
                    return Response({'message':"Tour is exhausted people"}, status=status.HTTP_204_NO_CONTENT)

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
                    ticket.user = request.user
                    bill.user = request.user
                    # TOTALS BILL
                    bill.totals_bill = ticket.price_real - ticket.totals_minus_money
                    ticket.bill = bill

                    message_email = "====== Tên Tour: {}\n- Giá Tour: {}\n- Giá đơn vé: {}/{}\n- Giảm giá: {}\n- Số vé: {}\n- Mã Bill: {}\n- Tổng tiền vé: {}\n- Đến Trang Thanh Toán: {}".\
                        format(tour_da.name_tour,convert_currency(tour_da.price_tour),convert_currency(type_people_da.price_booked),type_people_da.name_type_customer,convert_currency(ticket.totals_minus_money),
                               ticket.amount_ticket,bill.code_bill,convert_currency(bill.totals_bill),
                               set_paramater_url(bill.code_bill,bill.totals_bill,request.user.username,
                                                 "https://thuctran2207.pythonanywhere.com/",
                                                 "https://thuctran2207.pythonanywhere.com/",
                                                 "Thanh toan hoa don dat ve Tour"))
                    try:
                        bill.save()
                        ticket.save()
                        data = TicketSerializer(ticket).data
                        data['total-discount'] = ticket.totals_minus_money
                        data['bill-code'] = bill.code_bill

                        if request.user.email is not None:
                            list_mail = []
                            data['mail-result'] = "Đặt vé thành công, bạn có thể kiểm tra trong hộp thư Email."
                            data['payUrl'] =  set_paramater_url(bill.code_bill,bill.totals_bill,request.user.username,
                                                 "https://thuctran2207.pythonanywhere.com/",
                                                 "https://thuctran2207.pythonanywhere.com/",
                                                 "Thanh toan hoa don dat ve Tour")
                            list_mail.append(request.user.email)
                            send_mail(subject="Đặt vé Tour Thành Công, VUI LÒNG QUÝ KHÁCH THANH TOÁN !!",
                                      message=message_email,
                                      from_email=settings.EMAIL_HOST_USER, recipient_list=list_mail,
                                      fail_silently=False)
                        return Response(data, status=status.HTTP_201_CREATED)
                    except:
                        return Response({'message':"Some Thing Error When Booking Ticket"}, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({'message':"This tour that had ticket"}, status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({'message':"Data have a problem"}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message':"You can't add this ticket"}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, url_path='user-ticket')
    def get_user_ticket(self, request):
        queryset = Ticket.objects.filter(user=request.user)
        stt = self.request.query_params.get("stt")
        match stt:
            case 'Success':
                queryset = queryset.filter(status_ticket__icontains=stt, user=request.user)
            case 'Expired':
                queryset = queryset.filter(status_ticket__icontains=stt, user=request.user)
            case 'Cancel':
                queryset = queryset.filter(status_ticket__icontains=stt, user=request.user)
            case 'Pending':
                queryset = queryset.filter(status_ticket__icontains=stt, user=request.user)

        bill_code = self.request.query_params.get("billcode")
        if bill_code:
            bill = Bill.objects.get(code_bill__icontains=bill_code)
            queryset = queryset.filter(bill=bill, user=request.user)
            return Response(TicketDetailsSerializer(queryset, many=True).data)

        return Response(TicketDetailsSerializer(queryset, many=True).data)

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
                            bill.status_bill = "Cancel"
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

        # if self.action in ['get_all_bill', 'get_revenue']:
        #     return [CanGetUser()]

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
            return Response("You cant have permission", status=status.HTTP_204_NO_CONTENT)

        ticket = Ticket.objects.get(bill=bill)

        if bill.status_bill == "Expired" or ticket.status_ticket == "Expired" or bill.active == 0 or ticket.active == 0 or bill.status_bill == "Success" or ticket.status_ticket == "Success":
            return Response(BillSerializer(bill).data)

        bill.status_bill = request.data['status_bill']
        bill.method_pay = request.data['method_pay']

        if ticket.tour.remain_people == 0:
            bill.active = 0
            bill.status_bill = "Expired"
            bill.save()
            ticket.active = 0
            ticket.status_ticket = "Expired"
            ticket.save()
            list = Ticket.objects.filter(tour = ticket.tour, status_ticket = 'Pending')
            lenTick = len(list)
            for tick in list:
                print(tick.id)
                t = Ticket.objects.get(pk=tick.id)
                t.active = 0
                t.status_ticket = "Expired"
                t.save()

                b = Bill.objects.get(pk=tick.bill.id)
                b.active = 0
                b.status_bill = "Expired"
                b.save()
            return Response(BillSerializer(bill).data)

        if request.data['status_bill'] == "Cancel":
            bill.active = 0
            bill.save()
            ticket.active = 0
            ticket.status_ticket = "Cancel"
            ticket.save()
            return Response(BillSerializer(bill).data)

        tour = Tour.objects.get(id=ticket.tour.id)
        if tour.remain_people - ticket.amount_ticket < 0:
            ticket.status_ticket = "Expired"
            ticket.active = 0
            bill.status_bill = "Expired"
            bill.active = 0
            bill.save()
            ticket.save()
            return Response(BillSerializer(bill).data)

        bill.save()
        ticket.status_ticket = request.data['status_bill']

        tour.remain_people -= ticket.amount_ticket
        tour.save()
        ticket.save()
        return Response(BillSerializer(bill).data)

    @action(methods=['get'], detail=False, url_path='all-bill')
    def get_all_bill(self, request):
        queryset = Bill.objects.all()

        ### KW: STATUS
        stt = self.request.query_params.get("stt")
        match stt:
            case 'Success':
                queryset = queryset.filter(status_bill__icontains=stt)
            case 'Expired':
                queryset = queryset.filter(status_bill__icontains=stt)
            case 'Cancel':
                queryset = queryset.filter(status_bill__icontains=stt)
            case 'Pending':
                queryset = queryset.filter(status_bill__icontains=stt)

        ### KW: BILLCODE
        bill_code = self.request.query_params.get("billcode")
        if bill_code:
            queryset = queryset.filter(code_bill__icontains=bill_code)

        ## KW: NAME_CUSTOMERS
        name_customer = self.request.query_params.get("name_customer")
        if name_customer:
            queryset = queryset.filter(user__last_name__icontains=name_customer) | queryset.filter(user__first_name__icontains=name_customer)

        ## KW: PHONE_CUSTOMERS
        phone_customer = self.request.query_params.get("phone_customer")
        if phone_customer:
            queryset = queryset.filter(user__phone_number__icontains=phone_customer)

        return Response(BillShowStaffSerializer(queryset, many=True).data)

    @action(methods=['get'], detail=False, url_path='revenue')
    def get_revenue(self, request):
        queryset = Bill.objects.filter(status_bill = 'Success')
        totals_revenue = 0
        list_id_tour = []
        list_code_bill = []
        ## DATE EXACT
        date_exact = self.request.query_params.get('date_exact')
        if date_exact:
            list_date = date_exact.split('-')
            num_list = len(list_date)
            if num_list == 1:
                queryset = queryset.filter(created_date__year=list_date[0])
            if num_list == 2:
                queryset = queryset.filter(created_date__month=list_date[1],created_date__year=list_date[0])
            if num_list == 3:
                queryset = queryset.filter(created_date__day=list_date[2],created_date__month=list_date[1],created_date__year=list_date[0])

        # DATE FROM - TO
        date_fr = self.request.query_params.get('date_fr')
        date_to = self.request.query_params.get('date_to')
        print(date_fr)

        if date_fr:
            queryset = queryset.filter(created_date__gte=date_fr)
        if date_to:
            queryset = queryset.filter(created_date__lte=date_to)
        if date_fr and date_to:
            queryset = queryset.filter(created_date__gte=date_fr, created_date__lte=date_to)

        for bill in queryset:
            totals_revenue += bill.totals_bill
            list_id_tour.append(Ticket.objects.get(bill__code_bill__exact=bill.code_bill).tour.id)
            list_code_bill.append(bill.code_bill)

        data = {}
        data['RELATED_BILL'] = {}
        data['RELATED_BILL']['REVENUE'] = totals_revenue
        data['RELATED_BILL']['count_bill'] = len(queryset)
        data['RELATED_BILL']['list_bill'] = BillSerializer(queryset, many=True).data

        data['RELATED_TOUR'] = {}
        list_tour_serializer = []
        list_id_tour_temp = []
        list_ticket = []
        totals_ticket_per_tour = 0
        totals_money_per_tour = 0
        toals_ticket = 0
        for id_t in list_id_tour:
            if id_t not in list_id_tour_temp:
                list_id_tour_temp.append(id_t)
        if len(list_id_tour_temp) > 0:
            for id in list_id_tour_temp:
                da = TourBaseShow(Tour.objects.get(pk=id)).data

                for codebill in list_code_bill:
                    tic = Ticket.objects.get(bill__code_bill=codebill)
                    if tic.tour.id == id:
                        da_tic = TicketSerializer(tic).data
                        list_ticket.append(da_tic)
                        list_code_bill.remove(codebill)
                        toals_ticket += tic.amount_ticket
                        totals_ticket_per_tour += tic.amount_ticket
                        totals_money_per_tour += tic.bill.totals_bill
                da['totals_money_per_tour'] = totals_money_per_tour
                da['count_ticket_per_tour'] = totals_ticket_per_tour
                da['list_ticket'] = list_ticket
                list_ticket = []
                totals_ticket_per_tour = 0
                totals_money_per_tour = 0
                list_tour_serializer.append(da)

        data['RELATED_TOUR']['Count_Tour'] = len(list_id_tour_temp)
        data['RELATED_TOUR']['Count_Ticket'] = toals_ticket
        data['RELATED_TOUR']['Tour'] = list_tour_serializer

        return Response(data)

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

        sort = self.request.query_params.get("sort")
        match sort:
            case '0':
                queryset = queryset.filter(tour__remain_people=0)
            case '':
                queryset = queryset.filter(tour__remain_people__gt=0)

        return Response(WishListSerializer(queryset, many=True).data)

    @action(methods=['post'], detail=True, url_path='add-wish-list')
    def add_user_wishlist(self, request, pk):
        try:
            wish = WishList.objects.filter(tour=Tour.objects.get(id=pk),user=request.user)
            tour = Tour.objects.get(pk=pk)
            if len(wish) > 0:
                oldwish = WishList.objects.get(tour=Tour.objects.get(id=pk),user=request.user)
                if oldwish.is_like == 0:
                    oldwish.is_like = 1
                    tour.amount_like += 1
                else:
                    oldwish.is_like = 0
                    tour.amount_like -= 1
                oldwish.save()
                tour.save()
                return Response(WishListSerializer(oldwish).data)
            else:
                newwish = WishList(tour=Tour.objects.get(id=pk),user=request.user)
                newwish.is_like = 1
                tour.amount_like += 1
                newwish.save()
                tour.save()
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
        if not check_can_cmt_rate_tour(request.user, Tour.objects.get(id=pk)):
            return Response("You do not used to book this tour", status=status.HTTP_204_NO_CONTENT)
        try:
            star = float(request.data['amount_star_voting'])
            rating = RatingVote.objects.filter(tour=Tour.objects.get(id=pk),user=request.user)
            if len(rating) > 0:
                oldrate = RatingVote.objects.get(tour=Tour.objects.get(id=pk),user=request.user)
                oldrate.amount_star_voting = star
                oldrate.save()
                ## RE UPDATE COUNT RATING VOTE
                num_people = 0
                totals_rate = 0
                for star in range(1, 6):
                    num = len(RatingVote.objects.filter(amount_star_voting=star, tour=Tour.objects.get(id=pk)))
                    totals_rate += num * star
                    num_people += num

                tour = Tour.objects.get(pk=pk)
                tour.rating_count_tour = totals_rate / num_people
                tour.save()

                # Update Cache
                if cache.get(nameKey_Tour_Redis + str(pk)):
                    update_cache_details_tour(pk)

                return Response(RatingVoteSerializer(oldrate).data)
            else:
                newrate = RatingVote(tour=Tour.objects.get(id=pk),user=request.user)
                newrate.amount_star_voting = star
                newrate.save()

                ## RE UPDATE COUNT RATING VOTE
                num_people = 0
                totals_rate = 0
                for star in range(1, 6):
                    num = len(RatingVote.objects.filter(amount_star_voting=star, tour=Tour.objects.get(id=pk)))
                    totals_rate += num * star
                    num_people += num

                tour = Tour.objects.get(pk=pk)
                tour.rating_count_tour = totals_rate / num_people
                tour.save()

                # Update Cache
                if cache.get(nameKey_Tour_Redis + str(pk)):
                    update_cache_details_tour(pk)

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
        if not check_can_cmt_rate_tour(request.user, Tour.objects.get(id=pk)):
            return Response("You do not used to book this tour", status=status.HTTP_204_NO_CONTENT)
        try:
            content = request.data['content_cmt']
            add_comment = Comment(tour=Tour.objects.get(id=pk),user=request.user,content_cmt=content,amount_like_cmt=0,status_cmt="Run")
            add_comment.save()
            return Response(CommentShowSerializer(add_comment).data)
        except:
            return Response("Error Comment Comment", status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True, url_path='add-5-comment-tour')
    def add_user_5_comment(self, request, pk):
        try:
            for i in range(5):
                content = request.data['content_cmt'] + str(i) + " !!!!"
                add_comment = Comment(tour=Tour.objects.get(id=pk), user=request.user, content_cmt=content,
                                      amount_like_cmt=0, status_cmt="Run")
                add_comment.save()
            return Response(CommentShowSerializer(add_comment).data)
        except:
            return Response("Error Comment Comment", status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete'], detail=True, url_path='delete-comment-tour')
    def delete_user_comment(self, request, pk):
        try:
            cmt = Comment.objects.get(id=pk)
            if CommentOwnerUser.has_permission(self,request,cmt) == False:
                return Response("You cant have permission!!!", status=status.HTTP_204_NO_CONTENT)
            cmt.delete()
            return Response("Delete Successfully!!!")
        except:
            return Response("Error Delete Comment", status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=True, url_path='edit-comment-tour')
    def edit_user_comment(self, request, pk):
        try:
            cmt = Comment.objects.get(id=pk)
            if CommentOwnerUser.has_permission(self,request,cmt) == False:
                return Response("You cant have permission!!!", status=status.HTTP_204_NO_CONTENT)
            cmt.content_cmt = request.data['content_cmt']
            cmt.save()
            data = CommentShowSerializer(cmt).data
            data["status_update"] = "Update Successfully!!!"
            return Response(data)
        except:
            return Response("Error Update Comment", status=status.HTTP_204_NO_CONTENT)


####### Tour-Images:
class TourImagesViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = TourImages.objects.all()
    serializer_class = TourImagesSerializer
    pagination_class = TourPaginator

    @action(methods=['put'], detail=True, url_path='update-per-image-tour')
    def update_per_image_tour(self, request, pk):
        if CanCRUD_Tour.has_permission(self, request, request.user) == False:
            return Response("You don't have permission", status=status.HTTP_204_NO_CONTENT)
        else:
            try:
                tour_root = TourImages.objects.get(id=pk)

                if "image_tour" in request.data:
                    tour_root.image_tour = request.data["image_tour"]

                tour_root.save()

                # Update Cache
                if cache.get(nameKey_Tour_Redis + str(pk)):
                    update_cache_details_tour(pk)
                # Response
                data = TourImagesSerializer(tour_root).data
                return Response(data)
            except:
                return Response("Lỗi cập nhật", status=status.HTTP_204_NO_CONTENT)


###### BLOG
class BlogViewSet(viewsets.ViewSet, generics.ListAPIView):
    # queryset = Tour.objects.filter(active=True)
    serializer_class = BlogBaseShow
    pagination_class = TourPaginator
    parser_classes = [parsers.MultiPartParser, ]
    queryset = Blog.objects.filter(active=True).order_by('-count_like_blog')

    # PERMISSION
    # def get_permissions(self):
    #     if self.action in ['create_tour']:
    #         return [CanCRUD_Tour()]
    #
    #     return [permissions.AllowAny()]

    ######## GET
    def filter_queryset(self, queryset):
        #########
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(title_blog__icontains=q, content_blog__icontains=q)

        blog_id = self.request.query_params.get('blog_id')
        #########
        if blog_id:
            queryset = queryset.filter(id=blog_id)

        ###########
        name_address = self.request.query_params.get('address')
        if name_address:
            queryset = queryset.filter(address_blog__icontains=name_address)
        print(self.request.query_params.get('message'))
        return queryset

    @action(methods=['get'], detail=True, url_path='details-blog')
    def details_blog(self, request, pk):
        if cache.get(nameKey_Blog_Redis + str(pk)):
            data_details = cache.get(nameKey_Blog_Redis + str(pk))

            return Response(data_details)
        else:
            try:
                c = self.get_object()
                data = BlogDetailsSerializer(c).data

                l_cmt = len(CommentBlog.objects.filter(blog_id=c.id))
                if l_cmt > 0:
                    data['list_comment'] = CommentShowSerializer(CommentBlog.objects.filter(blog_id=c.id), many=True).data

                cache.set(nameKey_Blog_Redis + pk, str(data), 300)

                return Response(data)
            except:
                return Response('Have a problem')

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments_blog(self, request, pk):
            c = self.get_object()
            l_cmt = len(CommentBlog.objects.filter(blog_id=c.id))
            data = []
            if l_cmt > 0:
                data = CommentBlogShowSerializer(CommentBlog.objects.filter(blog_id=c.id), many=True).data
            return Response(data)

    #
    @action(methods=['post'], detail=False, url_path='create-10-blog')
    def create_10_blog(self, request):
        if CanCRUD_Tour.has_permission(self, request, request.user):
            try:
                for i in range(10):
                    blog = Blog(**BlogSerializer(request.data).data)
                    blog.title_blog += " _V" + str(i)
                    blog.image_blog = request.data['image_blog']
                    blog.address_blog = request.data['address_blog']
                    blog.country_blog = request.data['country_blog']

                    if len(request.FILES) == 2:
                        blog.image_content1_blog = request.data['image_content1_blog']
                    if len(request.FILES) == 3:
                        blog.image_content1_blog = request.data['image_content1_blog']
                        blog.image_content2_blog = request.data['image_content2_blog']

                    blog.user = request.user
                    blog.save()

                return Response(BlogBaseShow(blog).data)
            except:
                return Response("Data have a problem")
        return Response("You can't add this tour")

    ####### POST Create New
    @action(methods=['post'], detail=False, url_path='create-blog')
    def create_blog(self, request):
        if CanCRUD_Tour.has_permission(self, request, request.user):
            try:
                blog = Blog(**BlogSerializer(request.data).data)

                blog.image_blog = request.data['image_blog']
                blog.address_blog = request.data['address_blog']
                blog.country_blog = request.data['country_blog']

                if len(request.FILES) == 2:
                    blog.image_content1_blog = request.data['image_content1_blog']
                if len(request.FILES) == 3:
                    blog.image_content1_blog = request.data['image_content1_blog']
                    blog.image_content2_blog = request.data['image_content2_blog']

                blog.user = request.user
                blog.save()

                return Response(BlogDetailsSerializer(blog).data)
            except:
                return Response("Data have a problem")
        return Response("You can't add this tour")


    @action(methods=['put'], detail=True, url_path='update-blog')
    def update_tour(self, request, pk):
        if CanCRUD_Tour.has_permission(self, request, request.user) == False:
            return Response("You don't have permission", status=status.HTTP_204_NO_CONTENT)
        else:
            try:
                blog_root = Blog.objects.get(id=pk)

                for key, value in request.data.items():
                    if "uploadedfile.InMemoryUploadedFile" in str(type(value)):
                        continue
                    setattr(blog_root, key, value)

                if "image_blog" in request.data:
                    blog_root.image_tour = request.data["image_tour"]

                if "image_content1_blog" in request.data:
                    blog_root.image_content1_blog = request.data["image_content1_blog"]

                if "image_content2_blog" in request.data:
                    blog_root.image_content2_blog = request.data["image_content2_blog"]

                blog_root.save()

                # Update Cache
                if cache.get(nameKey_Blog_Redis + str(pk)):
                    update_cache_details_blog(pk)
                # Response
                data = BlogDetailsSerializer(blog_root).data

                return Response(data)
            except:
                return Response("Lỗi cập nhật", status=status.HTTP_204_NO_CONTENT)


####### Comment Blog:
class CommentBlogViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = CommentBlog.objects.all()
    serializer_class = CommentBlogSerializer
    pagination_class = CommentPaginator

    def get_permissions(self):
        if self.action in ['add_user_comment_blog']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='add-comment-blog')
    def add_user_comment_blog(self, request, pk):
        try:
            content = request.data['content_cmt']
            add_comment = CommentBlog(blog=Blog.objects.get(id=pk),user=request.user,content_cmt=content,amount_like_cmt=0,status_cmt="Run")
            add_comment.save()
            return Response(CommentBlogShowSerializer(add_comment).data)
        except:
            return Response("Error Comment Comment")

    @action(methods=['post'], detail=True, url_path='add-5-comment-blog')
    def add_user_comment(self, request, pk):
        try:
            for i in range(5):
                content = request.data['content_cmt'] + str(i) + " !!!!"
                add_comment = CommentBlog(blog=Blog.objects.get(id=pk),user=request.user,content_cmt=content,amount_like_cmt=0,status_cmt="Run")
                add_comment.save()
            return Response(CommentBlogShowSerializer(add_comment).data)
        except:
            return Response("Error Comment Comment")

    @action(methods=['delete'], detail=True, url_path='delete-comment-blog')
    def delete_user_comment(self, request, pk):
        try:
            cmt = CommentBlog.objects.get(id=pk)
            if CommentOwnerUser.has_permission(self,request,cmt) == False:
                return Response("You cant have permission!!!")
            cmt.delete()
            return Response("Delete Successfully!!!")
        except:
            return Response("Error Delete Comment")

    @action(methods=['patch'], detail=True, url_path='edit-comment-blog')
    def edit_user_comment(self, request, pk):
        try:
            cmt = CommentBlog.objects.get(id=pk)
            if CommentOwnerUser.has_permission(self,request,cmt) == False:
                return Response("You cant have permission!!!")
            cmt.content_cmt = request.data['content_cmt']
            cmt.save()
            data = CommentBlogShowSerializer(cmt).data
            data["status_update"] = "Update Successfully!!!"
            return Response(data)
        except:
            return Response("Error Update Comment")


####### Like Blog
class LikeBlogViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = LikeBlog.objects.all()
    serializer_class = LikeBlogSerializer
    pagination_class = WishListPaginator

    def get_permissions(self):
        if self.action in ['get_user_like_blog', 'add_user_like_blog']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='my-like-blog')
    def get_user_like_blog(self, request):
        queryset = LikeBlog.objects.all()
        queryset = queryset.filter(user=request.user, is_like=1)

        return Response(LikeBlogSerializer(queryset, many=True).data)

    @action(methods=['post'], detail=True, url_path='add-like-blog')
    def add_user_like_blog(self, request, pk):
        try:
            wish = LikeBlog.objects.filter(blog=Blog.objects.get(id=pk),user=request.user)
            blog = Blog.objects.get(id=pk)
            if len(wish) > 0:
                oldwish = LikeBlog.objects.get(blog=Blog.objects.get(id=pk),user=request.user)
                if oldwish.is_like == 0:
                    oldwish.is_like = 1

                    blog.count_like_blog += 1
                    blog.save()
                else:
                    oldwish.is_like = 0

                    blog.count_like_blog -= 1
                    blog.save()
                oldwish.save()
                return Response(LikeBlogSerializer(oldwish).data)
            else:
                newwish = LikeBlog(blog=Blog.objects.get(id=pk),user=request.user)
                newwish.is_like = 1
                newwish.save()

                blog.count_like_blog += 1
                blog.save()
                return Response(LikeBlogSerializer(newwish).data)
        except:
            return Response("Error Add Like Blog List")


####### Type Customer:
class TypeCustomerViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = TypeCustomer.objects.filter(active=True)
    serializer_class = TypeCustomerBaseShow
    pagination_class = TicketPaginator