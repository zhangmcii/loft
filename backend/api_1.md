| 方法                                    | 路径                                     | 说明           |
| ------------------------------------- |----------------------------------------| ------------ |
| **Posts & Comments（文章 & 评论）**         |                                        |              |
| `GET`                                 | `/posts`                               | 获取所有文章       |
| `POST`                                | `/posts`                               | 发布文章         |
| `GET`                                 | `/posts/<post_id>`                     | 获取文章详情       |
| `PUT`                                 | `/posts/<post_id>`                     | 修改文章         |
| `DELETE`                              | `/posts/<post_id>`                     | 删除文章         |
| `GET`                                 | `/posts/<post_id>/comments`            | 获取文章的评论      |
| `POST`                                | `/posts/<post_id>/comments`            | 发布评论         |
| `PUT`                                 | `/comments/<comment_id>`               | 修改评论         |
| `DELETE`                              | `/comments/<comment_id>`               | 删除评论         |
| `PATCH`                               | `/comments/<comment_id>`               | 启用/禁用评论      |
| **Users（用户 & 资料）**                    |                                        |              |
| `GET`                                 | `/users/<username>`                    | 获取用户信息       |
| `PUT`                                 | `/users/<user_id>`                     | 更新用户资料       |
| `POST`                                | `/users/<user_id>/image`               | 上传头像         |
| `GET`                                 | `/users/<user_id>/image`               | 获取头像         |
| **Social（关注 & 粉丝）**                   |                                        |              |
| `POST`                                | `/users/<username>/follow`             | 关注用户         |
| `DELETE`                              | `/users/<username>/follow`             | 取消关注         |
| `GET`                                 | `/users/<username>/followers`          | 获取粉丝列表       |
| `GET`                                 | `/users/<username>/followings`         | 获取关注列表       |
| **Likes（点赞）**                         |                                        |              |
| `POST`                                | `/posts/<post_id>/likes`               | 给文章点赞        |
| `DELETE`                              | `/posts/<post_id>/likes`               | 取消文章点赞       |
| `GET`                                 | `/posts/<post_id>/likes`               | 获取文章点赞用户列表   |
| `POST`                                | `/comments/<comment_id>/likes`         | 给评论点赞        |
| `DELETE`                              | `/comments/<comment_id>/likes`         | 取消评论点赞       |
| `GET`                                 | `/posts/<post_id>/comments?liked=true` | 获取当前用户已点赞的评论 |
| **Tags（标签）**                          |                                        |              |
| `GET`                                 | `/tags`                                | 获取所有公共标签     |
| `POST`                                | `/tags`                                | 新增标签         |
| `PUT`                                 | `/tags/<tag_id>`                       | 更新标签         |
| `POST`                                | `/users/<user_id>/tags`                | 更新用户标签       |
| **Messages & Notifications（消息 & 通知）** |                                        |              |
| `GET`                                 | `/conversations/<user_id>/messages`    | 获取聊天消息历史     |
| `PATCH`                               | `/conversations/<user_id>/messages`    | 批量标记消息为已读    |
| `GET`                                 | `/notifications`                       | 获取当前用户的通知    |
| `PATCH`                               | `/notifications`                       | 批量标记通知为已读    |
| **Files（文件/图片）**                      |                                        |              |
| `GET`                                 | `/files/token`                         | 获取上传凭证       |
| `POST`                                | `/files/urls`                          | 获取签名 URL     |
| `DELETE`                              | `/files/<file_id>`                     | 删除文件         |
| `GET`                                 | `/files/dir/<path>`                    | 查询目录下的文件名    |
| `GET`                                 | `/users/<user_id>/interest-images`     | 获取用户兴趣图片     |
| `POST`                                | `/users/<user_id>/interest-images`     | 上传用户兴趣图片     |
| **System（系统）**                        |                                        |              |
| `GET`                                 | `/logs`                                | 获取日志         |
| `DELETE`                              | `/logs`                                | 批量删除日志       |
| `GET`                                 | `/online-users`                        | 获取在线用户信息     |

# 🔍 检查与优化建议

### 1. **评论启用/禁用**

现在是：

```
POST /comments/<id>/enable
POST /comments/<id>/disable
```

👉 **问题**：这属于“状态切换”，不太 RESTful。
✅ 优化：用 `PATCH /comments/<id>`，请求体带 `{"status": "enabled"}` 或 `{"status": "disabled"}`。

---

### 2. **通知/消息的已读**

现在是：

```
POST /messages/read
POST /notifications/read
```

👉 **问题**：`read` 是动词，REST 中应避免动词挂在 URL。
✅ 优化：

* `PATCH /messages/<id>` → `{"read": true}`
* 或 `PATCH /messages` 批量标记已读（传 ID 数组）。
* 通知同理，改成 `/notifications/<id>` 或 `/notifications` 批量。

---

### 3. **点赞**

现在有：

```
POST /posts/<id>/likes
DELETE /posts/<id>/likes
```

👉 **问题**：这里 likes 本身是一个集合，写法合理，但 `GET /posts/<id>/likes` 返回的是“点赞人列表”，语义正确；但是 “查找某文章下用户已点赞的评论 id” 放在 `/posts/<id>/liked-comments`，有点别扭。
✅ 优化：可以改成

```
GET /posts/<id>/comments?liked=true
```

通过查询参数表达过滤，更 RESTful。

---

### 4. **标签**

```
PUT /tags/<id>
```

👉 **问题**：如果“更新公共标签”只是更新标签库项，OK；但如果只是更新标签名，最好明确语义。
✅ 优化：保持 `/tags/<id>`，但请求体更规范。用户自己的标签 → `/users/<id>/tags` 很合适。

---

### 5. **文件上传**

```
GET /files/upload-token
POST /files/signed-urls
DELETE /files/<file_id>
```

👉 **问题**：命名不一致，`upload-token`、`signed-urls` 不是资源，更像动作。
✅ 优化：

* `/files/token` → 上传凭证
* `/files/signed-urls` 可以接受，但也可以简化成 `/files/urls` + 参数 `{ "signed": true }`

---

### 6. **系统日志**

```
DELETE /logs
```

👉 **问题**：后端是批量删除（传 ID 数组），语义是 OK 的，但更 RESTful 的做法是 `DELETE /logs?ids=1,2,3`。
✅ 优化：前端传数组也可以接受。

---

### 7. **用户编辑**

```
PUT /users/<id>/profile
```

👉 **问题**：如果 profile 永远就是 user 的一部分，直接 `PUT /users/<id>` 更合理。`profile` 会让人以为是子资源。
✅ 优化：推荐直接 `PUT /users/<id>`。

---

# 📌 总结优化要点

1. **避免动词 URL**：`/read` `/enable` `/disable` → 改成 `PATCH /resource/<id>` + 状态字段。
2. **保持名词集合语义**：文件、通知、消息都尽量以资源表示。
3. **子资源 vs 参数**：像 “已点赞的评论” 这种，不要新起 URL，改为 query 参数更优雅。
4. **用户资料**：如果是 `users` 的属性，直接 `/users/<id>`，除非有复杂子对象。
