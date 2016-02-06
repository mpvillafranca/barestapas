from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
		url(r'^about', views.about, name='about'),
        url(r'^add_tapa/(?P<bar_name_slug>[\w\-]+)/$', views.add_tapa, name='add_tapa'),
        url(r'^reclama_datos/', views.reclama_datos, name='reclama_datos'),
        url(r'^like_tapa/$', views.like_tapa, name='like_tapa'),

        url(r'^bar/(?P<bar_name_slug>[\w\-]+)/$', views.bar, name='bar'),)  # New!
