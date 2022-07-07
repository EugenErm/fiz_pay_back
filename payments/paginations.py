from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'pageSize'
    offset_query_param = 'pageIndex'
    max_limit = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': self.count,
            'results': data
        })
