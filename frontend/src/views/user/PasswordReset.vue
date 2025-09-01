<script>
import authApi from '@/api/auth/authApi.js'
import ButtonClick from '@/utils/components/ButtonClick.vue'
import PageHeadBack from '@/utils/components/PageHeadBack.vue'

export default {
  components: {
    ButtonClick,
    PageHeadBack
  },
  data() {
    var validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else if (value.length < 6) {
        callback(new Error('密码长度不能少于6个字符'))
      } else {
        callback()
      }
    }
    return {
      form: {
        email: '',
        code: '',
        new_password: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          {
            type: 'email',
            message: '请输入正确的邮箱地址',
            trigger: ['blur', 'change']
          }
        ],
        code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
        new_password: [{ required: true, validator: validatePass, trigger: 'blur' }]
      },
      isEmailValid: false,
      value: '',
      showButton: true,
      loading: false,
      isChange: false
    }
  },
  computed: {
    isSubmit() {
      return !(this.isEmailValid && this.form.code && this.form.new_password)
    }
  },
  methods: {
    applyCode() {
      this.value = Date.now() + 1000 * 60
      this.showButton = !this.showButton
      authApi.applyCode({ email: this.form.email, action: 'reset' }).then((res) => {
        if (res.code == 200) {
          this.$message.success('验证码已发送')
        } else {
          this.$message.error('验证码发送失败')
        }
      })
    },
    resetPassword() {
      authApi.resetPassword(this.form).then((res) => {
         if (res.code == 200) {
          this.$message.success('密码重置成功')
          this.$router.push('/login')
        } else {
          this.$message.error('密码重置失败')
        }
      })
    },
    submitForm() {
      this.loading = true
      this.resetPassword()
      this.loading = false
      this.isChange = false
    },
    finish() {
      this.showButton = !this.showButton
    },
    validateEmail() {
      if (this.$refs.formRef) {
        this.$refs.formRef.validateField('email', (errorMessage) => {
          this.isEmailValid = errorMessage
        })
      }
    }
  }
}
</script>

<template>
  <PageHeadBack>
    <h1>重置您的密码</h1>
    <el-form
      label-position="top"
      label-width="auto"
      :model="form"
      :rules="rules"
      ref="formRef"
      style="max-width: 600px"
    >
      <el-form-item prop="email" label="邮箱">
        <el-input v-model="form.email" style="width: 65%" @blur="validateEmail" />
        <el-button @click="applyCode" type="primary" :disabled="!isEmailValid" v-if="showButton">
          发送验证码
        </el-button>
        <el-countdown prefix="重新发送" format="ss" :value="value" @finish="finish" v-else />
      </el-form-item>
      <el-form-item prop="code" label="验证码">
        <el-input v-model="form.code" style="width: 40%" />
      </el-form-item>
      <el-form-item prop="new_password" label="密码">
        <el-input v-model="form.new_password" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <ButtonClick
          content="提交"
          type="primary"
          :disabled="isSubmit"
          :round="true"
          width="100%"
          :loading="loading"
          @do-search="submitForm"
        />
      </el-form-item>
    </el-form>
  </PageHeadBack>
</template>
<style scoped>
h1 {
  text-align: center;
  margin-bottom: 50px;
}
</style>
