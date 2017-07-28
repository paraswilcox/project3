from django.conf.urls import url
from app1.views import signup_view, login_view, feed_view, post_view, like_view, comment_view,log_out, search, like_comm
from django.contrib import admin

urlpatterns = [
	url(r'admin/', admin.site.urls),
	url(r'^post/$', post_view),
	url(r'^feed/$', feed_view),
	url(r'^like/$', like_view),
	url(r'^comment/$', comment_view),
	url(r'^login/$', login_view),
	url(r'^$', signup_view),
	url(r'^log_out/$', log_out),
	url(r'^search/$',search),
	url(r'^like_comm/$', like_comm),
]