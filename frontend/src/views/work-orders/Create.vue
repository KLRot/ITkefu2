<template>
  <div class="create-work-order">
    <div class="header">
      <h2>创建工单</h2>
    </div>

    <el-card>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="报障人" prop="reporter_name">
          <el-input v-model="formData.reporter_name" />
        </el-form-item>

        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="formData.contact_phone" />
        </el-form-item>

        <el-form-item label="报障地点" prop="location">
          <el-input v-model="formData.location" />
        </el-form-item>

        <el-form-item label="问题类型" prop="problem_type_id">
          <el-select v-model="formData.problem_type_id" placeholder="请选择问题类型">
            <el-option
              v-for="type in problemTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-rate v-model="formData.priority" :max="5" />
        </el-form-item>

        <el-form-item label="问题描述" prop="problem_desc">
          <el-input
            v-model="formData.problem_desc"
            type="textarea"
            :rows="4"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">
            提交
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const formData = reactive({
  reporter_name: '',
  contact_phone: '',
  location: '',
  problem_desc: '',
  problem_type_id: null,
  priority: null
})

const rules = {
  reporter_name: [
    { required: true, message: '请输入报障人姓名', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入报障地点', trigger: 'blur' }
  ],
  problem_type_id: [
    { required: true, message: '请选择问题类型', trigger: 'change' }
  ],
  problem_desc: [
    { required: true, message: '请输入问题描述', trigger: 'blur' }
  ]
}

const problemTypes = ref([])

const loadProblemTypes = async () => {
  try {
    const response = await axios.get('/api/v1/settings/problem-types')
    problemTypes.value = response.data
  } catch (error) {
    console.error('加载问题类型失败:', error)
  }
}

onMounted(() => {
  loadProblemTypes()
})

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await axios.post('/api/v1/work-orders', formData, {
          headers: {
            'Authorization': 'Bearer kinglong',
            'Content-Type': 'application/json'
          }
        })
        if (response.data) {
          ElMessage.success('工单创建成功')
          router.push('/work-orders')
        }
      } catch (error) {
        console.error('工单创建失败:', error)
        ElMessage.error(error.response?.data?.detail || '工单创建失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.create-work-order {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.el-card {
  max-width: 800px;
}
</style> 