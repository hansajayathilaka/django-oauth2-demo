from django.urls import path
from . import views

urlpatterns = [
    path("hello/", views.HelloWorldView.as_view(), name="hello"),
    path("protected/", views.ProtectedView.as_view(), name="protected"),
    path("scoped/read/", views.ScopedReadView.as_view(), name="scoped_read"),
    path("scoped/write/", views.ScopedWriteView.as_view(), name="scoped_write"),
]
