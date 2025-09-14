<template>
  <div class="blacklist-list">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">黑名单管理</h1>
        <div class="page-actions">
          <el-button type="primary" @click="goToCreate">
            <el-icon><Plus /></el-icon>
            添加黑名单
          </el-button>
          <el-button type="success" @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入Excel
          </el-button>
          <el-button type="warning" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </div>

      <!-- 搜索表单 -->
      <div class="search-form">
        <el-form :model="searchForm" inline>
          <el-form-item label="风险等级">
            <el-select v-model="searchForm.risk_level" placeholder="选择风险等级" clearable>
              <el-option label="高风险" value="high" />
              <el-option label="中风险" value="medium" />
              <el-option label="低风险" value="low" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input
              v-model="searchForm.search"
              placeholder="搜索姓名、电话、KTT名字等"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <div class="table-container">
        <el-table
          :data="tableData"
          v-loading="loading"
          stripe
          border
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="sequence_number" label="序号" width="80" />
          
          <el-table-column prop="ktt_name" label="KTT名字" width="120" show-overflow-tooltip />
          
          <el-table-column prop="order_name_phone" label="下单人信息" width="200" show-overflow-tooltip />
          
          <el-table-column prop="phone_numbers" label="电话号码" width="200">
            <template #default="{ row }">
              <div v-if="row.phone_numbers && row.phone_numbers.length > 0">
                <el-tag 
                  v-for="(phone, index) in row.phone_numbers" 
                  :key="index" 
                  type="info" 
                  size="small"
                  style="margin-right: 5px; margin-bottom: 2px;"
                >
                  {{ phone }}
                </el-tag>
              </div>
              <span v-else class="text-gray-400">-</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="wechat_name" label="微信名字" width="120" show-overflow-tooltip />
          
          <el-table-column prop="wechat_id" label="微信ID" width="150" show-overflow-tooltip />
          
          <el-table-column prop="order_address1" label="下单地址" width="200" show-overflow-tooltip />
          
          <el-table-column prop="order_address2" label="下单地址二" width="200" show-overflow-tooltip />
          
          <el-table-column prop="risk_level" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag
                :type="getRiskLevelType(row.risk_level)"
                :class="`risk-${row.risk_level}`"
              >
                {{ getRiskLevelText(row.risk_level) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="blacklist_reason" label="入黑原因" min-width="200" show-overflow-tooltip />
          
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="goToEdit(row.id)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 批量操作 -->
      <div v-if="selectedRows.length > 0" class="batch-actions">
        <el-alert
          :title="`已选择 ${selectedRows.length} 条记录`"
          type="info"
          show-icon
          :closable="false"
        >
          <template #default>
            <div class="batch-buttons">
              <el-button type="danger" @click="handleBatchDelete">
                <el-icon><Delete /></el-icon>
                批量删除
              </el-button>
              <el-button type="warning" @click="handleBatchExport">
                <el-icon><Download /></el-icon>
                批量导出
              </el-button>
            </div>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入Excel文件"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-upload
        ref="uploadRef"
        :action="uploadAction"
        :headers="uploadHeaders"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :file-list="fileList"
        accept=".xlsx,.xls"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls 文件，且不超过 10MB
          </div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type UploadUserFile } from 'element-plus'
import {
  Plus,
  Upload,
  Download,
  Search,
  Refresh,
  Edit,
  Delete,
  UploadFilled
} from '@element-plus/icons-vue'
import { blacklistApi } from '@/api/blacklist'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const tableData = ref<any[]>([])
const selectedRows = ref<any[]>([])

// 确保tableData始终是数组
watch(tableData, (newVal) => {
  if (!Array.isArray(newVal)) {
    console.warn('tableData不是数组，正在修复:', newVal)
    tableData.value = []
  }
}, { immediate: true })

// 搜索表单
const searchForm = reactive({
  risk_level: '',
  search: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 导入对话框
const importDialogVisible = ref(false)
const uploadRef = ref()
const fileList = ref<UploadUserFile[]>([])

// 计算属性
const uploadAction = computed(() => '/api/v1/blacklist/import')
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))

// 获取黑名单列表
const fetchBlacklistList = async () => {
  try {
    loading.value = true
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      ...searchForm
    }
    
    const response = await blacklistApi.getBlacklistList(params)
    console.log('黑名单API响应:', response)
    
    // 处理分页响应
    if (response && response.data) {
      tableData.value = response.data
      pagination.total = (response as any).total || 0
      console.log(`加载了 ${response.data.length} 条记录，总共 ${(response as any).total} 条`)
    } else {
      console.error('API返回格式错误:', response)
      tableData.value = []
      pagination.total = 0
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取黑名单列表失败')
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchBlacklistList()
}

// 重置搜索
const handleReset = () => {
  searchForm.risk_level = ''
  searchForm.search = ''
  pagination.page = 1
  fetchBlacklistList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  fetchBlacklistList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchBlacklistList()
}

// 表格选择
const handleSelectionChange = (selection: any[]) => {
  console.log('表格选择变化:', selection)
  if (Array.isArray(selection)) {
    selectedRows.value = selection as any[]
  } else {
    console.warn('选择数据不是数组:', selection)
    selectedRows.value = []
  }
}

// 导航
const goToCreate = () => {
  router.push('/blacklist/create')
}

const goToEdit = (id: number) => {
  router.push(`/blacklist/${id}/edit`)
}

// 删除记录
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除黑名单记录"${row.ktt_name || '未知'}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await blacklistApi.deleteBlacklist(row.id)
    ElMessage.success('删除成功')
    fetchBlacklistList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条记录吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const ids = selectedRows.value.map(row => row.id)
    await blacklistApi.batchDeleteBlacklist(ids)
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchBlacklistList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

// 导入功能
const handleImport = () => {
  importDialogVisible.value = true
}

const beforeUpload = (file: File) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件!')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  
  return true
}

const handleUploadSuccess = () => {
  ElMessage.success('导入成功')
  importDialogVisible.value = false
  fileList.value = []
  fetchBlacklistList()
}

const handleUploadError = (error: any) => {
  ElMessage.error('导入失败')
  console.error('Upload error:', error)
}

// 导出功能
const handleExport = async () => {
  try {
    await blacklistApi.exportBlacklist(searchForm)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

const handleBatchExport = async () => {
  try {
    const ids = selectedRows.value.map(row => row.id)
    await blacklistApi.exportBlacklist({ ids })
    ElMessage.success('批量导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '批量导出失败')
  }
}

// 工具函数
const getRiskLevelType = (level: string) => {
  const types: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return types[level] || 'info'
}

const getRiskLevelText = (level: string) => {
  const texts: Record<string, string> = {
    high: '高风险',
    medium: '中风险',
    low: '低风险'
  }
  return texts[level] || '未知'
}

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 组件挂载
onMounted(async () => {
  try {
    // 确保认证状态已初始化
    if (!authStore.isAuthenticated) {
      console.log('用户未认证，等待认证状态初始化...')
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    console.log('开始获取黑名单数据...')
    await fetchBlacklistList()
  } catch (error) {
    console.error('组件挂载时获取数据失败:', error)
  }
})
</script>

<style scoped>
.blacklist-list {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.search-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  flex-shrink: 0;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-container .el-table {
  flex: 1;
  overflow: auto;
}

.pagination-container {
  padding: 20px;
  text-align: right;
  flex-shrink: 0;
  border-top: 1px solid #ebeef5;
}

.batch-actions {
  margin-top: 20px;
  flex-shrink: 0;
}

.batch-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.risk-high {
  color: #f56c6c;
  font-weight: 600;
}

.risk-medium {
  color: #e6a23c;
  font-weight: 600;
}

.risk-low {
  color: #67c23a;
  font-weight: 600;
}

.text-gray-400 {
  color: #c0c4cc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-container {
    padding: 15px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .page-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .search-form {
    padding: 15px;
  }
  
  .batch-buttons {
    flex-direction: column;
  }
}
</style>
