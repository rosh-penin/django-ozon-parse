from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from products.models import Product
from .serializers import ProductSerializer
from .utils import start_parser


class ProductsViewSet(ListModelMixin, RetrieveModelMixin,
                      GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        count = request.data.get('products_count')
        start_parser.delay(count)
        return Response(status=HTTP_201_CREATED)
