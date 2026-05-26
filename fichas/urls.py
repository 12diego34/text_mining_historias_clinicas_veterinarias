from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.index,        name='index'),
    path('upload/',             views.upload,       name='upload'),
    path('ficha/<int:pk>/',     views.detalle,      name='detalle'),
    path('ficha/<int:pk>/reprocesar/', views.reprocesar, name='reprocesar'),
    path('ficha/<int:pk>/estado/',    views.estado_json,  name='estado_json'),
    path('ficha/<int:pk>/eliminar/',  views.eliminar,     name='eliminar'),
    path('exportar/csv/',       views.exportar_csv, name='exportar_csv'),
]
