from django.db import models
from django.contrib.auth.models import User

from design.models import ERPSysBase

class GangWei(ERPSysBase):

    class Meta:
        verbose_name = "Dict-岗位"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class FuWuLeiBie(ERPSysBase):

    class Meta:
        verbose_name = "Dict-服务类别"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class RuChuKuCaoZuo(ERPSysBase):

    class Meta:
        verbose_name = "Dict-入出库操作"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Operator(ERPSysBase):
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    xi_tong_yong_hu = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统用户')
    gang_wei = models.ForeignKey(GangWei, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='岗位')

    class Meta:
        verbose_name = "Reserved-人员"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Material(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-物料"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Equipment(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-设备"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Device(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-工具"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Capital(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-资金"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Space(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-空间"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Information(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-信息"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class WorkOrder(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-工单"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Form(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")

    class Meta:
        verbose_name = "Reserved-表单"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Knowledge(ERPSysBase):
    zhi_shi_wen_jian = models.FileField(blank=True, null=True, verbose_name='知识文件')
    zhi_shi_wen_ben = models.TextField(blank=True, null=True, verbose_name='知识文本')

    class Meta:
        verbose_name = "Reserved-知识"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class WuLiaoTaiZhang(ERPSysBase):
    you_xiao_qi = models.DateField(blank=True, null=True, verbose_name='有效期')
    ri_qi = models.DateTimeField(blank=True, null=True, verbose_name='入出库时间')
    shu_liang = models.IntegerField(blank=True, null=True, verbose_name='数量')
    ling_yong_ren = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='ling_yong_ren', blank=True, null=True, verbose_name='领用人')
    shi_yong_ren = models.ManyToManyField(Operator, related_name='shi_yong_ren', blank=True, verbose_name='使用人')
    ru_chu_ku_cao_zuo = models.ForeignKey(RuChuKuCaoZuo, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='入出库操作')

    class Meta:
        verbose_name = "物料台账"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Service(ERPSysBase):
    config = models.JSONField(blank=True, null=True, verbose_name="配置")

    class Meta:
        verbose_name = "Reserved-服务"
        verbose_name_plural = verbose_name
        ordering = ["id"]

CLASS_MAPPING = {
    "GangWei": GangWei,
    "FuWuLeiBie": FuWuLeiBie,
    "RuChuKuCaoZuo": RuChuKuCaoZuo,
    "Operator": Operator,
    "Material": Material,
    "Equipment": Equipment,
    "Device": Device,
    "Capital": Capital,
    "Space": Space,
    "Information": Information,
    "WorkOrder": WorkOrder,
    "Form": Form,
    "Knowledge": Knowledge,
    "WuLiaoTaiZhang": WuLiaoTaiZhang,
    "Service": Service,
}

