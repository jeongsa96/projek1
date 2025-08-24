from django.contrib import admin
from .models import User, Project, Invoice, PO

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Invoice)
admin.site.register(PO)