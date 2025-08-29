# Pydantic 数据校验模型使用指南

## 概述

本项目使用 Pydantic 进行数据校验，提供了用户相关操作的完整校验模型。

## 校验模型

### 1. RegisterRequest - 注册请求校验

```python
from app.schemas.user_schemas import RegisterRequest

# 校验规则：
# - username: 3-20字符，支持字母、数字、下划线、中文
# - password: 6-128字符，必须包含字母和数字
# - confirm_password: 必须与password一致
# - email: 标准邮箱格式
# - verification_code: 4-6位纯数字
```

### 2. ChangePasswordRequest - 修改密码校验

```python
from app.schemas.user_schemas import ChangePasswordRequest

# 校验规则：
# - old_password: 原密码
# - new_password: 6-128字符，必须包含字母和数字，不能与原密码相同
# - confirm_password: 必须与new_password一致
```

### 3. ForgotPasswordRequest - 忘记密码校验

```python
from app.schemas.user_schemas import ForgotPasswordRequest

# 校验规则：
# - email: 标准邮箱格式
# - verification_code: 4-6位纯数字
# - new_password: 6-128字符，必须包含字母和数字
# - confirm_password: 必须与new_password一致
```

### 4. BindEmailRequest - 绑定邮箱校验

```python
from app.schemas.user_schemas import BindEmailRequest

# 校验规则：
# - email: 标准邮箱格式
# - verification_code: 4-6位纯数字
# - password: 可选，用于身份验证
```

### 5. ChangeEmailRequest - 修改邮箱校验

```python
from app.schemas.user_schemas import ChangeEmailRequest

# 校验规则：
# - old_email: 标准邮箱格式
# - new_email: 标准邮箱格式，不能与old_email相同
# - verification_code: 4-6位纯数字
# - password: 可选，用于身份验证
```

## 使用方法

### 方法一：使用装饰器（推荐）

```python
from flask import Blueprint
from app.schemas.user_schemas import RegisterRequest
from app.utils.validation import validate_json
from app.utils.response import response_success, response_error

bp = Blueprint('user', __name__)

@bp.route('/register', methods=['POST'])
@validate_json(RegisterRequest)
def register(validated_data: RegisterRequest):
    """
    注册接口
    validated_data 已经是经过校验的 RegisterRequest 对象
    """
    try:
        # 业务逻辑
        username = validated_data.username
        email = validated_data.email
        # ...
        
        return response_success(message="注册成功")
    except Exception as e:
        return response_error(500, str(e))
```

### 方法二：手动校验

```python
from flask import request
from pydantic import ValidationError
from app.schemas.user_schemas import RegisterRequest
from app.utils.response import response_error, response_success

@bp.route('/register', methods=['POST'])
def register():
    try:
        # 获取请求数据
        json_data = request.get_json()
        
        # 手动校验
        validated_data = RegisterRequest(**json_data)
        
        # 业务逻辑
        # ...
        
        return response_success(message="注册成功")
        
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        return response_error(400, error_msg)
    except Exception as e:
        return response_error(500, str(e))
```

## 密码强度规则

- 最少6个字符，最多128个字符
- 必须包含至少一个字母（a-z 或 A-Z）
- 必须包含至少一个数字（0-9）
- 如果密码长度少于8位，建议包含特殊字符以提高安全性

## 用户名规则

- 长度：3-20个字符
- 允许的字符：
  - 英文字母（a-z, A-Z）
  - 数字（0-9）
  - 下划线（_）
  - 中文字符

## 邮箱校验

使用 Pydantic 的 `EmailStr` 类型，自动进行标准邮箱格式校验。

## 验证码规则

- 长度：4-6位
- 必须为纯数字

## 错误处理

所有校验错误都会被自动转换为统一的响应格式：

```json
{
    "code": 400,
    "message": "具体的错误信息",
    "data": null
}
```

## 运行测试

```bash
# 运行所有校验相关测试
pytest backend/tests/test_schemas.py -v

# 运行校验工具测试
pytest backend/tests/test_validation_utils.py -v

# 运行集成测试
pytest backend/tests/test_user_validation_integration.py -v
```

## 扩展校验规则

如需添加新的校验规则，可以：

1. 在对应的模型中添加 `@validator` 装饰器
2. 创建自定义校验函数
3. 添加相应的单元测试

示例：

```python
@validator('username')
def validate_username_not_reserved(cls, v):
    """检查用户名是否为保留词"""
    reserved_words = ['admin', 'root', 'system']
    if v.lower() in reserved_words:
        raise ValueError('该用户名为系统保留，请选择其他用户名')
    return v