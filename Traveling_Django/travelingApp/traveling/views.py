from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.decorators import action
from rest_framework.views import Response
from .models import *
from .serializers import SaleOffSerializer, TourSerializer, TourDetailSerializer, UserSerializer, TicketSerializer
from .paginators import TourPaginator
from django.core.cache import cache
from django.contrib.auth.models import Permission
from datetime import datetime
import random


#### SALES OFF
class SalesOffViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = SaleOff.objects.all()
    serializer_class = SaleOffSerializer


##### TOUR
class TourViewSet(viewsets.ViewSet, generics.ListAPIView):
    # queryset = Tour.objects.filter(active=True)
    serializer_class = TourSerializer
    pagination_class = TourPaginator
    parser_classes = [parsers.MultiPartParser, ]
    queryset = Tour.objects.filter(active=True)

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

        return queryset

    @action(methods=['get'], detail=True, url_path='details-tour')
    def details_tour(self, request, pk):
        if cache.get('details' + pk):
            data_details = cache.get('details_tour_' + pk)
            return Response(data_details)
        else:
            try:
                c = self.get_object()
                cache.set("details_tour_" + pk, TourDetailSerializer(c).data, 120)
                return Response(TourDetailSerializer(c).data)
            except:
                return Response('Have a problem')

    ####### POST Create New
    @action(methods=['post'], detail=False, url_path='create-tour')
    def create_tour(self, request):
        if request.user.is_staff or request.user.is_superuser :
            try:
                tour = Tour(**TourSerializer(request.data).data)
                print(TourSerializer(request.data).data.get('image_tour'))
                tour.save()
                return Response(TourSerializer(request.data).data)
            except:
                return Response("Data have a problem")
        return Response("You can't add this tour")


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current_user', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)

    ####### FULL USER
    @action(methods=['get'], detail=False, url_path='all-users')
    def filter_queryset(self, request):
        if request.user.is_superuser or request.user.is_staff:
            users = User.objects.filter(is_active=True)
            return Response(UserSerializer(users, many=True).data)
        else:
            return Response("You can not entry this data")

class TicketViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Ticket.objects.filter(status_ticket__icontains="Wait")
    serializer_class = TicketSerializer

    def get_permissions(self):
        if self.action in ['current_user', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=False, url_path='create-ticket')
    def create_ticket(self, request):
        if request.user.is_superuser or request.user.is_staff or request.user.is_staff == False:
            try:
                ##### New Code
                code = datetime.now().strftime("D%m%d%Y-")
                num = ''
                for i in range(0, 7):
                    n = random.randint(1,9)
                    num += str(n)
                code = code + num
                bill = Bill(code_bill=code,status_bill="Pending")
                ##### Get Object
                tour_da = Tour.objects.get(id=int(request.data['tour']))
                type_people_da = TypeCustomer.objects.get(id=int(request.data['type_people']))
                ##### New Ticket
                ticket = Ticket(tour=tour_da,type_people=type_people_da,user=request.user,amount_ticket=int(request.data['amount']))
                ticket.price_real = (tour_da.price_tour + type_people_da.price_booked) * ticket.amount_ticket

                ### SET PRICE DISCOUNT
                if type_people_da.sales_off.id != 1:
                    if type_people_da.sales_off.price_value_sales != 0:
                        ticket.totals_minus_money = type_people_da.sales_off.price_value_sales * ticket.amount_ticket
                    elif type_people_da.sales_off.price_percent_sales != 0:
                        ticket.totals_minus_money = ((type_people_da.sales_off.price_percent_sales / 100) * type_people_da.price_booked) * ticket.amount_ticket
                else:
                    ticket.totals_minus_money = 0
                ticket.status_ticket = "Pending"

                ## TOTALS BILL
                bill.totals_bill = ticket.price_real - ticket.totals_minus_money
                ticket.bill = bill

                try:
                    # bill.save()
                    # ticket.save()
                    data = TicketSerializer(ticket).data
                    data['total-discount'] = ticket.totals_minus_money
                    data['bill-code'] = bill.code_bill
                    return Response(data, status=status.HTTP_201_CREATED)
                except:
                    return Response("Some Thing Erro When Booking Ticket")
            except:
                return Response("Data have a problem")
        return Response("You can't add this ticket")
