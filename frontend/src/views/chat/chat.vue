<!--
  注意： 
        1.看了源码，UChat组件挂载后会自动执行一次loadMore函数。所以loadMore函数包含了第一次加载的聊天记录
        2.返回的聊天记录不可以直接赋值给config.data。
          而是把已分页的数据传给finish()回调函数（底层应该是自动帮我们拼接给config.data）
        3.config.data中的id没什么用。界面是按数组顺序排列的，靠前的数组是最近发送的消息
-->
<template>
  <u-chat
    :config="config"
    style="max-height: 83vh"
    @load-more="loadMore"
    @submit="submit"
  >
    <template #header>
      <PageHeadBack :title="otherUser.priorityName" />
    </template>
  </u-chat>
</template>
<!-- 
  满屏高度： height:45vh; 
  无数据：   height:83vh
  所有尺寸： height:83vh
-->
<script setup>
import { reactive, onMounted } from "vue";
import { UChat } from "undraw-ui";
import chatApi from "@/api/chat/chatApi.js";
import emoji from "@/config/emoji.js";
import imageCfg from "@/config/image.js";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
const currentUser = useCurrentUserStore();
const otherUser = useOtherUserStore();

const config = reactive({
  user: {
    id: currentUser.userInfo.id,
    username: currentUser.priorityName,
    avatar: currentUser.userInfo.image
      ? currentUser.userInfo.image
      : imageCfg.logOut,
  },
  data: [],
  emoji: emoji, // 可选
});
const query = reactive({
  current: 0, // 当前页数
  size: 15, // 页大小
  total: 0, // 评论总数
  real_time_receive: false,
});
onMounted(() => {
  currentUser.enterChat(otherUser.userInfo.id);
  currentUser.socket.on("new_message", (msg) => {
    if (currentUser.activeChat === msg.sender_id) {
      query.real_time_receive = true;
      config.data.push(msg);
    }
    query.real_time_receive = false;
  });
});
function loadMore(finish) {
  // 打开页面第一次加载
  if (!query.current) {
    chatApi.getMessageHistory(otherUser.userInfo.id, 1).then((res) => {
      if (res.code === 200) {
        finish([...res.data]);
        if (res.total !== undefined) {
          query.total = res.total;
        }
        query.current = 2;
      }
    });
  } else if (query.current <= Math.ceil(query.total / query.size)) {
    chatApi
      .getMessageHistory(otherUser.userInfo.id, query.current)
      .then((res) => {
        if (res.code == 200) {
          query.current++;
          finish([...res.data]);
        }
      });
  } else {
    finish([]);
  }
}

function submit(val, finish) {
  let chat = {
    content: val,
    uid: currentUser.userInfo.id,
    user: {
      username: currentUser.priorityName,
      avatar: currentUser.userInfo.image
        ? currentUser.userInfo.image
        : imageCfg.logOut,
    },
    createTime: new Date(),
  };
  currentUser.sendMessage(chat, finish);
}
// 监听消息
// function newMessage() {
//   currentUser.socket.on('new_message', (msg) => {
//     console.log('接收消息', msg)
//     if (currentUser.activeChat === msg.sender_id) {
//       query.real_time_receive = true
//       real_data.data = [msg]
//       loadMore()
//     }
//   })
// }
</script>

<style lang="scss" scoped></style>
