from django.contrib import admin
from cartridge.shop.admin import ProductAdmin
from .models import Subscription, SubscriptionProfile


admin.site.register(Subscription, ProductAdmin)

class SubscriptionProfileAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets) 

admin.site.register(SubscriptionProfile, SubscriptionProfile)

