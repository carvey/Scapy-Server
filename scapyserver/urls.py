from django.conf.urls import url
from django.contrib import admin
from packets.views import packets, clear_packets, hosts


urlpatterns = [
    # url(r'^$', index, name="devices"),
    url(r'^$', packets, name="packets"),
    url(r'^remote/', hosts, name="remote_hosts"),
    url(r'^admin/', admin.site.urls),

    url(r'^clear/', clear_packets, name="clear")
]

