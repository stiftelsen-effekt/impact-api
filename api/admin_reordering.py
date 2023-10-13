from django.contrib.admin import AdminSite

class ReorderedSite(AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        for app in app_list:
            if app['app_label'] == 'api':
                # Reorder the models in our specified order
                app['models'].sort(key=lambda x: self.get_model_order().index(x['object_name']))
        return app_list

    def get_model_order(self):
        # List the models in the order they should appear in the admin section (including those
        # that don't appear, for simplicity)
        return ['Evaluation', 'Intervention', 'MaxImpactFundGrant', 'AllGrantsFundGrant',
                'Allotment', 'Charity']

# Instantiate the custom AdminSite
admin_site = ReorderedSite(name='reordered_admin')
