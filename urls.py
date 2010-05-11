from django.conf.urls.defaults import *
import spotlightdb as spotlightdb
# Uncomment the next two lines to enable the admin:
from django.contrib import admin, auth
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^spotlightdb/', include('spotlightdb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^admin$', include(admin.site.urls)),

    #NPNG URLs
    (r'^npng/', include('spotlightdb.npng.urls')),
    (r'^npng$', include('spotlightdb.npng.urls')),

    #(r'^spotlight/$', 'spotlightdb.backend.views.index'),
    #(r'^/$', 'spotlightdb.backend.views.index'),
    #(r'^spotlight/sensor/$', 'spotlightdb.backend.views.sensor_data'),
    #(r'^spotlight/sensordata/(?P<sensor_id>\d+)/$', 'spotlightdb.backend.views.get_graph'),
    
    # Login
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^login$', 'django.contrib.auth.views.login'),
    (r'^accounts/login$', 'django.contrib.auth.views.login'),
    (r'^logout$', 'django.contrib.auth.views.logout_then_login'),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    # Registration
    (r'^register$', 'spotlightdb.fieldstream.views.register'),
    (r'^register/$', 'spotlightdb.fieldstream.views.register'),
    (r'^register/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.register'),
    # Profile Updates
    (r'^updateprof$', 'spotlightdb.fieldstream.views.update_prof'),
    (r'^updateprof/$', 'spotlightdb.fieldstream.views.update_prof'),
    (r'^updateprof/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.update_prof'),
    # Wave Segment Series Changes/Additions
    #(r'^wssview$', 'spotlightdb.fieldstream.views.wss_form'),
    #(r'^wssview/$', 'spotlightdb.fieldstream.views.wss_form'),
    #(r'^wssupdate$', 'spotlightdb.fieldstream.views.wss_form'),
    #(r'^wssupdate/$', 'spotlightdb.fieldstream.views.wss_form'),
    #(r'^wssupdate/(?P<is_update>[0-9]*)$', 'spotlightdb.fieldstream.views.wss_form'),
    #(r'^wssupdate/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.wss_form'),
    # Sensor Node Changes/Additions
    (r'^snview$', 'spotlightdb.fieldstream.views.sensor_node_form'),
    (r'^snview/$', 'spotlightdb.fieldstream.views.sensor_node_form'),
    (r'^snupdate$', 'spotlightdb.fieldstream.views.sensor_node_form'),
    (r'^snupdate/$', 'spotlightdb.fieldstream.views.sensor_node_form'),
    (r'^snupdate/(?P<is_update>[0-9]*)$', 'spotlightdb.fieldstream.views.sensor_node_form'),
    (r'^snupdate/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.sensor_node_form'),
    # Sensor Channel Changes/Additions
    (r'^scview$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scview/$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scview/(?P<is_update>[0-9]*)$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scview/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scupdate$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scupdate/$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scupdate/(?P<is_update>[0-9]*)$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    (r'^scupdate/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.sensor_channel_form'),
    # WSS/Sensor Channel Mapping Changes/Additions
    #(r'^scmview$', 'spotlightdb.fieldstream.views.SCM_form'),
    #(r'^scmview/$', 'spotlightdb.fieldstream.views.SCM_form'),
    #(r'^scmupdate$', 'spotlightdb.fieldstream.views.SCM_form'),
    #(r'^scmupdate/$', 'spotlightdb.fieldstream.views.SCM_form'),
    #(r'^scmupdate/(?P<is_update>[0-9]*)$', 'spotlightdb.fieldstream.views.SCM_form'),
    #(r'^scmupdate/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.SCM_form'),
    # Data Upload
    (r'^upload/$', 'spotlightdb.fieldstream.views.upload_data'),
    (r'^upload$', 'spotlightdb.fieldstream.views.upload_data'),
    # Data Retrieval
    (r'^query/$', 'spotlightdb.fieldstream.views.get_data'),
    (r'^query$', 'spotlightdb.fieldstream.views.get_data'),
    # Data Retrieval Unsecure (TESTING ONLY!!!)
    (r'^query2/$', 'spotlightdb.fieldstream.views.get_data2'),
    (r'^query2$', 'spotlightdb.fieldstream.views.get_data2'),
    # Rule Upload
    (r'^rule_upload/$', 'spotlightdb.fieldstream.views.upload_rules'),
    (r'^rule_upload$', 'spotlightdb.fieldstream.views.upload_rules'),
    # Rules Changes/Additions
    (r'^rules$', 'spotlightdb.fieldstream.views.rules_form'),
    (r'^rules/$', 'spotlightdb.fieldstream.views.rules_form'),
    (r'^rules/(?P<is_update>[0-9]*)$', 'spotlightdb.fieldstream.views.rules_form'),
    (r'^rules/(?P<url>[A-z0-9.]*)$', 'spotlightdb.fieldstream.views.rules_form'),
    
    #(r'^spotlight/data/$', 'spotlightdb.backend.views.which_data'),
    #(r'^amline/amline_settings/(?P<sensor_id>\d+)$', 'spotlightdb.backend.views.amline_settings'),
    #(r'^amline/amline_data/(?P<sensor_id>\d+)$', 'spotlightdb.backend.views.amline_data'),
    #(r'^amline/(?P<url>[A-z0-9.]*)$', 'spotlightdb.backend.views.amline_swfobject'),
    #(r'^spotlight/$', 'spotlightdb.backend.views.index'),
    

    (r'$', 'spotlightdb.fieldstream.views.index'),
)

