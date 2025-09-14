<template>
  <div class="screening-results">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">筛查结果</h1>
        <div class="page-actions">
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出结果
          </el-button>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>
      </div>

      <!-- 任务信息 -->
      <div class="task-info">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>任务信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="info-item">
                <label>任务ID：</label>
                <span>{{ taskInfo.id }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <label>文件名：</label>
                <span>{{ taskInfo.filename }}</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <label>状态：</label>
                <el-tag :type="getStatusType(taskInfo.status)">
                  {{ getStatusText(taskInfo.status) }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-item">
                <label>创建时间：</label>
                <span>{{ formatDate(taskInfo.created_at) }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 统计信息 -->
      <div class="stats-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total-icon">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.total_records || 0 }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon matched-icon">
              <el-icon size="32"><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.matched_records || 0 }}</div>
              <div class="stat-label">匹配记录</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon safe-icon">
              <el-icon size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.safe_records || 0 }}</div>
              <div class="stat-label">安全记录</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rate-icon">
              <el-icon size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ matchRate }}%</div>
              <div class="stat-label">匹配率</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 结果列表 -->
      <div class="results-container">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>筛查结果详情</span>
            </div>
          </template>
          
          <el-table
            :data="resultsData"
            v-loading="loading"
            stripe
            border
            height="400"
          >
            <el-table-column prop="row_number" label="行号" width="80" />
            
            <el-table-column prop="name" label="姓名" width="120" show-overflow-tooltip />
            
            <el-table-column prop="phone" label="电话号码" width="130" />
            
            <el-table-column prop="match_status" label="匹配状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.match_status === 'matched' ? 'danger' : 'success'">
                  {{ row.match_status === 'matched' ? '匹配' : '安全' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="match_score" label="匹配分数" width="100">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.match_score" 
                  :color="getScoreColor(row.match_score)"
                  :show-text="false"
                />
                <span style="margin-left: 8px;">{{ row.match_score }}%</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="matched_blacklist" label="匹配的黑名单" min-width="200" show-overflow-tooltip />
            
            <el-table-column prop="risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getRiskLevelType(row.risk_level)">
                  {{ getRiskLevelText(row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Download,
  Document,
  Check,
  CircleCheck,
  TrendCharts,
  List
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const taskInfo = reactive({
  id: '',
  filename: '',
  status: '',
  created_at: ''
})

const stats = reactive({
  total_records: 0,
  matched_records: 0,
  safe_records: 0
})

const resultsData = ref([])

// 计算属性
const matchRate = computed(() => {
  if (stats.total_records === 0) return 0
  return Math.round((stats.matched_records / stats.total_records) * 100)
})

// 获取筛查结果详情
const fetchScreeningResults = async (taskId: string) => {
  try {
    loading.value = true
    // 这里应该调用实际的API
    // const response = await screeningApi.getScreeningResults(taskId)
    // Object.assign(taskInfo, response.task_info)
    // Object.assign(stats, response.stats)
    // resultsData.value = response.results
    
    console.log('获取筛查结果详情', taskId)
  } catch (error: any) {
    ElMessage.error(error.message || '获取筛查结果失败')
  } finally {
    loading.value = false
  }
}

// 导出结果
const handleExport = async () => {
  try {
    // 这里应该调用实际的API
    // await screeningApi.exportScreeningResults(route.params.taskId as string)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

// 返回列表
const goBack = () => {
  router.push('/screening')
}

// 工具函数
const getStatusType = (status: string) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || '未知'
}

const getScoreColor = (score: number) => {
  if (score >= 80) return '#f56c6c'
  if (score >= 60) return '#e6a23c'
  return '#67c23a'
}

const getRiskLevelType = (level: string) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return types[level] || 'info'
}

const getRiskLevelText = (level: string) => {
  const texts = {
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
onMounted(() => {
  const taskId = route.params.taskId as string
  if (taskId) {
    fetchScreeningResults(taskId)
  }
})
</script>

<style scoped>
.screening-results {
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

.task-info {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.info-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.total-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.matched-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.safe-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.rate-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.results-container {
  margin-bottom: 20px;
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
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-content {
    gap: 10px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-number {
    font-size: 20px;
  }
}
</style>
