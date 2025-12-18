<template>
  <div class="work-orders-container">
    <div class="header">
      <h2>工单管理</h2>
    </div>

    <el-card>
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 160px">
            <el-option label="未签收" :value="0" />
            <el-option label="处理中" :value="1" />
            <el-option label="已完成" :value="2" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="签收人">
          <el-select v-model="searchForm.assigned_to" placeholder="全部" clearable style="width: 160px">
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.full_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="报障人">
          <el-input v-model="searchForm.reporter_name" placeholder="请输入报障人" clearable style="width: 160px" />
        </el-form-item>
        
        <el-form-item label="联系电话">
          <el-input v-model="searchForm.contact_phone" placeholder="请输入联系电话" clearable style="width: 160px" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadWorkOrders">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table 
        :data="workOrders.slice((currentPage - 1) * pageSize, currentPage * pageSize)" 
        v-loading="loading"
        style="width: 100%"
        border
      >
        <el-table-column
          prop="order_no"
          label="工单编号"
          min-width="160"
          fixed="left"
        />
        <el-table-column
          prop="reporter_name"
          label="报障人"
          min-width="100"
        />
        <el-table-column
          prop="contact_phone"
          label="联系电话"
          min-width="120"
        />
        <el-table-column
          prop="location"
          label="报障地点"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column
          prop="problem_type"
          label="问题类型"
          min-width="120"
        >
          <template #default="{ row }">
            {{ row.problem_type || '未分类' }}
          </template>
        </el-table-column>
        <el-table-column
          prop="status"
          label="状态"
          min-width="100"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="签收人"
          min-width="100"
        >
          <template #default="{ row }">
            {{ row.assigned_to?.full_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column
          label="创建时间"
          min-width="160"
        >
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          min-width="120"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              @click="router.push(`/work-orders/${row.id}`)"
            >
              查看
            </el-button>
            <el-button
              v-if="row.status === 0"
              link
              type="warning"
              @click="handleAssign(row)"
            >
              签收
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页器 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="workOrders.length"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 签收对话框 -->
    <el-dialog
      v-model="showAssignDialog"
      title="签收工单"
      width="400px"
    >
      <div class="assign-content">
        <p>确定要签收该工单吗？</p>
        <p>工单号：{{ currentOrder?.order_no }}</p>
      </div>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="confirmAssign"
          :loading="assigning"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { formatDateTime } from '../../utils/time'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const assigning = ref(false)
const workOrders = ref([])
const showAssignDialog = ref(false)
const currentOrder = ref(null)

const searchForm = reactive({
  status: null,
  assigned_to: null,
  reporter_name: '',
  contact_phone: ''
})

const problemTypes = ref([])
const loadProblemTypes = async () => {
  try {
    const response = await axios.get('/api/v1/settings/problem-types')
    problemTypes.value = response.data
  } catch (error) {
    console.error('加载问题类型失败:', error)
  }
}

const users = ref([])
const loadUsers = async () => {
  try {
    const response = await axios.get('/api/v1/auth/users')
    users.value = response.data
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const loadWorkOrders = async () => {
  loading.value = true
  try {
    const params = {}
    
    // 状态筛选
    if (searchForm.status !== null) {
      params.status = searchForm.status
    }

    // 签收人筛选
    if (searchForm.assigned_to !== null) {
      params.assigned_to = searchForm.assigned_to
    }

    // 报障人筛选
    if (searchForm.reporter_name) {
      params.reporter_name = searchForm.reporter_name
    }

    // 联系电话筛选
    if (searchForm.contact_phone) {
      params.contact_phone = searchForm.contact_phone
    }

    // 始终不显示已归档工单
    params.status_lt = 3
    
    const response = await axios.get('/api/v1/work-orders', { 
      params,
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    workOrders.value = response.data
  } catch (error) {
    console.error('获取工单列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取工单列表失败')
  } finally {
    loading.value = false
  }
}

const handleAssign = (row) => {
  currentOrder.value = row
  showAssignDialog.value = true
}

const confirmAssign = async () => {
  if (!currentOrder.value) return
  
  assigning.value = true
  try {
    await axios.put(
      `/api/v1/work-orders/${currentOrder.value.id}/assign`,
      null,  // 不需要请求体
      {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      }
    )
    ElMessage.success('工单签收成功')
    showAssignDialog.value = false
    loadWorkOrders()
  } catch (error) {
    console.error('工单签收失败:', error)
    ElMessage.error(error.response?.data?.detail || '工单签收失败')
  } finally {
    assigning.value = false
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

// 添加分页相关的响应式变量
const currentPage = ref(1)
const pageSize = ref(10)

// 分页处理方法
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

onMounted(() => {
  loadProblemTypes()
  loadUsers()
  loadWorkOrders()
})
</script>

<style scoped>
.work-orders-container {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.assign-content {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .el-form-item {
    margin-right: 10px;
  }
}

@media (max-width: 768px) {
  .el-form {
    display: flex;
    flex-direction: column;
  }
  
  .el-form-item {
    margin-right: 0;
    width: 100%;
  }
}
</style> 