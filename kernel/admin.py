from django.contrib import admin
from django.contrib.auth.models import User
from django.template import context
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import *
from .sys_lib import search_profiles, get_entity_profile, get_program_entrypoints, ProcessCreator
from .views import CustomTokenObtainPairView, CustomTokenRefreshView
from .signals import operand_finished

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
            path('new_service_process/<str:entity_id>/<str:service_rule_id>/', self.new_service_process, name='new_service_process'),
            path('new_service_process_schedule/<str:entity_id>/<str:service_id>/', self.new_service_process_schedule, name='new_service_process_schedule'),
            path('manage_task/', self.manage_task, name='manage_task'),
            path('assign_operator/<int:pid>/', self.assign_operator, name='assign_operator'),
        ]
        return my_urls + urls

    def operator_context(self, request):
        user = request.user
        context = {}

        # 实体类型
        entity_types = SysParams.objects.get(label='实体类型').config
        # 为每个实体类型添加其对应的服务入口点
        for entity_type in entity_types:
            model_str = entity_type['model'].lower()  # 转换为小写
            entity_type['service_entrypoints'] = get_program_entrypoints(model_str)

        """
        实体类型格式:
        [
            {
                "id": "1",
                "model": "customer",
                "verbose_name": "客户",
                "service_entrypoints": [
                    {
                        "title": "入口点名称",
                        "service_rule_id": "入口点erpsys_id"
                    }
                ]
            }
        ]
        """
        context['entity_types'] = entity_types

        """
        员工列表格式:
        [
            {
                "id": "1",
                "name": "test",
                "allowed_services": []
            }
        ]
        """
        # 员工列表，过滤掉操作员自己，用于排班
        context['all_employees'] = [{'id': '1', 'name': 'test', 'allowed_services': []}]

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
        # 从request中获取操作人
        user = request.user
        operator = Operator.objects.get(user=user)

        # 获取服务
        service_rule_id = kwargs.get('service_rule_id', None)
        service_rule = ServiceRule.objects.get(erpsys_id = service_rule_id)
        program_entrypoint = service_rule.service_program.erpsys_id
        
        # 获取服务对象类型
        service = service_rule.service
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
            if not entity_label:
                entity_label = '未知'
            entity = eval(serve_content_type_str).objects.create(
                label = entity_label
            )

        print(f"为{entity}创建服务：{service}, entity_id={entity_id}")

        # 1. 定位服务上下文：获取或创建当前实体上下文        

        # 2. 在进程上下文中添加“开始服务程序”事件标识:start_service_program==True

        # 3. 创建新服务进程
        params = {
            'service_rule': service_rule,
            'service': service,
            'entity_content_object': entity,
            'operator': operator,
            'state': ProcessState.NEW.name,
            'priority': 0,
            'program_entrypoint': program_entrypoint,
            'init_params': {'start_service_program': True}
        }

        creator = ProcessCreator()
        proc = creator.create_process(params)

        # 发送登录作业完成信号
        operand_finished.send(sender=self.new_service_process, pid=proc, request=request, form_data=None, formset_data=None)

        return redirect(f'/{settings.CUSTOMER_SITE_NAME}/')

    # 创建新服务日程
    def new_service_process_schedule(self, request, **kwargs):
        """
        人工创建新服务日程
        """
        # 人工创建服务意味着：
        # 1. 操作人识别当前上下文位置，将此位置信息传入此处
        # 2. 上下文位置为空，则初始化一个新的上下文

        entity_id = kwargs.get('entity_id', None)
        service_id = kwargs.get('service_id', None)
        return redirect(f'/{settings.CUSTOMER_SITE_NAME}/')

    def index(self, request, extra_context=None):
        """
        系统主页: 用户任务看板
        """
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

applications_site = ApplicationsSite(name='ApplicationsSite')

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
    search_fields = ['label', 'name', 'pym']

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']
applications_site.register(Operator, OperatorAdmin)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Instruction._meta.fields]
    list_display_links = ['id', 'label', 'name',]

class ServiceRuleInline(admin.TabularInline):
    model = ServiceRule
    autocomplete_fields = ['event', 'service', 'operand_service']
    extra = 0

@admin.register(ServiceProgram)
class ServiceProgramAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceProgram._meta.fields]
    list_display_links = ['label', 'name',]
    search_fields = ['label', 'name', 'pym']
    inlines = [ServiceRuleInline]

@admin.register(ServiceRule)
class ServiceRuleAdmin(admin.ModelAdmin):
    list_display = ['service_program', 'order', 'label', 'service', 'event', 'system_instruction', 'operand_service', 'entity_content_type', 'entity_object_id', 'parameter_values', 'id']
    list_display_links = ['order', 'label']
    search_fields = ['label', 'name', 'pym']

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorkOrder._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Process._meta.fields]
    list_display_links = ['pid', 'name', 'service',]
    search_fields = ['pid', 'name', 'service', 'state']
    list_filter = ['state', 'service']
    autocomplete_fields = ['service']
    readonly_fields = ['created_at', 'updated_at']
    
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
        ('时间信息', {
            'fields': ('start_time', 'end_time', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(ProcessContextSnapshot)
class ProcessContextSnapshotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProcessContextSnapshot._meta.fields]
    list_display_links = ['id', ]
    search_fields = ['label', 'name', 'pym']

@admin.register(SysParams)
class SysParamsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SysParams._meta.fields]
    list_display_links = ['id', 'label', 'name',]
    search_fields = ['label', 'name', 'pym']

class ErpFormAdmin(admin.ModelAdmin):
    # list_fields = ['name', 'id']
    # exclude = ["label", "name", "customer", "operator", "creater", "pid", "cpid", "slug", "created_time", "updated_time", "pym"]
    view_on_site = False

    def has_change_permission(self, request, obj=None):
        # 修改表单时如果表单操作员与当前用户不一致，不允许修改
        if obj: 
            if request.user.operator != obj.pid.operator:
                return False
        return super().has_change_permission(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # base_form = 'base_form'
        # extra_context['base_form'] = base_form
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if any(key.endswith('-TOTAL_FORMS') for key in request.POST):
            # 表单数据包含InlineModelAdmin 实例, 由save_formset发送服务作业完成信号
            # 保存obj到request for later retrieval in save_formset
            request._saved_obj = obj                
        else: # 表单数据不包含InlineModelAdmin 实例, 由save_model发送服务作业完成信号
            # 把表单内容存入CustomerServiceLog
            # log = create_customer_service_log(form.cleaned_data, None, obj)
            print('操作完成(save_model)：', obj.pid)
            operand_finished.send(sender=self, pid=obj.pid, request=request, form_data=form.cleaned_data, formset_data=None)

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        # Retrieve obj from the request
        obj = getattr(request, '_saved_obj', None)

        form_data = form.cleaned_data
        formset_data = formset.cleaned_data

        # 把表单明细内容存入CustomerServiceLog
        # log = create_customer_service_log(form_data, formset_data, obj)
        print('操作完成(save_formset)：', obj.pid)
        operand_finished.send(sender=self, pid=obj.pid, request=request, form_data=form_data, formset_data=formset_data)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save': True,
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
            'show_delete': False
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    # def response_change(self, request, obj):        
    #     # 按照service.route_to的配置跳转
    #     if obj.pid.service.route_to == 'CUSTOMER_HOMEPAGE':
    #         return redirect(obj.customer)
    #     else:
    #         return redirect('index')

def hide_fields(fields):
    exclude_fields = ['id', 'created_time', 'label', 'name', 'pym', 'erpsys_id', 'pid', 'updated_time']
    for field in exclude_fields:
        if field in fields:
            fields.remove(field)
    fields.extend(['created_time', 'id'])