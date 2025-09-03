About
一个 Vue+Flask 前后端分离的社交平台
www.xx.com

---

## 关于：

本项目是基于狗书(Flask Web 开发)项目不断扩展而成。
狗书项目采用的是服务端渲染模式，但目前普遍采用前后端分离模式，所以前端改用 Vue，后端用 Flask， 用户身份验证采用 JWT，并加入很多新功能～ -补充狗书图片

在线体验：www.xx.com

## 前置工作：

**1.需要七牛云凭证, qq 邮箱授权码**

七牛云凭证共包含 4 项，包括 accesskey, secretkey,以及 bucket 和域名。

accesskey, secretkey 在个人信息中可以查到。Bucket 则是存储空间的名称，也就是新建存储空间时候输入的名字。如果是新用户，则找到对象存储，新建存储空间。如果没有域名，七牛云对每个存储空间分配了可使用 30 天的测试域名。有域名直接对存储空间进行绑定即可。

具体可参考如下文章：

[七牛云获取 qn（url、bucket、access-key、secret-key）\_教程-CSDN 专栏](https://download.csdn.net/blog/column/11693119/132181583)

qq 邮箱授权码的获取可参考如下文章：

[如何拿到 qq 邮箱服务授权码\_qq 邮箱授权码-CSDN 博客](<[如何拿到qq邮箱服务授权码_qq邮箱授权码-CSDN博客](https://blog.csdn.net/weixin_68846313/article/details/147430548)>)

**2.需要安装 mysql, redis**

## 开发环境：

前端：

```
1.克隆远程库： git clone xx
2.进入项目目录后，安装依赖: npm install
3.在项目根目录创建.env文件，将.env.example文件内容复制到.env中，然后修改对应变量的值
4.运行服务器: npm run dev
```

后端：

```
1.创建虚拟环境
2.cd blog_backend
3.pip install -r ./requirements/dev.txt
4.执行flask shell
5.进入到shell环境中后，执行 Role.insert_roles()；最后执行exit()退出shell环境
6.在项目根目录创建.env文件，将.env.example文件内容复制到.env中，然后修改对应变量的值
7.执行python flasky.py（redis需要提前启动，否则可能会报错）
```

注意： 步骤 4，5 只在第一次启动 Flask 应用时需要。后续启动只需要执行 `python flasky.py`

## 生产环境：

支持 docker 部署：

1.修改后端项目中 deploy.sh 文件 2.更改第一行： source /Users/v/Documents/proj/blog/blog_front/front.sh 为前端项目在本机的绝对位置 3.修改 remote_cmd_backend 命令中的环境变量值（参考前面写的修改.env 环境变量） 4.修改 ROMOTE_USER 和 ROMOTE_HOST 为远程主机的用户名和远程主机名（本项目中这两个变量存放在系统环境变量中，所以代码中未显式定义）

4.cd blog_backend 5.执行 ./deploy.sh 或者 bash ./deploy.sh 6.可访问云服务器 ip 地址+端口 （本项目中访问的端口是 1717，端口需要在云服务器上手动开放才能访问到）

## 内置功能：

- 注册，登录，上传用户图像、兴趣封面
- jwt 权限验证
- 修改密码/绑定邮箱支持邮箱验证码
- 发布文章（支持带图片，富文本）
- 评论，点赞文章
- 回复，点赞评论
- 用户间发送消息
- 关注用户
- @，评论，点赞，私信时 websocket 消息推送
- 普通用户，内容管理员（可禁用评论），管理员（可禁用评论）
- 评论敏感词过滤，图文请求限制次数
- 七牛云图片存储

## 预览页面：

## 技术栈：

前端：

- vue3

- vue-router

- pinia

- axios

- scss

- socket-io

- qiniu-js

后端：

- Flask

- Flask-JWT-Extended

- Flask-SQLAlchemy

- Flask-Limiter

- flask-socketio

- Celery

- redis

- mysql

七牛云凭证：存储用户图像，文章图片，资料卡兴趣图片

qq 邮箱授权码：账号邮件绑定，找回密码邮件验证

redis：充当 celery 异步任务的代理， 存储 websocket 用户状态， 存储邮件验证码, Limiter 请求次数限制

mysql：存储结构化数据

nginx：部署前端

docker：部署 Flask 应用、mysql、redis

| 环境             | 支持的功能                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------- |
| mysql            | 存储结构化数据                                                                              |
| redis            | 充当 celery 异步任务的代理， 存储 websocket 用户状态， 存储邮件验证码, Limiter 请求次数限制 |
| 七牛云凭证       | 存储用户图像，文章图片，资料卡兴趣图片                                                      |
| qq 邮箱授权码    | 账号邮件绑定，找回密码邮件验证                                                              |
| nginx            | 部署前端                                                                                    |
| docker(生产环境) | 部署 Flask 应用、mysql、redis                                                               |
