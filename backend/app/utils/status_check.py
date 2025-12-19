import time
from threading import Thread

from ..models import User
from ..websocket import init_ws_services
from .. import redis

_, presence, _ = init_ws_services(redis)


# 定时任务（每分钟执行）
def check_inactive_users():
    duration = 30
    print(f"加入检测用户状态线程， 每{duration}s执行一次")
    while True:
        # 每30秒执行一次
        time.sleep(duration)
        print("检测用户状态开始..")

        # 获取所有用户
        all_users = User.query.all()

        for user in all_users:
            user_presence = presence.get_user_presence(user.id)
            last_active = int(user_presence.get("last_active", 0))
            if time.time() - last_active > 60:  # 超过60秒未活跃
                presence.mark_user_offline(user.id)


Thread(target=check_inactive_users, daemon=True).start()
