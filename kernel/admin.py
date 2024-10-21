from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse

import json
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
        from core.business_functions import create_service_proc, dispatch_operator, eval_scheduled_time
        # 从request获取参数：customer, service, operator
        customer = Customer.objects.get(id=kwargs['customer_id'])
        current_operator = User.objects.get(username=request.user).customer
        service = Service.objects.get(id=kwargs['service_id'])
        service_operator = dispatch_operator(customer, service, current_operator, timezone.now(), None)

        # 区分服务类型是"1 管理调度服务"还是"2 诊疗服务"，获取ContentType
        if service.service_type == 1:
            content_type = ContentType.objects.get(app_label='service', model='customerschedulepackage')
        else:
            content_type = ContentType.objects.get(app_label='service', model=service.name.lower())

        # 准备新的服务作业进程参数
        proc_params = {}
        proc_params['service'] = service
        proc_params['customer'] = customer
        proc_params['creater'] = current_operator
        proc_params['operator'] = service_operator
        proc_params['priority_operator'] = None
        proc_params['state'] = 0  # or 0 根据服务作业权限判断

        # 如果当前操作员即是服务作业员，计划执行时间为当前时间，否则估算计划执行时间
        if current_operator == service_operator:
            proc_params['scheduled_time'] = timezone.now()
        else:
            proc_params['scheduled_time'] = eval_scheduled_time(service, service_operator)

        proc_params['contract_service_proc'] = None
        proc_params['content_type'] = content_type
        proc_params['form_data'] = None
        proc_params['apply_to_group'] = False
        proc_params['coroutine_result'] = None
        
        # 如果是推荐服务，解析parent_proc和passing_data
        if kwargs['recommended_service_id']:
            recommended_service = RecommendedService.objects.get(id=kwargs['recommended_service_id'])
            proc_params['parent_proc'] = recommended_service.pid
            proc_params['passing_data'] = recommended_service.passing_data

            # 获取父进程的表单数据
            field_names = [field.name for field in recommended_service.pid.content_object._meta.get_fields()][12:]
            form_data = {}
            for field_name in field_names:
                field_value = getattr(recommended_service.pid.content_object, field_name)
                # 如果字段是多对多字段，则获取QuerySet
                if isinstance(field_value, models.Manager):
                    field_value = field_value.all()
                form_data[field_name] = field_value
            proc_params['form_data'] = form_data

        else:
            # 人工创建服务，没有父进程
            proc_params['parent_proc'] = None
            # 人工创建服务，没有传递数据
            proc_params['passing_data'] = 0

        # 创建新的OperationProc服务作业进程实例
        new_proc = create_service_proc(**proc_params)

        # *************************************************
        # 管理可选服务队列
        # *************************************************
        # 如果请求来自一个可选服务条目，从可选服务队列中删除该条目
        if kwargs['recommended_service_id']:
            RecommendedService.objects.get(id=kwargs['recommended_service_id']).delete()

        # 如果开单给作业员本人，进入修改界面
        if service_operator == current_operator:
            # 重定向到/clinic/service/model/id/change
            return redirect(new_proc.entry)
        else:  # 否则显示提示消息：开单成功
            from django.contrib import messages
            messages.add_message(request, messages.INFO, f'{service.label}已开单')
            return redirect(customer)

    # 创建新服务日程
    def new_schedule(self, request, **kwargs):
        from core.business_functions import eval_scheduled_time, create_customer_schedule
        # 1. 创建"安排服务计划"服务进程
        customer_id = kwargs['customer_id']
        customer = Customer.objects.get(id=customer_id)
        current_operator = User.objects.get(username=request.user).customer
        service = Service.objects.get(name='CustomerSchedule')
        content_type = ContentType.objects.get(app_label='service', model='customerschedule')
        # 创建一个状态为“运行”的“安排服务计划”作业进程
        new_proc=OperationProc.objects.create(
            service=service,  # 服务
            customer=customer,  # 客户
            operator=current_operator,  # 作业人员
            creater=current_operator,  # 创建者
            scheduled_time=timezone.now(),  # 计划执行时间
            state=2,  # 进程状态：运行
            content_type=content_type,  # 内容类型
            overtime=service.overtime,  # 超时时间
            working_hours=service.working_hours,  # 工作时间
        )

        # 2. 创建服务计划安排: CustomerSchedule
        params = {
            'customer': customer,
            'operator': current_operator,
            'creater': current_operator,
            'service': Service.objects.get(id=kwargs['service_id']),  # 服务
            'scheduled_time': eval_scheduled_time(service, None),
            'pid': new_proc,
        }
        customer_schedule = create_customer_schedule(**params)  # 创建服务计划安排

        # 3. 更新OperationProc服务进程的form实例信息
        new_proc.object_id = customer_schedule.id
        new_proc.entry = f'/clinic/service/customerschedule/{customer_schedule.id}/change'
        new_proc.save()

        return redirect(new_proc.entry)

    # 更新服务日程
    def update_schedule(self, request, **kwargs):
        pass

    # 指派操作员
    def assign_operator(self, request, **kwargs):
        class CustomOperationProcForm(ModelForm):
            class Meta:
                model = OperationProc
                fields = ['id', 'service', 'operator', 'scheduled_time']

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields['service'].widget.attrs['readonly'] = 'readonly'

                if self.instance and self.instance.service:
                    # 获取所有该service关联的roles, 过滤选择Staff.role在roles里的员工
                    roles = self.instance.service.role.all()
                    staffs = Staff.objects.filter(role__in=roles).distinct()
                    self.fields['operator'].queryset = Customer.objects.filter(staff__in=staffs).distinct()

        parent_pid = kwargs['pid']
        parent_proc = OperationProc.objects.get(id=parent_pid)
        queryset=OperationProc.objects.filter(parent_proc = parent_proc, operator__isnull = True)
        class BaseAssignOperatorFormSet(BaseModelFormSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.queryset = queryset   

        AssignOperatorModelFormset = modelformset_factory(OperationProc, form=CustomOperationProcForm, formset=BaseAssignOperatorFormSet, extra=0, can_delete=False)
        if request.method == 'POST':
            action = request.POST.get('action_type')
            if action == '保存':
                assign_operator_model_formset = AssignOperatorModelFormset(request.POST)
                print('errors', assign_operator_model_formset.errors)
                if assign_operator_model_formset.is_valid():
                    assign_operator_model_formset.save()        

            # 按照service.route_to的配置跳转
            if parent_proc.service.route_to == 'CUSTOMER_HOMEPAGE':
                return redirect(parent_proc.customer)
            else:
                return redirect('index')

        else:
            assign_operator_model_formset = AssignOperatorModelFormset(queryset=queryset)
            context = {'formset': assign_operator_model_formset}
            # 如果有未分配操作员的进程，跳转到分配操作员的页面
            return render(request, 'assign_operator.html', context)

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

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]
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
