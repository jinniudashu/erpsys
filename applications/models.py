from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import uuid
import re
from pypinyin import Style, lazy_pinyin

from kernel.models import Operator, Process, Service, Customer, Organization

class FuWuLeiBie(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-服务类别"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class RuChuKuCaoZuo(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-入出库操作"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class KeHuLaiYuan(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-客户来源"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class HunFou(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-婚否"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ZhengZhuang(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-症状"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ZhenDuan(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-诊断"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Material(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    gui_ge = models.CharField(max_length=100, blank=True, null=True, verbose_name='规格')
    zui_xiao_ku_cun = models.IntegerField(blank=True, null=True, verbose_name='最小库存')
    jia_ge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='价格')

    class Meta:
        verbose_name = "Dict-物料"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Equipment(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-设备"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Device(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-工具"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Capital(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-资金"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Knowledge(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    zhi_shi_wen_ben = models.TextField(blank=True, null=True, verbose_name='知识文本')
    zhi_shi_wen_jian = models.FileField(blank=True, null=True, verbose_name='知识文件')

    class Meta:
        verbose_name = "Dict-知识"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Profile(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_Profile', blank=True, null=True, verbose_name="客户")
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    xing_bie = models.CharField(max_length=100, blank=True, null=True, verbose_name='性别')
    nian_ling = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    dian_hua = models.CharField(max_length=100, blank=True, null=True, verbose_name='电话')
    zhi_ye = models.CharField(max_length=100, blank=True, null=True, verbose_name='职业')
    chang_zhu_di = models.CharField(max_length=100, blank=True, null=True, verbose_name='常驻地')
    bing_li_hao = models.CharField(max_length=100, blank=True, null=True, verbose_name='病历号')
    ke_hu_lai_yuan = models.ForeignKey(KeHuLaiYuan, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='客户来源')
    lai_yuan_shuo_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='来源说明')
    bei_zhu = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = "Dict-个人资料"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class WuLiaoTaiZhang(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Material, on_delete=models.SET_NULL, related_name='property_set_wu_liao_tai_zhang', blank=True, null=True, verbose_name="物料")
    ri_qi = models.DateTimeField(blank=True, null=True, verbose_name='入出库时间')
    ru_chu_ku_cao_zuo = models.ForeignKey(RuChuKuCaoZuo, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='入出库操作')
    shu_liang = models.IntegerField(blank=True, null=True, verbose_name='数量')
    you_xiao_qi = models.DateField(blank=True, null=True, verbose_name='有效期')
    shi_yong_ren = models.ManyToManyField(Operator, related_name='shi_yong_ren', blank=True, verbose_name='使用人')
    ling_yong_ren = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, related_name='ling_yong_ren_wu_liao_tai_zhang', verbose_name='领用人')
    qi_chu = models.IntegerField(blank=True, null=True, verbose_name='期初')
    qi_mo = models.IntegerField(blank=True, null=True, verbose_name='期末')

    class Meta:
        verbose_name = "物料台账"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class YuYueJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_yu_yue_ji_lu', blank=True, null=True, verbose_name="客户")
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    dian_hua = models.CharField(max_length=100, blank=True, null=True, verbose_name='电话')
    nian_ling = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    chang_zhu_di = models.CharField(max_length=100, blank=True, null=True, verbose_name='常驻地')
    shou_zhen = models.BooleanField(default=False, verbose_name='首诊')
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name='预约时间')
    fu_wu_xiang_mu = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='服务项目')
    yu_yue_yi_sheng = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='预约医生')
    que_ren_yu_yue = models.BooleanField(default=False, verbose_name='确认预约')
    ke_hu_yi_dao_dian = models.BooleanField(default=False, verbose_name='客户已到店')
    ke_hu_lai_yuan = models.ForeignKey(KeHuLaiYuan, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='客户来源')
    lai_yuan_shuo_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='来源说明')
    bei_zhu = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        verbose_name = "预约记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class JianKangDiaoChaJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_jian_kang_diao_cha_ji_lu', blank=True, null=True, verbose_name="客户")
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    xing_bie = models.CharField(max_length=100, blank=True, null=True, verbose_name='性别')
    chu_sheng_ri_qi = models.DateField(blank=True, null=True, verbose_name='出生日期')
    hun_fou = models.ForeignKey(HunFou, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='婚否')
    dian_hua = models.CharField(max_length=100, blank=True, null=True, verbose_name='电话')
    chang_zhu_di = models.CharField(max_length=100, blank=True, null=True, verbose_name='常驻地')

    class Meta:
        verbose_name = "健康调查记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ZhuanKePingGuJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_zhuan_ke_ping_gu_ji_lu', blank=True, null=True, verbose_name="客户")
    zhu_su = models.TextField(blank=True, null=True, verbose_name='主诉')

    class Meta:
        verbose_name = "专科评估记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ZhenDuanJiChuLiYiJianJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_zhen_duan_ji_chu_li_yi_jian_ji_lu', blank=True, null=True, verbose_name="客户")
    zheng_zhuang = models.ManyToManyField(ZhengZhuang, related_name='zheng_zhuang', blank=True, verbose_name='症状')
    zhen_duan = models.ManyToManyField(ZhenDuan, related_name='zhen_duan', blank=True, verbose_name='诊断')
    jian_yi_fang_an = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='建议方案')

    class Meta:
        verbose_name = "诊断及处理意见记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class RouDuSuZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_rou_du_su_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "肉毒素治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ChaoShengPaoZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_chao_sheng_pao_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "超声炮治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class HuangJinWeiZhenZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_huang_jin_wei_zhen_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "黄金微针治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class DiaoQZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_diao_Q_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "调Q治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class GuangZiZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_guang_zi_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "光子治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class GuoSuanZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_guo_suan_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "果酸治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ShuiGuangZhenZhiLiaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_shui_guang_zhen_zhi_liao_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "水光针治疗记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ChongZhiJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_chong_zhi_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "充值记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class XiaoFeiJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_xiao_fei_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "消费记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class SuiFangJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_sui_fang_ji_lu', blank=True, null=True, verbose_name="客户")

    class Meta:
        verbose_name = "随访记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class FaSongZhiLiaoZhuYiShiXiangJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_fa_song_zhi_liao_zhu_yi_shi_xiang_ji_lu', blank=True, null=True, verbose_name="客户")
    fu_wu_xiang_mu = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='服务项目')
    yi_fa_song = models.BooleanField(default=False, verbose_name='已发送')

    class Meta:
        verbose_name = "发送治疗注意事项记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class QianShuZhiQingTongYiShuJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_qian_shu_zhi_qing_tong_yi_shu_ji_lu', blank=True, null=True, verbose_name="客户")
    fu_wu_xiang_mu = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='服务项目')
    yi_qian_shu = models.CharField(max_length=100, blank=True, null=True, verbose_name='已签署')

    class Meta:
        verbose_name = "签署知情同意书记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class DengLuQianDaoJiLu(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    master = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='property_set_deng_lu_qian_dao_ji_lu', blank=True, null=True, verbose_name="客户")
    qian_dao = models.BooleanField(default=False, verbose_name='签到')

    class Meta:
        verbose_name = "登录签到记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label if self.label else ''

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
CLASS_MAPPING = {
    "FuWuLeiBie": FuWuLeiBie,
    "RuChuKuCaoZuo": RuChuKuCaoZuo,
    "KeHuLaiYuan": KeHuLaiYuan,
    "HunFou": HunFou,
    "ZhengZhuang": ZhengZhuang,
    "ZhenDuan": ZhenDuan,
    "Material": Material,
    "Equipment": Equipment,
    "Device": Device,
    "Capital": Capital,
    "Knowledge": Knowledge,
    "Profile": Profile,
    "WuLiaoTaiZhang": WuLiaoTaiZhang,
    "YuYueJiLu": YuYueJiLu,
    "JianKangDiaoChaJiLu": JianKangDiaoChaJiLu,
    "ZhuanKePingGuJiLu": ZhuanKePingGuJiLu,
    "ZhenDuanJiChuLiYiJianJiLu": ZhenDuanJiChuLiYiJianJiLu,
    "RouDuSuZhiLiaoJiLu": RouDuSuZhiLiaoJiLu,
    "ChaoShengPaoZhiLiaoJiLu": ChaoShengPaoZhiLiaoJiLu,
    "HuangJinWeiZhenZhiLiaoJiLu": HuangJinWeiZhenZhiLiaoJiLu,
    "DiaoQZhiLiaoJiLu": DiaoQZhiLiaoJiLu,
    "GuangZiZhiLiaoJiLu": GuangZiZhiLiaoJiLu,
    "GuoSuanZhiLiaoJiLu": GuoSuanZhiLiaoJiLu,
    "ShuiGuangZhenZhiLiaoJiLu": ShuiGuangZhenZhiLiaoJiLu,
    "ChongZhiJiLu": ChongZhiJiLu,
    "XiaoFeiJiLu": XiaoFeiJiLu,
    "SuiFangJiLu": SuiFangJiLu,
    "FaSongZhiLiaoZhuYiShiXiangJiLu": FaSongZhiLiaoZhuYiShiXiangJiLu,
    "QianShuZhiQingTongYiShuJiLu": QianShuZhiQingTongYiShuJiLu,
    "DengLuQianDaoJiLu": DengLuQianDaoJiLu,
}

