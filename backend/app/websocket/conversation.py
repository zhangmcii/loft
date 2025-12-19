# ws/conversation.py
import time


class ConversationStateService:
    """
    管理用户在会话中的行为态（active_chat / typing）

    结构设计:
    user:{user_id}:active_chat        -> target_user_id  
    Type: STRING
    当前“正在看的聊天对象”

    typing:{user_id}:{user_id}    -> 1  
    Type: STRING
    只表示“最近有真实输入”            
    """

    ACTIVE_CHAT_TTL = 60 * 5      # 5 分钟
    TYPING_TTL = 3                # 3 秒

    def __init__(self, redis):
        self.redis = redis

    # ---------- Active Chat ----------

    def set_active_chat(self, user_id: int, target_user_id: int):
        """
        设置当前聊天对象
        """
        self.redis.set(
            f"user:{user_id}:active_chat",
            target_user_id,
            ex=self.ACTIVE_CHAT_TTL
        )

    def clear_active_chat(self, user_id: int):
        """
        清除当前聊天对象
        """
        self.redis.delete(f"user:{user_id}:active_chat")

    def get_active_chat(self, user_id: int) -> int | None:
        """
        获取当前聊天对象
        """
        value = self.redis.get(f"user:{user_id}:active_chat")
        return int(value) if value else None

    # ---------- Typing ----------

    def mark_typing(self, user_id: int, target_user_id: int):
        """
        标记 user 正在给 target_user 输入
        """
        self.redis.set(
            f"typing:{user_id}:{target_user_id}",
            1,
            ex=self.TYPING_TTL
        )

    def is_typing(self, user_id: int, target_user_id: int) -> bool:
        """
        判断 user 是否正在给 target_user 输入
        """
        return self.redis.exists(
            f"typing:{user_id}:{target_user_id}"
        )