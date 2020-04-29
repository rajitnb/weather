from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'home'),
    # path(r'^(?P<units>\w+)$', views.index, name='home'),
    path('delete/<city_name>/', views.delete_city, name='delete_city'),
    path('detail/<city_name>/', views.detailed_city, name='detail_city')
]