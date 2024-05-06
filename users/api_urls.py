from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

# from orders.views.bascket_views import BasketView
# from orders.views.product_views import ProductsList, \
#     ProductsView, SingleProductView, ShopView, ProductInfoViewSet
from users.views.user_views import LoginAccount, RegisterAccount, \
     ConfirmAccount, ContactViewSet, EditUser, UserEmailVerify, \
     ResetPasswordRequestToken, ResetPasswordConfirm
# from orders.views.partner_views import PartnerUpdate, PartnerState
# from orders.views.order_view import OrderView

app_name = 'orders'
router = DefaultRouter()
# router.register(r'user/contact', ContactViewSet, basename='user-contact')

urlpatterns = [
                  path('user/login', LoginAccount.as_view(), name='user-login'),
                  path('user/register', RegisterAccount.as_view(), name='user-register'),
                  path('user/register/confirm',
                       ConfirmAccount.as_view(), name='user-register-confirm'),
                  path('user/details', EditUser.as_view(), name='user-edit'),
                  path('user/verify_email/<token>/',
                       UserEmailVerify.as_view(), name='verify-email'),
                  path('user/password_reset', ResetPasswordRequestToken.as_view(),
                       name='password-reset'),
                  path('user/password_reset/confirm', ResetPasswordConfirm.as_view(),
                       name='password-reset-confirm'),
                  path('token/', obtain_auth_token),

              ] + router.urls
