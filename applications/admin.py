from django.contrib import admin

from kernel.admin import applications_site, ErpFormAdmin, hide_fields
from .models import *


@admin.register(FuWuLeiBie)
class FuWuLeiBieAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FuWuLeiBie._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(FuWuLeiBie, FuWuLeiBieAdmin)
    
@admin.register(RuChuKuCaoZuo)
class RuChuKuCaoZuoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RuChuKuCaoZuo._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(RuChuKuCaoZuo, RuChuKuCaoZuoAdmin)
    
@admin.register(KeHuLaiYuan)
class KeHuLaiYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KeHuLaiYuan._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(KeHuLaiYuan, KeHuLaiYuanAdmin)
    
@admin.register(HunFou)
class HunFouAdmin(admin.ModelAdmin):
    list_display = [field.name for field in HunFou._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(HunFou, HunFouAdmin)
    
@admin.register(ZhengZhuang)
class ZhengZhuangAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhengZhuang._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhengZhuang, ZhengZhuangAdmin)
    
@admin.register(ZhenDuan)
class ZhenDuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhenDuan._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhenDuan, ZhenDuanAdmin)
    
@admin.register(ShouFeiLeiXing)
class ShouFeiLeiXingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ShouFeiLeiXing._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ShouFeiLeiXing, ShouFeiLeiXingAdmin)
    
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Material._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Material, MaterialAdmin)
    
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Equipment._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Equipment, EquipmentAdmin)
    
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Device._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Device, DeviceAdmin)
    
@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Capital._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Capital, CapitalAdmin)
    
@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Knowledge._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Knowledge, KnowledgeAdmin)
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Profile, ProfileAdmin)
    
@admin.register(WuLiaoTaiZhang)
class WuLiaoTaiZhangAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoTaiZhang._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(WuLiaoTaiZhang, WuLiaoTaiZhangAdmin)
    
@admin.register(YuYueJiLu)
class YuYueJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in YuYueJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(YuYueJiLu, YuYueJiLuAdmin)
    
@admin.register(JianKangDiaoChaJiLu)
class JianKangDiaoChaJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in JianKangDiaoChaJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(JianKangDiaoChaJiLu, JianKangDiaoChaJiLuAdmin)
    
@admin.register(ZhuanKePingGuJiLu)
class ZhuanKePingGuJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhuanKePingGuJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhuanKePingGuJiLu, ZhuanKePingGuJiLuAdmin)
    
@admin.register(ZhenDuanJiChuLiYiJianJiLu)
class ZhenDuanJiChuLiYiJianJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhenDuanJiChuLiYiJianJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhenDuanJiChuLiYiJianJiLu, ZhenDuanJiChuLiYiJianJiLuAdmin)
    
@admin.register(RouDuSuZhiLiaoJiLu)
class RouDuSuZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RouDuSuZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(RouDuSuZhiLiaoJiLu, RouDuSuZhiLiaoJiLuAdmin)
    
@admin.register(ChaoShengPaoZhiLiaoJiLu)
class ChaoShengPaoZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChaoShengPaoZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ChaoShengPaoZhiLiaoJiLu, ChaoShengPaoZhiLiaoJiLuAdmin)
    
@admin.register(HuangJinWeiZhenZhiLiaoJiLu)
class HuangJinWeiZhenZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in HuangJinWeiZhenZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(HuangJinWeiZhenZhiLiaoJiLu, HuangJinWeiZhenZhiLiaoJiLuAdmin)
    
@admin.register(DiaoQZhiLiaoJiLu)
class DiaoQZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DiaoQZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(DiaoQZhiLiaoJiLu, DiaoQZhiLiaoJiLuAdmin)
    
@admin.register(GuangZiZhiLiaoJiLu)
class GuangZiZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuangZiZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(GuangZiZhiLiaoJiLu, GuangZiZhiLiaoJiLuAdmin)
    
@admin.register(GuoSuanZhiLiaoJiLu)
class GuoSuanZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GuoSuanZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(GuoSuanZhiLiaoJiLu, GuoSuanZhiLiaoJiLuAdmin)
    
@admin.register(ShuiGuangZhenZhiLiaoJiLu)
class ShuiGuangZhenZhiLiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ShuiGuangZhenZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ShuiGuangZhenZhiLiaoJiLu, ShuiGuangZhenZhiLiaoJiLuAdmin)
    
@admin.register(ChongZhiJiLu)
class ChongZhiJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChongZhiJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ChongZhiJiLu, ChongZhiJiLuAdmin)
    
@admin.register(XiaoFeiJiLu)
class XiaoFeiJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in XiaoFeiJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(XiaoFeiJiLu, XiaoFeiJiLuAdmin)
    
@admin.register(SuiFangJiLu)
class SuiFangJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SuiFangJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(SuiFangJiLu, SuiFangJiLuAdmin)
    
@admin.register(FaSongZhiLiaoZhuYiShiXiangJiLu)
class FaSongZhiLiaoZhuYiShiXiangJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FaSongZhiLiaoZhuYiShiXiangJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(FaSongZhiLiaoZhuYiShiXiangJiLu, FaSongZhiLiaoZhuYiShiXiangJiLuAdmin)
    
@admin.register(QianShuZhiQingTongYiShuJiLu)
class QianShuZhiQingTongYiShuJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in QianShuZhiQingTongYiShuJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(QianShuZhiQingTongYiShuJiLu, QianShuZhiQingTongYiShuJiLuAdmin)
    
@admin.register(DengLuQianDaoJiLu)
class DengLuQianDaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DengLuQianDaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(DengLuQianDaoJiLu, DengLuQianDaoJiLuAdmin)
    
@admin.register(YuYueTiXingJiLu)
class YuYueTiXingJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in YuYueTiXingJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(YuYueTiXingJiLu, YuYueTiXingJiLuAdmin)
    
@admin.register(ShouFeiJiLu)
class ShouFeiJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ShouFeiJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ShouFeiJiLu, ShouFeiJiLuAdmin)
    
@admin.register(ZhiLiaoXiangMuHeXiaoJiLu)
class ZhiLiaoXiangMuHeXiaoJiLuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhiLiaoXiangMuHeXiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhiLiaoXiangMuHeXiaoJiLu, ZhiLiaoXiangMuHeXiaoJiLuAdmin)
    