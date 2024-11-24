from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse

from .models import *
from .sys_lib import search_profiles, get_operator_profile
from .views import CustomTokenObtainPairView, CustomTokenRefreshView

def hide_fields(fields):
    exclude_fields = ['id', 'created_time', 'label', 'name', 'pym', 'erpsys_id', 'pid', 'updated_time']
    for field in exclude_fields:
        if field in fields:
            fields.remove(field)
    fields.extend(['created_time', 'id'])

admin.site.site_header = "..运营平台"
admin.site.site_title = ".."
admin.site.index_title = "工作台"

class ApplicationsSite(admin.AdminSite):
    site_header = '..运营平台'
    site_title = '..'
    index_title = '任务看板'
    enable_nav_sidebar = False
    index_template = 'index_applications.html'
    site_url = None

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
            path('manage_task/', self.manage_task),
            path('entity_operation/<str:id>/', self.entity_operation),
            path('entity_profile/<str:id>/', self.entity_profile),
            path('search/', self.search),
            path('new_service_process/<int:customer_id>/<int:service_id>/<int:recommended_service_id>/', self.new_service_process, name='new_service_process'),
            path('new_schedule/<int:customer_id>/<int:service_id>/', self.new_schedule, name='new_schedule'),
            path('update_schedule/<int:customer_schedule_package_id>/', self.update_schedule, name='update_schedule'),
            path('assign_operator/<int:pid>/', self.assign_operator, name='assign_operator')
        ]
        return my_urls + urls

    # 职员登录后的首页
    def index(self, request, extra_context=None):
        # user = User.objects.get(username=request.user).customer
        return super().index(request, extra_context=extra_context)

    # 管理任务状态
    def manage_task(self, request, **kwargs):
        operator = Operator.objects.get(user=request.user)

        pid = request.GET.get('pid', None)
        proc = Process.objects.get(pid=pid)
        
        op_code = request.GET.get('op_code', None)
        match op_code:
            case 'RECEIVE':
                proc.receive_task(operator)
            case 'ROLLBACK':
                proc.rollback_task()
            case 'SUSPEND_OR_RESUME':
                proc.suspend_or_resume_task()
            case 'CANCEL':
                proc.cancel_task(operator)
            case 'SHIFT':
                operator_id = request.GET.get('operator_id', None)
                shift_operator = Operator.objects.get(erpsys_id = operator_id)
                proc.shift_task(shift_operator)
        return redirect(f'/{settings.CUSTOMER_SITE_NAME}/')

    # 实体操作页面
    def entity_operation(self, request, **kwargs):
        context = {}

        user = request.user
        operator = Operator.objects.get(user=user)
        allowed_services = operator.allowed_services()
        customer_id = kwargs.get('id', None )

        response = render(request, 'entity_operation.html', context)

        response.set_cookie('operator_id', operator.erpsys_id)
        services_ids_string = ','.join([service.erpsys_id for service in allowed_services])
        response.set_cookie('allowed_services_id', services_ids_string)
        
        return response

    # 搜索实体，返回实体基本信息列表
    def search(self, request):
        operator = Operator.objects.get(user=request.user)
        search_content = request.GET.get('search_content')
        search_text = request.GET.get('search_text')

        profile_list, profile_header = [], []
        if search_content and search_text:
            profile_list, profile_header = search_profiles(search_content, search_text, operator)

        return JsonResponse({
            'profile_list': profile_list, 
            'profile_header': profile_header
        }, safe=False)
    
    def entity_profile(self, request, **kwargs):
        customer_id = kwargs.get('id', None )
        context = {}
        if customer_id:
            customer = Operator.objects.get(erpsys_id = customer_id)
            return JsonResponse(get_operator_profile(customer), safe=False)

    # 创建服务
    def new_service_process(self, request, **kwargs):
        '''
        人工创建新服务：作业进程+表单进程
        从kwargs获取参数：customer_id, service_id
        '''
        pass

    # 创建新服务日程
    def new_schedule(self, request, **kwargs):
        pass

    # 更新服务日程
    def update_schedule(self, request, **kwargs):
        pass

    # 指派操作员
    def assign_operator(self, request, **kwargs):
        pass
    
applications_site = ApplicationsSite(name = 'ApplicationsSite')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'session_data', 'expire_date']

@admin.register(ERPSysRegistry)
class ERPSysRegistryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ERPSysRegistry._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Organization._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Role._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    filter_horizontal = ['services']

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Instruction._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(ServiceRule)
class ServiceRuleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceRule._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorkOrder._meta.fields]
    list_display_links = ['id', 'label', 'name',]

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Process._meta.fields]
    list_display_links = ['pid', 'name', 'service',]
    search_fields = ['pid', 'name', 'service', 'state']
    list_filter = ['state', 'service']
    autocomplete_fields = ['service']
    readonly_fields = ['created_time', 'updated_time']

@admin.register(Stacks)
class StacksAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Stacks._meta.fields]
    list_display_links = ['id', 'process',]
    search_fields = ['id', 'process']
    list_filter = ['process']
    readonly_fields = ['id', 'created_time', 'updated_time']

@admin.register(SysParams)
class SysParamsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SysParams._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']
