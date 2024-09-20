from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

import json
from enum import Enum

class ResultEnum(Enum):
    """Result状态枚举类"""
    SUCCESS = 0,
    ERROR = -1,
    TIMEOUT = 401,
    TYPE = 'success',

# @ensure_csrf_cookie
@csrf_exempt  # 取消 CSRF 保护，仅用于测试或特殊情况，生产环境应遵守安全实践
@require_http_methods(["POST"])  # 限制该视图只接受 POST 请求
def login_view(request):
    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username')
    password = data.get('password')
    print('login:', request.POST, username, password)
    user = authenticate(request, username=username, password=password)
    print('login success:', user, user.__dict__)

    roles = [{'roleName': 'roleName', 'value': 'value'},]

    if user is not None:
        session_id = login(request, user)
        return JsonResponse({
            'code': 0,  # 使用枚举值0表示成功
            'result': {
                'userId': user.id,
                'token': 'fakeToken1',
                'roles': roles,
            },
            'message': "Logged in successfully"
        }, status=200)
    else:
        return JsonResponse({
            'code': -1,  # 使用枚举值-1表示错误
            'result': {},
            'message': "Authentication failed"
        }, status=200)  # 状态码设置为200，但错误信息包含在返回的JSON中

def logout_view(request):
    # 可选：检查用户是否已登录
    print('logout:', request.GET)
    print('logout:', request.user)
    print('logout:', request.user.is_authenticated)

    if not request.user.is_authenticated:
        return JsonResponse({
            'code': -1,  # 使用枚举值-1表示错误
            'result': {},
            'message': "No user is currently logged in."
        }, status=200)

    # 执行登出操作
    logout(request)
    return JsonResponse({
        'code': 0,  # 使用枚举值0表示成功
        'result': {},
        'message': "Logged out successfully"
    }, status=200)

def get_user_info(request):
    return JsonResponse({
        'code': 0,  # 使用枚举值0表示成功
        'result': {
            'roles': [{'roleName': 'roleName', 'value': 'value'},],
            'userId': 1,
            'username': 'admin',
            'realName': 'Miles' + ' ' + 'Jiang',
            'avatar': 'avatar',
            'desc': '',
        },
        'message': "get_user_info successfully"
    }, status=200)

def get_perm_code(request):
    return JsonResponse({
        'code': 0,  # 使用枚举值0表示成功
        'result': ['1000', '3000', '5000'],
        'message': "get_perm_code successfully"
    }, status=200)

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

def get_menu_list(request):
    return JsonResponse({
        'code': 0,  # 使用枚举值0表示成功
            "result": [
                dashboardRoute,
                authRoute,
                levelRoute,
                sysRoute,
                linkRoute, 
            ],
        'message': "get_perm_code successfully"
    }, status=200)
