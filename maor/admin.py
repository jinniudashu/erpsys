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


@admin.register(RenYuan)
class RenYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RenYuan._meta.fields]
    list_display_links = ['id']
maor_site.register(RenYuan, RenYuanAdmin)

@admin.register(WuLiao)
class WuLiaoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiao._meta.fields]
    list_display_links = ['id']
maor_site.register(WuLiao, WuLiaoAdmin)

@admin.register(SheBei)
class SheBeiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SheBei._meta.fields]
    list_display_links = ['id']
maor_site.register(SheBei, SheBeiAdmin)

@admin.register(GongJu)
class GongJuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GongJu._meta.fields]
    list_display_links = ['id']
maor_site.register(GongJu, GongJuAdmin)

@admin.register(ZiJin)
class ZiJinAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZiJin._meta.fields]
    list_display_links = ['id']
maor_site.register(ZiJin, ZiJinAdmin)

@admin.register(KongJian)
class KongJianAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KongJian._meta.fields]
    list_display_links = ['id']
maor_site.register(KongJian, KongJianAdmin)

@admin.register(XinXi)
class XinXiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in XinXi._meta.fields]
    list_display_links = ['id']
maor_site.register(XinXi, XinXiAdmin)

@admin.register(FuWuXiangMu)
class FuWuXiangMuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FuWuXiangMu._meta.fields]
    list_display_links = ['id']
maor_site.register(FuWuXiangMu, FuWuXiangMuAdmin)

@admin.register(CaoZuoYuan)
class CaoZuoYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CaoZuoYuan._meta.fields]
    list_display_links = ['id']
maor_site.register(CaoZuoYuan, CaoZuoYuanAdmin)

@admin.register(XiTongLeiXing)
class XiTongLeiXingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in XiTongLeiXing._meta.fields]
    list_display_links = ['id']
maor_site.register(XiTongLeiXing, XiTongLeiXingAdmin)

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

@admin.register(KeHu)
class KeHuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KeHu._meta.fields]
    list_display_links = ['id']
maor_site.register(KeHu, KeHuAdmin)

@admin.register(ZhiYuan)
class ZhiYuanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhiYuan._meta.fields]
    list_display_links = ['id']
maor_site.register(ZhiYuan, ZhiYuanAdmin)

@admin.register(GongDan)
class GongDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GongDan._meta.fields]
    list_display_links = ['id']
maor_site.register(GongDan, GongDanAdmin)

@admin.register(ZhenShi)
class ZhenShiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ZhenShi._meta.fields]
    list_display_links = ['id']
maor_site.register(ZhenShi, ZhenShiAdmin)

@admin.register(WuLiaoTaiZhang)
class WuLiaoTaiZhangAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoTaiZhang._meta.fields]
    list_display_links = ['id']
maor_site.register(WuLiaoTaiZhang, WuLiaoTaiZhangAdmin)

@admin.register(YiSheng)
class YiShengAdmin(admin.ModelAdmin):
    list_display = [field.name for field in YiSheng._meta.fields]
    list_display_links = ['id']
maor_site.register(YiSheng, YiShengAdmin)

@admin.register(HuShi)
class HuShiAdmin(admin.ModelAdmin):
    list_display = [field.name for field in HuShi._meta.fields]
    list_display_links = ['id']
maor_site.register(HuShi, HuShiAdmin)

@admin.register(KeFu)
class KeFuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in KeFu._meta.fields]
    list_display_links = ['id']
maor_site.register(KeFu, KeFuAdmin)

@admin.register(LingYongRen)
class LingYongRenAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LingYongRen._meta.fields]
    list_display_links = ['id']
maor_site.register(LingYongRen, LingYongRenAdmin)

@admin.register(ShiYongRen)
class ShiYongRenAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ShiYongRen._meta.fields]
    list_display_links = ['id']
maor_site.register(ShiYongRen, ShiYongRenAdmin)

@admin.register(SuiFangJiLuDan)
class SuiFangJiLuDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SuiFangJiLuDan._meta.fields]
    list_display_links = ['id']

@admin.register(WuLiaoChuKuDan)
class WuLiaoChuKuDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoChuKuDan._meta.fields]
    list_display_links = ['id']

@admin.register(WuLiaoRuKuDan)
class WuLiaoRuKuDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WuLiaoRuKuDan._meta.fields]
    list_display_links = ['id']

@admin.register(YuYueJiLuDan)
class YuYueJiLuDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in YuYueJiLuDan._meta.fields]
    list_display_links = ['id']

@admin.register(RouDuSuZhiLiaoJiLuDan)
class RouDuSuZhiLiaoJiLuDanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RouDuSuZhiLiaoJiLuDan._meta.fields]
    list_display_links = ['id']
