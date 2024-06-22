from django.contrib import admin
from .models import *


@admin.register(XiTongLeiXing)
class XiTongLeiXingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in XiTongLeiXing._meta.fields]
    list_display_links = ['id']

@admin.register(GangWei)
class GangWeiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GangWei._meta.fields]
    list_display_links = ['id']

@admin.register(FuWuLeiBie)
class FuWuLeiBieAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FuWuLeiBie._meta.fields]
    list_display_links = ['id']

@admin.register(RuChuKuCaoZuo)
class RuChuKuCaoZuoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RuChuKuCaoZuo._meta.fields]
    list_display_links = ['id']

@admin.register(RenYuan)
class RenYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RenYuan._meta.fields]
    list_display_links = ['id']

@admin.register(WuLiao)
class WuLiaoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiao._meta.fields]
    list_display_links = ['id']

@admin.register(SheBei)
class SheBeiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SheBei._meta.fields]
    list_display_links = ['id']

@admin.register(GongJu)
class GongJuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GongJu._meta.fields]
    list_display_links = ['id']

@admin.register(ZiJin)
class ZiJinAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZiJin._meta.fields]
    list_display_links = ['id']

@admin.register(KongJian)
class KongJianAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KongJian._meta.fields]
    list_display_links = ['id']

@admin.register(XinXi)
class XinXiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in XinXi._meta.fields]
    list_display_links = ['id']

@admin.register(FuWuXiangMu)
class FuWuXiangMuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FuWuXiangMu._meta.fields]
    list_display_links = ['id']

@admin.register(CaoZuoYuan)
class CaoZuoYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CaoZuoYuan._meta.fields]
    list_display_links = ['id']

@admin.register(GongDan)
class GongDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GongDan._meta.fields]
    list_display_links = ['id']

@admin.register(ZhenShi)
class ZhenShiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhenShi._meta.fields]
    list_display_links = ['id']

@admin.register(WuLiaoTaiZhang)
class WuLiaoTaiZhangAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoTaiZhang._meta.fields]
    list_display_links = ['id']

@admin.register(KeHu)
class KeHuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KeHu._meta.fields]
    list_display_links = ['id']

@admin.register(ZhiYuan)
class ZhiYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhiYuan._meta.fields]
    list_display_links = ['id']

@admin.register(YiSheng)
class YiShengAdmin(admin.ModelAdmin):
    list_display = [field.name for field in YiSheng._meta.fields]
    list_display_links = ['id']

@admin.register(HuShi)
class HuShiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in HuShi._meta.fields]
    list_display_links = ['id']

@admin.register(KeFu)
class KeFuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KeFu._meta.fields]
    list_display_links = ['id']
