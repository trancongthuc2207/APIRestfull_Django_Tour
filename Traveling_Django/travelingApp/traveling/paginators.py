from rest_framework import pagination


class TourPaginator(pagination.PageNumberPagination):
    page_size = 20


class TicketPaginator(pagination.PageNumberPagination):
    page_size = 15


class BillPaginator(pagination.PageNumberPagination):
    page_size = 20


class WishListPaginator(pagination.PageNumberPagination):
    page_size = 20


class RatingVotePaginator(pagination.PageNumberPagination):
    page_size = 20


class CommentPaginator(pagination.PageNumberPagination):
    page_size = 10