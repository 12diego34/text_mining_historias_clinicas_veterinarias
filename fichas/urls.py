from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('health/',             views.health,       name='health'),
    path('login/',              LoginView.as_view(template_name='fichas/login.html'), name='login'),
    path('logout/',             LogoutView.as_view(), name='logout'),
    path('',                    views.index,        name='index'),
    path('upload/',             views.upload,       name='upload'),
    path('ficha/<int:pk>/',     views.detalle,      name='detalle'),
    path('ficha/<int:pk>/reprocesar/', views.reprocesar, name='reprocesar'),
    path('ficha/<int:pk>/estado/',    views.estado_json,  name='estado_json'),
    path('ficha/<int:pk>/eliminar/',  views.eliminar,     name='eliminar'),
    path('exportar/csv/',       views.exportar_csv, name='exportar_csv'),
]
