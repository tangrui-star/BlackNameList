<template>
  <div class="screening-list">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">订单筛查</h1>
        <div class="page-actions">
          <el-button type="primary" @click="goToUpload">
            <el-icon><Upload /></el-icon>
            上传筛查文件
          </el-button>
        </div>
      </div>

      <!-- 搜索表单 -->
      <div class="search-form">
        <el-form :model="searchForm" inline>
          <el-form-item label="任务状态">
            <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
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
        >
          <el-table-column prop="id" label="任务ID" width="80" />
          
          <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
          
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="total_records" label="总记录数" width="100" />
          
          <el-table-column prop="matched_records" label="匹配记录数" width="120" />
          
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                @click="goToResults(row.id)"
                :disabled="row.status !== 'completed'"
              >
                <el-icon><View /></el-icon>
                查看结果
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  Search,
  Refresh,
  View,
  Delete
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const tableData = ref([])

// 搜索表单
const searchForm = reactive({
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取筛查任务列表
const fetchScreeningList = async () => {
  try {
    loading.value = true
    // 这里应该调用实际的API
    // const response = await screeningApi.getScreeningList(params)
    // tableData.value = response
    console.log('获取筛查任务列表')
  } catch (error: any) {
    ElMessage.error(error.message || '获取筛查任务列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchScreeningList()
}

// 重置搜索
const handleReset = () => {
  searchForm.status = ''
  pagination.page = 1
  fetchScreeningList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  fetchScreeningList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchScreeningList()
}

// 导航
const goToUpload = () => {
  router.push('/screening/upload')
}

const goToResults = (taskId: number) => {
  router.push(`/screening/${taskId}/results`)
}

// 删除任务
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除筛查任务"${row.filename}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用实际的API
    // await screeningApi.deleteScreeningTask(row.id)
    ElMessage.success('删除成功')
    fetchScreeningList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 工具函数
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || '未知'
}

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 组件挂载
onMounted(() => {
  fetchScreeningList()
})
</script>

<style scoped>
.screening-list {
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.pagination-container {
  padding: 20px;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
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
}
</style>
