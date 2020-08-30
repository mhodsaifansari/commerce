from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_list",views.create_list,name="create_list"),
    path("view_list/<int:id>",views.listing_page,name="listing_page"),
    path("comments/<int:id>",views.comment_view,name="comment_view"),
    path("watchlist",views.watchlist_view,name="watchlist"),
    path("cateogry",views.cateogry,name="grouplist"),
    path("cateogry/<str:name>",views.cateogry,name="grouplist"),
    path("close/<int:id>",views.close,name="close_listing"),
    path("mylist",views.mylist,name="mylist"),
    path("wonlist",views.wonlist,name="wonlist")
]
