# WebSocket 管理模块重构说明

## 重构内容

1. **WebSocket 管理器 (socket_util.py)**
   - 增强了单例模式实现
   - 添加了详细的日志记录
   - 修复了用户连接映射中的错误
   - 添加了连接计数和孤立连接清理功能
   - 改进了错误处理和线程安全

2. **WebSocket 辅助函数 (socket_helper.py)**
   - 创建了安全的消息发送函数
   - 提供了专用的通知和消息发送接口
   - 增加了错误处理和日志记录

3. **WebSocket 事件处理 (event.py)**
   - 改进了连接和断开连接的处理逻辑
   - 增强了用户身份验证
   - 添加了详细的日志记录
   - 使用新的辅助函数发送消息

4. **业务模块集成**
   - 统一使用 `send_notification` 函数发送通知
   - 确保即使用户连接不存在也不会出错

5. **日志系统**
   - 添加了专用的 WebSocket 日志记录器

## 主要改进

1. **连接管理**
   - 正确注册和注销用户连接
   - 支持一个用户多个连接
   - 防止连接泄漏和内存溢出

2. **错误处理**
   - 所有操作都有适当的错误处理
   - 异常不会导致整个系统崩溃

3. **日志记录**
   - 详细记录连接、断开和消息发送
   - 便于调试和问题排查

4. **线程安全**
   - 使用锁确保并发操作的安全性
   - 避免数据竞争和不一致状态

## 使用方法

### 发送通知
```python
from app.utils.socket_helper import send_notification

# 发送通知给用户
send_notification(user_id, notification_data)
```

### 发送消息
```python
from app.utils.socket_helper import send_message

# 发送消息给用户
send_message(user_id, message_data)
```

### 广播事件
```python
from app.utils.socket_helper import broadcast_event

# 广播事件给所有连接的用户
broadcast_event(event_name, event_data)