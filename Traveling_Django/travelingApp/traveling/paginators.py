from rest_framework import pagination


class TourPaginator(pagination.PageNumberPagination):
    page_size = 20
