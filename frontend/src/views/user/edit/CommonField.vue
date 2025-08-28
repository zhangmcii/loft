<!-- 修改昵称，签名，社交账号 -->
<script setup>
import { useCurrentUserStore } from '@/stores/user'
import { useOtherUserStore } from '@/stores/otherUser'
import { cloneDeep } from '@pureadmin/utils'
import { ElLoading } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import editApi from '@/api/user/editApi.js'
import PageHeadBack from '@/utils/components/PageHeadBack.vue'
import socialLinks from '@/config/socialLinks.json'
import { useChange } from '@/utils/composedFunc/change.js'
const user = useCurrentUserStore()
const other = useOtherUserStore()
const router = useRouter()
const route = useRoute()

const data = reactive({
  type: 1,
  localUserInfo: {
    nickname: '',
    about_me: '',
    social_account: {
      qq: '',
      wechat: '',
      bilibili: '',
      github: '',
      twitter: '',
      email: ''
    }
  }
})

data.type = Number(route.query.type)
data.localUserInfo = cloneDeep(user.userInfo)

const { isChange } = useChange(data, getAttr(data.type))

async function saveNickname() {
  await editApi.editUser(user.userInfo.id, { nickname: data.localUserInfo.nickname })
}
async function saveAboutMe() {
  await editApi.editUser(user.userInfo.id, { about_me: data.localUserInfo.about_me })
}
async function saveSocialLinks() {
  await editApi.editUser(user.userInfo.id, { social_account: data.localUserInfo.social_account })
}
async function save() {
  const loading = ElLoading.service({
    lock: true,
    text: '正在保存',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  if (data.type === 1) {
    await saveNickname()
  } else if (data.type === 2) {
    await saveAboutMe()
  } else if (data.type === 3) {
    await saveSocialLinks()
  }
  user.setUserInfo(data.localUserInfo)
  other.setUserInfo(data.localUserInfo)
  loading.close()
  router.back()
}
function getAttr(type) {
  switch (type) {
    case 1:
      return 'localUserInfo.nickname'
    case 2:
      return 'localUserInfo.about_me'
    case 3:
      return 'localUserInfo.social_account'
    default:
      return ''
  }
}
</script>
<template>
  <PageHeadBack>
    <template #action>
       <el-button :disabled="!isChange" @click="save">保存</el-button>
    </template>
    <div v-if="data.type === 1">
      <div class="title">修改昵称</div>
      <el-input v-model="data.localUserInfo.nickname" />
    </div>

    <div v-if="data.type === 2">
      <div class="title">修改签名</div>
      <el-input
        v-model="data.localUserInfo.about_me"
        autosize
        type="textarea"
        show-word-limit
        maxlength="30"
      />
    </div>

    <div v-if="data.type === 3">
      <div class="title">修改社交账号</div>
      <van-cell-group inset>
        <van-field v-model="data.localUserInfo.social_account.github" label="github">
          <template #left-icon>
            <img class="icon" :src="socialLinks[0].icon" height="20" />
          </template>
        </van-field>
        <van-field v-model="data.localUserInfo.social_account.email" label="邮箱">
          <template #left-icon>
            <img class="icon" :src="socialLinks[1].icon" height="20" />
          </template>
        </van-field>
        <van-field v-model="data.localUserInfo.social_account.qq" type="digit" label="qq">
          <template #left-icon>
            <img class="icon" :src="socialLinks[2].icon" height="20" />
          </template>
        </van-field>
        <van-field v-model="data.localUserInfo.social_account.wechat" label="微信">
          <template #left-icon>
            <img class="icon" :src="socialLinks[3].icon" height="20" />
          </template>
        </van-field>
        <van-field v-model="data.localUserInfo.social_account.bilibili" label="bilibili">
          <template #left-icon>
            <img class="icon" :src="socialLinks[4].icon" height="20" />
          </template>
        </van-field>
        <van-field v-model="data.localUserInfo.social_account.twitter" label="twitter">
          <template #left-icon>
            <img class="icon" :src="socialLinks[5].icon" height="20" />
          </template>
        </van-field>
      </van-cell-group>
    </div>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.title {
  text-align: center;
  margin-bottom: 20px;
}
img {
  background-color: black;
}
</style>
