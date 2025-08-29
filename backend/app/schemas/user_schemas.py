"""
用户相关的数据校验模型
"""
import re
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from ..utils.response import error


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    # email: EmailStr = Field(..., description="邮箱")
    # verification_code: str = Field(..., min_length=4, max_length=6, description="验证码")

    @field_validator('username')
    def validate_username(cls, v):
        """校验用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文字符')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        """校验密码强度"""
        # 密码必须包含至少一个字母和一个数字
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        # 检查是否包含特殊字符（推荐但不强制）
        if len(v) < 8 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码长度不足8位时，建议包含特殊字符以提高安全性')
        return v

    @field_validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """校验确认密码"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v

    # @field_validator('verification_code')
    # def validate_verification_code(cls, v):
    #     """校验验证码格式"""
    #     if not v.isdigit():
    #         raise ValueError('验证码必须为纯数字')
    #     return v


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @field_validator('new_password')
    def validate_new_password(cls, v):
        """校验新密码强度"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        if len(v) < 8 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码长度不足8位时，建议包含特殊字符以提高安全性')
        return v

    @field_validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """校验确认密码"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @field_validator('new_password')
    def validate_password_different(cls, v, values):
        """校验新密码不能与原密码相同"""
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与原密码相同')
        return v


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求模型"""
    email: EmailStr = Field(..., description="邮箱")
    verification_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
    # confirm_password: str = Field(..., description="确认新密码")

    @field_validator('new_password')
    def validate_new_password(cls, v):
        """校验新密码强度"""
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        if len(v) < 8 and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码长度不足8位时，建议包含特殊字符以提高安全性')
        return v

    # @field_validator('confirm_password')
    # def validate_confirm_password(cls, v, values):
    #     """校验确认密码"""
    #     if 'new_password' in values and v != values['new_password']:
    #         raise ValueError('两次输入的密码不一致')
    #     return v

    @field_validator('verification_code')
    def validate_verification_code(cls, v):
        """校验验证码格式"""
        if not v.isdigit():
            raise ValueError('验证码必须为纯数字')
        return v


class BindEmailRequest(BaseModel):
    """绑定邮箱请求模型"""
    email: EmailStr = Field(..., description="邮箱")
    verification_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    # password: Optional[str] = Field(None, description="当前密码（用于身份验证）")

    @field_validator('verification_code')
    def validate_verification_code(cls, v):
        """校验验证码格式"""
        if not v.isdigit():
            raise ValueError('验证码必须为纯数字')
        return v


class ChangeEmailRequest(BaseModel):
    """修改邮箱请求模型"""
    # old_email: EmailStr = Field(..., description="原邮箱")
    new_email: EmailStr = Field(..., description="新邮箱")
    verification_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    password: Optional[str] = Field(None, description="当前密码（用于身份验证）")

    @field_validator('new_email')
    def validate_email_different(cls, v, values):
        """校验新邮箱不能与原邮箱相同"""
        if 'old_email' in values and v == values['old_email']:
            raise ValueError('新邮箱不能与原邮箱相同')
        return v

    @field_validator('verification_code')
    def validate_verification_code(cls, v):
        """校验验证码格式"""
        if not v.isdigit():
            raise ValueError('验证码必须为纯数字')
        return v


# 校验错误处理装饰器
def handle_validation_error(func):
    """处理Pydantic校验错误的装饰器"""
    from functools import wraps
    from pydantic import ValidationError
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            # 提取第一个错误信息
            error_msg = e.errors()[0]['msg']
            return error(400, error_msg)
        except ValueError as e:
            return error(400, str(e))
    return wrapper