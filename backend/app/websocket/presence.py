import time


class UserPresenceService:
    """
    管理用户在线状态与活跃信息

    结构设计:
    Key: online:users  ->    { user_id1, user_id2, ... }
    Type: SET
    是否在线的唯一判断


    Key: user:{user_id}:status  -> 
    Type: HASH
    Fields:
    - online       -> 0 / 1
    - last_active  -> unix_timestamp
    """

    def __init__(self, redis):
        self.redis = redis

    # ---------- 状态变更（明确副作用） ----------

    def mark_user_online(self, user_id: int):
        """
        将用户标记为在线
        """
        pipe = self.redis.pipeline()
        pipe.sadd("online:users", user_id)
        pipe.hset(
            f"user:{user_id}:status",
            mapping={
                "online": 1,
                "last_active": int(time.time())
            }
        )
        pipe.execute()

    def mark_user_offline(self, user_id: int):
        """
        将用户标记为离线
        """
        pipe = self.redis.pipeline()
        pipe.srem("online:users", user_id)
        pipe.hset(f"user:{user_id}:status", "online", 0)
        pipe.execute()

    def update_last_active(self, user_id: int):
        """
        更新用户最后活跃时间
        """
        self.redis.hset(
            f"user:{user_id}:status",
            "last_active",
            int(time.time())
        )

    # ---------- 查询（无副作用） ----------

    def is_user_online(self, user_id: int) -> bool:
        """
        判断用户是否在线
        """
        return self.redis.sismember("online:users", user_id)

    def list_online_users(self) -> set[int]:
        """
        获取所有在线用户 ID
        """
        return {int(user_id) for user_id in self.redis.smembers("online:users")}

    def count_online_users(self) -> int:
        """
        获取在线用户数量
        """
        return self.redis.scard("online:users")

    def get_user_presence(self, user_id: int) -> dict:
        """
        获取用户在线相关状态
        """
        return self.redis.hgetall(f"user:{user_id}:status") or {}
