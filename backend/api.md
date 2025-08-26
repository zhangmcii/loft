后端接口迁移成RESTful形式

| 模块          | 原路由（main 蓝图）                      | 方法       | 描述           | RESTful 路由（api 蓝图）                        | 方法     |
| ----------- | --------------------------------- | -------- | ------------ | ----------------------------------------- | ------ |
| **文章**      | `/`                               | GET      | 获取所有文章       | `/api/v1/posts`                           | GET    |
|             | `/`                               | POST     | 发布文章         | `/api/v1/posts`                           | POST   |
|             | `/user/<username>`                | GET      | 获取用户文章资料页    | `/api/v1/users/<username>/posts`          | GET    |
|             | `/edit/<id>`                      | GET/PUT  | 编辑文章         | `/api/v1/posts/<id>`                      | PUT    |
|             |                                   |          | 获取文章         | `/api/v1/posts/<id>`                      | GET    |
|             |                                   |          | 删除文章         | `/api/v1/posts/<id>`                      | DELETE |
|             | `/rich_post`                      | POST     | 发布富文本文章      | `/api/v1/posts/rich`                      | POST   |
| **用户资料**    | `/edit-profile`                   | POST     | 编辑当前用户资料     | `/api/v1/users/profile`                   | PUT    |
|             | `/edit-profile/<id>`              | POST     | 管理员编辑用户资料    | `/api/v1/users/<id>/profile`              | PUT    |
|             | `/image`                          | POST     | 存储用户头像       | `/api/v1/users/avatar`                    | POST   |
|             | `/users/<username>`               | GET      | 获取用户数据       | `/api/v1/users/<username>`                | GET    |
|             | `/can/<perm>`                     | GET      | 检查权限         | `/api/v1/users/permissions/<perm>`        | GET    |
|             | `/user_posts`                     | GET      | 批量生成用户和文章    | `/api/v1/users/generate_posts`            | POST   |
|             | `/socketData`                     | GET      | 获取在线用户信息     | `/api/v1/users/online`                    | GET    |
|             | `/user/<user_id>/interest_images` | GET      | 获取用户兴趣图片     | `/api/v1/users/<user_id>/interest_images` | GET    |
|             |                                   |          | 获取用户信息       | `/api/v1/users/<user_id>`                 | GET    |
| **评论**      | `/post/<id>`                      | POST     | 发布评论         | `/api/v1/posts/<id>/comments`             | POST   |
|             | `/moderate`                       | GET      | 管理评论         | `/api/v1/comments/moderate`               | GET    |
|             | `/moderate/enable/<id>`           | GET      | 恢复评论         | `/api/v1/comments/<id>/enable`            | PUT    |
|             | `/moderate/disable/<id>`          | GET      | 禁用评论         | `/api/v1/comments/<id>/disable`           | PUT    |
|             |                                   |          | 获取文章的根评论     | `/api/v1/posts/<post_id>/comments/`       | GET    |
|             |                                   |          | 获取评论的回复      | `/api/v1/reply_comments/`                 | GET    |
| **关注/粉丝**   | `/follow/<username>`              | GET      | 关注用户         | `/api/v1/users/<username>/followers`      | POST   |
|             | `/unfollow/<username>`            | GET      | 取消关注         | `/api/v1/users/<username>/followers`      | DELETE |
|             | `/followers/<username>`           | GET      | 获取粉丝列表       | `/api/v1/users/<username>/followers`      | GET    |
|             | `/followed_by/<username>`         | GET      | 获取关注的人列表     | `/api/v1/users/<username>/following`      | GET    |
| **消息**      | `/msg`                            | GET      | 获取聊天历史记录     | `/api/v1/messages`                        | GET    |
|             | `/msg/read`                       | POST     | 标记消息已读       | `/api/v1/messages/read`                   | PUT    |
| **通知**      | `/notifications`                  | GET      | 获取通知         | `/api/v1/notifications`                   | GET    |
|             | `/notification/read`              | POST     | 标记通知已读       | `/api/v1/notifications/read`              | PUT    |
| **点赞**      | `/praise/<id>`                    | GET/POST | 文章点赞         | `/api/v1/posts/<id>/likes`                | POST   |
|             |                                   |          | 取消文章点赞       | `/api/v1/posts/<id>/likes`                | DELETE |
|             | `/praise/comment/<id>`            | GET/POST | 评论点赞         | `/api/v1/comments/<id>/likes`             | POST   |
|             |                                   |          | 取消评论点赞       | `/api/v1/comments/<id>/likes`             | DELETE |
|             | `/has_praised/<post_id>`          | GET      | 查询文章下已点赞评论id | `/api/v1/posts/<post_id>/likes`           | GET    |
| **日志**      | `/logs`                           | GET      | 获取系统日志       | `/api/v1/logs`                            | GET    |
|             | `/deleteLog`                      | POST     | 删除日志         | `/api/v1/logs`                            | DELETE |
| **标签**      | `/tags_list`                      | GET      | 获取所有标签       | `/api/v1/tags`                            | GET    |
|             | `/update_user_tag`                | POST     | 更新当前用户标签     | `/api/v1/users/me/tags`                   | PUT    |
|             | `/update_tag`                     | POST     | 更新公共标签库      | `/api/v1/tags`                            | PUT    |
| **文件/图片上传** | `/get_upload_token`               | GET      | 获取上传凭证       | `/api/v1/upload/token`                    | GET    |
|             | `/get_signed_image_urls`          | POST     | 获取私有图片 URL   | `/api/v1/images/signed_urls`              | POST   |
|             | `/del_image`                      | DELETE   | 删除图片         | `/api/v1/images/<image_id>`               | DELETE |
|             | `/dir_name`                       | GET      | 查询 bucket 目录 | `/api/v1/images/dir`                      | GET    |
|             | `/user/<user_id>/interest_images` | POST     | 上传兴趣封面       | `/api/v1/users/<user_id>/interest_images` | POST   |

管理员 获取所有评论，获取所有日志 结构相同
