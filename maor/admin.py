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

@admin.register(KeHuLaiYuan)
class KeHuLaiYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KeHuLaiYuan._meta.fields]
    list_display_links = ['id']
maor_site.register(KeHuLaiYuan, KeHuLaiYuanAdmin)

@admin.register(ShiFouDaoDian)
class ShiFouDaoDianAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ShiFouDaoDian._meta.fields]
    list_display_links = ['id']
maor_site.register(ShiFouDaoDian, ShiFouDaoDianAdmin)

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

@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Knowledge._meta.fields]
    list_display_links = ['id']
maor_site.register(Knowledge, KnowledgeAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]
    list_display_links = ['id']
maor_site.register(Profile, ProfileAdmin)

@admin.register(WuLiaoTaiZhang)
class WuLiaoTaiZhangAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoTaiZhang._meta.fields]
    list_display_links = ['id']
maor_site.register(WuLiaoTaiZhang, WuLiaoTaiZhangAdmin)

@admin.register(YuYueJiLu)
class YuYueJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in YuYueJiLu._meta.fields]
    list_display_links = ['id']
maor_site.register(YuYueJiLu, YuYueJiLuAdmin)
