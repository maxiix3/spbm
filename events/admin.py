from django.contrib import admin
from events.models import Event,Shift
from workers.models import Worker
from society.models import Society

class ShiftInline(admin.TabularInline):
	model = Shift
	extra = 0

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "worker":
			if not request.user.is_superuser:
				kwargs['queryset'] = Worker.objects.filter(society=request.user.spfuser.society)
		return super(ShiftInline,self).formfield_for_choice_field(db_field, request, **kwargs)
	

class EventAdmin(admin.ModelAdmin):
	inlines = [ShiftInline]

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "society":
			if not request.user.is_superuser:
				kwargs['queryset'] = Society.objects.filter(id=request.user.spfuser.society.id)
		return super(EventAdmin,self).formfield_for_choice_field(db_field, request, **kwargs)
	

	
	def get_queryset(self, request):
		qs = super(EventAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		
		if hasattr(request.user, 'spfuser'):
			return qs.filter(society=request.user.spfuser.society)
		else:
			return qs.none()

admin.site.register(Event, EventAdmin)
