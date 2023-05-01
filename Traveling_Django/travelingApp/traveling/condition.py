from .models import *
from .serializers import *

#Check tour exist: (Tour & type_ticket)
def check_can_book_ticket(id_user, id_tour, type_people):
    queryset = Ticket.objects.filter(tour=id_tour,user=id_user,active=True)
    list = TicketDetailsSerializer(queryset,many=True).data
    for ticket in list:
        if ticket['type_people']['name_type_customer'] == type_people.name_type_customer:
            return False
    return True


def check_can_cmt_rate_tour(id_user, id_tour):
    amount = len(Ticket.objects.filter(tour=id_tour,user=id_user))
    if amount == 0:
        return False
    return True

def check_amount_to_book(amount_book, amount_remain_tour):
    if amount_book > amount_remain_tour:
        return False
    return True