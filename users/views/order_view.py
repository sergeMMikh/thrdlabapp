from django.db.utils import IntegrityError
from orders.models import Order
from django.db.models import F, Sum
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from orders.serializers import OrderSerializer
from orders.tasks import send_email
from rest_framework import status


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями
    """
    permission_classes = [IsAuthenticated]

    # получить мои заказы
    def get(self, request, *args, **kwargs):

        """
        Метод get проверяет наличие авторизации,
        возвращает заказы покупателю или список заказов магазина
        """
        if request.user.user_type != 'shop':

            order = Order.objects.filter(
                user_id=request.user.id).exclude(state='basket').prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter',
            ).annotate(
                total_sum=Sum(F(
                    'ordered_items__quantity',
                ) * F(
                    'ordered_items__product_info__price',
                )),
            ).distinct()

        else:
            order = Order.objects.filter(
                ordered_items__product_info__shop__user_id=request.user.id).exclude(
                state='basket').prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter',
            ).select_related(
                'contact',
            ).annotate(
                total_sum=Sum(F(
                    'ordered_items__quantity',
                ) * F(
                    'ordered_items__product_info__price',
                ))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        # проверка пользователя
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False,
                                 'Error': 'Log in required'},
                                status=status.HTTP_403_FORBIDDEN)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                order = Order.objects.filter(
                    user_id=request.user.id,
                    id=request.data['id'])
                try:
                    is_updated = order.update(
                        contact_id=request.data['contact'],
                        state='new')
                    print(f'is_updated: {is_updated}')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False,
                                         'Errors':
                                             'Неправильно указаны аргументы'},
                                        status=400)
                else:
                    if is_updated:
                        basket = Order.objects.filter(id=request.data['id']).annotate(
                            total_sum=Sum(
                                F('ordered_items__quantity')
                                * F('ordered_items__product_info__price'))).distinct()

                        serializer = OrderSerializer(basket, many=True)
                        send_email(user_email=request.user.email,
                                   sabject='Your order confirmation.',
                                   message=f"{serializer.data}")
                        # new_order.send(sender=self.__class__,
                        # user_id=request.user.id)
                        return JsonResponse(
                            {'Status': True},
                            status=status.HTTP_200_OK,
                        )

        return JsonResponse({'Status': False,
                             'Errors': 'Не указаны все необходимые аргументы'},
                            status=status.HTTP_400_BAD_REQUEST)
