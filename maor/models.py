from django.db import models
from django.contrib.auth.models import User

class XiTongLeiXing(models.Model):

    class Meta:
        verbose_name = "系统类型"
        verbose_name_plural = verbose_name
        ordering = ['id']

class GangWei(models.Model):
    gang_wei_ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='岗位名称')

    class Meta:
        verbose_name = "岗位"
        verbose_name_plural = verbose_name
        ordering = ['id']

class FuWuLeiBie(models.Model):
    zhi = models.CharField(max_length=100, blank=True, null=True, verbose_name='值')

    class Meta:
        verbose_name = "服务类别"
        verbose_name_plural = verbose_name
        ordering = ['id']

class RuChuKuCaoZuo(models.Model):

    class Meta:
        verbose_name = "入出库操作"
        verbose_name_plural = verbose_name
        ordering = ['id']

class RenYuan(models.Model):
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')

    class Meta:
        verbose_name = "人员"
        verbose_name_plural = verbose_name
        ordering = ['id']

class WuLiao(models.Model):
    ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "物料"
        verbose_name_plural = verbose_name
        ordering = ['id']

class SheBei(models.Model):
    ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = verbose_name
        ordering = ['id']

class GongJu(models.Model):
    ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "工具"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ZiJin(models.Model):
    ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "资金"
        verbose_name_plural = verbose_name
        ordering = ['id']

class KongJian(models.Model):
    ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "空间"
        verbose_name_plural = verbose_name
        ordering = ['id']

class XinXi(models.Model):
    ming_cheng = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "信息"
        verbose_name_plural = verbose_name
        ordering = ['id']

class FuWuXiangMu(models.Model):

    class Meta:
        verbose_name = "服务项目"
        verbose_name_plural = verbose_name
        ordering = ['id']

class CaoZuoYuan(models.Model):
    xi_tong_yong_hu = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='系统用户')

    class Meta:
        verbose_name = "操作员"
        verbose_name_plural = verbose_name
        ordering = ['id']

class GongDan(models.Model):

    class Meta:
        verbose_name = "工单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ZhenShi(models.Model):

    class Meta:
        verbose_name = "诊室"
        verbose_name_plural = verbose_name
        ordering = ['id']

class WuLiaoTaiZhang(models.Model):
    wu_liao = models.ForeignKey(WuLiao, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='物料')
    ru_chu_ku_cao_zuo = models.ForeignKey(RuChuKuCaoZuo, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='入出库操作')
    shu_liang = models.IntegerField(blank=True, null=True, verbose_name='数量')

    class Meta:
        verbose_name = "物料台账"
        verbose_name_plural = verbose_name
        ordering = ['id']

class KeHu(models.Model):
    bing_li_hao = models.CharField(max_length=100, blank=True, null=True, verbose_name='病历号')

    class Meta:
        verbose_name = "客户"
        verbose_name_plural = verbose_name
        ordering = ['id']

class ZhiYuan(models.Model):

    class Meta:
        verbose_name = "职员"
        verbose_name_plural = verbose_name
        ordering = ['id']

class YiSheng(models.Model):

    class Meta:
        verbose_name = "医生"
        verbose_name_plural = verbose_name
        ordering = ['id']

class HuShi(models.Model):

    class Meta:
        verbose_name = "护士"
        verbose_name_plural = verbose_name
        ordering = ['id']

class KeFu(models.Model):

    class Meta:
        verbose_name = "客服"
        verbose_name_plural = verbose_name
        ordering = ['id']

class SuiFangJiLuDan(models.Model):

    class Meta:
        verbose_name = "随访记录单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class WuLiaoChuKuDan(models.Model):
    wu_liao_ming_xi_ji_lu = models.ForeignKey(WuLiaoTaiZhang, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='物料台账')

    class Meta:
        verbose_name = "物料出库单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class WuLiaoRuKuDan(models.Model):
    wu_liao_ming_xi_ji_lu = models.ForeignKey(WuLiaoTaiZhang, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='物料台账')

    class Meta:
        verbose_name = "物料入库单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class YuYueJiLuDan(models.Model):

    class Meta:
        verbose_name = "预约记录单"
        verbose_name_plural = verbose_name
        ordering = ['id']

class RouDuSuZhiLiaoJiLuDan(models.Model):

    class Meta:
        verbose_name = "肉毒素治疗记录单"
        verbose_name_plural = verbose_name
        ordering = ['id']

