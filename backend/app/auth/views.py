from flask import request
from flask_jwt_extended import create_access_token, jwt_required, current_user
from ..decorators import admin_required
from . import auth
from ..models import User
from .. import db
from ..mycelery.tasks import send_email
from ..utils.time_util import DateUtils
from ..utils.response import success, error
from ..utils.validation import validate_json
from ..schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    BindEmailRequest,
    ChangeEmailRequest
)


@auth.before_app_request
@jwt_required(optional=True)
def before_request():
    if current_user:
        current_user.ping()
        # if not current_user.confirmed and request.endpoint and request.blueprint != 'auth' and request.endpoint != 'static':
        #     return '用户邮件未认证'


@auth.route('/login', methods=['post'])
def login():
    j = request.get_json()
    user = User.query.filter_by(username=j.get('uiAccountName')).one_or_none()
    if user and user.verify_password(j.get('uiPassword')):
        token = create_access_token(identity=user, expires_delta=False)
        user.ping()
        return success(data=user.to_json(), token='Bearer ' + token)
    return error(code=400, message='账号或密码错误')


@auth.route('/register', methods=['POST'])
@validate_json(RegisterRequest)
def register(validated_data):
    # 检查用户名是否已存在
    u = User.query.filter_by(username=validated_data.username).first()
    if u:
        return error(message='该用户名已被注册，请换一个')
    
    # 检查邮箱是否已存在
    if validated_data.email:
        existing_email = User.query.filter_by(email=validated_data.email).first()
        if existing_email:
            return error(message='该邮箱已被注册，请换一个')
    
    email = validated_data.email if validated_data.email else None
    user = User(
        email=email, 
        username=validated_data.username, 
        password=validated_data.password, 
        image=getattr(validated_data, 'image', '')
    )
    db.session.add(user)
    db.session.commit()
    return success()


@auth.route('/applyCode', methods=['POST'])
@jwt_required(optional=True)
@DateUtils.record_time
def apply_code():
    email = request.get_json().get('email')
    action = request.get_json().get('action')
    # if action == 'confirm' and User.query.filter_by(email=email).first():
    #     return jsonify(data='', msg='fail', detail='填写的邮箱已经存在')
    # if action == 'confirm' and current_user.email and email != current_user.email:
    #     return jsonify(data='', msg='fail', detail='请输入该用户的正确的邮件')
    # if (action == 'confirm' or action == 'change') and not current_user.email:
    if action == 'confirm' or action == 'change':
        current_user.email = request.get_json().get('email')
        db.session.add(current_user)
        db.session.commit()
    code = User.generate_code(email)
    # 重置密码
    send_email.delay(email, 'Confirm Your Account', user='User', code=code)
    return success()


@auth.route('/confirm', methods=['POST'])
@jwt_required()
@validate_json(BindEmailRequest)
def confirm(validated_data):
    email = validated_data.email
    code = validated_data.code
    
    if current_user.email and email != current_user.email:
        return error(message='输入的邮件与用户的邮件不一致')
    if current_user.confirm(email, code):
        db.session.commit()
        return success(data={
            'isConfirmed': current_user.confirmed,
            'roleId': current_user.role_id
        })
    return error(message='绑定失败')


@auth.route('/changeEmail', methods=['POST'])
@jwt_required()
@validate_json(ChangeEmailRequest)
def change_email(validated_data):
    email = validated_data.new_email
    code = validated_data.code
    
    if User.query.filter_by(email=email).first():
        return error(message='填写的邮箱已经存在')
    if current_user.email == email:
        return error(message='请更换新的邮箱地址')
    
    # 验证码
    if current_user.change_email(email, code):
        db.session.commit()
        return success()
    return error(message='验证码错误')


@auth.route('/changePassword', methods=['POST'])
@jwt_required()
@validate_json(ChangePasswordRequest)
def change_password(validated_data):
    if current_user.verify_password(validated_data.old_password):
        current_user.password = validated_data.new_password
        db.session.add(current_user)
        db.session.commit()
        return success()
    return error(message='原密码错误')


@auth.route('/resetPassword', methods=['POST'])
@validate_json(ForgotPasswordRequest)
def reset_password(validated_data):
    email = validated_data.email
    code = validated_data.code
    password = validated_data.new_password
    
    # 验证码
    if User.compare_code(email, code):
        user = User.query.filter_by(email=email).first()
        if not user:
            return error(message='此邮箱尚未绑定')
        user.password = password
        db.session.add(user)
        db.session.commit()
        return success()
    return error(message='验证码错误')


@auth.route('/helpChangePassword', methods=['POST'])
@admin_required
@jwt_required()
def change_password_admin():
    username = request.get_json().get('username')
    new_password = request.get_json().get('newPassword')
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return success()
    return error(message='用户不存在')
