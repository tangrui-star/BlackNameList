<template>
  <div class="admin-panel">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">系统管理</h1>
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
            <div class="stat-icon user-icon">
              <el-icon size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.user_stats?.total_users || 0 }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 管理功能 -->
      <div class="admin-sections">
        <el-row :gutter="20">
          <!-- 系统配置 -->
          <el-col :span="12">
            <el-card class="admin-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Setting /></el-icon>
                  <span>系统配置</span>
                </div>
              </template>
              <div class="config-list">
                <div class="config-item" v-for="(config, key) in systemConfig" :key="key">
                  <div class="config-label">{{ config.description || key }}</div>
                  <div class="config-value">{{ config.value }}</div>
                </div>
              </div>
              <div class="card-actions">
                <el-button type="primary" @click="showConfigDialog = true">
                  <el-icon><Edit /></el-icon>
                  编辑配置
                </el-button>
              </div>
            </el-card>
          </el-col>

          <!-- 数据管理 -->
          <el-col :span="12">
            <el-card class="admin-card">
              <template #header>
                <div class="card-header">
                  <el-icon><DataBoard /></el-icon>
                  <span>数据管理</span>
                </div>
              </template>
              <div class="data-actions">
                <el-button type="success" @click="handleBackup">
                  <el-icon><Download /></el-icon>
                  创建备份
                </el-button>
                <el-button type="warning" @click="handleImport">
                  <el-icon><Upload /></el-icon>
                  导入数据
                </el-button>
                <el-button type="info" @click="handleExport">
                  <el-icon><Download /></el-icon>
                  导出数据
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 系统日志 -->
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="24">
            <el-card class="admin-card">
              <template #header>
                <div class="card-header">
                  <el-icon><Document /></el-icon>
                  <span>系统日志</span>
                </div>
              </template>
              <div class="log-filters">
                <el-form :model="logFilters" inline>
                  <el-form-item label="日志级别">
                    <el-select v-model="logFilters.level" placeholder="选择级别" clearable>
                      <el-option label="INFO" value="INFO" />
                      <el-option label="WARNING" value="WARNING" />
                      <el-option label="ERROR" value="ERROR" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="fetchLogs">
                      <el-icon><Search /></el-icon>
                      查询日志
                    </el-button>
                    <el-button @click="resetLogFilters">
                      <el-icon><Refresh /></el-icon>
                      重置
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
              <div class="log-content">
                <div v-if="logs.length === 0" class="no-logs">
                  暂无日志数据
                </div>
                <div v-else class="log-list">
                  <div v-for="(log, index) in logs" :key="index" class="log-item">
                    <div class="log-time">{{ formatDate(log.created_at) }}</div>
                    <div class="log-level" :class="`level-${log.level?.toLowerCase()}`">
                      {{ log.level }}
                    </div>
                    <div class="log-message">{{ log.message }}</div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 配置编辑对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      title="编辑系统配置"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="configForm" label-width="120px">
        <el-form-item
          v-for="(config, key) in systemConfig"
          :key="key"
          :label="config.description || key"
        >
          <el-input
            v-if="config.type === 'string'"
            v-model="configForm[key]"
            :placeholder="`请输入${config.description || key}`"
          />
          <el-input-number
            v-else-if="config.type === 'number'"
            v-model="configForm[key]"
            :placeholder="`请输入${config.description || key}`"
          />
          <el-switch
            v-else-if="config.type === 'boolean'"
            v-model="configForm[key]"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UserFilled,
  Warning,
  Search,
  User,
  Setting,
  Edit,
  DataBoard,
  Download,
  Upload,
  Document,
  Refresh
} from '@element-plus/icons-vue'
import { adminApi } from '@/api/admin'
import dayjs from 'dayjs'

// 响应式数据
const stats = ref({})
const systemConfig = ref({})
const logs = ref([])
const showConfigDialog = ref(false)
const saving = ref(false)

// 日志筛选
const logFilters = reactive({
  level: ''
})

// 配置表单
const configForm = reactive({})

// 获取系统统计
const fetchStats = async () => {
  try {
    const response = await adminApi.getStats()
    stats.value = response.data || response
  } catch (error: any) {
    ElMessage.error(error.message || '获取统计数据失败')
  }
}

// 获取系统配置
const fetchSystemConfig = async () => {
  try {
    const response = await adminApi.getConfig()
    systemConfig.value = response.data || response
    
    // 初始化配置表单
    const configData = response.data || response
    Object.keys(configData).forEach(key => {
      configForm[key] = configData[key].value
    })
  } catch (error: any) {
    ElMessage.error(error.message || '获取系统配置失败')
  }
}

// 获取系统日志
const fetchLogs = async () => {
  try {
    const response = await adminApi.getLogs(logFilters)
    logs.value = response.data || response
  } catch (error: any) {
    ElMessage.error(error.message || '获取系统日志失败')
  }
}

// 重置日志筛选
const resetLogFilters = () => {
  logFilters.level = ''
  fetchLogs()
}

// 保存配置
const saveConfig = async () => {
  try {
    saving.value = true
    await adminApi.updateConfig(configForm)
    ElMessage.success('配置保存成功')
    showConfigDialog.value = false
    fetchSystemConfig()
  } catch (error: any) {
    ElMessage.error(error.message || '保存配置失败')
  } finally {
    saving.value = false
  }
}

// 数据管理操作
const handleBackup = async () => {
  try {
    await adminApi.createBackup()
    ElMessage.success('备份创建成功')
  } catch (error: any) {
    ElMessage.error(error.message || '创建备份失败')
  }
}

const handleImport = () => {
  ElMessage.info('数据导入功能开发中')
}

const handleExport = () => {
  ElMessage.info('数据导出功能开发中')
}

// 工具函数
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 组件挂载
onMounted(() => {
  fetchStats()
  fetchSystemConfig()
  fetchLogs()
})
</script>

<style scoped>
.admin-panel {
  height: 100%;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
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

.user-icon {
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

.admin-sections {
  margin-bottom: 20px;
}

.admin-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.config-list {
  margin-bottom: 20px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.config-item:last-child {
  border-bottom: none;
}

.config-label {
  font-weight: 500;
  color: #606266;
}

.config-value {
  color: #909399;
  font-family: monospace;
}

.card-actions {
  text-align: right;
}

.data-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.log-filters {
  margin-bottom: 20px;
}

.log-content {
  max-height: 400px;
  overflow-y: auto;
}

.no-logs {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.log-list {
  font-family: monospace;
  font-size: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  width: 150px;
  color: #909399;
  margin-right: 15px;
}

.log-level {
  width: 80px;
  font-weight: 600;
  margin-right: 15px;
}

.level-info {
  color: #409eff;
}

.level-warning {
  color: #e6a23c;
}

.level-error {
  color: #f56c6c;
}

.log-message {
  flex: 1;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
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
  
  .data-actions {
    flex-direction: column;
  }
  
  .log-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .log-time,
  .log-level {
    width: auto;
    margin-right: 0;
  }
}
</style>
