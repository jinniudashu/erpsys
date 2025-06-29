# Generated by Django 4.2.7 on 2025-03-17 03:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import kernel.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ERPSysRegistry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('sys_registry', models.JSONField(blank=True, null=True, verbose_name='系统注册表')),
            ],
            options={
                'verbose_name': '系统注册表',
                'verbose_name_plural': '系统注册表',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='描述表达式')),
                ('expression', models.CharField(blank=True, max_length=255, null=True, verbose_name='表达式')),
                ('parameters', models.JSONField(blank=True, null=True, verbose_name='事件参数')),
            ],
            options={
                'verbose_name': '事件',
                'verbose_name_plural': '事件',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('is_list', models.BooleanField(default=False, verbose_name='列表')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='配置')),
            ],
            options={
                'verbose_name': '表单',
                'verbose_name_plural': '表单',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('sys_call', models.CharField(max_length=255, verbose_name='系统调用')),
                ('parameters', models.JSONField(blank=True, null=True, verbose_name='参数')),
            ],
            options={
                'verbose_name': '系统指令',
                'verbose_name_plural': '系统指令',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('active', models.BooleanField(default=False, verbose_name='启用')),
                ('context', models.JSONField(blank=True, null=True, verbose_name='上下文')),
            ],
            options={
                'verbose_name': '人员',
                'verbose_name_plural': '人员',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
            ],
            options={
                'verbose_name': '组织',
                'verbose_name_plural': '组织',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
            ],
            options={
                'verbose_name': '资源',
                'verbose_name_plural': '资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ResourceRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('resource_type', models.CharField(max_length=50, verbose_name='资源类型')),
                ('capacity', models.PositiveIntegerField(default=1, verbose_name='容量')),
            ],
            options={
                'verbose_name': '资源需求',
                'verbose_name_plural': '资源需求',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ResourceStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('capacity', models.PositiveIntegerField(default=1, verbose_name='容量')),
                ('current_usage', models.PositiveIntegerField(default=0, verbose_name='当前使用量')),
                ('busy_until', models.DateTimeField(blank=True, null=True, verbose_name='忙碌到期时间')),
            ],
            options={
                'verbose_name': '资源状态',
                'verbose_name_plural': '资源状态',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('manual_start', models.BooleanField(default=False, verbose_name='手动启动')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='配置')),
                ('serve_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_type_served', to='contenttypes.contenttype', verbose_name='服务对象类型')),
            ],
            options={
                'verbose_name': '服务',
                'verbose_name_plural': '服务',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='SysParams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='配置')),
                ('expires_in', models.PositiveIntegerField(default=8, verbose_name='过期时间')),
            ],
            options={
                'verbose_name': '系统参数',
                'verbose_name_plural': '系统参数',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('config', models.JSONField(blank=True, null=True, verbose_name='配置')),
            ],
            options={
                'verbose_name': '工单',
                'verbose_name_plural': '工单',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ServiceRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('order', models.SmallIntegerField(default=0, verbose_name='顺序')),
                ('entity_object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='实体ID')),
                ('parameter_values', models.JSONField(blank=True, null=True, verbose_name='参数值')),
                ('entity_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kernel_service_rule', to='contenttypes.contenttype', verbose_name='实体类型')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.event', verbose_name='事件')),
                ('operand_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ruled_as_next_service', to='kernel.service', verbose_name='后续服务')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.service', verbose_name='服务')),
                ('system_instruction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.instruction', verbose_name='系统指令')),
                ('target_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services_belong_to', to='kernel.service', verbose_name='隶属服务')),
            ],
            options={
                'verbose_name': '服务规则',
                'verbose_name_plural': '服务规则',
                'ordering': ['target_service', 'order', 'service', 'event', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('services', models.ManyToManyField(blank=True, related_name='roles', to='kernel.service', verbose_name='服务项目')),
            ],
            options={
                'verbose_name': '角色',
                'verbose_name_plural': '角色',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ResourceCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('start_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='结束时间')),
                ('resource', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.resourcerequirement', verbose_name='资源')),
            ],
            options={
                'verbose_name': '资源日历',
                'verbose_name_plural': '资源日历',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('pid', kernel.models.PidField(default=0, verbose_name='进程id')),
                ('entity_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('state', models.CharField(choices=[('NEW', 1), ('READY', 2), ('RUNNING', 3), ('WAITING', 4), ('TERMINATED', 5), ('SUSPENDED', 6), ('ERROR', 7)], default='NEW', max_length=50, verbose_name='状态')),
                ('priority', models.PositiveSmallIntegerField(default=0, verbose_name='优先级')),
                ('scheduled_time', models.DateTimeField(blank=True, null=True, verbose_name='计划时间')),
                ('time_window', models.DurationField(blank=True, null=True, verbose_name='时间窗')),
                ('form_object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='表单ID')),
                ('form_url', models.CharField(blank=True, max_length=512, null=True, verbose_name='表单路径')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('program_entrypoint', models.CharField(blank=True, max_length=255, null=True, verbose_name='程序入口')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='as_creator_process', to='kernel.operator', verbose_name='创建者')),
                ('entity_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='as_entity_process', to='contenttypes.contenttype')),
                ('form_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='表单类型')),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='as_operator_process', to='kernel.operator', verbose_name='操作员')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_instances', to='kernel.process', verbose_name='父进程')),
                ('previous', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next_instances', to='kernel.process', verbose_name='前一个进程')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.service', verbose_name='服务')),
                ('work_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.workorder', verbose_name='工单')),
            ],
            options={
                'verbose_name': '进程',
                'verbose_name_plural': '进程',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='operator',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.organization', verbose_name='组织'),
        ),
        migrations.AddField(
            model_name='operator',
            name='related_staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='kernel.operator', verbose_name='关系人'),
        ),
        migrations.AddField(
            model_name='operator',
            name='role',
            field=models.ManyToManyField(blank=True, to='kernel.role', verbose_name='角色'),
        ),
        migrations.AddField(
            model_name='operator',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='operator', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.CreateModel(
            name='ProcessContextSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('version', models.PositiveIntegerField(default=1, verbose_name='版本号')),
                ('context_data', models.JSONField(blank=True, null=True, verbose_name='上下文数据')),
                ('context_hash', models.CharField(blank=True, max_length=64, null=True, verbose_name='上下文哈希')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kernel.process', verbose_name='进程')),
            ],
            options={
                'verbose_name': '进程上下文快照',
                'verbose_name_plural': '进程上下文快照',
                'ordering': ['-version'],
                'unique_together': {('process', 'version')},
            },
        ),
    ]
