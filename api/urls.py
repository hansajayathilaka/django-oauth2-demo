from django.urls import path
from . import views, demo_views

urlpatterns = [
    # Class-based views (original examples)
    path("hello/", views.HelloWorldView.as_view(), name="hello"),
    path("protected/", views.ProtectedView.as_view(), name="protected"),
    path("scoped/read/", views.ScopedReadView.as_view(), name="scoped_read"),
    path("scoped/write/", views.ScopedWriteView.as_view(), name="scoped_write"),

    # Function-based view demos
    path("demo/simple/", demo_views.demo_simple_protected, name="demo_simple"),
    path("demo/read-scope/", demo_views.demo_read_scope, name="demo_read_scope"),
    path("demo/write-scope/", demo_views.demo_write_scope, name="demo_write_scope"),
    path("demo/read-or-write/", demo_views.demo_read_or_write, name="demo_read_or_write"),
    path("demo/admin/", demo_views.demo_admin_scope, name="demo_admin"),
    path("demo/manual-scope/", demo_views.demo_manual_scope_check, name="demo_manual_scope"),
    path("demo/multi-scope/", demo_views.demo_multiple_scopes, name="demo_multi_scope"),
    path("demo/token-info/", demo_views.demo_token_info, name="demo_token_info"),
    path("demo/public/", demo_views.demo_public, name="demo_public"),
    path("demo/optional-auth/", demo_views.demo_optional_auth, name="demo_optional_auth"),
]
