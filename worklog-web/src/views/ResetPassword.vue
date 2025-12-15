<template>
  <div class="reset-password-container">
    <div class="reset-password-box">
      <div class="reset-password-header">
        <Logo size="large" :show-text="true" />
      </div>
      
      <!-- 重置密码表单 -->
      <el-form
        v-if="!resetSuccess"
        ref="formRef"
        :model="form"
        :rules="rules"
        class="reset-password-form"
      >
        <div class="form-title">重置密码</div>
        <div class="form-subtitle">请输入您的新密码</div>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="submit-button"
            :loading="loading"
            @click="handleSubmit"
          >
            重置密码
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 成功提示 -->
      <div v-else class="success-message">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <div class="success-title">密码重置成功</div>
        <div class="success-text">
          您的密码已成功重置，请使用新密码登录
        </div>
        <el-button type="primary" @click="goToLogin" class="back-login-button">
          前往登录
        </el-button>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="tokenError" class="error-message">
        <el-icon class="error-icon"><CircleClose /></el-icon>
        <div class="error-title">链接无效或已过期</div>
        <div class="error-text">
          重置密码链接无效或已过期，请重新申请密码重置
        </div>
        <el-button type="primary" @click="goToForgotPassword" class="back-forgot-button">
          重新申请
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { userApi } from '@/api/user'
import Logo from '@/components/Logo.vue'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const loading = ref(false)
const resetSuccess = ref(false)
const tokenError = ref(false)
const token = ref('')

const form = reactive({
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

onMounted(() => {
  const tokenParam = route.query.token as string
  if (!tokenParam) {
    tokenError.value = true
    ElMessage.error('缺少重置密码令牌')
  } else {
    token.value = tokenParam
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    await userApi.resetPassword(token.value, form.password)
    
    resetSuccess.value = true
    ElMessage.success('密码重置成功')
  } catch (error: any) {
    console.error('重置密码错误:', error)
    const errorMessage = error.response?.data?.detail || error.message || '重置密码失败'
    ElMessage.error(errorMessage)
    
    // 如果是token相关错误，显示错误页面
    if (errorMessage.includes('无效') || errorMessage.includes('过期')) {
      tokenError.value = true
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}

const goToForgotPassword = () => {
  router.push('/forgot-password')
}
</script>

<style scoped>
.reset-password-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.reset-password-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.reset-password-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  text-align: center;
  margin-bottom: 10px;
}

.form-subtitle {
  font-size: 14px;
  color: #909399;
  text-align: center;
  margin-bottom: 30px;
}

.reset-password-form {
  margin-top: 20px;
}

.submit-button {
  width: 100%;
}

.success-message,
.error-message {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 64px;
  color: #f56c6c;
  margin-bottom: 20px;
}

.success-title,
.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.success-text,
.error-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 30px;
}

.back-login-button,
.back-forgot-button {
  width: 100%;
}

@media (max-width: 576px) {
  .reset-password-box {
    width: 90%;
    max-width: 400px;
    padding: 20px;
  }
}
</style>

