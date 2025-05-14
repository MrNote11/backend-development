from django.contrib import admin
from .models import UserProfile, UserOTP, SiteSetting, TierAmountDb
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(UserOTP)
admin.site.register(SiteSetting)
admin.site.register(TierAmountDb)

