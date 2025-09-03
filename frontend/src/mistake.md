`tag标签页` 加`下拉刷新` 的 `列表`
问题现象： 切换标签页时，会多请求一次数据，导致展示双倍数据
～～～
onClickTab() {
this.currentPage = 1
this.getFollowList()
}
～～～

解决： 1.监听点击 tag 标签时不发出数据请求。因为列表的 finished 为 false，会自动请求一次，当你监听点击 tag 标签时发出的网络请求会多余。
～～～
onClickTab() {
this.currentPage = 1
}
～～～

2.不同 tag 页的列表要用不同的 finished 变量。公用一个 finished 变量时，第一页加载完成后切换到第二个 tag 页，第二页得到的 finished 为 true，导致停止加载。
～～～
<van-tab>
<FollowsList2
          v-model:finished="fanTab.finished">
</FollowsList2>
</van-tab>
<van-tab title="关注" name="followed">
<FollowsList2
          v-model:finished="followedTab.finished">
</van-tab>
～～～

在 data 中直接使用 props 会导致数据的重复和不一致。
背景：父组件 A 挂载完成对请求回的数据传递值给子组件 B，B 在路由进入前发送请求，把请求欧的数据给子组件 C
问题现象:C 在 data 中把 props 赋值给变量，props 的 post.praise 更新了，但 C 模版表达式值未同步变化

```
 props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          body: '文章',
          body_html: null,
          timestamp: '2024-9-20 12:14:00',
          author: '张三',
          commentCount: 20,
          disabled: false,
          image: '',
          praise_num: 0,
          has_praised: false
        }
      }
    },
 }
  data() {
    return {
      praiseNum: this.post.praise_num,
      hasPraised: this.post.has_praised
    }
  }

  <el-text class="mx-1">{{ praiseNum }}</el-text>
```

解决：在子组件创建一个局部状态来存储 props 值，使用 watch 监听 props，同时更新局部状态
结论：不要在 data 中使用 props,这个 props 并不因此具有响应性
参考：https://www.51cto.com/article/801688.html

子组件初始化 watch 监听不到 props 值：
背景：父组件 A 挂载完成对请求回的数据传递值给子组件 B
现象：父组件 A 传递值给子组件 B，子组件第一次展示模版监听值不发生变化
～～～
props: {
post: {
type: Object,
default() {
return {
id: 1,
body: '文章',
body_html: null,
timestamp: '2024-9-20 12:14:00',
author: '张三',
commentCount: 20,
disabled: false,
image: '',
praise_num: 0,
has_praised: false
}
}
},
}

watch:{
'post.has_praised'(newValue) {
console.log('22', newValue)
this.hasPraised = newValue
},
}
～～～

解决：设置 immediate：true 在创建侦听器时立刻执行一次回调
～～～
'post.has_praised':{
handler(newValue){
this.hasPraised = newValue
},
immediate:true
}
～～～

结论：1.父组件 A 传递值给子组件 B，子组件模版监听值不发生变化
2.watch 可以监听到网络请求后值的变化

撤回提交
撤销本次提交，暂存区也撤销，但保留工作区的修改
～～～
git reset --mixed HEAD^

如果想撤销上上次提交，可以使用 HEAD^^，或者 HEAD ～ 2

点赞动画
消失的组件对应 leave 动画
即将出现的对应 enter 动画

所以： 未点赞组件对应 leave ，已点赞组件对应 enter

element-plus 表格设置表头行或者单元格样式
解决：样式需要加 :deep(), 即影响到子组件
～～～
<el-table
    :header-cell-class-name="tableHeadStyleName"
  />

tableHeadStyleName({ row, column, rowIndex, columnIndex }){
return 'table-header'
}

# 重点

:deep(.table-header) {
color: #333333;
}

# 前端有哪些性能优化手段 开启压缩优化（gzip、brotli 格式）

gzip: 是 GNUzip 的缩写，也是一个文件压缩程序，可以将文件压缩进后缀为.gz 的压缩包。
如果服务端支持 gzip 算法，则会返回以下的响应头： content-encoding: gzi

brotli： Brotli 通过变种的 LZ77 算法、Huffman 编码以及二阶文本建模等方式进行数据压缩，与其他压缩算法相比，它有着更高的压缩效率。支持 Brotli 压缩算法的浏览器使用的内容编码类型为 br
如果服务端支持 Brotli 算法，则会返回以下的响应头： Content-Encoding: br

## 谁来做这个压缩？ (服务端 or 用户端)

我们的例子是在接到请求时，由 node 服务器进行压缩处理, 这也是比较普遍的一种做法，由服务端进行压缩处理。
服务器了解到我们这边有一个 gzip 压缩的需求，它会启动自己的 CPU 去为我们完成这个任务。而压缩文件这个过程本身是需要耗费时间的，大家可以理解为我们以服务器压缩的时间开销和 CPU 开销（以及浏览器解析压缩文件的开销）为代价，`省下了一些传输过程中的时间开销`。

我们现在讨论的就是构建时进行压缩，可以省去服务器压缩的时间，`减少一些服务端的消耗`。
所以构建时压缩可以： 减少 `服务端+传输过程中` 的时间开销

使用 vite-plugin-compression 对平台进行 gzip 或者 brotli 压缩

参考：https://juejin.cn/post/6844903887871148046

# 开发模式下 页面打开时出现重新加载并强制刷新页面的情况

现象:

```
1.new dependencies optimized: element-plus/es/components/loading/style/css, element-plus/es/components/table/style/css, element-plus/es/components/table-column/style/css

2.new dependencies optimized: vant/es/share-sheet/style/index, vant/es/list/style/index
17:37:30 [vite] ✨ optimized dependencies changed. reloading
```

原因:未能有效完成 vite 预构建
解决： 1.在 main.js 中引入 vant 样式
～～～
import 'vant/lib/index.css';
2.element-plus 的自动引入不稳定。改为手动全局引入。

主机免密传送文件到云服务器
1、原理：
将公钥拷贝到需要免登录的设备，私钥是自己的
通过用户名和主机名来核对公钥

A(公钥，私钥) --> B（A 的公钥）

2、 生成登录公钥私钥对

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

命令参数含义与之前介绍的相同。执行过程中，系统会提示你选择保存密钥的位置，默认路径是 `~/.ssh/id_rsa`，直接回车即可。如果你不想设置密码短语（即私钥的保护密码），在提示输入时直接回车两次。

### 上传公钥到云服务器

有两种常见的方法可以将 Mac 电脑生成的公钥上传到云服务器：

#### 手动操作

1. 在 Mac 的终端中，查看公钥文件内容：

```bash
cat ~/.ssh/id_rsa.pub
```

2. 全选并复制上述命令输出的公钥内容。

3. 通过 SSH 登录到云服务器。打开一个新的终端窗口，运行：

```bash
ssh username@server_ip
```

4. 登录到云服务器后，创建或编辑 `~/.ssh/authorized_keys` 文件。如果不存在 `.ssh` 目录，先创建该目录：

```bash
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
```

5. 在打开的 `nano` 编辑器中，粘贴从 Mac 复制的公钥内容。粘贴完成后，按 `Ctrl + X`，然后按 `Y`，再按 `Enter` 保存并退出编辑器。

### 验证免密传输

完成上述操作后，在 Mac 电脑上使用 `scp` 命令尝试向云服务器传送文件，例如：

```bash
scp /path/to/local_file username@server_ip:/path/to/remote_directory
```

# mac 传后端容器到服务器执行报错了（但 windows 不报错）

> unable to start container process: exec: "./boot.sh": permission denied: unknown.

根因： mac 直接直接独对 boot.sh 文件就无权限执行，打包成镜像在服务区上也无权限执行。所以在打镜像前，赋予 boot.sh 可执行权限
解决： chmod +x boot.sh

评论+通知模型+：

场景： A 发了文章，B 评论， C 回复了 B， D 回复了 C。  
结果：
B 的操作，会通知 A
C 的操作，会通知 A，B
D 的操作，会通知 A，B，C

前端：

首页会从数据库拉取该用户所有未读的通知。统一对通知分为四类： @，评论，点赞，私信，随后传递到各组件中。

如何对通知分类？ 1.筛选出@的用户
type=at 2.筛选出评论文章还是评论回复？
3.1 type =“comment 是评论文章
3.2 type=“reply”是评论回复 3.筛选出文章点赞还是评论点赞？
筛选出 type =“like”
2.1 当 commentId 为 None 时，是文章点赞。
2.2 当 commentId，postId 都不为 None 时，是评论点赞 4.筛选出聊天
type=chat
只统计出同一对用户的未读的数量和最近的一条信息（前端预览需要）

定义用户的评论分为三类：根评论， 一级回复， 其他回复
￼

根据 undraw-ui 评论组件， 从 submit 函数的回调函数中结构出 reply 变量。当你发起的是根评论，reply 对象为 undefined；当发起的是一级回复或其他回复时，reply.id 为直接父评论 id

所以当用户发起
根评论： 传递的 directParentId 字段为 null
一级评论或其他回复： 传递的 directParentId 字段就等于 reply.id

后端：
当用户发起了评论或回复，如何正确的通知到对应用户？ 1.接收到 directParentId 字段，根据 directParentId 查询数据库，得到直接父评论对象和根评论对象(因为所有的评论或回复都从属于一个根评论，要么是空值要么是其他评论对象罢了。) 2.根据 directParentId 字段，判断这个评论是哪种类型？（根评论 或一级回复 或 其他回复）
2.1 根评论： directParentCommentId =parentCommentId =None
2.2 一级回复：directParentComment != None && (directParentComment = parentComment)
2.3 其他回复：directParentComent != parentComment 3.如果是
3.1 根评论：
预执行：通知文章作者（产生一条通知）
当前不是文章作者：
通知文章作者 有人评论了你的文章
3.3 一级回复：
预执行：通知文章作者、根评论（产生两条通知）
当前不是文章作者：
通知文章作者 有人评论了你的文章
当前不是根评论用户：
通知根评论用户 有人回复了你的评论
3.4 其他回复:
预执行：通知文章作者、根评论用户、直接父评论用户（产生三条通知）
当前不是文章作者：
通知文章作者 有人评论了你的文章
当前用户不是根评论用户
通知根评论用户 有人回复了你的评论
当前用户不是直接父评论用户
通知直接父评论用户 有人回复了你的评论
这样做的目的遵循一个原则，就是自己执行的操作不能通知自己。比如说 A 用户评论了 B 的文章，那么 B 用户会一定会收到一条通知： A 评论了你的文章。 A 用户作为触发方是不会收到通知的。

mysql：

class Comment(db.Model):
**tablename** = 'comments'
id # 评论 id
body # 评论内容
timestamp # 时间戳
disabled # 是否禁用
author_id # 用户 id
post_id # 文章 id
root_comment_id # 根评论 Id
direct_parent_id # 直接父评论 id

class Notification(db.Model):
**tablename** = 'notifications'
id # 通知 id
type # 通知类型
is_read # 是否已读
created_at # 创建时间
receiver_id # 接收者（文章作者）
trigger_user_id # 触发者（评论/点赞用户）
post_id # 文章 id
comment_id # 评论 id

# 上传图片：

假设最好的情况，就是上传过程中一切顺利。(最好限制一下图片的数量为三个以内，降低风险)
做法： 上传完图片后，拿到图片的 URL，然后跟随文字一起送到后台

真实过程可能出现的问题： 1.上传多张图片
如果任意一个图片失败会造成不可管理的后果。前面几张上传成功了，中间一张失败，那么这个文章不会保存到数据库，但前面几张已存入云端
(这个想了一下，也好解决。无非抽个工具管理类，记录过程中失败的图片，增加失败重传机制，使不可靠变为可靠。重试次数用完，删除已上传的图片。并通知用户“图片上传异常，请稍候再试”)

2.文字失败：
重试机制：
重试次数用完，删除所有已上传图片，并通知用户“图片上传异常，请稍候再试”

3.发布次数超出限制 （已实现）
收到 429 状态码后，删除指定 key 的图片

目前这些预防措施待实现

原来想法：
想法一：将文章文字加在 qiniu.upload()的 Extra 参数中随图片一起上传到七牛云，图片上传成功后，会将成功消息和文字通过回调请求发送给后端服务器，后端服务器拿到文字和 url 数据会存入数据库。

但发现七牛图不支持一个 post 请求上传多张图片, 这样会导致上传 9 张图片，会发送给后端服务器 9 个回调请求。不得不放弃这种想法。

想法二：
发布图文时分两次提交
第一次提交文字，在数据库生成图文记录，假设 id=10。
若第一次提交文字失败，退出函数。
若第一次提交文字成功：
上传图片至七牛云。
若上传失败，通知用户稍后再试，并删除数据库中 id=10 的记录
若图片上传成功，第二次提交图片 url，设置图片 url，并且修改 id=10 的图片状态为已提交

前端渲染：
当种类=图文，并且图片状态=已提交 才返回给前端。
定期清理 种类=图文，并且图片状态=未提交 的数据

图片存储及命名
图片在七牛云上按业务逻辑存储：
user*image/user*${this.currentUser.userInfo.id}/article/*.png  文章图片
user_image/user_${this.currentUser.userInfo.id}/avatars/_.png 用户图像
user*image/user*${this.currentUser.userInfo.id}/backgrounds/_.png 背景图片
user*image/user*${this.currentUser.userInfo.id}/comments/\*.png 评论图片

图片命名规则： 1.使用 uuid(目前采用) 2.包含关键信息 user*{user_id}*{时间戳(精确到时分 即可)}_{场景}\_image_{版本(如 v1)}.png

图片预处理： 1.上传前压缩处理

安全设置：
对于敏感的用户图片，如私人相册，将储存桶设置为私有，听过生成带签名的 URL 来控制访问权限 (目前无此需求)

# Base64 编码

应用：常用于传输图片或音频文件。

定义：Base64，就是包括小写字母 a-z、大写字母 A-Z、数字 0-9、符号"+"、"/"一共 64 个字符的字符集，（任何符号都可以转换成这个字符集中的字符，这个转换过程就叫做 base64 编码

# 压缩上传

用户选择了图片后，客户端立刻进行压缩 1.用户第一次选择 1 张图片 --> 客户端压缩并展示
第二次选择 2 张不同的图片 --> 客户端压缩并展示

    用户删除最后一张图片 --> 触发移除事件 --> 移除该原始图片和压缩的图片
    由于是3张不同名称的图片，一切正常

2.用户第一次选择 1 张图片 --> 客户端压缩并展示
第二次选择 2 张图片，其中 1 张与第一次选择的相同 --> 提示不能上传同名文件，但客户端仍然压缩并展示

    用户删除第2张图片 --> 触发移除事件 --> 第一张和第二张都移除了，因为它们的名称相同 (这是我们不想看到的情况)

3.不能上传同名文件
当用户点击发布后，将压缩后的图片上传至七牛云

# 书架

前端 1.资料页展示最近在看的电影
以卡片+文字形式展示

2.用户通过编辑资料
用户编辑资料时，页面会自动加载已有的电影封面。
若已有的电影封面数量为 0，则相当于步骤 2.1
若已有的电影封面数量不为 0：
若数量 = 3 , 则满了。用户可以删除，可以全选删除。然后上传新的电影封面和文字
若数量 < 3 , 未满。用户可以删除，可以全选删除。也可以新增电影封面

2.1 初始化： 最多上传 3 张图片
选择电影封面和对应的文字
客户端上传完成后，可以点击预览。
当用户确认预览无问题后，点击上传，会将封面上传直七牛云，并且 url 以及名称保 存至后端
2.2 删除某一张封面
删除七牛云图片和数据库中该 url

2.3 新增封面
保存至七牛云和数据库

后端：
已有用户模型

1.新增图片模型

2.增加”图片顺序”字段
其实不用。可按照主键递增确认顺序

书架和个性签名有什么不同呢，只不过多了图片罢了。
把图片想象成 3 个文字，这 3 个文字有顺序，可删，增 即可

编辑封面 UI：
点击”新增”按钮(不点击新增，不出现该对上传编辑组件)：
每个 el-upload 组件与 el-input 成对出现。el-upload 限制只能上传一张图片，el-input 在下面。
上传块可以点击删除，移除

# 表单的 formData 对象存在的意义

formData 对象可以包含文件对象和其他二进制数据，使得在文件上传场景中非常适用
场景： 表单中需要上传文件时
虽然直接使用 json 传递表单数据也可以，但包含文件时，json 格式不支持处理二进制。

兴趣展示 完成：4.26 ～ 5.14

前端：
1.tabs 组件展示图片 2.点击上传后跳转到上传图片页面。上传到图片会覆盖已有的图片，每次上传当作一次覆盖上传。

后端： 1.增加图片模型 2.增加 将 url 保存到数据库的接口。
2.1 根据用户 id 和图片类型查询图片模型已有的记录，得到已有的图片 key 后，删除七牛云上的图片。
2.2 保存新上传的图片 key 到数据库 3.查询用户资料接口 增加 interest 字段，该字段保存着兴趣封面 url

目前有文章图片上传，兴趣图片上传，图片上传

originalFiles: [], //原始文件
compressedImages: [], //压缩后的文件
在选择本机图片后，会立刻进行压缩。当选择删除时，会移除源图像和对应的压缩图片。
最后在点击发布或者上传按钮时，统一上传图片到七牛云。

# 用户 Tags： 多对多关系

用户设置标签页面时，请求 tags 表所有 tag 展示。
当用户选择了 3 个标签后，后段会在 User 表的 tag 字段设置该用户对应的标签
当用户删除修改已选择的 tag 呢？

解决： 把最终结果和用户已有的 tags 作交集对比，

假设原始 A，结果 B，设置一个待删除，一个待添加的列表
原理：
B-A： 待添加的
A-B：待删除的

举例：
A：{1,2}, B:{1,2,3}
很显然，用户在原有基础上增加了一个 tag3,  
B-A=3 代表待添加的。
A-B={}代表待删除的。可以

A：{1,2,3}, B:{1,2}
很显然，用户在原有基础上删除了一个 tag3,  
B-A={}代表待添加的。
A-B=3 代表待删除的。 可以

A：{1}, B:{2,3}
很显然，用户在原有基础上删除了一个 tag1, 并且添加了新的 tag2 和 tag3。
B-A={2,3}, 代表待添加的
A-B={1},代表待删除的。 可以

综上，可以。最后对非空的列表，发往后端的对应的操作

资料页展示时，返回的 json 会包含用户的 tags。

默认的 tag 内容和数量，后期对 tag 的增加或删除该怎么做？由管理员来维护？

# 社交地址比如 B 站，github 地址用一个 json 类型字段，方便后续可能的扩展。

可更换的背景图片地址，这个直接在前端写死，还是在后端保存

先前端写死吧

重构编辑资料页面：
路由变化： 编辑资料只有当前用户才能进入。所以，页面路由不再携带用户 id 参数
删除 beforeRouteEnter 钩子
去除进入骨架屏效果

获取所有用户标签函数调用时机改在打开 tag 面板时候。

# 用户资料页：

路由变化： 1.使用 pinia
好处是减少请求次数
坏处代码需要大改

2.还是加载时请求用户信息
好处是不用改代码
坏处是请求次数增多

方法 1 行不通。 pinia 存储的是登录返回的用户信息字段，是非全量数据，仅靠 pinia 中的用户数据是无法应对资料页，所以还是页面加载时单独请求。

方法 2 是一直采取的方法，请求到用户数据后，更新 pinia, 并且保存一份给本地变量 user。后续都从 user 中取得数据。 保留

注册用户默认背景怎么解决？ 解决

交给前端。
在当前用户和非当前用户中设置默认图像字段，当用户的背景图片字段为空时，自动采用默认图像。 解决

还得加上图像等待的逻辑。 解决

获取用户数据的回调中，不能简单将数据赋值给 pinia 的当前用户，会将游客变为已登录用户。 解决
为了解决这个问题，可以加一个判断逻辑，
if 已登录&&是当前用户时，才赋值。
else 跳过

为什么一定要赋值给 pinia，因为可以保证编辑资料页时不用发送请求。 解决

后端 @main.route('/user/<username>')该路由没有遵循函数功能单一职责原则，它本来是获取用户博客文章的函数，又兼返回用户资料。
导致后续文章分也请求时，也会返回用户资料。前端对获取到用户资料后的逻辑只需在首次获取后执行一遍即可，但现在后续都会被重复执行。
现在要将该函数变成职责单一。 解决

用户资料页优先使用 pinia 中数据 解决
进入自己资料页：currentuser 保存自己的， otherCurrentUser 也保存自己的信息

进入别人资料页：currentuser 不设置， otherCurrentUser 保存别人的信息

所以，在模版中直接使用 otherCurrentUser 对象来渲染即可。

-> 有个问题,编辑资料返回主页，修改的信息不变化，除非模版用的是 currentUser
解决办法： 写 currentUser 时，同时写入 otherUse 对应字段. 代码性能开销几乎不计，存储开销也很少，因为字段很有限

界面加载后，先判断
if otherCurrentUser.username !== route.params.userName，
则请求后端。把请求结果赋值给 otherCurrentUser
else
user = otherCurrentUser
等于则用 pinia 中的，不请求。

必须用 pinia 的，不能用该页 js 的我全局变量，因为每次打开时会消失
这样做，不会每次打开或者返回该页面时都有加载现象。

用户资料页还是放进 layout 合理，可以享受缓存，而且返回首页式，首页也不用加载，也有函数也不用每次加载。 解决
但需要调整布局样式了。

# 反向代理

目前没有设置反向代理，前端直接用 ip 返回后端接口，更近一步，用户反问前端是通过 nginx 代理的，但前端到后端是**直接访问的服务器，并未经过 nginx**（已查询 nginx 日志验证过）.

下面是 axios 基址的配置
const $http = axios.create({
baseURL: requestUrl.baseUrl + ':' + requestUrl.backendPort,
timeout: 10000
})
可以看出，基址直接用的 ip+端口，所以每次返回后端都是直接用的 ip
当前端查询文章数据时，发出查询：https://xxx.com:4289/?page=1&tabName=all

现在要把基址改为/api, 通过 vite 本地服务器进行代理到正在的后端
现在发出查询：https://localhost:5172/api/?page=1&tabName=all
会被代理到：https://xxx.com:4289/?page=1&tabName=

成功了！

我原以为要在后端接口前统一加上/api, 原来这个代理是在前端做功夫， 设置/api 为后端入口，由代理服务器进行转发到真正的后端地址处。这会让用户觉得/api 是后端入口，做到了反向代理。

生产环境中，我以为反向代理到后端也用 https，实际情况是用 http 返回后端。

为什么 Nginx 到后端用 HTTP？
SSL 终止（SSL Termination）
Nginx 作为前端的入口，负责处理 HTTPS 加密和解密（SSL 终止），之后与后端的通信可以使用普通 HTTP。这样做的好处是：
减少后端服务器的加密解密负担（尤其对高并发场景）。
集中管理 SSL 证书（只需在 Nginx 配置，无需在每个后端服务配置）。
简化后端配置
后端服务无需关心 HTTPS 细节，只需专注业务逻辑，降低部署和维护成本。

总结
推荐配置：Nginx 处理 HTTPS（前端 → Nginx 用 HTTPS），Nginx → 后端用 HTTP，并通过 X-Forwarded-Proto 告诉后端实际协议。
优势：简化配置、降低后端负担、集中管理 SSL。

代理 websocket:

踩坑点：
开始的写法：
'/socket.io/': {
target: `${loadEnv(mode, process.cwd()).VITE_SERVE}`,
changeOrigin: true,
rewrite: (path) => path.replace(/^\/socket.io/, ''),
ws: true, // 启用 WebSocket 代理
}

我在请求路径上根本没写 socket.io，他是所有请求都默认加上的，所以在做代理时就用他来做代理路径（不是可以，是唯一，如果你在创建 socket 的请求使用其他路径来做代理，那不好意思，会发生错误，错误一般是 invaid namespace）。

我们已经知道 socket.io 会在所有请求中加上前缀"/socket.io/"，所以我们在代理时将它去掉，但这会引发错误，导致链连接失败。
正确的做法是，保留"/socket.io/"，换句话说就是 什么也别干

'/socket.io/': {
target: `${loadEnv(mode, process.cwd()).VITE_SERVE}`,
changeOrigin: true,
ws: true, // 启用 WebSocket 代理
}

你上面说要把 websocket 的 http 换成 https, 又说反向代理后依然用 http 返回后端， 这不是冲突了吗
不冲突，这是两个不同的通信环节，需要区分清楚 “客户端 ↔ Nginx” 和 “Nginx ↔ 后端服务器” 这两个链路的协议：

心区别：两个通信链路
通信链路 协议选择 作用
客户端（浏览器）→ Nginx HTTPS（wss://） 保证公网传输的安全性（加密）
Nginx → 后端服务器 HTTP（ws://） 内部网络通信，无需重复加密（高效）

现在返回 io(http://xx.com) 会代理到 http:后端//

主要是在前端 axio 设置基址，代理基址
socket 是在代理'/socket.io/'即可

就这样简单 解决

# 注册时随机指定一个图像

点击注册后按钮后，
请求后端得到图像库数组。
随机选择一个 url 为当前用户图像 image。
提交注册信息，包括 image 字段到后端。

# 关注 tab 的红点

当用户发布文章时，会推送消息给粉丝。自己发布的文章，不会推送给自己
这个消息不会出现在粉丝的通知中，但会出现使粉丝的关注 tab 出现小红点
当用户切换到关注的 tab 后，会向后端发送所有文章已读，小红点消失

每次打开首页时，同样会拉取未读的关注消息

# 将图片上传逻辑抽成功能函数

## 用户图像上传：

选择后自动上传
定义：
data(){
uploadToken: '',
imageKey: [],
imageUrls: [],

    // 原始文件
    originalFiles: [],
    // 压缩后的文件
    compressedImages: []

}
压缩选择的图像。 compressImages()

上传至七牛云。 uploadFiles()
需要：已压缩的图片， 图片存储地址，token（可以放在函数内一起完成）
返回：key 数组， 完整 url 数组

url 保存至后端。 submitAvatars()
需要：图像的 key 数组

## 文章图片上传：

选择后后立刻压缩，点击按钮才会执行上传

data(){
uploadToken: '',
imageUrls: [],
imageKey: [],

      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
      // 默认压缩比率为80%
      compressedRatio: 80

}

压缩选择的图像。compressImages()
上传图片。uploadFiles()
需要：已压缩的图片， 图片存储地址，token
返回：key 数组， 完整 url 数组
url 保存至后端。 submitBlog()
需要：图片的 key 数组

## 兴趣图片上传

选择后后立刻压缩，点击按钮才会执行上传

data(){
uploadToken: '',
// 上传成功后得到的 key
imageKey: [],
// 上传成功后完整的 url
imageUrls: [],

      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
      // 默认压缩比率为80%
      compressedRatio: 80,

}

压缩选择的图像。compressImages()
上传图片。uploadFiles()
需要：已压缩的图片， 图片存储地址，token
返回：key 数组， 完整 url 数组
url 保存至后端。 submitBlog()
需要：图片的 key 数组

## md 文章图片上传

选择后后立刻压缩，点击按钮才会执行上传
data(){
uploadToken: '',
imageUrls: [],
imageKey: [],

      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
      // 默认压缩比率为80%
      compressedRatio: 80

}
压缩选择的图像。compressImages()
上传图片。uploadFiles()
需要：已压缩的图片， 图片存储地址，token
返回：携带 pos 位置的 key 对象数组， 完整 url 数组
url 保存至后端。 richEditorPublish()
需要：图片的 key 数组

# elementPlus 的回到顶部组件不显示

原因：如果是简单的页面，直接使用那没问题但遇到复杂的大项目时组件之间的嵌套会特别深，再加上各种 div 的包裹，回顶组件通常无法生效了。这里出现问题的关键在于 target 属性。
**target 要指向触发滚动的对象——通俗来讲即这个滚动条到底是哪个最外侧组件的。**
问题来了实际开发中项目复杂，页面层级嵌套巨多。这时该如何快速定位到滚动的对象是哪个呢

```
//把下边的代码粘贴到浏览器Console中敲回车，然后滚动界面，它会输出滚动的元素
function findScroller(element) {
    element.onscroll = function() { console.log(element)}

    Array.from(element.children).forEach(findScroller);
}

findScroller(document.body);
```

解决： 1.要写于最外层块级区域的第一行，不可写于代码末尾。 2.指定 target 为外层的滚动条 class

```
 <el-backtop target=".scrollbar-container" :right="20" :bottom="100" />
```

参考：https://juejin.cn/post/7272283132664365112?searchId=202508152049008F48141D136848CE3AD0

# 后端 docker 容器日志挂在到宿主机目录

```
mkdir -p /var/log/loft
chmod 777 /var/log/loft
docker run -v /var/log/loft:/home/flasky/logs
```

注意：不要直接挂载到宿主机的/root 目录下
把目录挂载到了 /home/flasky/logs，但宿主机目录是在 /root/...，root 用户才能写，而容器里的进程不一定是 root。
