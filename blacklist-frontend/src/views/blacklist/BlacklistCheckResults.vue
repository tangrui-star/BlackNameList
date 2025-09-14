<template>
  <div class="blacklist-check-results">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <el-icon class="title-icon"><Warning /></el-icon>
          黑名单检测结果
        </h1>
        <p class="page-description">订单黑名单风险检测与匹配结果展示</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="statistics-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.total_orders || 0 }}</div>
                <div class="stat-label">总订单数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon checked">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.checked_orders || 0 }}</div>
                <div class="stat-label">已检测订单</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon matches">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.blacklist_matches || 0 }}</div>
                <div class="stat-label">黑名单匹配</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon rate">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.match_rate || 0 }}%</div>
                <div class="stat-label">匹配率</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作区域 -->
    <div class="action-bar">
      <div class="action-left">
        <el-button type="primary" @click="startBatchCheck" :loading="checking">
          <el-icon><Refresh /></el-icon>
          批量检测
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
          刷新数据
        </el-button>
      </div>
      <div class="action-right">
        <el-select v-model="filters.risk_level" placeholder="风险等级" clearable @change="handleFilterChange">
          <el-option label="高风险" value="HIGH" />
          <el-option label="中风险" value="MEDIUM" />
          <el-option label="低风险" value="LOW" />
        </el-select>
        <el-button type="success" @click="exportResults">
          <el-icon><Download /></el-icon>
          导出结果
        </el-button>
      </div>
    </div>

    <!-- 结果表格 -->
    <div class="results-table">
      <el-table
        :data="blacklistMatches"
        v-loading="loading"
        stripe
        border
        height="600"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="order_id" label="订单ID" width="80" />
        
        <el-table-column prop="group_tour_number" label="跟团号" width="100" />
        
        <el-table-column prop="orderer" label="下单人" width="120" show-overflow-tooltip />
        
        <el-table-column prop="contact_phone" label="联系电话" width="130" />
        
        <el-table-column prop="detailed_address" label="详细地址" width="200" show-overflow-tooltip />
        
        <el-table-column prop="order_amount" label="订单金额" width="100">
          <template #default="{ row }">
            <span class="amount">¥{{ row.order_amount }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="order_status" label="订单状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.order_status)">
              {{ getOrderStatusText(row.order_status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskLevelType(row.risk_level)" size="large">
              {{ getRiskLevelText(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="match_info" label="匹配信息" width="150" show-overflow-tooltip />
        
        <el-table-column prop="match_details" label="匹配详情" width="200" show-overflow-tooltip />
        
        <el-table-column prop="payment_time" label="支付时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.payment_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewOrderDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
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

    <!-- 订单详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="订单黑名单匹配详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单ID">{{ selectedOrder.order_id }}</el-descriptions-item>
          <el-descriptions-item label="跟团号">{{ selectedOrder.group_tour_number }}</el-descriptions-item>
          <el-descriptions-item label="下单人">{{ selectedOrder.orderer }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedOrder.contact_phone }}</el-descriptions-item>
          <el-descriptions-item label="详细地址" :span="2">{{ selectedOrder.detailed_address }}</el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ selectedOrder.order_amount }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">{{ getOrderStatusText(selectedOrder.order_status) }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskLevelType(selectedOrder.risk_level)">
              {{ getRiskLevelText(selectedOrder.risk_level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="匹配信息">{{ selectedOrder.match_info }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="match-details">
          <h4>匹配详情：</h4>
          <p>{{ selectedOrder.match_details }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Warning, Document, Check, TrendCharts, Refresh, RefreshRight, Download
} from '@element-plus/icons-vue'
import { blacklistCheckApi, type BlacklistStatistics, type OrderBlacklistInfo } from '@/api/blacklistCheck'
import { formatDate } from '@/utils/date'

// 响应式数据
const loading = ref(false)
const checking = ref(false)
const statistics = ref<BlacklistStatistics>({
  total_orders: 0,
  checked_orders: 0,
  blacklist_matches: 0,
  match_rate: 0,
  risk_level_distribution: {}
})

const blacklistMatches = ref<OrderBlacklistInfo[]>([])
const selectedRows = ref<OrderBlacklistInfo[]>([])

const filters = reactive({
  risk_level: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const detailDialogVisible = ref(false)
const selectedOrder = ref<OrderBlacklistInfo | null>(null)

// 计算属性
const hasSelection = computed(() => selectedRows.value.length > 0)

// 方法
const loadStatistics = async () => {
  try {
    const data = await blacklistCheckApi.getStatistics()
    statistics.value = data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const loadBlacklistMatches = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      risk_level: filters.risk_level || undefined
    }
    const data = await blacklistCheckApi.getBlacklistMatches(params)
    blacklistMatches.value = data.results
    pagination.total = data.total_matches
  } catch (error) {
    console.error('加载黑名单匹配数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const startBatchCheck = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要开始批量检测所有订单吗？这可能需要一些时间。',
      '确认批量检测',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    checking.value = true
    ElMessage.info('开始批量检测，请稍候...')
    
    const data = await blacklistCheckApi.checkOrders({
      skip: 0,
      limit: 1000
    })
    
    ElMessage.success(`批量检测完成！检测了 ${data.total_checked} 个订单，发现 ${data.blacklist_matches} 个黑名单匹配`)
    
    // 刷新数据
    await Promise.all([loadStatistics(), loadBlacklistMatches()])
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量检测失败:', error)
      ElMessage.error('批量检测失败')
    }
  } finally {
    checking.value = false
  }
}

const refreshData = async () => {
  await Promise.all([loadStatistics(), loadBlacklistMatches()])
  ElMessage.success('数据已刷新')
}

const handleFilterChange = () => {
  pagination.page = 1
  loadBlacklistMatches()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadBlacklistMatches()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadBlacklistMatches()
}

const handleSelectionChange = (selection: OrderBlacklistInfo[]) => {
  selectedRows.value = selection
}

const viewOrderDetail = (order: OrderBlacklistInfo) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

const exportResults = () => {
  if (blacklistMatches.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  // 这里可以实现导出功能
  ElMessage.info('导出功能开发中...')
}

// 工具方法
const getOrderStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'PAID': 'success',
    'PENDING': 'warning',
    'CANCELLED': 'danger',
    'SHIPPED': 'info',
    'DELIVERED': 'success',
    'REFUNDED': 'info'
  }
  return statusMap[status] || 'info'
}

const getOrderStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'PAID': '已支付',
    'PENDING': '待支付',
    'CANCELLED': '已取消',
    'SHIPPED': '已发货',
    'DELIVERED': '已送达',
    'REFUNDED': '已退款'
  }
  return statusMap[status] || status
}

const getRiskLevelType = (level: string) => {
  const levelMap: Record<string, string> = {
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'success'
  }
  return levelMap[level] || 'info'
}

const getRiskLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'HIGH': '高风险',
    'MEDIUM': '中风险',
    'LOW': '低风险'
  }
  return levelMap[level] || level
}

// 生命周期
onMounted(() => {
  loadStatistics()
  loadBlacklistMatches()
})
</script>

<style scoped>
.blacklist-check-results {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: #e6a23c;
  font-size: 28px;
}

.page-description {
  color: #606266;
  margin: 4px 0 0 0;
  font-size: 14px;
}

.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.checked {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.matches {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.stat-icon.rate {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.action-left {
  display: flex;
  gap: 12px;
}

.action-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.results-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.amount {
  font-weight: 600;
  color: #67c23a;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.order-detail {
  padding: 20px 0;
}

.match-details {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.match-details h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.match-details p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}
</style>
