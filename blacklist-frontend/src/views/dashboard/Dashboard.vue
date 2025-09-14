<template>
  <div class="dashboard">
    <div class="page-container">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎回来，{{ user?.full_name || user?.username }}！</h1>
        <p class="welcome-subtitle">黑名单管理系统为您提供全面的风险控制解决方案</p>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon blacklist-icon">
              <el-icon size="32"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.blacklist_stats?.total || 0 }}</div>
              <div class="stat-label">黑名单总数</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon high-risk-icon">
              <el-icon size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.blacklist_stats?.high_risk || 0 }}</div>
              <div class="stat-label">高风险记录</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon screening-icon">
              <el-icon size="32"><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.screening_stats?.total_tasks || 0 }}</div>
              <div class="stat-label">筛查任务</div>
            </div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon result-icon">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.screening_stats?.total_results || 0 }}</div>
              <div class="stat-label">筛查结果</div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>黑名单风险分布</span>
                </div>
              </template>
              <div ref="riskChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>筛查任务状态</span>
                </div>
              </template>
              <div ref="taskChartRef" class="chart-container"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 快速操作 -->
      <div class="quick-actions">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button type="primary" @click="goToBlacklist">
              <el-icon><Plus /></el-icon>
              添加黑名单
            </el-button>
            <el-button type="success" @click="goToScreening">
              <el-icon><Upload /></el-icon>
              上传筛查文件
            </el-button>
            <el-button type="info" @click="goToUsers" v-if="hasAnyRole(['超级管理员', '管理员'])">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            <el-button type="warning" @click="goToAdmin" v-if="hasAnyRole(['超级管理员', '管理员'])">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  UserFilled,
  Warning,
  Search,
  Document,
  Plus,
  Upload,
  User,
  Setting
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { adminApi } from '@/api/admin'
import * as echarts from 'echarts'

const router = useRouter()
const authStore = useAuthStore()

// 图表引用
const riskChartRef = ref<HTMLElement>()
const taskChartRef = ref<HTMLElement>()

// 统计数据
const stats = ref({
  blacklist_stats: {
    total: 0,
    high_risk: 0,
    medium_risk: 0,
    low_risk: 0
  },
  screening_stats: {
    total_tasks: 0,
    completed_tasks: 0,
    processing_tasks: 0,
    pending_tasks: 0,
    total_results: 0,
    high_risk_results: 0,
    verified_results: 0
  },
  user_stats: {
    total_users: 0
  }
})

// 当前用户
const user = computed(() => authStore.user)

// 权限检查
const hasAnyRole = (roles: string[]) => {
  return authStore.hasAnyRole(roles)
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await adminApi.getStats()
    stats.value = response
    // 数据加载完成后重新初始化图表
    nextTick(() => {
      initRiskChart()
      initTaskChart()
    })
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 初始化风险分布图表
const initRiskChart = () => {
  if (!riskChartRef.value || !stats.value?.blacklist_stats) return
  
  const chart = echarts.init(riskChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '风险分布',
        type: 'pie',
        radius: '50%',
        data: [
          { value: stats.value.blacklist_stats.high_risk || 0, name: '高风险', itemStyle: { color: '#f56c6c' } },
          { value: stats.value.blacklist_stats.medium_risk || 0, name: '中风险', itemStyle: { color: '#e6a23c' } },
          { value: stats.value.blacklist_stats.low_risk || 0, name: '低风险', itemStyle: { color: '#67c23a' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 初始化任务状态图表
const initTaskChart = () => {
  if (!taskChartRef.value || !stats.value?.screening_stats) return
  
  const chart = echarts.init(taskChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}'
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        data: [
          { value: stats.value.screening_stats.completed_tasks || 0, name: '已完成', itemStyle: { color: '#67c23a' } },
          { value: stats.value.screening_stats.processing_tasks || 0, name: '处理中', itemStyle: { color: '#409eff' } },
          { value: stats.value.screening_stats.pending_tasks || 0, name: '待处理', itemStyle: { color: '#e6a23c' } }
        ],
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 快速操作
const goToBlacklist = () => {
  router.push('/blacklist/create')
}

const goToScreening = () => {
  router.push('/screening/upload')
}

const goToUsers = () => {
  router.push('/users')
}

const goToAdmin = () => {
  router.push('/admin')
}

// 组件挂载
onMounted(async () => {
  await fetchStats()
  // 延迟初始化图表，确保DOM已渲染
  setTimeout(() => {
    initRiskChart()
    initTaskChart()
  }, 100)
})
</script>

<style scoped>
.dashboard {
  height: 100%;
  overflow-y: auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
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
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.blacklist-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.high-risk-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.screening-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.result-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  height: 300px;
}

.quick-actions {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  height: 40px;
  padding: 0 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-subtitle {
    font-size: 14px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .stat-content {
    gap: 15px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .action-buttons .el-button {
    flex: 1;
    min-width: 120px;
  }
}
</style>
