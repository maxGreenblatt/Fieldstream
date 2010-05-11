from spotlightdb.backend.models import *
from django.contrib import admin
from django.forms.models import modelformset_factory
from django.forms import ModelForm
from django.contrib.auth.models import User

"""
class RelationshipInline(admin.TabularInline):
	model = Subject
	#SubjectFormSet = modelformset_factory(Subject)
	#formset = SubjectFormSet(queryset = Subject.objects.filter(isGroup__exact = True))

class RelationshipAdmin(admin.ModelAdmin):
	inlines = [
		RelationshipInline,
	]
"""

admin.site.register(SensorNode)
admin.site.register(SensorChannel)
admin.site.register(WaveSegSeries)
admin.site.register(WaveSeg)
admin.site.register(Subject)
#admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(Relationship)
admin.site.register(Sensor)
admin.site.register(Placement)
admin.site.register(SensorType)
admin.site.register(LocationMapping)
admin.site.register(TimeMapping)
admin.site.register(Location)
admin.site.register(Data)
#admin.site.register(User)
