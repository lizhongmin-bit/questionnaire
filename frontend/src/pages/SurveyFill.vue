<template>
  <div class="container">
    <div class="card">
      <div v-if="!success" :class="['card-header', submitted ? 'logo-left' : 'logo-right']">
        <div class="brand-logo">
          <img :src="logoUrl" alt="品牌Logo" />
        </div>
      </div>
      <div v-if="submitted" class="submitted-panel">
        <div class="submitted-icon">✓</div>
        <div class="submitted-title">此问卷已提交，感谢您的支持！</div>
        <div class="notice">如需修改，请联系问卷发放方。</div>
        <div class="qr-block">
          <img :src="qrUrl" alt="问卷二维码" class="qr-image" />
          <div class="notice">如需进一步了解车旺大卡或咨询入驻事宜，请扫码添加工作人员微信。</div>
        </div>
      </div>
      <template v-else>
        <div class="section-title">{{ survey.title || '问卷加载中' }}</div>
        <div class="desc-block">
          <div class="notice" style="text-align:center;">{{ survey.description }}</div>
          <div class="qr-block">
            <img :src="qrUrl" alt="问卷二维码" class="qr-image" />
            <div class="notice">如需进一步了解车旺大卡或咨询入驻事宜，请扫码添加工作人员微信。</div>
          </div>
        </div>
        <div v-for="(q, index) in survey.questions" :key="q.id" class="question-card">
          <div class="question-title">
            <span v-if="q.required" class="required-star">*</span>
            {{ index + 1 }}. {{ q.title }}
          </div>
          <div v-if="q.description" class="question-desc">{{ q.description }}</div>
          <div class="radio-group">
            <label
              v-for="opt in q.options"
              :key="opt.id"
              class="radio-item"
              :class="{ selected: answers[q.id] === opt.id }"
            >
              <input type="radio" :name="`q-${q.id}`" :value="opt.id" v-model="answers[q.id]" />
              <span>{{ opt.text }}</span>
            </label>
          </div>
        </div>
        <div class="footer-submit">
          <button class="btn-primary" @click="submit">提交</button>
          <div v-if="error" class="error">{{ error }}</div>
          <div v-if="success" class="success-panel">
            <div class="submitted-icon">✓</div>
            <div class="submitted-title">提交成功，感谢您的参与！</div>
            <div class="qr-block">
              <img :src="qrUrl" alt="问卷二维码" class="qr-image" />
              <div class="notice">如需进一步了解车旺大卡或咨询入驻事宜，请扫码添加工作人员微信。</div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetch } from '../utils/api'

const route = useRoute()
const survey = reactive({ title: '', description: '', questions: [] })
const answers = reactive({})
const error = ref('')
const success = ref(false)
const submitted = ref(false)
const qrUrl = 'https://cwdk-s3.sinoiov.com/api/urlBrowse/cwdk-old/newapp/front/9ba003b3a2364b25b6edcfc6444f47ad.png'
const logoUrl = 'https://cwdk-s3.sinoiov.com/api/urlBrowse/cwdk-old/newapp/front/5a41726fb02f4fef804ccc61ca990411.png'

const loadSurvey = async () => {
  const token = route.params.token
  const res = await apiFetch(`/api/s/${token}`)
  const data = await res.json()
  submitted.value = Boolean(data.submitted)
  survey.title = data.title
  survey.description = data.description
  survey.questions = data.questions || []
}

const submit = async () => {
  error.value = ''
  success.value = false
  for (const q of survey.questions) {
    if (q.required && !answers[q.id]) {
      error.value = '请填写所有必答题'
      return
    }
  }
  const payload = {
    answers: survey.questions
      .filter(q => answers[q.id])
      .map(q => ({
        question_id: q.id,
        option_id: answers[q.id]
      }))
  }
  const token = route.params.token
  try {
    await apiFetch(`/api/s/${token}/submit`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    success.value = true
  } catch (err) {
    error.value = '提交失败，请稍后再试'
  }
}

onMounted(loadSurvey)
</script>
