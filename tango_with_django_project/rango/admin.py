from django.contrib import admin
from rango.models import Bar, Tapa

# Register your models here.
class BarAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('nombre',)}

admin.site.register(Bar, BarAdmin)
admin.site.register(Tapa)
