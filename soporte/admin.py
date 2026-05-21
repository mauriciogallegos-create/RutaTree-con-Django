from django.contrib import admin
from .models import Nodo


@admin.register(Nodo)
class NodoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'parent', 'orden', 'depth']
    list_filter = ['parent']
    search_fields = ['nombre']

    def depth(self, obj):
        return obj.get_depth()
