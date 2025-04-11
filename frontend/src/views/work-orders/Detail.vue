<template>
  <div class="work-order-detail">
    <div class="header">
      <h2>工单详情</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="16">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-tag :type="getStatusType(workOrder.status)">
                {{ getStatusText(workOrder.status) }}
              </el-tag>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="workOrder"
            label-width="100px"
            :disabled="!canEdit"
          >
            <el-descriptions :column="2" border>
              <el-descriptions-item label="工单编号">
                {{ workOrder.order_no }}
              </el-descriptions-item>
              <el-descriptions-item label="报障人">
                {{ workOrder.reporter_name }}
              </el-descriptions-item>
              <el-descriptions-item label="联系电话">
                {{ workOrder.contact_phone }}
              </el-descriptions-item>
              <el-descriptions-item label="报障地点">
                {{ workOrder.location }}
              </el-descriptions-item>
              <el-descriptions-item label="问题描述" :span="2">
                {{ workOrder.problem_desc }}
              </el-descriptions-item>
            </el-descriptions>

            <div v-if="workOrder.status !== 0" class="process-form">
              <el-form-item label="问题类型">
                <el-select 
                  v-if="workOrder.status === 1" 
                  v-model="workOrder.problem_type" 
                  placeholder="请选择问题类型"
                >
                  <el-option
                    v-for="type in problemTypes"
                    :key="type.name"
                    :label="type.name"
                    :value="type.name"
                  />
                </el-select>
                <span v-else>{{ workOrder.problem_type || '-' }}</span>
              </el-form-item>

              <el-form-item label="处理说明" prop="processing_desc">
                <el-input
                  v-model="workOrder.processing_desc"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入处理说明"
                  :disabled="!canEdit"
                />
              </el-form-item>

              <el-form-item label="解决方案" prop="solution_type">
                <el-select 
                  v-if="workOrder.status === 1" 
                  v-model="workOrder.solution_type" 
                  placeholder="请选择解决方案类型"
                >
                  <el-option
                    v-for="type in solutionTypes"
                    :key="type.name"
                    :label="type.name"
                    :value="type.name"
                  />
                </el-select>
                <span v-else>{{ workOrder.solution_type || '-' }}</span>
              </el-form-item>
            </div>

            <div class="actions" v-if="canEdit">
              <el-button
                type="primary"
                @click="handleComplete"
                :loading="updating"
              >
                完成处理
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>处理信息</span>
            </div>
          </template>

          <el-descriptions direction="vertical" :column="1" border>
            <el-descriptions-item label="签收人">
              {{ workOrder.assigned_to?.full_name || '未签收' }}
            </el-descriptions-item>
            <el-descriptions-item label="签收时间">
              {{ formatDateTime(workOrder.assigned_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(workOrder.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDateTime(workOrder.modified_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { formatDateTime } from '../../utils/time'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)

const loading = ref(false)
const updating = ref(false)
const workOrder = ref({})
const problemTypes = ref([])
const solutionTypes = ref([])

// 判断是否可以编辑工单
const canEdit = computed(() => {
  return (workOrder.value.status === 1 && 
         workOrder.value.assigned_to?.id === userStore.id) || 
         userStore.isAdmin
})

const loadProblemTypes = async () => {
  try {
    const response = await axios.get('/api/v1/settings/problem-types')
    problemTypes.value = response.data
  } catch (error) {
    console.error('加载问题类型失败:', error)
  }
}

const loadSolutionTypes = async () => {
  try {
    const response = await axios.get('/api/v1/settings/solution-types')
    solutionTypes.value = response.data
  } catch (error) {
    console.error('加载解决方案类型失败:', error)
  }
}

const loadWorkOrder = async () => {
  try {
    const response = await axios.get(`/api/v1/work-orders/${route.params.id}`)
    workOrder.value = response.data
  } catch (error) {
    console.error('加载工单详情失败:', error)
    ElMessage.error('加载工单详情失败')
  }
}

const handleComplete = async () => {
  if (!workOrder.value.problem_type) {
    ElMessage.warning('请选择问题类型')
    return
  }
  if (!workOrder.value.processing_desc) {
    ElMessage.warning('请填写处理说明')
    return
  }
  if (!workOrder.value.solution_type) {
    ElMessage.warning('请选择解决方案类型')
    return
  }

  updating.value = true
  try {
    await axios.put(
      `/api/v1/work-orders/${workOrder.value.id}`,
      {
        status: 2,  // 已完成
        problem_type: workOrder.value.problem_type,
        processing_desc: workOrder.value.processing_desc,
        solution_type: workOrder.value.solution_type
      },
      {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      }
    )
    ElMessage.success('工单处理完成')
    await loadWorkOrder()
  } catch (error) {
    console.error('更新工单失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新工单失败')
  } finally {
    updating.value = false
  }
}

const getStatusText = (status) => {
  const statuses = {
    0: '新建',
    1: '处理中',
    2: '已完成',
    3: '已归档'
  }
  return statuses[status] || '未知'
}

const getStatusType = (status) => {
  const types = {
    0: '',
    1: 'warning',
    2: 'success',
    3: 'info'
  }
  return types[status] || 'info'
}

onMounted(() => {
  loadProblemTypes()
  loadSolutionTypes()
  loadWorkOrder()
})
</script>

<style scoped>
.work-order-detail {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-card {
  margin-bottom: 20px;
}

.process-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style> 