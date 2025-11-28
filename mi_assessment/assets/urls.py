from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("purchases/", views.purchases, name="purchases"),
    path("transfers/", views.transfers, name="transfers"),
    path("assignments/", views.assignments, name="assignments"),
    path("api/auth/token/", views.ObtainAuthTokenView.as_view(), name="api_token"),
    path("api/dashboard/", views.DashboardView.as_view(), name="api_dashboard"),
    path("api/purchase/", views.PurchaseListCreate.as_view(), name="api_purchase"),
    path("api/transfer/", views.TransferListCreate.as_view(), name="api_transfer"),
    path("api/assignment/", views.AssignmentListCreate.as_view(), name="api_assignment"),
    path("api/bases/", views.BaseList.as_view(), name="api_bases"),
    path("api/assets/", views.AssetList.as_view(), name="api_assets"),
]
