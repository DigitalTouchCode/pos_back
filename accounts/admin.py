from django.contrib import admin

from .models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "is_active")
    fieldsets = (
        (None, {"fields": ("name", "domain", "owner", "is_active")}),
        (
            "Email Configuration",
            {
                "fields": (
                    "email_host",
                    "email_port",
                    "email_use_tls",
                    "email_use_ssl",
                    "email_host_user",
                    "email_host_password",
                    "email_from",
                    "email_from_name",
                ),
                "classes": ("collapse",),
            },
        ),
    )


admin.site.register(User)
