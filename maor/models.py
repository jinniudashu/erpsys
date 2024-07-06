from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

from design.models import ERPSysBase

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

class Role(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-角色"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Operator(ERPSysBase):
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    bing_li_hao = models.CharField(max_length=100, blank=True, null=True, verbose_name='病历号')
    xing_bie = models.CharField(max_length=100, blank=True, null=True, verbose_name='性别')
    chu_zhen_ri_qi = models.DateField(blank=True, null=True, verbose_name='初诊日期')
    nian_ling = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    xi_tong_yong_hu = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统用户')

    class Meta:
        verbose_name = "Reserved-人员"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class Material(ERPSysBase):
    gui_ge = models.CharField(max_length=100, blank=True, null=True, verbose_name='规格')
    jia_ge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='价格')
    zui_xiao_ku_cun = models.IntegerField(blank=True, null=True, verbose_name='最小库存')

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
    qi_chu = models.IntegerField(blank=True, null=True, verbose_name='期初')
    qi_mo = models.IntegerField(blank=True, null=True, verbose_name='期末')
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

class Event(ERPSysBase):

    class Meta:
        verbose_name = "Reserved-事件"
        verbose_name_plural = verbose_name
        ordering = ["id"]

CLASS_MAPPING = {
    "FuWuLeiBie": FuWuLeiBie,
    "RuChuKuCaoZuo": RuChuKuCaoZuo,
    "Role": Role,
    "Operator": Operator,
    "Material": Material,
    "Equipment": Equipment,
    "Device": Device,
    "Capital": Capital,
    "Space": Space,
    "Information": Information,
    "Form": Form,
    "Knowledge": Knowledge,
    "WuLiaoTaiZhang": WuLiaoTaiZhang,
    "Service": Service,
    "Event": Event,
}

