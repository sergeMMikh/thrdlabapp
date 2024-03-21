from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from orders.models import Product, Shop, ProductInfo, Category
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.serializers import ProductSerializer, ShopSerializer, ProductViewSerializer, \
    SingleProductViewSerializer, CategorySerializer


class ProductsList(ListAPIView):
    """
    Список товаров
    """
    queryset = Product.objects.filter(product_info__shop__state=True)
    serializer_class = ProductSerializer


class ProductDetailAPIView(APIView):

    def get(self, request, *args, **kwargs):
        print(f"self.request: {self.request.query_params.get('shop_id')}")
        return Response(status=status.HTTP_200_OK)


class CategoryView(ListAPIView):
    """
    Список категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductsView(APIView):
    """
    Получение списка товаров по категории и магазину
    """
    def get(self, request):
        category = request.data.get('category')
        shop = request.data.get('shop')
        print(f'category: {category}')
        print(f'shop: {shop}')

        products = Product.objects.filter(product_info__shop__name=shop,
                                          category__name=category)

        serializer = ProductViewSerializer(products, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class SingleProductView(APIView):
    """
    Поиск товаров по product_id
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        print(f'product_id: {product_id}')

        queryset = ProductInfo.objects.filter(product__id=product_id)

        serializer = SingleProductViewSerializer(queryset, many=True)

        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class ProductInfoViewSet(APIView):
    """
    Класс для поиска товаров
    по:
    product_id
    shop_id
    category_id
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Метод get_queryset принимает критерии для поиска,
        возвращает товары, в соотвествии с запросом. """

        query = Q(shop__state=True)
        product_id = request.data.get('product_id')
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if product_id:
            query = query & Q(product__id=product_id)

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        print(f'query: {query}')

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = SingleProductViewSerializer(queryset, many=True)

        return Response(serializer.data,
                        status=status.HTTP_200_OK)
