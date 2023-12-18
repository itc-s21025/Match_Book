from django.urls import path
from Matching import views
from Matching.views import profile_detail, send_like, send_direct_message, get_notifications, \
    show_notifications, matched_list, show_notifications_matching, book_thoughts_form, book_thoughts_list, \
    book_thoughts_detail, send_liked, my_page

urlpatterns = [
    path("profile_detail/<int:profile_id>/", profile_detail, name="profile_detail"),
    path("send_like/<int:approached_user_id>/", send_like, name="send_like"),
    path("send_direct_message/<int:receiver_id>/", send_direct_message, name="send_direct_message"),
    path('api/notifications/', get_notifications, name='get_notifications'),
    path('show_notifications/', show_notifications, name='show_notifications'),
    path('matched_list/', matched_list, name='matched_list'),
    path('show_notifications_mathing/', show_notifications_matching, name='show_notifications_matching'),
    path('book_thoughts_form/', book_thoughts_form, name='book_thoughts_form'),
    path("create_profile/", views.CreateProfileView.as_view(), name="create_profile"),
    path('book_thoughts_list/', book_thoughts_list, name='book_thoughts_list'),
    path('book_thoughts/<int:thought_id>/', book_thoughts_detail, name='book_thoughts_detail'),
    path('send_liked/', send_liked, name='send_liked'),
    path('my_page/', my_page, name='my_page'),
]

