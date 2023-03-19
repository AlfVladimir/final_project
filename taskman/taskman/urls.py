from rest_framework import routers
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import include, path
from tmapp.views import task_list, task_detail, task_new, task_edit, task_delete
from tmapp.views import project_new, project_list, project_detail
from tmapp.views import project_delete, project_edit
from tmapp.views import sprint_edit, sprint_delete
from tmapp.views import status_list, status_new, status_edit, status_delete
from tmapp.views import signup, sprint_new
from tmapp.forms import LoginForm
from django.conf import settings
from tmapp.views import TaskDRFViewSet, ProjectDRFViewSet
from tmapp.views import SprintDRFViewSet, StatusDRFViewSet




router = routers.DefaultRouter()
router.register(prefix="task",viewset=TaskDRFViewSet,)
router.register(prefix="project",viewset=ProjectDRFViewSet,)
router.register(prefix="sprint",viewset=SprintDRFViewSet,)
router.register(prefix="status",viewset=StatusDRFViewSet,)


urlpatterns = [
    path('', task_list, name = 'tasklist'),
    path('task/<int:id>/', task_detail, name = 'task'),
    path('task/del/<int:id>/', task_delete, name = 'taskdelete'),    
    path('task/edit/<int:id>/', task_edit, name = 'taskedit'),    
    path('task/', task_new, name='tasknew'),

    path('project/list/', project_list, name = 'projectlist'),    
    path('project/', project_new, name='projectnew'),
    path('project/<int:id>/', project_detail, name = 'project'),
    path('project/edit/<int:id>/', project_edit, name = 'projectedit'),    
    path('project/del/<int:id>/', project_delete, name = 'projectdelete'),    

    path('sprint/', sprint_new, name='sprintnew'),
    path('sprint/edit/<int:id>/', sprint_edit, name = 'sprintedit'),    
    path('sprint/del/<int:id>/', sprint_delete, name = 'sprintdelete'),       
    
    path('status/list/', status_list, name='statuslist'),            
    path('status/', status_new, name='statusnew'),
    path('status/edit/<int:id>/', status_edit, name='statusedit'),    
    path('status/delete/<int:id>/', status_delete, name='statusdelete'),        

    path('signup/', signup, name = 'signup'),
    path('login/', auth_views.LoginView.as_view(
                template_name='login.html',
                authentication_form=LoginForm
                ),
            name='login'
    ),    
    path('logout/',
        auth_views.LogoutView.as_view(),
        {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'
    ),
    
    path('admin/', admin.site.urls),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))
]
