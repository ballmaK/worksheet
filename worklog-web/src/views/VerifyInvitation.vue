<template>
  <div class="verify-invitation-container">
    <el-card class="verify-card">
      <template #header>
        <div class="card-header">
          <h2>验证团队邀请</h2>
        </div>
      </template>
      
      <div class="invitation-info" v-if="invitationInfo">
        <el-alert
          :title="`${invitationInfo.inviter} 邀请您加入团队「${invitationInfo.teamName}」`"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        @submit.prevent="handleVerify"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="form.email" 
            placeholder="请输入您的邮箱地址"
            type="email"
            :disabled="!!invitationInfo.email"
          />
        </el-form-item>
        
        <el-form-item label="验证码" prop="verificationCode">
          <el-input 
            v-model="form.verificationCode" 
            placeholder="请输入6位验证码"
            maxlength="6"
            show-word-limit
            style="width: 200px"
          />
          <div class="verification-tip">
            <el-text size="small" type="info">
              验证码已发送到您的邮箱，10分钟内有效
            </el-text>
          </div>
        </el-form-item>
        
        <!-- 如果用户不存在，显示创建账户的字段 -->
        <template v-if="needCreateAccount">
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="form.password" 
              type="password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="form.confirmPassword" 
              type="password"
              placeholder="请再次输入密码"
              show-password
            />
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="verifying">
            {{ needCreateAccount ? '创建账户并加入团队' : '验证并加入团队' }}
          </el-button>
          <el-button @click="$router.push('/login')">返回登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { teamInviteApi } from '@/api/team-invite'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const verifying = ref(false)
const needCreateAccount = ref(false)

// 从URL获取邀请信息
const invitationInfo = reactive({
  inviter: route.query.inviter as string || '',
  teamName: route.query.team_name as string || '',
  email: route.query.email as string || ''
})

const form = ref({
  email: invitationInfo.email,
  verificationCode: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule: any, value: string, callback: any) => {
  if (needCreateAccount.value && value === '') {
    callback(new Error('请再次输入密码'))
  } else if (needCreateAccount.value && value !== form.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  verificationCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 6, max: 6, message: '验证码为6位数字', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码必须为6位数字', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ]
}

const handleVerify = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  if (needCreateAccount.value && form.value.password !== form.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    verifying.value = true
    
    const verifyData: any = {
      email: form.value.email,
      verification_code: form.value.verificationCode
    }
    
    // 如果需要创建账户，添加用户名和密码
    if (needCreateAccount.value) {
      verifyData.username = form.value.username
      verifyData.password = form.value.password
    }
    
    const result = await teamInviteApi.verifyInvitation(verifyData)
    
    ElMessage.success(result.message || '验证成功！')
    
    // 如果创建了新账户，跳转到登录页面
    if (result.user_created) {
      ElMessage.info('账户创建成功，请使用新账户登录')
      router.push('/login')
    } else {
      // 如果用户已存在，跳转到首页
      router.push('/')
    }
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message
    
    // 如果错误提示需要创建账户，显示创建账户的字段
    if (errorMessage.includes('用户不存在') || errorMessage.includes('请提供用户名和密码')) {
      needCreateAccount.value = true
      ElMessage.warning('检测到您还没有账户，请填写以下信息创建账户')
    } else {
      ElMessage.error('验证失败: ' + errorMessage)
    }
  } finally {
    verifying.value = false
  }
}

onMounted(() => {
  // 如果从URL获取到邮箱，自动填充
  if (invitationInfo.email) {
    form.value.email = invitationInfo.email
  }
})
</script>

<style scoped>
.verify-invitation-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.verify-card {
  width: 450px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.invitation-info {
  margin-bottom: 20px;
}

.verification-tip {
  margin-top: 8px;
}
</style> 