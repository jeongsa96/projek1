from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('register/', views.register, name="register"),
    path('pm/', views.Project_Manager, name="project-manager"),
    path('pm/projek-db/', views.Project_Manager_PD, name="pm-projekdb"),
    path('pm/projek-db/<str:client>/', views.Project_Manager_PD, name="detail-projek"),
    path('logistik/', views.Logistik, name="logistik"),
    path('logistik/input-PO', views.Logistik_PO, name="logistik-po"),
    path('logistik/document-log', views.Logistik_DL, name="logistik-dl"),
    path('finance/', views.Finance, name="finance"),
    path('finance/data-invoice', views.Finance_DI, name="finance-invoice"),
    path('finance/update-status/<int:id>', views.Finance_updateStatus, name="finance-update"),
    path('finance/anggaran', views.Finance_A, name="finance-anggaran"),
    path('finance/cek-anggaran', views.Finance_AC, name="finance-cek-anggaran"),
    path('finance/expense', views.Finance_E, name="finance-expense"),
    path('admin-jangga/', views.Admin, name="admin-jangga"),
    path('admin-jangga/projek-db', views.Admin_PD, name="admin-projekdb"),
    path('admin-jangga/projek-baru', views.Admin_PB, name="admin-projek-baru"),
    path('admin-jangga/invoice-baru', views.Admin_IB, name="admin-invoice-baru"),
    path('admin-jangga/po-request', views.Admin_PR, name="admin-po-request"),
    path('admin-jangga/po-request/update-status/<int:id>', views.Admin_updateStatus, name="admin-update"),
    path('logout/', views.Logout, name="logout"),

]