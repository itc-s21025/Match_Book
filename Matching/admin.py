from django.contrib import admin
from Matching.models import Profile, Matching, DirectMessage, Notification, NotificationMatching, BookThoughts


# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('__str__', 'create_by', 'age', 'sex', 'introduction', 'created_at', 'favorite_book_category', 'like_book', 'favorite_author',  'nickname' )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Matching)
admin.site.register(DirectMessage)
admin.site.register(Notification)
admin.site.register(NotificationMatching)
admin.site.register(BookThoughts)


