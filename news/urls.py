from django.urls import path

from news import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsList.as_view(), name='home'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='detail'),  # URL к странице новости
    path(
        'delete_comment/<int:pk>/',
        views.CommentDelete.as_view(),
        name='delete'
    ),
    path('edit_comment/<int:pk>/', views.CommentUpdate.as_view(), name='edit'),
]

# Unittest: тестирование маршрутов
# Адресом страницы с новостью, созданной в фикстуре, будет /news/1/: нам точно известно, что это первый объект, который создан в пустой таблице БД. 
# Единица в адресе — это id новости и, одновременно, её первичный ключ (Primary Key, pk). 
# Если в описании модели явно не указано, какое поле служит первичным ключом (а в модели News это не указано), 
# то Django автоматически добавляет в модель поле с первичным ключом. 