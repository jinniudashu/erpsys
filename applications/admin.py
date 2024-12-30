from django.contrib import admin

from kernel.admin import applications_site, ErpFormAdmin, hide_fields
from .models import *


@admin.register(FuWuLeiBie)
class FuWuLeiBieAdmin(ErpFormAdmin):
    list_display = [field.name for field in FuWuLeiBie._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(FuWuLeiBie, FuWuLeiBieAdmin)
    
@admin.register(RuChuKuCaoZuo)
class RuChuKuCaoZuoAdmin(ErpFormAdmin):
    list_display = [field.name for field in RuChuKuCaoZuo._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(RuChuKuCaoZuo, RuChuKuCaoZuoAdmin)
    
@admin.register(KeHuLaiYuan)
class KeHuLaiYuanAdmin(ErpFormAdmin):
    list_display = [field.name for field in KeHuLaiYuan._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(KeHuLaiYuan, KeHuLaiYuanAdmin)
    
@admin.register(HunFou)
class HunFouAdmin(ErpFormAdmin):
    list_display = [field.name for field in HunFou._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(HunFou, HunFouAdmin)
    
@admin.register(ZhengZhuang)
class ZhengZhuangAdmin(ErpFormAdmin):
    list_display = [field.name for field in ZhengZhuang._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhengZhuang, ZhengZhuangAdmin)
    
@admin.register(ZhenDuan)
class ZhenDuanAdmin(ErpFormAdmin):
    list_display = [field.name for field in ZhenDuan._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhenDuan, ZhenDuanAdmin)
    
@admin.register(ShouFeiLeiXing)
class ShouFeiLeiXingAdmin(ErpFormAdmin):
    list_display = [field.name for field in ShouFeiLeiXing._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ShouFeiLeiXing, ShouFeiLeiXingAdmin)
    
@admin.register(Material)
class MaterialAdmin(ErpFormAdmin):
    list_display = [field.name for field in Material._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Material, MaterialAdmin)
    
@admin.register(Equipment)
class EquipmentAdmin(ErpFormAdmin):
    list_display = [field.name for field in Equipment._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Equipment, EquipmentAdmin)
    
@admin.register(Device)
class DeviceAdmin(ErpFormAdmin):
    list_display = [field.name for field in Device._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Device, DeviceAdmin)
    
@admin.register(Capital)
class CapitalAdmin(ErpFormAdmin):
    list_display = [field.name for field in Capital._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Capital, CapitalAdmin)
    
@admin.register(Knowledge)
class KnowledgeAdmin(ErpFormAdmin):
    list_display = [field.name for field in Knowledge._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Knowledge, KnowledgeAdmin)
    
@admin.register(Profile)
class ProfileAdmin(ErpFormAdmin):
    list_display = [field.name for field in Profile._meta.fields]
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(Profile, ProfileAdmin)
    
@admin.register(WuLiaoTaiZhang)
class WuLiaoTaiZhangAdmin(ErpFormAdmin):
    list_display = [field.name for field in WuLiaoTaiZhang._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(WuLiaoTaiZhang, WuLiaoTaiZhangAdmin)
    
@admin.register(YuYueJiLu)
class YuYueJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in YuYueJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(YuYueJiLu, YuYueJiLuAdmin)
    
@admin.register(JianKangDiaoChaJiLu)
class JianKangDiaoChaJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in JianKangDiaoChaJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(JianKangDiaoChaJiLu, JianKangDiaoChaJiLuAdmin)
    
@admin.register(ZhuanKePingGuJiLu)
class ZhuanKePingGuJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ZhuanKePingGuJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhuanKePingGuJiLu, ZhuanKePingGuJiLuAdmin)
    
@admin.register(ZhenDuanJiChuLiYiJianJiLu)
class ZhenDuanJiChuLiYiJianJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ZhenDuanJiChuLiYiJianJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhenDuanJiChuLiYiJianJiLu, ZhenDuanJiChuLiYiJianJiLuAdmin)
    
@admin.register(RouDuSuZhiLiaoJiLu)
class RouDuSuZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in RouDuSuZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(RouDuSuZhiLiaoJiLu, RouDuSuZhiLiaoJiLuAdmin)
    
@admin.register(ChaoShengPaoZhiLiaoJiLu)
class ChaoShengPaoZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ChaoShengPaoZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ChaoShengPaoZhiLiaoJiLu, ChaoShengPaoZhiLiaoJiLuAdmin)
    
@admin.register(HuangJinWeiZhenZhiLiaoJiLu)
class HuangJinWeiZhenZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in HuangJinWeiZhenZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(HuangJinWeiZhenZhiLiaoJiLu, HuangJinWeiZhenZhiLiaoJiLuAdmin)
    
@admin.register(DiaoQZhiLiaoJiLu)
class DiaoQZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in DiaoQZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(DiaoQZhiLiaoJiLu, DiaoQZhiLiaoJiLuAdmin)
    
@admin.register(GuangZiZhiLiaoJiLu)
class GuangZiZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in GuangZiZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(GuangZiZhiLiaoJiLu, GuangZiZhiLiaoJiLuAdmin)
    
@admin.register(GuoSuanZhiLiaoJiLu)
class GuoSuanZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in GuoSuanZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(GuoSuanZhiLiaoJiLu, GuoSuanZhiLiaoJiLuAdmin)
    
@admin.register(ShuiGuangZhenZhiLiaoJiLu)
class ShuiGuangZhenZhiLiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ShuiGuangZhenZhiLiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ShuiGuangZhenZhiLiaoJiLu, ShuiGuangZhenZhiLiaoJiLuAdmin)
    
@admin.register(ChongZhiJiLu)
class ChongZhiJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ChongZhiJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ChongZhiJiLu, ChongZhiJiLuAdmin)
    
@admin.register(XiaoFeiJiLu)
class XiaoFeiJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in XiaoFeiJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(XiaoFeiJiLu, XiaoFeiJiLuAdmin)
    
@admin.register(SuiFangJiLu)
class SuiFangJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in SuiFangJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(SuiFangJiLu, SuiFangJiLuAdmin)
    
@admin.register(FaSongZhiLiaoZhuYiShiXiangJiLu)
class FaSongZhiLiaoZhuYiShiXiangJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in FaSongZhiLiaoZhuYiShiXiangJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(FaSongZhiLiaoZhuYiShiXiangJiLu, FaSongZhiLiaoZhuYiShiXiangJiLuAdmin)
    
@admin.register(QianShuZhiQingTongYiShuJiLu)
class QianShuZhiQingTongYiShuJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in QianShuZhiQingTongYiShuJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(QianShuZhiQingTongYiShuJiLu, QianShuZhiQingTongYiShuJiLuAdmin)
    
@admin.register(DengLuQianDaoJiLu)
class DengLuQianDaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in DengLuQianDaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(DengLuQianDaoJiLu, DengLuQianDaoJiLuAdmin)
    
@admin.register(YuYueTiXingJiLu)
class YuYueTiXingJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in YuYueTiXingJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(YuYueTiXingJiLu, YuYueTiXingJiLuAdmin)
    
@admin.register(ShouFeiJiLu)
class ShouFeiJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ShouFeiJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ShouFeiJiLu, ShouFeiJiLuAdmin)
    
@admin.register(ZhiLiaoXiangMuHeXiaoJiLu)
class ZhiLiaoXiangMuHeXiaoJiLuAdmin(ErpFormAdmin):
    list_display = [field.name for field in ZhiLiaoXiangMuHeXiaoJiLu._meta.fields]
    hide_fields(list_display)
    list_display_links = list_display
    search_fields = ['label', 'name', 'pym']
    list_filter = list_display
applications_site.register(ZhiLiaoXiangMuHeXiaoJiLu, ZhiLiaoXiangMuHeXiaoJiLuAdmin)
    