<template>
  <div class="settings-container">
    <div class="header">
      <h2>系统设置</h2>
    </div>

    <el-row :gutter="20">
      <!-- 系统设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本设置</span>
            </div>
          </template>

          <el-form
            ref="settingsForm"
            :model="settings"
            label-width="120px"
            v-loading="loading"
          >
            <el-form-item label="自动归档时间">
              <el-input-number
                v-model="settings.archive_hours"
                :min="1"
                :max="720"
                :step="1"
              />
              <span class="form-tip">小时后自动归档已完成的工单</span>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="saveSettings"
                :loading="saving"
              >
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 问题类型管理 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>问题类型管理</span>
              <el-button
                type="primary"
                link
                @click="showTypeDialog = true"
              >
                添加类型
              </el-button>
            </div>
          </template>

          <el-table :data="problemTypes" v-loading="loadingTypes">
            <el-table-column prop="name" label="类型名称" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  link
                  type="danger"
                  @click="handleDeleteType(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 解决方案类型管理 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>解决方案类型管理</span>
              <el-button
                type="primary"
                link
                @click="showSolutionTypeDialog = true"
              >
                添加类型
              </el-button>
            </div>
          </template>

          <el-table :data="solutionTypes" v-loading="loadingSolutionTypes">
            <el-table-column prop="name" label="类型名称" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  link
                  type="danger"
                  @click="handleDeleteSolutionType(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建问题类型对话框 -->
    <el-dialog
      v-model="showTypeDialog"
      title="添加问题类型"
      width="500px"
    >
      <el-form
        ref="typeFormRef"
        :model="typeForm"
        :rules="typeRules"
        label-width="100px"
      >
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="typeForm.name" placeholder="请输入类型名称" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showTypeDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="saveType"
          :loading="savingType"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="删除问题类型"
      width="400px"
    >
      <div class="delete-content">
        <p>确定要删除该问题类型吗？此操作不可恢复。</p>
        <p>类型名称：{{ currentType?.name }}</p>
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

    <!-- 创建解决方案类型对话框 -->
    <el-dialog
      v-model="showSolutionTypeDialog"
      title="添加解决方案类型"
      width="500px"
    >
      <el-form
        ref="solutionTypeFormRef"
        :model="solutionTypeForm"
        :rules="typeRules"
        label-width="100px"
      >
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="solutionTypeForm.name" placeholder="请输入类型名称" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showSolutionTypeDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="saveSolutionType"
          :loading="savingSolutionType"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除解决方案类型确认对话框 -->
    <el-dialog
      v-model="showDeleteSolutionDialog"
      title="删除解决方案类型"
      width="400px"
    >
      <div class="delete-content">
        <p>确定要删除该解决方案类型吗？此操作不可恢复。</p>
        <p>类型名称：{{ currentSolutionType?.name }}</p>
      </div>
      <template #footer>
        <el-button @click="showDeleteSolutionDialog = false">取消</el-button>
        <el-button
          type="danger"
          @click="confirmDeleteSolution"
          :loading="deletingSolution"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 系统设置相关
const loading = ref(false)
const saving = ref(false)
const settings = reactive({
  archive_hours: 72
})

// 问题类型相关
const loadingTypes = ref(false)
const savingType = ref(false)
const deleting = ref(false)
const problemTypes = ref([])
const showTypeDialog = ref(false)
const showDeleteDialog = ref(false)
const currentType = ref(null)

const typeForm = reactive({
  name: ''
})

const typeRules = {
  name: [
    { required: true, message: '请输入类型名称', trigger: 'blur' }
  ]
}

const typeFormRef = ref()

// 加载系统设置
const loadSettings = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/settings/system')
    settings.archive_hours = response.data.archive_hours
  } catch (error) {
    ElMessage.error('加载系统设置失败')
  } finally {
    loading.value = false
  }
}

// 保存系统设置
const saveSettings = async () => {
  saving.value = true
  try {
    await axios.put('/api/v1/settings/system', {
      archive_hours: settings.archive_hours
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 加载问题类型列表
const loadProblemTypes = async () => {
  loadingTypes.value = true
  try {
    const response = await axios.get('/api/v1/settings/problem-types')
    problemTypes.value = response.data
  } catch (error) {
    ElMessage.error('加载问题类型失败')
  } finally {
    loadingTypes.value = false
  }
}

// 重置问题类型表单
const resetTypeForm = () => {
  if (typeFormRef.value) {
    typeFormRef.value.resetFields()
  }
  typeForm.name = ''
  currentType.value = null
}

// 处理删除问题类型
const handleDeleteType = (row) => {
  currentType.value = row
  showDeleteDialog.value = true
}

// 确认删除问题类型
const confirmDelete = async () => {
  if (!currentType.value) return
  
  deleting.value = true
  try {
    await axios.delete(`/api/v1/settings/problem-types/${currentType.value.name}`)
    ElMessage.success('删除成功')
    showDeleteDialog.value = false
    await loadProblemTypes()
  } catch (error) {
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
  }
}

// 保存问题类型
const saveType = async () => {
  if (!typeFormRef.value) return
  
  await typeFormRef.value.validate(async (valid) => {
    if (valid) {
      savingType.value = true
      try {
        await axios.post('/api/v1/settings/problem-types', typeForm)
        ElMessage.success('创建成功')
        showTypeDialog.value = false
        await loadProblemTypes()
        resetTypeForm()
      } catch (error) {
        ElMessage.error('创建失败')
      } finally {
        savingType.value = false
      }
    }
  })
}

// 解决方案类型相关
const loadingSolutionTypes = ref(false)
const savingSolutionType = ref(false)
const deletingSolution = ref(false)
const solutionTypes = ref([])
const showSolutionTypeDialog = ref(false)
const showDeleteSolutionDialog = ref(false)
const currentSolutionType = ref(null)

const solutionTypeForm = reactive({
  name: ''
})

const solutionTypeFormRef = ref()

// 加载解决方案类型列表
const loadSolutionTypes = async () => {
  loadingSolutionTypes.value = true
  try {
    const response = await axios.get('/api/v1/settings/solution-types')
    solutionTypes.value = response.data
  } catch (error) {
    ElMessage.error('加载解决方案类型失败')
  } finally {
    loadingSolutionTypes.value = false
  }
}

// 重置解决方案类型表单
const resetSolutionTypeForm = () => {
  if (solutionTypeFormRef.value) {
    solutionTypeFormRef.value.resetFields()
  }
  solutionTypeForm.name = ''
  currentSolutionType.value = null
}

// 处理删除解决方案类型
const handleDeleteSolutionType = (row) => {
  currentSolutionType.value = row
  showDeleteSolutionDialog.value = true
}

// 确认删除解决方案类型
const confirmDeleteSolution = async () => {
  if (!currentSolutionType.value) return
  
  deletingSolution.value = true
  try {
    await axios.delete(`/api/v1/settings/solution-types/${currentSolutionType.value.name}`)
    ElMessage.success('删除成功')
    showDeleteSolutionDialog.value = false
    await loadSolutionTypes()
  } catch (error) {
    ElMessage.error('删除失败')
  } finally {
    deletingSolution.value = false
  }
}

// 保存解决方案类型
const saveSolutionType = async () => {
  if (!solutionTypeFormRef.value) return
  
  await solutionTypeFormRef.value.validate(async (valid) => {
    if (valid) {
      savingSolutionType.value = true
      try {
        await axios.post('/api/v1/settings/solution-types', solutionTypeForm)
        ElMessage.success('创建成功')
        showSolutionTypeDialog.value = false
        await loadSolutionTypes()
        resetSolutionTypeForm()
      } catch (error) {
        ElMessage.error('创建失败')
      } finally {
        savingSolutionType.value = false
      }
    }
  })
}

onMounted(() => {
  loadSettings()
  loadProblemTypes()
  loadSolutionTypes()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 14px;
}
</style> 