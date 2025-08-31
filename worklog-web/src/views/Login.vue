<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <Logo size="large" :show-text="true" />
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
        
        <!-- 注册链接 -->
        <el-form-item class="register-link">
          <div class="register-text">
            还没有账号？
            <el-button type="text" @click="goToRegister" class="register-button">
              立即注册
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { userApi } from '@/api/user'
import { useUserStore } from '@/stores/user'
import Logo from '@/components/Logo.vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 1. 获取token
    const response = await userApi.login({
      username: form.username,
      password: form.password
    })
    
    // 2. 设置token
    userStore.setToken(response.access_token)
    
    // 3. 获取用户信息
    const userInfo = await userApi.getCurrentUser()
    userStore.setUser({
      userId: userInfo.id,
      username: userInfo.username,
      email: userInfo.email,
      role: userInfo.role
    })
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    console.error('登录错误:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '登录失败')
  } finally {
    loading.value = false
  }
}

// 跳转到注册页面
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
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

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.login-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
}

.register-link {
  margin-top: 16px;
  text-align: center;
}

.register-text {
  color: #606266;
  font-size: 14px;
}

.register-button {
  color: #409eff;
  font-weight: 500;
  padding: 0 4px;
}

.register-button:hover {
  color: #66b1ff;
}

@media (max-width: 576px) {
  .login-box {
    width: 90%;
    max-width: 400px;
    padding: 20px;
  }
}
</style> 