from django.urls import path
from . import views

urlpatterns = [
    path('', views.tree_view, name='tree_view'),
    path('api/nodos/', views.api_nodos, name='api_nodos'),
    path('api/nodos/create/', views.api_nodo_create, name='api_nodo_create'),
    path('api/nodos/<int:nodo_id>/', views.api_nodo_detail, name='api_nodo_detail'),
    path('api/nodos/<int:nodo_id>/children/', views.api_nodo_children, name='api_nodo_children'),
    path('api/nodos/<int:nodo_id>/update/', views.api_nodo_update, name='api_nodo_update'),
    path('api/nodos/<int:nodo_id>/delete/', views.api_nodo_delete, name='api_nodo_delete'),
    path('api/nodos/<int:nodo_id>/ancestors/', views.api_nodo_ancestors, name='api_nodo_ancestors'),
    path('api/nodos/<int:nodo_id>/move/', views.api_nodo_move, name='api_nodo_move'),
    path('api/raices/', views.api_raices, name='api_raices'),
    path('api/tree/', views.api_tree_full, name='api_tree_full'),
    path('api/tree/stats/', views.api_tree_stats, name='api_tree_stats'),
    path('api/search/', views.api_nodo_search, name='api_nodo_search'),
    path('api/seed/', views.api_seed_data, name='api_seed_data'),
]
