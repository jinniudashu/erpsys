from django.contrib import admin
from .models import *

class MaorSite(admin.AdminSite):
    site_header = '广州颜青医疗美容诊所'
    site_title = 'Maor'
    index_title = '工作台'
    enable_nav_sidebar = False
    index_template = 'admin/index_maor.html'
    site_url = None

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
        ]
        return my_urls + urls

    # 职员登录后的首页
    def index(self, request, extra_context=None):
        print('MaorSite index:', request.user, extra_context)
        # user = User.objects.get(username=request.user).customer
        return super().index(request, extra_context=extra_context)

maor_site = MaorSite(name = 'MaorSite')

# class ServiceAttributesInline(admin.TabularInline):
#     model = ServiceAttributes
#     extra = 0

# class ResourceDependencyInline(admin.TabularInline):
#     model = ResourceDependency
#     extra = 0

# class ServiceConsistsInline(admin.TabularInline):
#     model = ServiceConsists
#     fk_name = 'service'  # 指定使用的外键字段名
#     extra = 0
#     autocomplete_fields = ['service', 'sub_service']

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ['label', 'name', 'form', 'subject', 'work_order', 'route_to', 'program', 'service_type', ]
#     list_display_links = ['label', 'name',]
#     inlines = [ServiceConsistsInline, ResourceDependencyInline, ServiceAttributesInline]
#     search_fields = ['label', 'name', 'pym']
#     autocomplete_fields = ['form', 'subject', 'work_order', 'route_to']

# class FormComponentsInline(admin.TabularInline):
#     model = FormComponents
#     extra = 0
#     autocomplete_fields = ['data_item']

# class FormComponentsConfigInline(admin.TabularInline):
#     model = FormComponentsConfig
#     extra = 0
#     autocomplete_fields = ['data_item']

# @admin.register(Form)
# class FormAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Form._meta.fields]
#     list_display_links = ['label', 'name',]
#     inlines = [FormComponentsInline, FormComponentsConfigInline]
#     search_fields = ['label', 'name', 'pym']

# @admin.register(Event)
# class EventAdmin(admin.ModelAdmin):
#     list_display = ['id', 'label', 'name', 'pym', 'rule']
#     list_display_links = ['label', 'name',]
#     search_fields = ['label', 'name', 'pym']



@admin.register(GangWei)
class GangWeiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GangWei._meta.fields]
    list_display_links = ['id']
maor_site.register(GangWei, GangWeiAdmin)

@admin.register(FuWuLeiBie)
class FuWuLeiBieAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FuWuLeiBie._meta.fields]
    list_display_links = ['id']
maor_site.register(FuWuLeiBie, FuWuLeiBieAdmin)

@admin.register(RuChuKuCaoZuo)
class RuChuKuCaoZuoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RuChuKuCaoZuo._meta.fields]
    list_display_links = ['id']
maor_site.register(RuChuKuCaoZuo, RuChuKuCaoZuoAdmin)

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Operator._meta.fields]
    list_display_links = ['id']
maor_site.register(Operator, OperatorAdmin)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Material._meta.fields]
    list_display_links = ['id']
maor_site.register(Material, MaterialAdmin)

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Equipment._meta.fields]
    list_display_links = ['id']
maor_site.register(Equipment, EquipmentAdmin)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Device._meta.fields]
    list_display_links = ['id']
maor_site.register(Device, DeviceAdmin)

@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Capital._meta.fields]
    list_display_links = ['id']
maor_site.register(Capital, CapitalAdmin)

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Space._meta.fields]
    list_display_links = ['id']
maor_site.register(Space, SpaceAdmin)

@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Information._meta.fields]
    list_display_links = ['id']
maor_site.register(Information, InformationAdmin)

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorkOrder._meta.fields]
    list_display_links = ['id']
maor_site.register(WorkOrder, WorkOrderAdmin)

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Form._meta.fields]
    list_display_links = ['id']
maor_site.register(Form, FormAdmin)

@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Knowledge._meta.fields]
    list_display_links = ['id']
maor_site.register(Knowledge, KnowledgeAdmin)

@admin.register(WuLiaoTaiZhang)
class WuLiaoTaiZhangAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoTaiZhang._meta.fields]
    list_display_links = ['id']
maor_site.register(WuLiaoTaiZhang, WuLiaoTaiZhangAdmin)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    list_display_links = ['id']
maor_site.register(Service, ServiceAdmin)
