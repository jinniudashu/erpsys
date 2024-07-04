from django.db import models
from django.contrib.auth.models import User
import uuid
import re
from pypinyin import Style, lazy_pinyin

from design.models import Service

class MaorBase(models.Model):
    label = models.CharField(max_length=255, null=True, verbose_name="中文名称")
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="名称")
    pym = models.CharField(max_length=255, blank=True, null=True, verbose_name="拼音码")
    maor_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="ERPSysID")

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.label)

    def save(self, *args, **kwargs):
        if self.maor_id is None:
            self.maor_id = uuid.uuid1()
        if self.label and self.name is None:
            label = re.sub(r'[^一-龥]', '', self.label)
            self.pym = ''.join(lazy_pinyin(label, style=Style.FIRST_LETTER))
            # 使用正则表达式过滤掉label非汉字内容, 截取到8个汉字以内
            self.name = "_".join(lazy_pinyin(label[:8]))
            self.label = label
        super().save(*args, **kwargs)

class GangWei(MaorBase):

    class Meta:
        verbose_name = "Dict-岗位"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class FuWuLeiBie(MaorBase):

    class Meta:
        verbose_name = "Dict-服务类别"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class RuChuKuCaoZuo(MaorBase):

    class Meta:
        verbose_name = "Dict-入出库操作"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class RenYuan(MaorBase):
    xing_ming = models.CharField(max_length=100, blank=True, null=True, verbose_name='姓名')
    gang_wei = models.ForeignKey(GangWei, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='岗位')
    xi_tong_yong_hu = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='系统用户')

    class Meta:
        verbose_name = "人员"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class WuLiao(MaorBase):

    class Meta:
        verbose_name = "物料"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class SheBei(MaorBase):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class GongJu(MaorBase):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "工具"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class ZiJin(MaorBase):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "资金"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class KongJian(MaorBase):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "空间"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class XinXi(MaorBase):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='名称')

    class Meta:
        verbose_name = "信息"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class WuLiaoTaiZhang(MaorBase):
    wu_liao = models.ForeignKey(WuLiao, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='物料')
    ru_chu_ku_cao_zuo = models.ForeignKey(RuChuKuCaoZuo, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='入出库操作')
    shu_liang = models.IntegerField(blank=True, null=True, verbose_name='数量')
    ri_qi = models.DateTimeField(blank=True, null=True, verbose_name='入出库时间')
    ling_yong_ren = models.ForeignKey(RenYuan, on_delete=models.SET_NULL, related_name='ling_yong_ren', blank=True, null=True, verbose_name='领用人')
    shi_yong_ren = models.ManyToManyField(RenYuan, related_name='shi_yong_ren', blank=True, verbose_name='使用人')
    you_xiao_qi = models.DateField(blank=True, null=True, verbose_name='有效期')

    class Meta:
        verbose_name = "物料台账"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class FuWu(MaorBase):
    gong_dan = models.ForeignKey(XinXi, on_delete=models.SET_NULL, related_name='gong_dan', blank=True, null=True, verbose_name='工单')

    class Meta:
        verbose_name = "服务"
        verbose_name_plural = verbose_name
        ordering = ["id"]

class_mappings = {
    "GangWei": GangWei,
    "FuWuLeiBie": FuWuLeiBie,
    "RuChuKuCaoZuo": RuChuKuCaoZuo,
    "RenYuan": RenYuan,
    "WuLiao": WuLiao,
    "SheBei": SheBei,
    "GongJu": GongJu,
    "ZiJin": ZiJin,
    "KongJian": KongJian,
    "XinXi": XinXi,
    "WuLiaoTaiZhang": WuLiaoTaiZhang,
    "FuWu": FuWu,
}

