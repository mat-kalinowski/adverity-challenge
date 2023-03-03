from django.urls import path
from .views import FileFetchView, FileListView, PeopleView, PeopleLoadView, CountView, CountLoadView

urlpatterns = [
    path('', FileListView.as_view(), name='file-list'),
    path('file/fetch', FileFetchView.as_view(), name='file-fetch'),
    path('people/<str:file>', PeopleView.as_view(), name="people"),
    path('people/load/<str:file>', PeopleLoadView.as_view(), name="people-load"),
    path('count/<str:file>', CountView.as_view(), name="count"),
    path('count/load/<str:file>', CountLoadView.as_view(), name="count-load")
]