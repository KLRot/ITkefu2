<template>
  <div class="users-container">
    <div class="header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        创建用户
      </el-button>
    </div>

    <el-card>
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column prop="full_name" label="姓名" width="180" />
        <el-table-column prop="is_admin" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : ''">
              {{ row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button
              v-if="row.id !== userStore.id"
              link
              type="primary"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.id !== userStore.id"
              link
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑用户' : '创建用户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-switch
            v-model="form.is_admin"
            active-text="管理员"
            inactive-text="普通用户"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="删除用户"
      width="400px"
    >
      <div class="delete-content">
        <p>确定要删除该用户吗？此操作不可恢复。</p>
        <p>用户名：{{ currentUser?.username }}</p>
      </div>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button
          type="danger"
          @click="confirmDelete"
          :loading="deleting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const users = ref([])
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const currentUser = ref(null)
const formRef = ref(null)

const form = reactive({
  username: '',
  full_name: '',
  password: '',
  is_admin: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const isEdit = ref(false)
const showCreateDialog = computed({
  get: () => showDialog.value && !isEdit.value,
  set: (val) => {
    showDialog.value = val
    if (val) {
      isEdit.value = false
      resetForm()
    }
  }
})

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/auth/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.username = ''
  form.full_name = ''
  form.password = ''
  form.is_admin = false
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleEdit = (row) => {
  isEdit.value = true
  showDialog.value = true
  currentUser.value = row
  form.username = row.username
  form.full_name = row.full_name
  form.is_admin = row.is_admin
  form.password = '' // 编辑时密码可选
}

const handleDelete = (row) => {
  currentUser.value = row
  showDeleteDialog.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await axios.put(`/api/v1/auth/users/${currentUser.value.id}`, form)
          ElMessage.success('用户更新成功')
        } else {
          await axios.post('/api/v1/auth/users', form)
          ElMessage.success('用户创建成功')
        }
        showDialog.value = false
        loadUsers()
      } catch (error) {
        ElMessage.error(isEdit.value ? '用户更新失败' : '用户创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const confirmDelete = async () => {
  if (!currentUser.value) return
  
  deleting.value = true
  try {
    await axios.delete(`/api/v1/auth/users/${currentUser.value.id}`)
    ElMessage.success('用户删除成功')
    showDeleteDialog.value = false
    loadUsers()
  } catch (error) {
    ElMessage.error('用户删除失败')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.delete-content {
  padding: 20px;
}
</style> 