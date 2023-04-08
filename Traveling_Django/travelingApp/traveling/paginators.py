from rest_framework import pagination


class TourPaginator(pagination.PageNumberPagination):
    page_size = 20


class TicketPaginator(pagination.PageNumberPagination):
    page_size = 15

class BillPaginator(pagination.PageNumberPagination):
    page_size = 20