from django.urls import path
from haberler.api import views


# Function Based Views Urls

#urlpatterns = [
#        path('makaleler/', views.makale_list_create_api_view, name="makale-listesi"),
#        path('makaleler/<int:pk>', views.makale_detail_api_view, name="makale-detayi")
#]


# Class Based Views Urls

urlpatterns = [
        path('yazarlar/', views.YazarListCreateAPIView.as_view(), name="yazar-listesi"),
        path('makaleler/', views.MakaleListCreateAPIView.as_view(), name="makale-listesi"),
        path('makaleler/<int:pk>', views.MakaleDetailAPIView.as_view(), name="makale-detayi")
]