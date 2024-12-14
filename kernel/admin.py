from django.contrib import admin
from django.contrib.auth.models import User
from django.template import context
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import *
from .sys_lib import search_profiles, get_entity_profile
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
            path('operator_context/', self.operator_context, name='operator_context'),
            path('entity_operation/<str:entity_type>/<str:id>/', self.entity_operation, name='entity_operation'),
            path('entity_context/<str:id>/', self.entity_context, name='entity_context'),
            path('search/', self.search, name='search'),
            path('new_service_process/<str:entity_id>/<str:service_id>/', self.new_service_process, name='new_service_process'),
            path('new_service_process_schedule/<str:entity_id>/<str:service_id>/', self.new_service_process_schedule, name='new_service_process_schedule'),
            path('manage_task/', self.manage_task, name='manage_task'),
            path('assign_operator/<int:pid>/', self.assign_operator, name='assign_operator'),
        ]
        return my_urls + urls

    def operator_context(self, request, **kwargs):
        context = {}

        # 实体类型
        context['entity_types'] = SysParams.objects.get(label='实体类型').config

        # 员工列表，过滤掉操作员自己，用于排班
        context['all_employees'] = [{'id': '1', 'name': 'test', 'allowed_services': []}]

        # 新建实体服务
        context['new_entity_services'] = [{'title': '客户服务', 'id': 'bb592f4c-b3ac-11ef-a6d8-0e586f6f8a1e'}]

        return JsonResponse(context, safe=False)

    def entity_operation(self, request, **kwargs):
        """
        实体操作页面
        """
        # 准备上下文
        context = {}

        user = request.user
        operator = Operator.objects.get(user=user)
        allowed_services = operator.allowed_services()
        
        entity_type = kwargs.get('entity_type', None)
        entity_id = kwargs.get('id', None )

        response = render(request, 'entity_operation.html', context)

        response.set_cookie('operator_id', operator.erpsys_id)
        services_ids_string = ','.join([service.erpsys_id for service in allowed_services])
        response.set_cookie('allowed_services_id', services_ids_string)
        
        return response

    def entity_context(self, request, **kwargs):
        entity_id = kwargs.get('id', None )
        context = {}
        if entity_id:
            customer = Operator.objects.get(erpsys_id = entity_id)
            context['profile'] = get_entity_profile(customer)
            return JsonResponse(context, safe=False)

    # 搜索实体，返回实体基本信息列表
    def search(self, request):
        operator = Operator.objects.get(user=request.user)
        search_content = request.GET.get('search_content')
        search_text = request.GET.get('search_text')

        profile_list, profile_header = [], []
        if search_content:
            profile_list, profile_header = search_profiles(search_content, search_text, operator)

        return JsonResponse({
            'profile_list': profile_list, 
            'profile_header': profile_header
        }, safe=False)
    
    # 创建服务
    def new_service_process(self, request, **kwargs):
        """
        人工创建新服务
        """
        # 获取服务
        service_id = kwargs.get('service_id', None)
        service = Service.objects.get(erpsys_id = service_id)
        # 获取服务对象类型
        serve_content_type_str = service.config['serve_content_type']

        # 获取或创建新实体
        entity_id = kwargs.get('entity_id', None)
        if entity_id!='0':
            # 为已有实体创建服务
            entity = eval(serve_content_type_str).objects.get(erpsys_id = entity_id)
        else:
            # 为新实体创建服务
            # 创建实体实例
            entity_label = request.GET.get('entity_label', None)
            entity = eval(serve_content_type_str).objects.create(
                label = entity_label
            )

        print(f"为{entity}创建服务：{service}, entity_id={entity_id}")
        # 1. 定位服务上下文：获取或创建当前实体上下文        

        # 2. 在进程上下文中添加“开始服务程序”事件标识:start_service_program==True

        # 3. 创建服务进程
        # params = {
        #     'service': service,
        #     'entity_content_object': entity,
        #     'operator': operator,
        #     'state': ProcessState.TERMINATED.name,
        #     'priority': 0
        # }
        # Process.objects.create(**params)

        return redirect(f'/{settings.CUSTOMER_SITE_NAME}/')

    # 创建新服务日程
    def new_service_process_schedule(self, request, **kwargs):
        """
        人工创建新服务日程
        """
        # 人工创建服务意味着：
        # 1. 操作人识别当前上下文位置，将此位置信息传入此处
        # 2. 上下文位置为空，则初始化一个新的上下文

        # 定位服务上下文

        entity_id = kwargs.get('entity_id', None)
        service_id = kwargs.get('service_id', None)
        return redirect(f'/{settings.CUSTOMER_SITE_NAME}/')

    def index(self, request, extra_context=None):
        """
        系统主页: 用户任务看板
        """
        # user = User.objects.get(username=request.user).customer
        return super().index(request, extra_context=extra_context)

    def manage_task(self, request, **kwargs):
        """
        管理任务状态
        """
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

    # 指派操作员
    def assign_operator(self, request, **kwargs):
        pass

applications_site = ApplicationsSite(name = 'ApplicationsSite')

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
    list_display = ['order', 'label', 'service', 'event', 'system_instruction', 'operand_service', 'parameter_values', 'id']
    list_display_links = ['order', 'label']
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
    
    # 添加content_type字段到表单中
    raw_id_fields = ['entity_content_type', 'form_content_type']
    
    # 在表单中显示GenericForeignKey字段
    fieldsets = (
        (None, {
            'fields': ('name', 'erpsys_id', 'pid', 'parent', 'previous', 'service', 'state', 'priority', 
                      'scheduled_time', 'time_window', 'operator', 'work_order')
        }),
        ('实体关联', {
            'fields': ('entity_content_type', 'entity_object_id'),
            'classes': ('collapse',),
        }),
        ('表单关联', {
            'fields': ('form_url', 'form_content_type', 'form_object_id'),
            'classes': ('collapse',),
        }),
        ('进程控制', {
            'fields': ('program', 'pc', 'registers', 'io_status', 'cpu_scheduling', 
                      'accounting', 'sp', 'pcb', 'stack', 'schedule_context', 
                      'control_context'),
            'classes': ('collapse',),
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time', 'created_time', 'updated_time'),
            'classes': ('collapse',),
        }),
    )

@admin.register(ProcessFrameState)
class ProcessFrameStateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProcessFrameState._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(SysParams)
class SysParamsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SysParams._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

# @admin.register(Stacks)
# class StacksAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Stacks._meta.fields]
#     list_display_links = ['id', 'process',]
#     search_fields = ['id', 'process']
#     list_filter = ['process']
#     readonly_fields = ['id', 'created_time', 'updated_time']
