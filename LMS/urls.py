
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('Auth.urls')),
    path('management/', include('Management.urls')),

]
