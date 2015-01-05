from django.contrib.admin.sites import AdminSite

ui = AdminSite(name='UI')
ui.login_template = 'registration/login.html'
