<template>
  <div class="dashboard">
    <h2>工作台</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的工单</span>
          <el-button
            type="primary"
            link
            @click="router.push('/work-orders')"
          >
            查看全部
          </el-button>
        </div>
      </template>

      <el-table :data="myWorkOrders" v-loading="loading">
        <el-table-column prop="order_no" label="工单编号" width="180" />
        <el-table-column prop="reporter_name" label="报障人" width="120" />
        <el-table-column prop="problem_type" label="问题类型" width="120">
          <template #default="{ row }">
            {{ row.problem_type || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="router.push(`/work-orders/${row.id}`)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { formatDateTime } from '../utils/time'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const myWorkOrders = ref([])

const loadMyWorkOrders = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/work-orders', {
      params: { 
        assigned_to: userStore.id,
        status: 1  // 只获取状态为"处理中"的工单
      }
    })
    myWorkOrders.value = response.data
  } catch (error) {
    ElMessage.error('获取工单列表失败')
  } finally {
    loading.value = false
  }
}

const getProblemTypeText = (type) => {
  const types = {
    1: '硬件故障',
    2: '软件故障',
    3: '网络故障',
    4: '账号问题',
    99: '其他'
  }
  return types[type] || '未知'
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
  loadMyWorkOrders()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
 