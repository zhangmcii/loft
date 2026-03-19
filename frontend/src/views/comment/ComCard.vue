<template>
  <div class="comment-section">
    <el-skeleton
      :loading="isLoading"
      animated
      :throttle="{
        leading: skeletonDelay,
        trailing: skeletonDelay,
        initVal: true,
      }"
    >
      <template #template>
        <div class="comment-header">
          <el-skeleton-item variant="text" style="width: 80px; height: 24px" />
          <el-skeleton-item variant="text" style="width: 120px" />
        </div>
        <div class="comment-skeleton">
          <div class="skeleton-comment-item" v-for="i in 2" :key="i">
            <el-skeleton-item
              variant="circle"
              style="width: 40px; height: 40px"
            />
            <div class="skeleton-content">
              <el-skeleton-item
                variant="text"
                style="width: 120px; margin-bottom: 8px"
              />
              <el-skeleton-item
                variant="text"
                style="width: 100%; margin-bottom: 6px"
              />
              <el-skeleton-item
                variant="text"
                style="width: 80%; margin-bottom: 8px"
              />
              <el-skeleton-item variant="text" style="width: 60px" />
            </div>
          </div>
        </div>
      </template>

      <template #default>
        <!-- <div class="comment-header">
          <h3 class="comment-title">评论区</h3>
          <div class="comment-count">共 {{ query.total }} 条评论</div>
        </div> -->

        <u-comment-scroll
          :disable="disable"
          @more="more"
          class="comment-scroll"
          :class="{ 'comment-scroll-disabled': disable }"
        >
          <u-comment
            ref="commentRef"
            :config="config"
            @submit="submit"
            @like="like"
            @mention-search="mentionSearch"
            @reply-page="replyPage"
            @show-info="showInfo"
            class="UComment"
          >
            <u-comment-nav
              v-model="latest"
              @sorted="sorted"
              class="comment-nav"
            ></u-comment-nav>
            <template #avatar="scope">
              <el-avatar
                alt="用户图像"
                :src="scope.user.avatar"
                class="comment-avatar"
              />
            </template>
            <template #operate="scope">
              <Operate
                :comment="scope"
                :post-author="props.postAuthor"
                @remove="remove"
              />
            </template>
            <template #card="scope">
              <UserInfo :scope="scope" :loading="loading" :config="config" />
            </template>
          </u-comment>
        </u-comment-scroll>

        <div v-if="query.total === 0" class="empty-comments">
          <van-icon name="comment-o" class="empty-icon" />
          <p>暂无评论，快来发表第一条评论吧！</p>
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import emoji from "@/config/emoji.js";
import Operate from "./components/CommentOperate.vue";
import UserInfo from "./components/UserInfo.vue";
import commentApi from "@/api/comment/commentApi.js";
import praiseApi from "@/api/praise/praiseApi.js";
import userApi from "@/api/user/userApi.js";
import imageCfg from "@/config/image.js";
import { useCurrentUserStore } from "@/stores/user";
import { loginReminder } from "@/utils/common.js";
import message from "@/utils/message";

const currentUser = useCurrentUserStore();
const props = defineProps({ postId: Number, postAuthor: String });
const emit = defineEmits(["count-change"]);
const config = reactive({
  user: {}, // 当前用户信息
  emoji: emoji, // 表情包数据
  comments: [], // 评论数据
  relativeTime: true, // 开启人性化时间
  show: {
    likes: true,
    level: false,
    address: false,
  },
  page: true, // 开启分页
  mention: {
    // 开启提交功能
    data: currentUser.userInfo.followed,
    alias: {
      username: "name",
    },
    showAvatar: true,
  },
});

config.user = {
  id: currentUser.userInfo.id,
  username: currentUser.priorityName,
  // level: 6,
  avatar: currentUser.userInfo.image
    ? currentUser.userInfo.image
    : imageCfg.logOut,
  // 评论id数组 建议:存储方式用户id和文章id和评论id组成关系,根据用户id和文章id来获取对应点赞评论id,然后加入到数组中返回
  // 存储已点赞的评论id
  likeIds: [],
};

// 用户信息是否加载
const loading = ref(false);
// 评论加载状态（用于骨架屏）
const isLoading = ref(true);
// 骨架屏延时配置（毫秒）
const skeletonDelay = 500;

const showInfo = (uid, finish) => {
  loading.value = true;

  userApi
    .getUser(uid)
    .then((res) => {
      if (res.code === 200) {
        const u = res.data;
        const userInfo = {
          username: u.name || u.username,
          level: 6,
          avatar: u.image,
          like: u.praised_count,
          attention: u.followed_count,
          follower: u.followers_count,
          id: u.id,
          isFollowed: currentUser.userInfo.followed.some(
            (item) => item.uName === u.username
          ),
          uName: u.username,
          nickname: u.nickname,
        };
        loading.value = false;
        finish(userInfo);
      } else {
        ElMessage.error(res.message || "获取用户信息失败");
        loading.value = false;
      }
    })
    .catch((error) => {
      loading.value = false;
      ElMessage.error("获取用户信息失败");
      console.error(error);
    });
};

// 提交触发搜索: 模拟请求接口返回搜索用户数据
const mentionSearch = (val) => {
  config.mention.data = currentUser.userInfo.followed.filter((v) =>
    v.name.includes(val)
  );
};
// 评论提交事件
const submit = ({ content, parentId, reply, finish, mentionList }) => {
  if (!currentUser.isLogin) {
    loginReminder("快去登录再发布评论吧");
    return;
  }

  const directParentId = reply === undefined ? null : reply.id;
  commentApi
    .submitComment(props.postId, {
      body: content,
      directParentId: directParentId,
      at: mentionList,
    })
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        finish(res.data);
        query.total++;
        ElMessage.info("评论成功!");
      } else {
        ElMessage.error(res.message || "评论失败");
      }
    })
    .catch((error) => {
      if (error === "请求频率超限") {
        ElMessage.warning("操作太快了，慢点点~");
      } else {
        ElMessage.error("评论失败，请稍后重试");
      }
    });
};

// 点赞按钮事件
const like = (id, finish) => {
  if (!currentUser.isLogin) {
    loginReminder("快去登录再点赞吧");
    return;
  }

  // 确保 likeIds 是数组
  if (!config.user.likeIds || !Array.isArray(config.user.likeIds)) {
    config.user.likeIds = [];
  }

  if (config.user.likeIds.findIndex((item) => item == id) == -1) {
    // 点赞
    praiseApi
      .submitPraiseComment(id)
      .then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          currentUser.addItemLikeIds(id);
          finish();
        } else {
          ElMessage.error(res.message || "点赞失败");
        }
      })
      .catch((error) => {
        console.error(error);
      });
  } else {
    // 取消点赞
  }
};

//请求回复分页
const replyPage = ({ parentId, current, finish }) => {
  commentApi
    .getReplyComment(parentId, current)
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        let tmp = {
          total: res.total || 0,
          // 分页提取回复
          list: res.data,
        };
        finish(tmp);
      } else {
        ElMessage.error(res.message || "获取回复失败");
      }
    })
    .catch((error) => {
      ElMessage.error("获取回复失败，请稍后重试");
      console.error(error);
    });
};

const query = reactive({
  current: 1, // 当前页数
  size: 10, // 页大小
  total: 0, // 评论总数
});
// 是否禁用滚动加载评论
const disable = ref(false);

// 请求接口请求加载更多评论
const more = () => {
  if (query.current <= Math.ceil(query.total / query.size)) {
    commentApi
      .getComment(props.postId, query.current)
      .then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          config.comments.push(...res.data);
          query.current++;
        } else {
          ElMessage.error(res.message || "加载评论失败");
        }
      })
      .catch((error) => {
        ElMessage.error("加载评论失败，请稍后重试");
        console.error(error);
      });
  } else {
    disable.value = true;
  }
};

//排序
const latest = ref(true);
const sorted = (latest) => {
  if (latest) {
    // 按最新时间排序（时间从新到旧）
    config.comments.sort(
      (a, b) => new Date(b.createTime) - new Date(a.createTime)
    );
  } else {
    // 按点赞数量排序（点赞数从高到低）
    config.comments.sort((a, b) => b.likes - a.likes);
  }
};

const commentRef = ref();
// 删除评论
const remove = (comment) => {
  if (!currentUser.isLogin) {
    loginReminder("请先登录");
    return;
  }

  showConfirmDialog({
    title: "删除确认",
    message: "确定要删除这条评论吗？删除后无法恢复。",
    confirmButtonText: "确定删除",
    cancelButtonText: "取消",
  })
    .then(() => {
      commentApi
        .deleteComment(comment.id)
        .then((res) => {
          if (res.code === 200) {
            ElMessage.success("删除成功");
            // 从列表中移除评论
            commentRef.value?.remove(comment);

            // 更新评论总数
            if (query.total > 0) {
              query.total--;
            }
          } else {
            ElMessage.error(res.message || "删除失败");
          }
        })
        .catch((error) => {
          if (error.response?.status === 403) {
            ElMessage.error("没有权限删除此评论");
          } else {
            ElMessage.error("删除失败，请稍后重试");
          }
          console.error(error);
        });
    })
    .catch(() => {
      // 用户取消删除
    });
};

let currentRequestId = 0;
function getComment() {
  isLoading.value = true;
  const requestId = ++currentRequestId;
  commentApi
    .getComment(props.postId, query.current)
    .then((res) => {
      if (requestId !== currentRequestId) {
        // 忽略非最新请求的结果
        return;
      }

      // 适配新的统一接口返回格式
      if (res.code === 200) {
        config.comments = [...res.data];
        query.current++;
        query.total = res.total || 0;

        // 如果评论为空或已经加载完所有评论，禁用滚动加载
        if (
          query.total === 0 ||
          query.current > Math.ceil(query.total / query.size)
        ) {
          disable.value = true;
        } else {
          disable.value = false;
        }
      } else {
        ElMessage.error(res.message || "获取评论失败");
      }
    })
    .catch((error) => {
      // ElMessage.error('获取评论失败，请稍后重试')
      message.error("获取评论失败，请稍后重试");
      console.error(error);
    })
    .finally(() => {
      isLoading.value = false;
    });
}
function has_praised() {
  praiseApi
    .has_praised_comment_ids(props.postId)
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        config.user.likeIds = [...res.data];
      } else {
        ElMessage.error(res.message || "获取点赞状态失败");
      }
    })
    .catch((error) => {
      // ElMessage.error('获取点赞状态失败，请稍后重试')
      message.error("获取点赞状态失败，请稍后重试");
      console.error(error);
    });
}
watch(
  () => props.postId,
  () => {
    // 重置状态
    config.comments = [];
    // 一定要重置页码。否则导致请求的页码不正确，返回的数据为空数组
    query.current = 1;
    query.total = 0;
    disable.value = true; // 初始状态禁用，等数据加载后再启用
    isLoading.value = true;

    // 立即请求评论数据，不使用 setTimeout
    getComment();
    if (currentUser.isLogin) {
      has_praised();
    }
  }
);

watch(
  () => query.total,
  (newVal) => {
    emit("count-change", Number(newVal) || 0);
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.comment-section {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

// .comment-header {
//   display: flex;
//   justify-content: space-between;
//   align-items: center;
//   margin-bottom: 20px;
//   padding: 0;
// }

.comment-title {
  font-size: 17px;
  font-weight: 600;
  color: #151515;
  margin: 0;
}

.comment-count {
  font-size: 13px;
  color: #8a8a8a;
}

.comment-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .skeleton-comment-item {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-radius: 0;
  }

  .skeleton-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
}

.comment-scroll {
  &.comment-scroll-disabled {
    :deep(.scroll-btn) {
      display: none !important;
    }
  }
}

.UComment {
  padding: 0;

  :deep(.u-comment-box) {
    border-radius: 0;
    box-shadow: none;
    border: 1px solid #ececec;
    background: #fff;

    .u-comment-textarea {
      border-radius: 0;
      border-color: #e6e6e6;
      color: #222;

      &:focus {
        border-color: #111;
        box-shadow: none;
      }
    }

    .u-comment-submit {
      background-color: #111;
      border-radius: 0;
      border: 1px solid #111;

      &:hover {
        background-color: #222;
      }
    }
  }

  :deep(.u-comment-item) {
    padding: 14px 0;
    margin-bottom: 0;
    border-radius: 0;
    background-color: transparent;
    border-bottom: 1px solid #efefef;
    transition: none;

    &:hover {
      background-color: transparent;
    }
  }

  :deep(.u-comment-content) {
    color: #222;
    line-height: 1.8;
  }

  :deep(.u-comment-info),
  :deep(.u-comment-time),
  :deep(.u-comment-username),
  :deep(.u-comment-action) {
    color: #7d7d7d;
  }

  :deep(.u-comment-like),
  :deep(.u-comment-reply) {
    color: #6f6f6f;
  }
}

.comment-avatar {
  border: 1px solid #ececec;
  box-shadow: none;
}

.comment-nav {
  margin-bottom: 18px;

  :deep(.u-comment-nav-item) {
    padding: 4px 0;
    margin-right: 18px;
    border-radius: 0;
    color: #8a8a8a;

    &.active {
      background-color: transparent;
      color: #111;
      font-weight: 500;
    }
  }
}

.empty-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0 24px;
  color: #8d8d8d;

  .empty-icon {
    font-size: 40px;
    margin-bottom: 12px;
    color: #d6d6d6;
  }

  p {
    font-size: 14px;
    margin: 0;
  }
}

@media (max-width: 768px) {
  .comment-section {
    margin-top: 0;
    padding-top: 0;
  }

  .comment-title {
    font-size: 16px;
  }

  .comment-count {
    font-size: 12px;
  }

  .comment-skeleton {
    .skeleton-comment-item {
      padding: 10px 0;
    }
  }

  .UComment {
    :deep(.u-comment-item) {
      padding: 12px 0;
    }
  }
}
</style>
