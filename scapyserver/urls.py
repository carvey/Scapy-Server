from django.conf.urls import url
from django.contrib import admin
from packets.views import index, packets


urlpatterns = [
    url(r'^$', index, name="devices"),
    url(r'^packets/', packets, name="packets"),
    url(r'^admin/', admin.site.urls),
]
