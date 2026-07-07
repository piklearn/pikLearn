from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("courses/", views.MyCoursesView.as_view(), name="my_courses"),
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:pk>/remove/", views.WishlistRemoveView.as_view(), name="wishlist_remove"),
    path("orders/", views.OrdersView.as_view(), name="orders"),
    path("orders/<int:pk>/invoice/", views.OrderInvoiceView.as_view(), name="order_invoice"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]