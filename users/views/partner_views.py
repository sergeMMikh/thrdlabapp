from rest_framework.permissions import IsAuthenticated

from orders.models import Product, Shop, ProductInfo, Parameter, \
    ProductParameter, Category
from django.core.validators import URLValidator
from django.http import JsonResponse
from requests import get
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework.views import APIView

from yaml import Loader, load as load_yaml

from pprint import pprint
from orders.serializers import ShopSerializer


def strtobool(value: str):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif value in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (value,))


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # если тип пользователя не "магазин"
        if request.user.user_type != 'shop':
            print('тип пользователя не "магазин"')
            return JsonResponse(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=status.HTTP_403_FORBIDDEN)

        url = request.data.get('url')
        print(f'url: {url}')

        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                print('ValidationError')
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)
                print('data:')
                pprint(data)

                # Обработка данных магазина
                shop, _ = Shop.objects.get_or_create(name=data['shop'],
                                                     user_id=request.user.id)

                # Обработка категории товара
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'],
                        name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()

                # Обработка данных товара
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:

                    # Продукт
                    product, _ = Product.objects.get_or_create(
                        name=item['name'],
                        category_id=item['category'])
                    # Данные продукта
                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        # Параметры продукта
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return JsonResponse(
                    {'Status': True},
                    status=status.HTTP_200_OK)

        print('Не указаны все необходимые аргументы')
        return JsonResponse(
            {'Status': False,
             'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST)


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """

    # получить текущий статус
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=status.HTTP_403_FORBIDDEN)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse(
                {'Status': False, 'Error': 'Log in required'},
                status=status.HTTP_403_FORBIDDEN)

        if request.user.user_type != 'shop':
            return JsonResponse(
                {'Status': False, 'Error': 'Только для магазинов'},
                status=status.HTTP_403_FORBIDDEN)
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(
                    user_id=self.request.user.pk,
                ).update(state=strtobool(state))
                return JsonResponse({'Status': True})
            except ValueError as error:
                return JsonResponse({'Status': False,
                                     'Errors': str(error)},
                                    status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(
            {'Status': False,
             'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST)
