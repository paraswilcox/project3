from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(UserModel)
admin.site.register(PostModel)
admin.site.register(SessionToken)
admin.site.register(LikeModel)
admin.site.register(CommentModel)