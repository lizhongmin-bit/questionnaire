<template>
  <div class="container">
    <div class="card" style="max-width: 420px; margin: 80px auto;">
      <div class="section-title">后台登录</div>
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width: 100%;" @click="login">登录</el-button>
        </el-form-item>
      </el-form>
      <div v-if="error" class="error">{{ error }}</div>
      <div class="notice" style="margin-top: 12px;">默认账号：admin / admin123</div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { apiFetch, setAdminToken } from '../utils/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = reactive({
  username: 'admin',
  password: 'admin123'
})
const error = ref('')

const login = async () => {
  error.value = ''
  try {
    const res = await apiFetch('/api/admin/login', {
      method: 'POST',
      body: JSON.stringify(form)
    })
    const data = await res.json()
    setAdminToken(data.token)
    router.push('/admin')
  } catch (err) {
    error.value = '登录失败，请检查账号密码'
  }
}
</script>
