from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

import uuid
import re
from pypinyin import Style, lazy_pinyin

from kernel.models import Operator, Process

class FuWuLeiBie(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-服务类别"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-入出库操作"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-客户来源"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class ShiFouDaoDian(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Dict-是否到店"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    gui_ge = models.CharField(max_length=100, blank=True, null=True, verbose_name='规格')
    zui_xiao_ku_cun = models.IntegerField(blank=True, null=True, verbose_name='最小库存')
    jia_ge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='价格')

    class Meta:
        verbose_name = "Reserved-物料"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Reserved-设备"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Reserved-工具"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Reserved-资金"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.erpsys_id is None:
            self.erpsys_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^\w一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            self.name = "_".join(lazy_pinyin(label[:10]))
            self.label = label
        super().save(*args, **kwargs)
    
class Space(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    erpsys_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "Reserved-空间"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    zhi_shi_wen_ben = models.TextField(blank=True, null=True, verbose_name='知识文本')
    zhi_shi_wen_jian = models.FileField(blank=True, null=True, verbose_name='知识文件')

    class Meta:
        verbose_name = "Reserved-知识"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="人员")
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
        verbose_name = "Reserved-个人资料"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    ri_qi = models.DateTimeField(blank=True, null=True, verbose_name='入出库时间')
    ru_chu_ku_cao_zuo = models.ForeignKey(RuChuKuCaoZuo, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='入出库操作')
    shu_liang = models.IntegerField(blank=True, null=True, verbose_name='数量')
    you_xiao_qi = models.DateField(blank=True, null=True, verbose_name='有效期')
    shi_yong_ren = models.ManyToManyField(Operator, related_name='shi_yong_ren', blank=True, verbose_name='使用人')
    ling_yong_ren = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='ling_yong_ren', blank=True, null=True, verbose_name='领用人')
    qi_chu = models.IntegerField(blank=True, null=True, verbose_name='期初')
    qi_mo = models.IntegerField(blank=True, null=True, verbose_name='期末')

    class Meta:
        verbose_name = "物料台账"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, related_name='%(class)s_attributes', null=True, blank=True, verbose_name="隶属主体")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="隶属id")
    content_object = GenericForeignKey('content_type', 'object_id')
    pid = models.ForeignKey(Process, on_delete=models.SET_NULL, blank=True, null=True, related_name='%(class)s_pid', verbose_name="作业进程")
    created_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间")
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    dian_hua = models.CharField(max_length=100, blank=True, null=True, verbose_name='电话')
    nian_ling = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    chang_zhu_di = models.CharField(max_length=100, blank=True, null=True, verbose_name='常驻地')
    shou_zhen = models.BooleanField(default=False, verbose_name='首诊')
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name='预约时间')
    ke_hu_lai_yuan = models.ForeignKey(KeHuLaiYuan, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='客户来源')
    lai_yuan_shuo_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='来源说明')
    shi_fou_dao_dian = models.ForeignKey(ShiFouDaoDian, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='是否到店')
    bei_zhu = models.TextField(blank=True, null=True, verbose_name='备注')
    cao_zuo_yuan = models.ForeignKey(Operator, on_delete=models.SET_NULL, related_name='cao_zuo_yuan', blank=True, null=True, verbose_name='操作员')
    created_time = models.DateTimeField(blank=True, null=True, verbose_name='作业时间')

    class Meta:
        verbose_name = "预约记录"
        verbose_name_plural = verbose_name
        ordering = ["id"]
    
    def __str__(self):
        return self.label

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
    "ShiFouDaoDian": ShiFouDaoDian,
    "Material": Material,
    "Equipment": Equipment,
    "Device": Device,
    "Capital": Capital,
    "Space": Space,
    "Knowledge": Knowledge,
    "Profile": Profile,
    "WuLiaoTaiZhang": WuLiaoTaiZhang,
    "YuYueJiLu": YuYueJiLu,
}

