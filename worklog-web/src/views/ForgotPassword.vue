<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <div class="forgot-password-header">
        <Logo size="large" :show-text="true" />
      </div>
      
      <!-- 输入邮箱表单 -->
      <el-form
        v-if="!emailSent"
        ref="formRef"
        :model="form"
        :rules="rules"
        class="forgot-password-form"
      >
        <div class="form-title">忘记密码</div>
        <div class="form-subtitle">请输入您的邮箱地址，我们将发送密码重置链接到您的邮箱</div>
        
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱地址"
            :prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="submit-button"
            :loading="loading"
            @click="handleSubmit"
          >
            发送重置链接
          </el-button>
        </el-form-item>
        
        <el-form-item class="back-link">
          <el-button type="text" @click="goToLogin" class="back-button">
            返回登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 成功提示 -->
      <div v-else class="success-message">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <div class="success-title">邮件已发送</div>
        <div class="success-text">
          我们已向 <strong>{{ form.email }}</strong> 发送了密码重置链接，
          请查收邮件并点击链接重置密码。
        </div>
        <div class="success-tip">如果未收到邮件，请检查垃圾邮件文件夹或稍后重试</div>
        <el-button type="primary" @click="goToLogin" class="back-login-button">
          返回登录
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, CircleCheck } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { userApi } from '@/api/user'
import Logo from '@/components/Logo.vue'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const emailSent = ref(false)

const form = reactive({
  email: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    await userApi.forgotPassword(form.email)
    
    emailSent.value = true
    ElMessage.success('邮件发送成功，请查收')
  } catch (error: any) {
    console.error('发送邮件错误:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '发送邮件失败')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.forgot-password-container {
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

.forgot-password-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.forgot-password-header {
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
  line-height: 1.5;
}

.forgot-password-form {
  margin-top: 20px;
}

.submit-button {
  width: 100%;
}

.back-link {
  margin-top: 16px;
  text-align: center;
}

.back-button {
  color: #409eff;
  font-weight: 500;
  padding: 0 4px;
}

.back-button:hover {
  color: #66b1ff;
}

.success-message {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 20px;
}

.success-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.success-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

.success-text strong {
  color: #303133;
}

.success-tip {
  font-size: 12px;
  color: #909399;
  margin-bottom: 30px;
}

.back-login-button {
  width: 100%;
}

@media (max-width: 576px) {
  .forgot-password-box {
    width: 90%;
    max-width: 400px;
    padding: 20px;
  }
}
</style>

