from django.urls import path

from . import views

app_name = 'repository'
urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('submit/', views.submit, name='submit'),
    path('save-to-xlsx', views.save_to_xlsx, name='save-to-xlsx')

]
