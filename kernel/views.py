from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import Operator, Service

# 获取员工列表，过滤掉操作员自己，用于排班
def get_employees(request):
    # operator = User.objects.get(username=request.user).customer.staff
    # shift_employees = []
    # for staff in Operator.objects.filter(role__isnull=False).distinct().exclude(id=operator.id):
    #     allowed_services = [service.id for service in Service.objects.filter(service_type__in=[1,2]) if set(service.role.all()).intersection(set(staff.role.all()))]
    #     shift_employees.append({'id': staff.customer.id, 'name': staff.name, 'allowed_services': allowed_services})
    # return JsonResponse(shift_employees, safe=False)
    return JsonResponse([{'id': '1', 'name': 'test', 'allowed_services': []}], safe=False)


# Dictionary structures mimicking the Vue mock setup for authRoute, levelRoute, sysRoute, linkRoute
dashboardRoute = {
  'path': '/dashboard',
  'name': 'Dashboard',
  'component': 'LAYOUT',
  'redirect': '/dashboard/analysis',
  'meta': {
    'title': 'routes.dashboard.dashboard',
    'hideChildrenInMenu': True,
    'icon': 'bx:bx-home',
  },
  'children': [
    {
      'path': 'analysis',
      'name': 'Analysis',
      'component': '/dashboard/analysis/index',
      'meta': {
        'hideMenu': True,
        'hideBreadcrumb': True,
        'title': 'routes.dashboard.analysis',
        'currentActiveMenu': '/dashboard',
        'icon': 'bx:bx-home',
      },
    },
    {
      'path': 'workbench',
      'name': 'Workbench',
      'component': '/dashboard/workbench/index',
      'meta': {
        'hideMenu': True,
        'hideBreadcrumb': True,
        'title': 'routes.dashboard.workbench',
        'currentActiveMenu': '/dashboard',
        'icon': 'bx:bx-home',
      },
    },
  ],
}

backRoute = {
  'path': 'back',
  'name': 'PermissionBackDemo',
  'meta': {
    'title': 'routes.demo.permission.back',
  },

  'children': [
    {
      'path': 'page',
      'name': 'BackAuthPage',
      'component': '/demo/permission/back/index',
      'meta': {
        'title': 'routes.demo.permission.backPage',
      },
    },
    {
      'path': 'btn',
      'name': 'BackAuthBtn',
      'component': '/demo/permission/back/Btn',
      'meta': {
        'title': 'routes.demo.permission.backBtn',
      },
    },
  ],
}

authRoute = {
  'path': '/permission',
  'name': 'Permission',
  'component': 'LAYOUT',
  'redirect': '/permission/front/page',
  'meta': {
    'icon': 'carbon:user-role',
    'title': 'routes.demo.permission.permission',
  },
  'children': [backRoute],
}

levelRoute = {
  'path': '/level',
  'name': 'Level',
  'component': 'LAYOUT',
  'redirect': '/level/menu1/menu1-1',
  'meta': {
    'icon': 'carbon:user-role',
    'title': 'routes.demo.level.level',
  },

  'children': [
    {
      'path': 'menu1',
      'name': 'Menu1Demo',
      'meta': {
        'title': 'Menu1',
      },
      'children': [
        {
          'path': 'menu1-1',
          'name': 'Menu11Demo',
          'meta': {
            'title': 'Menu1-1',
          },
          'children': [
            {
              'path': 'menu1-1-1',
              'name': 'Menu111Demo',
              'component': '/demo/level/Menu111',
              'meta': {
                'title': 'Menu111',
              },
            },
          ],
        },
        {
          'path': 'menu1-2',
          'name': 'Menu12Demo',
          'component': '/demo/level/Menu12',
          'meta': {
            'title': 'Menu1-2',
          },
        },
      ],
    },
    {
      'path': 'menu2',
      'name': 'Menu2Demo',
      'component': '/demo/level/Menu2',
      'meta': {
        'title': 'Menu2',
      },
    },
  ],
}

sysRoute = {
  'path': '/system',
  'name': 'System',
  'component': 'LAYOUT',
  'redirect': '/system/account',
  'meta': {
    'icon': 'ion:settings-outline',
    'title': 'routes.demo.system.moduleName',
  },
  'children': [
    {
      'path': 'account',
      'name': 'AccountManagement',
      'meta': {
        'title': 'routes.demo.system.account',
        'ignoreKeepAlive': True,
      },
      'component': '/demo/system/account/index',
    },
    {
      'path': 'account_detail/:id',
      'name': 'AccountDetail',
      'meta': {
        'hideMenu': True,
        'title': 'routes.demo.system.account_detail',
        'ignoreKeepAlive': True,
        'showMenu': False,
        'currentActiveMenu': '/system/account',
      },
      'component': '/demo/system/account/AccountDetail',
    },
    {
      'path': 'role',
      'name': 'RoleManagement',
      'meta': {
        'title': 'routes.demo.system.role',
        'ignoreKeepAlive': True,
      },
      'component': '/demo/system/role/index',
    },

    {
      'path': 'menu',
      'name': 'MenuManagement',
      'meta': {
        'title': 'routes.demo.system.menu',
        'ignoreKeepAlive': True,
      },
      'component': '/demo/system/menu/index',
    },
    {
      'path': 'dept',
      'name': 'DeptManagement',
      'meta': {
        'title': 'routes.demo.system.dept',
        'ignoreKeepAlive': True,
      },
      'component': '/demo/system/dept/index',
    },
    {
      'path': 'changePassword',
      'name': 'ChangePassword',
      'meta': {
        'title': 'routes.demo.system.password',
        'ignoreKeepAlive': True,
      },
      'component': '/demo/system/password/index',
    },
  ],
}

linkRoute = {
  'path': '/link',
  'name': 'Link',
  'component': 'LAYOUT',
  'meta': {
    'icon': 'ion:tv-outline',
    'title': 'routes.demo.iframe.frame',
  },
  'children': [
    {
      'path': 'doc',
      'name': 'Doc',
      'meta': {
        'title': 'routes.demo.iframe.doc',
        'frameSrc': 'https://doc.vvbin.cn/',
      },
    },
    {
      'path': 'https://doc.vvbin.cn/',
      'name': 'DocExternal',
      'component': 'LAYOUT',
      'meta': {
        'title': 'routes.demo.iframe.docExternal',
      },
    },
  ],
}

from django.http import JsonResponse

from django.http import JsonResponse

def get_menu_list(request):
    try:
        data = {
            "result": [
                dashboardRoute,
                authRoute,
                levelRoute,
                sysRoute,
                # linkRoute, 
            ],
            "code": 0,  # Use 0 to indicate success, matching the ResultEnum.SUCCESS
            "message": "Success"
        }
        print('获取菜单：', request)
        return JsonResponse(data)
    except Exception as e:
        error_data = {
            "result": None,
            "code": -1,  # Use -1 to indicate general errors, matching the ResultEnum.ERROR
            "message": str(e)  # Exception message as the error message
        }
        return JsonResponse(error_data, status=500)
