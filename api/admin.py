from django.contrib import admin
from oauth2_provider.models import Application, AccessToken, RefreshToken, Grant


class ApplicationAdmin(admin.ModelAdmin):
    """
    Custom admin interface for OAuth2 Applications (Client IDs and Secrets).
    """
    list_display = ('name', 'client_id', 'client_type', 'authorization_grant_type', 'created', 'updated')
    list_filter = ('client_type', 'authorization_grant_type', 'skip_authorization')
    search_fields = ('name', 'client_id')
    readonly_fields = ('client_id', 'client_secret', 'created', 'updated')

    fieldsets = (
        ('Application Info', {
            'fields': ('name', 'user', 'client_type', 'authorization_grant_type')
        }),
        ('Client Credentials', {
            'fields': ('client_id', 'client_secret'),
            'description': 'These credentials are used to authenticate your application. Keep the client secret secure!'
        }),
        ('OAuth2 Configuration', {
            'fields': ('redirect_uris', 'allowed_origins', 'skip_authorization', 'algorithm'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Make client_id and timestamps readonly, but allow viewing client_secret.
        """
        if obj:  # Editing an existing object
            return self.readonly_fields
        return ('created', 'updated')  # Creating new object


class AccessTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing and managing access tokens.
    """
    list_display = ('token_preview', 'user', 'application', 'expires', 'scope', 'created')
    list_filter = ('application', 'created', 'expires')
    search_fields = ('user__username', 'application__name', 'token')
    readonly_fields = ('token', 'created', 'updated')

    def token_preview(self, obj):
        """Show only first 20 characters of token for security."""
        return f"{obj.token[:20]}..." if obj.token else ""
    token_preview.short_description = "Token"


class RefreshTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing and managing refresh tokens.
    """
    list_display = ('token_preview', 'user', 'application', 'created', 'revoked')
    list_filter = ('application', 'created', 'revoked')
    search_fields = ('user__username', 'application__name', 'token')
    readonly_fields = ('token', 'created', 'updated')

    def token_preview(self, obj):
        """Show only first 20 characters of token for security."""
        return f"{obj.token[:20]}..." if obj.token else ""
    token_preview.short_description = "Token"


# Unregister the default admin (if any) and register our customized versions
admin.site.unregister(Application)
admin.site.register(Application, ApplicationAdmin)

admin.site.unregister(AccessToken)
admin.site.register(AccessToken, AccessTokenAdmin)

admin.site.unregister(RefreshToken)
admin.site.register(RefreshToken, RefreshTokenAdmin)

# Customize admin site header
admin.site.site_header = "OAuth2 Server Administration"
admin.site.site_title = "OAuth2 Admin"
admin.site.index_title = "Manage OAuth2 Applications and Tokens"
