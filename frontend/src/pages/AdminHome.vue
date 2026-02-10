<template>
  <div class="container">
    <el-card shadow="never" style="margin-bottom: 16px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div class="section-title" style="text-align:left;">问卷管理后台</div>
          <div class="notice">支持中文题目、选项、Excel 导入导出</div>
        </div>
        <el-button type="primary" plain @click="refresh">刷新</el-button>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :md="6">
        <el-card>
          <template #header>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>问卷列表</span>
              <el-button size="small" type="primary" @click="newSurvey">新建</el-button>
            </div>
          </template>
          <el-menu :default-active="String(current?.id || '')" class="el-menu-vertical">
            <el-menu-item v-for="item in surveys" :key="item.id" :index="String(item.id)" @click="loadSurvey(item.id)">
              <div style="display:flex; flex-direction:column; gap:4px; width:100%;">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
                  <span>{{ item.title }}</span>
                  <el-button size="small" type="danger" plain @click.stop="confirmDelete(item)">删除</el-button>
                </div>
                <el-tag size="small" type="info">{{ item.status }}</el-tag>
              </div>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="18">
        <el-card style="margin-bottom:16px;">
          <template #header>
            <span>问卷配置</span>
          </template>
          <el-form label-position="top">
            <el-form-item label="问卷标题">
              <el-input v-model="form.title" placeholder="请输入问卷标题" />
            </el-form-item>
            <el-form-item label="问卷描述">
              <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
            </el-form-item>
            <el-form-item label="链接模板（必须包含 ${link}）">
              <el-input
                v-model="form.link_template"
                type="textarea"
                :rows="3"
                placeholder="例如：请点击填写问卷：${link}"
              />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="form.status" placeholder="请选择">
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
              </el-select>
            </el-form-item>
          </el-form>

          <div style="margin-top: 16px;">
            <div style="font-weight:600; margin-bottom:8px;">题目</div>
            <el-card v-for="(q, qIndex) in form.questions" :key="qIndex" shadow="never" style="margin-bottom:12px;">
              <el-form label-position="top">
                <el-form-item label="题目标题">
                  <el-input v-model="q.title" placeholder="题目标题" />
                </el-form-item>
                <el-form-item label="题目描述（可选）">
                  <el-input v-model="q.description" placeholder="可填写补充说明" />
                </el-form-item>
                <el-form-item>
                  <el-switch v-model="q.required" active-text="必答" inactive-text="选答" />
                </el-form-item>
              </el-form>

              <div style="margin-top: 8px;">
                <div style="font-weight:600; margin-bottom:6px;">选项</div>
                <div v-for="(opt, oIndex) in q.options" :key="oIndex" style="display:flex; gap:10px; align-items:center; margin-bottom:8px;">
                  <el-tag type="info" size="small">选项 {{ oIndex + 1 }}</el-tag>
                  <el-input v-model="opt.text" placeholder="选项内容" />
                  <el-button type="danger" plain @click="removeOption(qIndex, oIndex)">删除</el-button>
                </div>
                <el-button size="small" @click="addOption(qIndex)">添加选项</el-button>
              </div>

              <div style="margin-top: 12px;">
                <el-button type="danger" plain @click="removeQuestion(qIndex)">删除题目</el-button>
              </div>
            </el-card>
            <el-button type="primary" plain @click="addQuestion">添加题目</el-button>
          </div>

          <div style="margin-top: 16px; display:flex; gap:10px; align-items:center;">
            <el-button type="primary" @click="saveSurvey">保存问卷</el-button>
            <span class="notice">保存后可进行发放与统计</span>
          </div>
          <div v-if="message" class="notice" style="margin-top:10px;">{{ message }}</div>
        </el-card>

        <el-card style="margin-bottom:16px;">
          <template #header>
            <span>发放管理</span>
          </template>
          <div class="notice" style="margin-bottom:8px;">导入 Excel 列名固定为 ID，可下载模板。</div>
          <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
            <input type="file" @change="onFileChange" />
            <el-button type="primary" plain @click="uploadIds">上传导入</el-button>
            <el-button @click="downloadTemplate">下载模板</el-button>
            <el-button type="primary" @click="exportLinks">导出链接</el-button>
          </div>
          <div v-if="importResult" class="notice" style="margin-top:8px;">{{ importResult }}</div>
        </el-card>

        <el-card>
          <template #header>
            <span>结果与统计</span>
          </template>
          <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:10px;">
            <el-button @click="loadSubmissions">刷新提交列表</el-button>
            <el-button @click="loadStats">刷新统计</el-button>
            <el-button type="primary" @click="exportAnswers">导出答案</el-button>
          </div>
          <div v-if="submissions.length" style="margin-bottom:12px;">
            <el-table :data="submissions" stripe style="width: 100%;">
              <el-table-column prop="real_id" label="ID" width="180" />
              <el-table-column label="提交时间">
                <template #default="scope">
                  {{ formatTime(scope.row.submitted_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-if="stats.questions.length">
            <el-card v-for="q in stats.questions" :key="q.question_id" shadow="never" style="margin-bottom:12px;">
              <div style="font-weight:600; margin-bottom:6px;">{{ q.title }}</div>
              <div class="notice">总提交：{{ q.total }}</div>
              <el-table :data="q.options" size="small" style="width:100%; margin-top:6px;">
                <el-table-column prop="text" label="选项" />
                <el-table-column label="数量/占比">
                  <template #default="scope">
                    {{ scope.row.count }} / {{ (scope.row.ratio * 100).toFixed(1) }}%
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { apiFetch, getPublicBaseUrl } from '../utils/api'

const surveys = ref([])
const current = ref(null)
const fileRef = ref(null)
const message = ref('')
const importResult = ref('')
const submissions = ref([])
const stats = reactive({ questions: [] })

const form = reactive({
  id: null,
  title: '',
  description: '',
  status: 'draft',
  link_template: '',
  questions: []
})

const refresh = async () => {
  message.value = ''
  const res = await apiFetch('/api/admin/surveys', { admin: true })
  surveys.value = await res.json()
}

const newSurvey = () => {
  current.value = null
  form.id = null
  form.title = ''
  form.description = ''
  form.status = 'draft'
  form.link_template = ''
  form.questions = []
}

const loadSurvey = async (id) => {
  const res = await apiFetch(`/api/admin/surveys/${id}`, { admin: true })
  const data = await res.json()
  current.value = data
  form.id = data.id
  form.title = data.title
  form.description = data.description || ''
  form.status = data.status
  form.link_template = data.link_template || ''
  form.questions = data.questions.map(q => ({
    title: q.title,
    description: q.description || '',
    required: q.required,
    sort_order: q.sort_order,
    options: q.options.map(o => ({ text: o.text, sort_order: o.sort_order }))
  }))
}

const addQuestion = () => {
  form.questions.push({
    title: '',
    description: '',
    required: true,
    sort_order: form.questions.length + 1,
    options: []
  })
}

const removeQuestion = (index) => {
  form.questions.splice(index, 1)
}

const addOption = (qIndex) => {
  form.questions[qIndex].options.push({ text: '', sort_order: form.questions[qIndex].options.length + 1 })
}

const removeOption = (qIndex, oIndex) => {
  form.questions[qIndex].options.splice(oIndex, 1)
}

const saveSurvey = async () => {
  message.value = ''
  const payload = {
    title: form.title,
    description: form.description,
    status: form.status,
    link_template: form.link_template,
    questions: form.questions.map((q, idx) => ({
      title: q.title,
      description: q.description,
      required: q.required,
      sort_order: idx + 1,
      options: q.options.map((o, oIdx) => ({ text: o.text, sort_order: oIdx + 1 }))
    }))
  }
  if (form.id) {
    await apiFetch(`/api/admin/surveys/${form.id}`, { method: 'PUT', body: JSON.stringify(payload), admin: true })
    message.value = '问卷已更新'
  } else {
    const res = await apiFetch('/api/admin/surveys', { method: 'POST', body: JSON.stringify(payload), admin: true })
    const data = await res.json()
    form.id = data.id
    message.value = '问卷已创建'
  }
  await refresh()
}

const confirmDelete = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定删除问卷「${item.title}」吗？该操作会删除所有关联数据。`,
      '删除确认',
      { type: 'warning' }
    )
    await ElMessageBox.confirm(
      '请再次确认：删除后数据无法恢复。',
      '二次确认',
      { type: 'warning' }
    )
  } catch {
    return
  }
  await deleteSurvey(item.id)
}

const deleteSurvey = async (id) => {
  await apiFetch(`/api/admin/surveys/${id}`, { method: 'DELETE', admin: true })
  if (current.value?.id === id) {
    newSurvey()
  }
  await refresh()
}

const onFileChange = (e) => {
  fileRef.value = e.target.files[0]
}

const uploadIds = async () => {
  importResult.value = ''
  if (!form.id) {
    importResult.value = '请先保存问卷'
    return
  }
  if (!fileRef.value) {
    importResult.value = '请选择文件'
    return
  }
  const fd = new FormData()
  fd.append('file', fileRef.value)
  const res = await apiFetch(`/api/admin/surveys/${form.id}/import-ids`, { method: 'POST', body: fd, admin: true })
  const data = await res.json()
  importResult.value = `导入成功：${data.imported} 条 / ${data.total} 条`
}

const getFilenameFromHeader = (res) => {
  const disposition = res.headers.get('Content-Disposition') || ''
  const matchUtf8 = disposition.match(/filename\*\=UTF-8''([^;]+)/i)
  if (matchUtf8 && matchUtf8[1]) {
    try {
      return decodeURIComponent(matchUtf8[1])
    } catch {
      return matchUtf8[1]
    }
  }
  const matchPlain = disposition.match(/filename=([^;]+)/i)
  if (matchPlain && matchPlain[1]) {
    return matchPlain[1].replace(/^"+|"+$/g, '')
  }
  return ''
}

const downloadBlob = async (path, filename) => {
  const res = await apiFetch(path, { admin: true })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const headerFilename = getFilenameFromHeader(res)
  a.download = filename || headerFilename || 'download'
  a.click()
  URL.revokeObjectURL(url)
}

const downloadTemplate = () => downloadBlob('/api/admin/id-template', 'ID导入模板.xlsx')

const exportLinks = () => {
  if (!form.id) return
  const baseUrl = getPublicBaseUrl()
  const qs = baseUrl ? `?public_base_url=${encodeURIComponent(baseUrl)}` : ''
  downloadBlob(`/api/admin/surveys/${form.id}/export-links${qs}`)
}

const exportAnswers = () => {
  if (!form.id) return
  downloadBlob(`/api/admin/surveys/${form.id}/export-answers`, '答案导出.xlsx')
}

const loadSubmissions = async () => {
  if (!form.id) return
  const res = await apiFetch(`/api/admin/surveys/${form.id}/submissions`, { admin: true })
  submissions.value = await res.json()
}

const loadStats = async () => {
  if (!form.id) return
  const res = await apiFetch(`/api/admin/surveys/${form.id}/stats`, { admin: true })
  const data = await res.json()
  stats.questions = data.questions || []
}

const formatTime = (value) => {
  if (!value) return ''
  return value.replace('T', ' ').slice(0, 19)
}

onMounted(refresh)
</script>
