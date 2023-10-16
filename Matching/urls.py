from django.urls import path
from Matching import views
from Matching.views import profile_detail, send_like, send_direct_message, direct_messages

urlpatterns = [
    path("profile_detail/<int:profile_id>/", profile_detail, name="profile_detail"),
    path("send_like/<int:approached_user_id>/", send_like, name="send_like"),
    path("send_direct_message/<int:receiver_id>/", send_direct_message, name="send_direct_message"),
    path("direct_messages/", direct_messages, name="direct_messages"),

]

