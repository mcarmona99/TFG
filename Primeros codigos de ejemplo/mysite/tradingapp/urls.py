from django.urls import path

from . import views

app_name = 'tradingapp'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pair_id>/graph_form/', views.graph_form, name='graph_form'),
    path('<int:pair_id>/graph_form/detail/', views.detail, name='detail'),
]
