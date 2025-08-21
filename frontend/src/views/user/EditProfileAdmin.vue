<script>
import editApi from '@/api/user/editApi.js'
import userApi from '@/api/user/userApi.js'
import ButtonClick from '@/utils/components/ButtonClick.vue'
import PageHeadBack from '@/utils/components/PageHeadBack.vue'
export default {
  components: {
    ButtonClick,
    PageHeadBack
  },
  data() {
    return {
      formLabelAlign: {
        email: '',
        username: '',
        confirmed: '',
        role: '',
        name: '',
        location: '',
        about_me: ''
      },
      user: {},
      userId: -1,
      roles: [
        {
          value: 1,
          label: '普通用户'
        },
        {
          value: 2,
          label: '内容协调员'
        },
        {
          value: 3,
          label: '管理员'
        }
      ],
      confirm: [
        {
          value: false,
          label: '未认证'
        },
        {
          value: true,
          label: '已认证'
        }
      ],
      originalForm: {},
      loading: false,
      isChange: false
    }
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.userId = to.params.id
      vm.getUserInfo(vm.userId)
      vm.$nextTick(() => {})
    })
  },
  watch: {
    formLabelAlign: {
      deep: true,
      handler(newVal) {
        this.isChange = JSON.stringify(newVal) !== this.originalForm
      }
    }
  },
  methods: {
    getUserInfo(userId) {
      userApi.getUser(userId).then((res) => {
        if (res.code == 200) {
          this.user = res.data
          this.originalForm = JSON.stringify(res.data)
          this.formLabelAlign = res.data
        }
      })
    },
    submit() {
      this.loading = true
      editApi.editProfileAdmin(this.formLabelAlign).then((res) => {
        this.loading = false
        this.isChange = false
        if (res.code == 200) {
          this.$message.success('修改成功')
          this.$router.push(`/user/${this.formLabelAlign.username}`)
        } else {
          this.$message.error('修改失败')
        }
      })
    }
  }
}
</script>

<template>
  <PageHeadBack>
    <el-form
      :model="formLabelAlign"
      ref="formLabelAlign"
      label-position="top"
      label-width="auto"
      style="max-width: 600px"
    >
      <el-form-item
        prop="email"
        label="邮件"
        :rules="[
          {
            type: 'email',
            message: '请输入正确的邮件地址',
            trigger: ['blur', 'change']
          }
        ]"
      >
        <el-input v-model="formLabelAlign.email" />
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="formLabelAlign.username" />
      </el-form-item>
      <el-form-item label="认证状态">
        <el-select v-model="formLabelAlign.confirmed" placeholder="Select" style="width: 240px">
          <el-option
            v-for="item in confirm"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="formLabelAlign.role" placeholder="Select" style="width: 240px">
          <el-option
            v-for="item in roles"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="昵称">
        <el-input v-model="formLabelAlign.nickname" />
      </el-form-item>
      <el-form-item label="城市">
        <el-input v-model="formLabelAlign.location" />
      </el-form-item>
      <el-form-item label="关于我">
        <el-input v-model="formLabelAlign.about_me" show-word-limit maxlength="30" />
      </el-form-item>
      <el-form-item>
        <ButtonClick
          content="提交"
          type="primary"
          :disabled="!isChange"
          :loading="loading"
          @do-search="submit"
        />
      </el-form-item>
    </el-form>
  </PageHeadBack>
</template>
<style scoped></style>
