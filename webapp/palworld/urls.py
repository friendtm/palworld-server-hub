from django.urls import path

from . import views

app_name = 'palworld'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('map/', views.map_view, name='map'),
    path('map/tiles/<int:z>/<int:x>/<int:y>.png', views.map_tile, name='map_tile'),
    path('map/icons/<slug:icon_key>.png', views.map_icon, name='map_icon'),
    path('api/map/points/', views.map_points, name='map_points'),
    path('api/map/pal-locations/<slug:pal_id>/', views.pal_locations, name='pal_locations'),
    path('api/health/', views.health, name='health'),
    path('api/config/', views.config, name='config'),
    path('api/palworld/endpoints/', views.palworld_endpoints, name='palworld_endpoints'),
    path('api/palworld/<slug:endpoint>/', views.palworld_proxy, name='palworld_proxy'),
]
