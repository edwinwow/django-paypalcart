from django.contrib import admin
from cartridge.shop.admin import ProductAdmin
from .models import Subscription, UserSubscription


admin.site.register(Subscription, ProductAdmin)

class UserSubscriptionAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets) 

admin.site.register(UserSubscription, UserSubscriptionAdmin)

