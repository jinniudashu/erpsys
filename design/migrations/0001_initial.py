# Generated by Django 4.2.7 on 2025-03-17 03:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Api',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('url', models.CharField(blank=True, max_length=255, null=True, verbose_name='URL')),
                ('request_method', models.CharField(blank=True, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')], default='POST', max_length=10, null=True, verbose_name='请求方法')),
                ('content_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='内容类型')),
                ('response_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='响应类型')),
                ('document_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='文档URL')),
            ],
            options={
                'verbose_name': '外部API',
                'verbose_name_plural': '外部API',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ApiFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('req_res', models.CharField(blank=True, choices=[('Request', '请求'), ('Response', '响应')], default='Response', max_length=50, null=True, verbose_name='请求/响应')),
                ('field_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='字段名称')),
                ('field_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='字段类型')),
                ('default_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='默认值')),
                ('api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.api', verbose_name='API')),
            ],
            options={
                'verbose_name': 'API字段',
                'verbose_name_plural': 'API字段',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Capital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
            ],
            options={
                'verbose_name': '资源-资金',
                'verbose_name_plural': '资源-资金',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CapitalRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('resource_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.capital', verbose_name='资源对象')),
            ],
            options={
                'verbose_name': '资金资源',
                'verbose_name_plural': '资金资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='DataItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('field_type', models.CharField(blank=True, choices=[('CharField', '单行文本'), ('IntegerField', '整数'), ('TypeField', '类型'), ('BooleanField', '是否'), ('User', '系统用户'), ('Reserved', '系统保留'), ('DecimalField', '固定精度小数'), ('TextField', '多行文本'), ('DateTimeField', '日期时间'), ('DateField', '日期'), ('TimeField', '时间'), ('JSONField', 'JSON'), ('FileField', '文件'), ('ComputedField', '计算字段'), ('Process', '进程')], default='CharField', max_length=50, null=True, verbose_name='数据类型')),
                ('sub_class', models.CharField(blank=True, max_length=255, null=True, verbose_name='子类')),
                ('implement_type', models.CharField(choices=[('Field', '字段'), ('Model', '数据表'), ('KernelModel', '系统表'), ('Log', '日志'), ('View', '视图'), ('MenuItem', '菜单项'), ('Program', '程序')], default='Field', max_length=50, verbose_name='实现类型')),
                ('dependency_order', models.PositiveSmallIntegerField(default=0, verbose_name='依赖顺序')),
                ('default_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='默认值')),
                ('is_multivalued', models.BooleanField(default=False, verbose_name='多值')),
                ('max_length', models.PositiveSmallIntegerField(blank=True, default=255, null=True, verbose_name='最大长度')),
                ('max_digits', models.PositiveSmallIntegerField(blank=True, default=10, null=True, verbose_name='最大位数')),
                ('decimal_places', models.PositiveSmallIntegerField(blank=True, default=2, null=True, verbose_name='小数位数')),
                ('computed_logic', models.TextField(blank=True, null=True, verbose_name='计算逻辑')),
                ('init_content', models.JSONField(blank=True, null=True, verbose_name='初始内容')),
                ('affiliated_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='property_set', to='design.dataitem', verbose_name='业务隶属')),
                ('business_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instances', to='design.dataitem', verbose_name='业务类型')),
            ],
            options={
                'verbose_name': '数据项',
                'verbose_name_plural': '数据项',
                'ordering': ['implement_type', 'dependency_order', 'field_type', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
            ],
            options={
                'verbose_name': '资源-器材',
                'verbose_name_plural': '资源-器材',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='DeviceRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('resource_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.device', verbose_name='资源对象')),
            ],
            options={
                'verbose_name': '器材资源',
                'verbose_name_plural': '器材资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
            ],
            options={
                'verbose_name': '资源-设备',
                'verbose_name_plural': '资源-设备',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EquipmentRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('resource_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.equipment', verbose_name='资源对象')),
            ],
            options={
                'verbose_name': '设备资源',
                'verbose_name_plural': '设备资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='描述表达式')),
                ('expression', models.TextField(blank=True, max_length=1024, null=True, verbose_name='表达式')),
                ('is_timer', models.BooleanField(default=False, verbose_name='定时事件')),
                ('parameters', models.JSONField(blank=True, null=True, verbose_name='事件参数')),
            ],
            options={
                'verbose_name': '服务-事件',
                'verbose_name_plural': '服务-事件',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
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
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
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
            name='Knowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('zhi_shi_wen_jian', models.FileField(blank=True, null=True, upload_to='', verbose_name='知识文件')),
                ('zhi_shi_wen_ben', models.TextField(blank=True, null=True, verbose_name='知识文本')),
            ],
            options={
                'verbose_name': '资源-知识',
                'verbose_name_plural': '资源-知识',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='KnowledgeRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('resource_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.knowledge', verbose_name='资源对象')),
            ],
            options={
                'verbose_name': '知识资源',
                'verbose_name_plural': '知识资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
            ],
            options={
                'verbose_name': '资源-物料',
                'verbose_name_plural': '资源-物料',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='MaterialRequirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('resource_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.material', verbose_name='资源对象')),
            ],
            options={
                'verbose_name': '物料资源',
                'verbose_name_plural': '物料资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('active', models.BooleanField(default=False, verbose_name='启用')),
                ('context', models.JSONField(blank=True, null=True, verbose_name='上下文')),
            ],
            options={
                'verbose_name': '资源-人员',
                'verbose_name_plural': '资源-人员',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
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
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('domain', models.CharField(blank=True, max_length=255, null=True, verbose_name='域名')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='项目描述')),
            ],
            options={
                'verbose_name': '项目',
                'verbose_name_plural': '项目',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('res_type', models.CharField(blank=True, choices=[('Consumption', '消耗'), ('TDM', '分时复用'), ('Recycle', '回收'), ('Shared', '共享')], default='Consumption', max_length=50, null=True, verbose_name='资源类型')),
            ],
            options={
                'verbose_name': '资源',
                'verbose_name_plural': '资源',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('primitive', models.BooleanField(default=True, verbose_name='基本服务')),
                ('manual_start', models.BooleanField(default=False, verbose_name='手动启动')),
                ('action_func_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='动作函数名')),
                ('action_api_params', models.JSONField(blank=True, null=True, verbose_name='API参数')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='价格')),
                ('program', models.JSONField(blank=True, null=True, verbose_name='服务程序')),
                ('service_type', models.CharField(choices=[('MANUAL', '人工'), ('AGENT', '代理'), ('SYSTEM', '系统')], default='MANUAL', max_length=50, verbose_name='服务类型')),
                ('action_api', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.api', verbose_name='API')),
                ('capital_requirements', models.ManyToManyField(through='design.CapitalRequirements', to='design.capital', verbose_name='资金需求')),
            ],
            options={
                'verbose_name': '服务',
                'verbose_name_plural': '服务',
                'ordering': ['service_type', 'id'],
            },
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
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
            name='WorkOrderFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('value_expression', models.CharField(blank=True, max_length=255, null=True, verbose_name='值表达式')),
                ('visible', models.BooleanField(default=True, verbose_name='可见')),
                ('order', models.SmallIntegerField(default=10, verbose_name='顺序')),
                ('work_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.workorder', verbose_name='工单')),
            ],
            options={
                'verbose_name': '工单字段',
                'verbose_name_plural': '工单字段',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='SourceCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='名称')),
                ('code', models.TextField(null=True, verbose_name='源代码')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='design.project', verbose_name='项目')),
            ],
            options={
                'verbose_name': '项目源码',
                'verbose_name_plural': '项目源码',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ServiceRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('order', models.SmallIntegerField(default=0, verbose_name='顺序')),
                ('entity_object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='实体ID')),
                ('parameter_values', models.JSONField(blank=True, null=True, verbose_name='参数值')),
                ('entity_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='design_service_rule', to='contenttypes.contenttype', verbose_name='实体类型')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='design.event', verbose_name='事件')),
                ('operand_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ruled_as_operand_service', to='design.service', verbose_name='操作服务')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='design.service', verbose_name='主体服务')),
                ('system_instruction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.instruction', verbose_name='系统指令')),
                ('target_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services_belong_to', to='design.service', verbose_name='隶属服务')),
            ],
            options={
                'verbose_name': '服务-规则',
                'verbose_name_plural': '服务-规则',
                'ordering': ['target_service', 'order', 'service', 'event', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ServiceConsists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_services', to='design.service', verbose_name='服务')),
                ('sub_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_services', to='design.service', verbose_name='子服务')),
            ],
            options={
                'verbose_name': '服务组成',
                'verbose_name_plural': '服务组成',
                'ordering': ['id'],
                'unique_together': {('service', 'sub_service')},
            },
        ),
        migrations.AddField(
            model_name='service',
            name='consists',
            field=models.ManyToManyField(through='design.ServiceConsists', to='design.service', verbose_name='服务组成'),
        ),
        migrations.AddField(
            model_name='service',
            name='device_requirements',
            field=models.ManyToManyField(through='design.DeviceRequirements', to='design.device', verbose_name='器材需求'),
        ),
        migrations.AddField(
            model_name='service',
            name='equipment_requirements',
            field=models.ManyToManyField(through='design.EquipmentRequirements', to='design.equipment', verbose_name='设备需求'),
        ),
        migrations.AddField(
            model_name='service',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.form', verbose_name='表单'),
        ),
        migrations.AddField(
            model_name='service',
            name='knowledge_requirements',
            field=models.ManyToManyField(through='design.KnowledgeRequirements', to='design.knowledge', verbose_name='知识需求'),
        ),
        migrations.AddField(
            model_name='service',
            name='material_requirements',
            field=models.ManyToManyField(through='design.MaterialRequirements', to='design.material', verbose_name='物料需求'),
        ),
        migrations.AddField(
            model_name='service',
            name='reference',
            field=models.ManyToManyField(blank=True, related_name='referenced_services', to='design.dataitem', verbose_name='引用'),
        ),
        migrations.AddField(
            model_name='service',
            name='route_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='services_routed_from', to='design.operator', verbose_name='传递至'),
        ),
        migrations.AddField(
            model_name='service',
            name='serve_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='服务对象类型'),
        ),
        migrations.AddField(
            model_name='service',
            name='subject',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('implement_type__in', ['Model', 'Log'])), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='served_services', to='design.dataitem', verbose_name='作业记录'),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('services', models.ManyToManyField(blank=True, related_name='roles', to='design.service', verbose_name='服务项目')),
            ],
            options={
                'verbose_name': '角色',
                'verbose_name_plural': '角色',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='operator',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.organization', verbose_name='组织'),
        ),
        migrations.AddField(
            model_name='operator',
            name='related_staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.operator', verbose_name='关系人'),
        ),
        migrations.AddField(
            model_name='operator',
            name='role',
            field=models.ManyToManyField(blank=True, to='design.role', verbose_name='角色'),
        ),
        migrations.AddField(
            model_name='operator',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='design_operator', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='中文名称')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='名称')),
                ('pym', models.CharField(blank=True, max_length=255, null=True, verbose_name='拼音码')),
                ('erpsys_id', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ERPSysID')),
                ('path', models.CharField(blank=True, max_length=100, null=True, verbose_name='路径')),
                ('title', models.CharField(blank=True, max_length=100, null=True, verbose_name='标题')),
                ('icon', models.CharField(blank=True, max_length=50, null=True, verbose_name='图标名称')),
                ('redirect', models.CharField(blank=True, max_length=100, null=True, verbose_name='默认子菜单项')),
                ('hide_in_menu', models.BooleanField(default=False, verbose_name='隐藏菜单')),
                ('hide_breadcrumb', models.BooleanField(default=False, verbose_name='隐藏面包屑')),
                ('form', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.form', verbose_name='表单')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='design.menuitem', verbose_name='父菜单')),
            ],
            options={
                'verbose_name': '菜单项',
                'verbose_name_plural': '菜单项',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='materialrequirements',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.service', verbose_name='服务'),
        ),
        migrations.AddField(
            model_name='knowledgerequirements',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.service', verbose_name='服务'),
        ),
        migrations.CreateModel(
            name='FormFields',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expand_data_item', models.BooleanField(default=False, verbose_name='展开数据项')),
                ('default_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='默认值')),
                ('readonly', models.BooleanField(default=False, verbose_name='只读')),
                ('is_required', models.BooleanField(default=False, verbose_name='必填')),
                ('choice_type', models.CharField(blank=True, choices=[('Select', '下拉单选'), ('RadioSelect', '单选按钮列表'), ('CheckboxSelectMultiple', '复选框列表'), ('SelectMultiple', '下拉多选')], max_length=50, null=True, verbose_name='选择类型')),
                ('is_aggregate', models.BooleanField(default=False, verbose_name='聚合字段')),
                ('visible', models.BooleanField(default=True, verbose_name='可见')),
                ('order', models.PositiveSmallIntegerField(default=10, verbose_name='顺序')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.dataitem', verbose_name='字段')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.form', verbose_name='表单')),
            ],
            options={
                'verbose_name': '表单字段',
                'verbose_name_plural': '表单字段',
                'ordering': ['order', 'id'],
                'unique_together': {('form', 'field')},
            },
        ),
        migrations.AddField(
            model_name='form',
            name='fields',
            field=models.ManyToManyField(through='design.FormFields', to='design.dataitem', verbose_name='表单字段'),
        ),
        migrations.AddField(
            model_name='equipmentrequirements',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.service', verbose_name='服务'),
        ),
        migrations.AddField(
            model_name='devicerequirements',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.service', verbose_name='服务'),
        ),
        migrations.CreateModel(
            name='DataItemConsists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(default=10, verbose_name='顺序')),
                ('default_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='默认值')),
                ('data_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subset', to='design.dataitem', verbose_name='数据项')),
                ('map_api_field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.apifields', verbose_name='映射API字段')),
                ('sub_data_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='superset', to='design.dataitem', verbose_name='子数据项')),
            ],
            options={
                'verbose_name': '数据项组成',
                'verbose_name_plural': '数据项组成',
                'ordering': ['order', 'id'],
                'unique_together': {('data_item', 'sub_data_item')},
            },
        ),
        migrations.AddField(
            model_name='dataitem',
            name='consists',
            field=models.ManyToManyField(related_name='parent', through='design.DataItemConsists', to='design.dataitem', verbose_name='数据项组成'),
        ),
        migrations.AddField(
            model_name='capitalrequirements',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.service', verbose_name='服务'),
        ),
        migrations.AddField(
            model_name='api',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='design.organization', verbose_name='提供者'),
        ),
    ]
