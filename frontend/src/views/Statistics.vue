<template>
  <div class="statistics">
    <h2>统计分析</h2>

    <!-- 查询条件 -->
    <el-card class="mb-4">
      <template #header>
        <div class="card-header">
          <span>查询条件</span>
          <div>
            <el-button type="primary" @click="searchWorkOrders">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
            <el-button @click="exportToExcel" :disabled="!hasData">导出Excel</el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" ref="searchFormRef">
        <el-form-item label="工单编号">
          <el-input
            v-model="searchForm.orderNo"
            placeholder="请输入工单编号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            :default-time="[
              new Date(2000, 1, 1, 0, 0, 0),
              new Date(2000, 1, 1, 23, 59, 59),
            ]"
            style="width: 380px"
          />
        </el-form-item>
        
        <el-form-item label="工单状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="请选择状态" 
            clearable
            style="width: 160px"
          >
            <el-option label="新建" :value="0" />
            <el-option label="处理中" :value="1" />
            <el-option label="已完成" :value="2" />
            <el-option label="已归档" :value="3" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="问题类型">
          <el-select 
            v-model="searchForm.problemType" 
            placeholder="请选择类型" 
            clearable
            style="width: 160px"
          >
            <el-option
              v-for="type in problemTypes"
              :key="type.name"
              :label="type.name"
              :value="type.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="签收人">
          <el-select 
            v-model="searchForm.assignedTo" 
            placeholder="请选择签收人" 
            clearable
            style="width: 160px"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.full_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 工单列表 -->
    <el-card class="mt-4">
      <template #header>
        <div class="card-header">
          <span>工单列表</span>
          <div class="header-actions">
            <el-button
              v-if="userStore.isAdmin && selectedOrders.length > 0"
              type="danger"
              size="small"
              @click="handleBatchDelete"
            >
              批量删除({{ selectedOrders.length }})
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="paginatedData"
        v-loading="loading"
        style="width: 100%"
        border
        @selection-change="handleSelectionChange"
        row-key="id"
      >
        <el-table-column
          v-if="userStore.isAdmin"
          type="selection"
          width="55"
          fixed="left"
        />
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
          min-width="100"
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

    <!-- 统计卡片 -->
    <el-card class="mt-4">
      <el-row :gutter="20" class="statistics-cards">
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">总工单数</div>
            <div class="stat-number">{{ statistics.total || 0 }}</div>
          </div>
        </el-col>
        <el-col :span="4" v-for="(count, status) in statistics.status" :key="status">
          <div class="stat-item">
            <div class="stat-label">{{ getStatusText(Number(status)) }}</div>
            <div class="stat-number">{{ count }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="批量删除工单"
      width="400px"
    >
      <div class="delete-content">
        <p>确定要删除选中的 {{ selectedOrders.length }} 个工单吗？此操作不可恢复。</p>
      </div>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button
          type="danger"
          @click="confirmDelete"
          :loading="deleting"
        >
          确定删除
        </el-button>
      </template>
    </el-dialog>

    <!-- 图表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>工单状态分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-progress
              v-for="(value, status) in statistics.status"
              :key="status"
              :percentage="getPercentage(value)"
              :color="getStatusColor(Number(status))"
              :format="() => `${getStatusText(Number(status))} (${value}件, ${getPercentage(value)}%)`"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>问题类型分布</span>
            </div>
          </template>
          <div class="chart-container">
            <el-progress
              v-for="(value, key) in statistics.by_type"
              :key="key"
              :percentage="getPercentage(value)"
              :color="getProblemTypeColor(key)"
              :format="() => `${getProblemTypeText(key)} (${value}件, ${getPercentage(value)}%)`"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { formatDateTime } from '../utils/time'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const deleting = ref(false)
const workOrders = ref([])
const statistics = ref({
  total: 0,
  status: {},
  by_type: {}
})
const selectedOrders = ref([])
const showDeleteDialog = ref(false)
const hasData = computed(() => workOrders.value.length > 0)

// 添加数据
const searchFormRef = ref(null)
const problemTypes = ref([])
const users = ref([])

const searchForm = reactive({
  orderNo: '',
  dateRange: [],
  status: null,
  problemType: null,
  assignedTo: null
})

// 添加分页相关的响应式变量
const currentPage = ref(1)
const pageSize = ref(10)

// 添加计算属性
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return workOrders.value.slice(start, end)
})

// 加载问题类型列表
const loadProblemTypes = async () => {
  try {
    const response = await axios.get('/api/v1/settings/problem-types')
    problemTypes.value = response.data
  } catch (error) {
    console.error('加载问题类型失败:', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await axios.get('/api/v1/auth/users')
    users.value = response.data
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 修改查询方法
const searchWorkOrders = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.orderNo?.trim()) params.order_no = searchForm.orderNo.trim()
    if (searchForm.dateRange?.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    if (searchForm.status !== null) params.status = searchForm.status
    if (searchForm.problemType) params.problem_type = searchForm.problemType
    if (searchForm.assignedTo !== null) params.assigned_to = searchForm.assignedTo
    
    const [ordersRes, statsRes] = await Promise.all([
      axios.get('/api/v1/work-orders', { params }),
      axios.get('/api/v1/work-orders/statistics', { params })
    ])
    
    workOrders.value = ordersRes.data
    statistics.value = statsRes.data
    // 重置分页
    currentPage.value = 1
    selectedOrders.value = []
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取数据失败')
  } finally {
    loading.value = false
  }
}

const exportToExcel = () => {
  const data = workOrders.value.map(order => ({
    '工单编号': order.order_no,
    '报障人': order.reporter_name,
    '联系电话': order.contact_phone,
    '报障地点': order.location,
    '问题类型': getProblemTypeText(order.problem_type),
    '状态': getStatusText(order.status),
    '创建时间': formatDateTime(order.created_at),
    '签收时间': formatDateTime(order.assigned_time),
    '更新时间': formatDateTime(order.modified_at)
  }))
  
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '工单列表')
  
  const fileName = `工单统计_${new Date().toLocaleDateString()}.xlsx`
  XLSX.writeFile(wb, fileName)
}

const getPercentage = (value) => {
  return Math.round((value / statistics.value.total) * 100) || 0
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

const getProblemTypeText = (type) => {
  return type || '未分类'
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

const getStatusColor = (status) => {
  const colors = {
    0: '#909399',  // 新建
    1: '#E6A23C',  // 处理中
    2: '#67C23A',  // 已完成
    3: '#909399'   // 已归档
  }
  return colors[status] || '#909399'
}

const getProblemTypeColor = (type) => {
  // 使用固定的几种颜色循环显示
  const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A', '#909399']
  const index = problemTypes.value.findIndex(t => t.name === type)
  if (index === -1) return '#909399' // 未分类使用灰色
  return colors[index % colors.length]
}

const handleSelectionChange = (selection) => {
  selectedOrders.value = selection
}

const handleBatchDelete = () => {
  if (selectedOrders.value.length === 0) {
    ElMessage.warning('请选择要删除的工单')
    return
  }
  showDeleteDialog.value = true
}

const confirmDelete = async () => {
  if (selectedOrders.value.length === 0) return
  
  deleting.value = true
  try {
    // 批量删除选中的工单
    for (const order of selectedOrders.value) {
      await axios.delete(`/api/v1/work-orders/${order.id}`)
    }
    
    ElMessage.success('工单删除成功')
    showDeleteDialog.value = false
    
    // 重新加载数据
    await searchWorkOrders()
  } catch (error) {
    console.error('删除工单失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除工单失败')
  } finally {
    deleting.value = false
  }
}

// 分页处理方法
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 修改重置方法
const resetSearch = () => {
  searchForm.orderNo = ''
  searchForm.dateRange = []
  searchForm.status = null
  searchForm.problemType = null
  searchForm.assignedTo = null
  
  searchFormRef.value?.resetFields()
  currentPage.value = 1
  selectedOrders.value = []
  searchWorkOrders()
}

onMounted(async () => {
  await loadProblemTypes()
  await loadUsers()
})
</script>

<style scoped>
.statistics {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.mt-4 {
  margin-top: 20px;
}

.statistics-cards {
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-row {
  margin-top: 20px;
}

.chart-container {
  padding: 20px;
}

.el-progress {
  margin-bottom: 15px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .statistics-cards {
    flex-wrap: wrap;
  }
  
  .stat-item {
    margin: 10px 0;
  }
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style> 