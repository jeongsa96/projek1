from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Invoice)
admin.site.register(PO)
admin.site.register(Jenis_Anggaran)
admin.site.register(Anggaran)
admin.site.register(data_Expense)
admin.site.register(Pekerjaan_mapping)
admin.site.register(Mapping_Report)