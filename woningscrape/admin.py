from django.contrib import admin
from django.utils.http import urlquote
from models import *

class GemeenteAdmin(admin.ModelAdmin):
    pass

class WoningAdmin(admin.ModelAdmin):
    list_display = ('adres', 'wijk', 'gemeente', 'oppervlakte', 'reacties', 'kamers', 'leegper','leeftijd', 'rekenhuur', 'address_to_map', 'woningnet_link')
    list_filter = ('gemeente','wijk','kamers','woonversnelling')
    list_per_page = 25
    list_select_related = True
    search_fields = ('adres', 'postcode', 'gemeente__naam','wijk__naam','woningtype')
    
    def address_to_map(self, obj):
        return '<a href="http://maps.google.com/maps?f=q&hl=nl&geocode=&q=%s,%%20%s&t=p&z=13" target="top">Kaart</a>' % (urlquote(obj.adres), urlquote(obj.gemeente.naam))
    address_to_map.short_description = ''
    address_to_map.allow_tags = True

    def woningnet_link(self, obj):
        return '<a href="%s" target="top">Link</a>' % obj.get_absolute_url()
    woningnet_link.short_description = ''
    woningnet_link.allow_tags = True

    

#admin.site.register(Gemeente, GemeenteAdmin)
admin.site.register(Woning, WoningAdmin)

