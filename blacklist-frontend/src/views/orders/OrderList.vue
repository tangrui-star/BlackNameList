<template>
  <div class="order-list">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">订单管理</h1>
        <div class="page-actions">
          <!-- <el-button type="primary" @click="goToCreate">
            <el-icon><Plus /></el-icon>
            添加订单
          </el-button> -->
          <el-button type="success" @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入Excel
          </el-button>
          <!-- <el-button type="warning" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
          <el-button type="danger" @click="handleBatchCheckBlacklist" :disabled="selectedRows.length === 0">
            <el-icon><Search /></el-icon>
            批量检测黑名单
          </el-button> -->
        </div>
      </div>

      <!-- 分组管理区域 -->
      <div class="group-management">
        <div class="group-header">
          <h2 class="group-title">分组管理</h2>
          <div class="group-actions">
            <el-button type="primary" @click="handleCreateGroup">
              <el-icon><Plus /></el-icon>
              创建分组
            </el-button>
            <el-button type="success" @click="handleGroupImport">
              <el-icon><Upload /></el-icon>
              导入到分组
            </el-button>
            <el-button 
              type="warning" 
              @click="handleGroupBatchCheck" 
              :disabled="!selectedGroup"
              :loading="groupCheckLoading"
            >
              <el-icon><Search /></el-icon>
              批量检测黑名单
              <span v-if="!selectedGroup" style="margin-left: 8px; font-size: 12px; color: #999;">
                (请先选择分组)
              </span>
            </el-button>
          </div>
        </div>
        
        <!-- 分组列表 -->
        <div class="group-list">
          <el-table
            :data="groupList"
            v-loading="groupLoading"
            stripe
            border
            @row-click="handleGroupSelect"
            highlight-current-row
            style="width: 100%"
          >
            <el-table-column prop="name" label="分组名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
            <el-table-column prop="file_name" label="文件名" min-width="200" show-overflow-tooltip />
            <el-table-column prop="total_orders" label="订单总数" width="100" align="center" />
            <el-table-column prop="checked_orders" label="已检测" width="100" align="center" />
            <el-table-column prop="blacklist_matches" label="黑名单匹配" width="120" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.blacklist_matches > 0" type="danger">
                  {{ row.blacklist_matches }}
                </el-tag>
                <span v-else>{{ row.blacklist_matches }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getGroupStatusType(row.status)">
                  {{ getGroupStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="warning" @click="handleGroupBlacklistCheck(row)">
                  <el-icon><Search /></el-icon>
                  检测黑名单
                </el-button>
                <el-button size="small" @click="handleGroupEdit(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleGroupDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 当前选中分组信息 -->
        <div v-if="selectedGroup" class="selected-group-info">
          <el-alert
            :title="`当前选中分组: ${selectedGroup.name}`"
            :description="getGroupStatsDescription(selectedGroup)"
            type="info"
            show-icon
            :closable="false"
          />
        </div>
      </div>

      <!-- 搜索表单 -->
      <div class="search-form">
        <el-form :model="searchForm" inline>
          <el-form-item label="分组">
            <el-select 
              v-model="searchForm.group_id" 
              placeholder="选择分组" 
              clearable
              @change="handleGroupChange"
            >
              <el-option
                v-for="group in groupList"
                :key="group.id"
                :label="group.name"
                :value="group.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="跟团号">
            <el-input
              v-model="searchForm.group_tour_number"
              placeholder="输入跟团号"
              clearable
            />
          </el-form-item>
          <el-form-item label="下单人">
            <el-input
              v-model="searchForm.orderer"
              placeholder="输入下单人姓名"
              clearable
            />
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input
              v-model="searchForm.contact_phone"
              placeholder="输入联系电话"
              clearable
            />
          </el-form-item>
          <el-form-item label="订单状态">
            <el-select v-model="searchForm.order_status" placeholder="选择订单状态" clearable>
              <el-option label="待处理" value="pending" />
              <el-option label="已支付" value="paid" />
              <el-option label="已发货" value="shipped" />
              <el-option label="已送达" value="delivered" />
              <el-option label="已取消" value="cancelled" />
              <el-option label="已退款" value="refunded" />
            </el-select>
          </el-form-item>
          <el-form-item label="黑名单检测">
            <el-select v-model="searchForm.is_blacklist_checked" placeholder="选择检测状态" clearable>
              <el-option label="未检测" value="no" />
              <el-option label="已检测" value="yes" />
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
          @selection-change="handleSelectionChange"
          :default-sort="{ prop: 'id', order: 'descending' }"
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="订单ID" width="80" sortable />
          <el-table-column prop="group_tour_number" label="跟团号" min-width="120" show-overflow-tooltip />
          <el-table-column prop="orderer" label="下单人（KTT名字）" min-width="120" show-overflow-tooltip />
          <el-table-column prop="member_remarks" label="团员备注" min-width="150" show-overflow-tooltip />
          <el-table-column prop="payment_time" label="支付时间" min-width="160" sortable>
            <template #default="{ row }">
              {{ formatDate(row.payment_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="group_leader_remarks" label="团长备注" min-width="150" show-overflow-tooltip />
          <el-table-column prop="product" label="商品" min-width="200" show-overflow-tooltip />
          <el-table-column prop="order_amount" label="订单金额" width="100" sortable>
            <template #default="{ row }">
              <span class="amount">¥{{ row.order_amount || '0.00' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="refund_amount" label="退款金额" width="100">
            <template #default="{ row }">
              <span class="refund-amount">¥{{ row.refund_amount || '0.00' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="order_status" label="订单状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getOrderStatusType(row.order_status)">
                {{ getOrderStatusText(row.order_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pickup_point" label="自提点" min-width="150" show-overflow-tooltip />
          <el-table-column prop="consignee" label="收货人" min-width="100" show-overflow-tooltip />
          <el-table-column prop="contact_phone" label="联系电话" min-width="140" show-overflow-tooltip />
          <el-table-column prop="detailed_address" label="详细地址" min-width="200" show-overflow-tooltip />
          <el-table-column prop="is_blacklist_checked" label="黑名单检测" width="120">
            <template #default="{ row }">
              <el-tag :type="getBlacklistCheckType(row.is_blacklist_checked)">
                {{ getBlacklistCheckText(row.is_blacklist_checked) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="blacklist_risk_level" label="风险等级" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.blacklist_risk_level && row.blacklist_risk_level !== 'none'" 
                     :type="getRiskLevelType(row.blacklist_risk_level)">
                {{ getRiskLevelText(row.blacklist_risk_level) }}
              </el-tag>
              <span v-else class="text-gray-400">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="blacklist_match_info" label="匹配信息" width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.blacklist_match_info && row.blacklist_match_info !== '未匹配到黑名单'" 
                    class="match-info">
                {{ row.blacklist_match_info }}
              </span>
              <span v-else class="text-gray-400">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="blacklist_match_details" label="匹配详情" width="250" show-overflow-tooltip>
            <template #default="{ row }">
              <span v-if="row.blacklist_match_details" class="match-details">
                {{ row.blacklist_match_details }}
              </span>
              <span v-else class="text-gray-400">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" sortable>
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="goToEdit(row.id)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="warning" size="small" @click="handleCheckBlacklist(row)">
                <el-icon><Search /></el-icon>
                检测黑名单
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

    <!-- 检测结果展示区域 -->
    <div v-if="detectionResults.length > 0" class="detection-results-section">
      <el-card class="detection-results-card">
        <template #header>
          <div class="detection-header">
            <div class="detection-title">
              <el-icon class="warning-icon"><Warning /></el-icon>
              <span>黑名单检测结果</span>
            </div>
            <div class="detection-actions">
              <el-button type="primary" size="small" @click="showDetectionResults">
                <el-icon><View /></el-icon>
                查看详情
              </el-button>
              <el-button type="success" size="small" @click="exportDetectionResults">
                <el-icon><Download /></el-icon>
                导出结果
              </el-button>
            </div>
          </div>
        </template>
        
        <!-- 检测统计 -->
        <div class="detection-stats">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ detectionStats.total_orders }}</div>
                <div class="stat-label">总订单数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ detectionStats.checked_orders }}</div>
                <div class="stat-label">已检测订单</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item danger">
                <div class="stat-number">{{ detectionResults.length }}</div>
                <div class="stat-label">匹配订单数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item warning">
                <div class="stat-number">{{ highRiskResults.length }}</div>
                <div class="stat-label">高风险订单</div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 检测结果预览 -->
        <div class="detection-preview">
          <h4>黑名单匹配订单预览（前5条）</h4>
          <el-table :data="detectionResults.slice(0, 5)" stripe size="small">
            <el-table-column prop="id" label="订单ID" width="80" />
            <el-table-column prop="group_tour_number" label="跟团号" width="100" />
            <el-table-column prop="orderer" label="下单人" width="120" show-overflow-tooltip />
            <el-table-column prop="consignee" label="收货人" width="100" show-overflow-tooltip />
            <el-table-column prop="contact_phone" label="联系电话" width="130" />
            <el-table-column prop="order_amount" label="订单金额" width="100">
              <template #default="{ row }">
                <span class="amount">¥{{ row.order_amount || '0.00' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="blacklist_risk_level" label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getRiskLevelType(row.blacklist_risk_level)" size="small">
                  {{ getRiskLevelText(row.blacklist_risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="blacklist_match_info" label="匹配信息" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.blacklist_match_info && row.blacklist_match_info !== '未匹配到黑名单'" 
                      class="match-info">
                  {{ row.blacklist_match_info }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="blacklist_match_details" label="匹配详情" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.blacklist_match_details" class="match-details">
                  {{ row.blacklist_match_details }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewOrderDetail(row)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入Excel文件"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="upload-instructions">
        <h4>Excel文件格式要求：</h4>
        <ul>
          <li>文件格式：.xlsx 或 .xls</li>
          <li>文件大小：不超过10MB</li>
          <li>必须包含以下列：跟团号、下单人、团员备注、支付时间、团长备注、商品、订单金额、退款金额、订单状态、自提点、收货人、联系电话、详细地址</li>
          <li>可选列：分类、数量（如果存在会被忽略）</li>
        </ul>
      </div>
      
      <!-- 分组名称输入 -->
      <div class="group-selection" style="margin-bottom: 20px;">
        <el-form-item label="分组名称">
          <el-input 
            v-model="importGroupName" 
            placeholder="留空则使用文件名作为分组名称" 
            style="width: 100%"
            clearable
          />
        </el-form-item>
      </div>
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

    <!-- 检测结果详情弹窗 -->
    <el-dialog
      v-model="detectionModalVisible"
      title="黑名单检测结果详情"
      width="1200px"
      :close-on-click-modal="false"
      class="detection-modal"
    >
      <div class="detection-modal-content">
        <!-- 检测统计概览 -->
        <div class="detection-overview">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon total">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">{{ detectionStats.total_orders }}</div>
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
                    <div class="stat-number">{{ detectionStats.checked_orders }}</div>
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
                    <div class="stat-number">{{ detectionResults.length }}</div>
                    <div class="stat-label">匹配订单数</div>
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
                    <div class="stat-number">{{ highRiskResults.length }}</div>
                    <div class="stat-label">高风险订单</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 筛选按钮组 -->
        <div class="filter-buttons">
          <el-button-group>
            <el-button 
              :type="currentFilter === 'all' ? 'primary' : ''" 
              @click="setFilter('all')"
            >
              全部匹配 ({{ detectionResults.length }})
            </el-button>
            <el-button 
              :type="currentFilter === 'high' ? 'primary' : ''" 
              @click="setFilter('high')"
            >
              高风险 ({{ highRiskResults.length }})
            </el-button>
            <el-button 
              :type="currentFilter === 'medium' ? 'primary' : ''" 
              @click="setFilter('medium')"
            >
              中风险 ({{ mediumRiskResults.length }})
            </el-button>
          </el-button-group>
        </div>

        <!-- 检测结果表格 -->
        <div class="detection-table">
          <el-table
            :data="filteredResults"
            stripe
            border
            height="500"
            @row-click="viewOrderDetail"
            style="cursor: pointer;"
            :default-sort="{ prop: 'blacklist_risk_level', order: 'descending' }"
          >
            <el-table-column prop="id" label="订单ID" width="80" sortable />
            <el-table-column prop="group_tour_number" label="跟团号" width="100" />
            <el-table-column prop="orderer" label="下单人" width="120" show-overflow-tooltip />
            <el-table-column prop="member_remarks" label="团员备注" width="150" show-overflow-tooltip />
            <el-table-column prop="consignee" label="收货人" width="100" show-overflow-tooltip />
            <el-table-column prop="contact_phone" label="联系电话" width="130" />
            <el-table-column prop="detailed_address" label="详细地址" width="200" show-overflow-tooltip />
            <el-table-column prop="order_amount" label="订单金额" width="100" sortable>
              <template #default="{ row }">
                <span class="amount">¥{{ row.order_amount || '0.00' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="order_status" label="订单状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getOrderStatusType(row.order_status)">
                  {{ getOrderStatusText(row.order_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="blacklist_risk_level" label="风险等级" width="100" sortable>
              <template #default="{ row }">
                <el-tag :type="getRiskLevelType(row.blacklist_risk_level)" size="large">
                  {{ getRiskLevelText(row.blacklist_risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="blacklist_match_info" label="匹配信息" width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.blacklist_match_info && row.blacklist_match_info !== '未匹配到黑名单'" 
                      class="match-info">
                  {{ row.blacklist_match_info }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="blacklist_match_details" label="匹配详情" width="250" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.blacklist_match_details" class="match-details">
                  {{ row.blacklist_match_details }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160" sortable>
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click.stop="viewOrderDetail(row)">
                  <el-icon><View /></el-icon>
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 操作按钮 -->
        <div class="detection-actions">
          <el-button type="success" @click="exportDetectionResults">
            <el-icon><Download /></el-icon>
            导出检测结果
          </el-button>
          <el-button type="primary" @click="refreshDetectionResults">
            <el-icon><Refresh /></el-icon>
            刷新结果
          </el-button>
          <el-button @click="closeDetectionModal">
            关闭
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
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
  UploadFilled,
  Warning,
  View,
  Document,
  Check,
  TrendCharts
} from '@element-plus/icons-vue'
import { orderApi } from '@/api/order'
import { groupApi } from '@/api/group'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'
import type { Group } from '@/types/group'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const tableData = ref<any[]>([])
const selectedRows = ref<any[]>([])

// 分组相关数据
const groupLoading = ref(false)
const groupList = ref<Group[]>([])
const selectedGroup = ref<Group | null>(null)
const groupCheckLoading = ref(false)

// 检测结果相关数据
const detectionResults = ref<any[]>([])
const detectionModalVisible = ref(false)
const detectionStats = ref({
  total_orders: 0,
  checked_orders: 0,
  blacklist_matches: 0,
  new_matches: 0
})

// 筛选相关数据
const currentFilter = ref('all')
const filteredResults = ref<any[]>([])

// 搜索表单
const searchForm = reactive({
  group_id: null as number | null,
  group_tour_number: '',
  orderer: '',
  contact_phone: '',
  order_status: '',
  is_blacklist_checked: ''
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
const importGroupName = ref<string>('')

// 计算属性
const uploadAction = computed(() => {
  const baseUrl = '/api/v1/orders/upload-excel'
  // 如果有分组名称则使用，否则后端会使用文件名
  if (importGroupName.value && importGroupName.value.trim()) {
    return `${baseUrl}?group_name=${encodeURIComponent(importGroupName.value.trim())}`
  }
  return baseUrl
})
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))

// 获取分组列表
const fetchGroupList = async () => {
  try {
    groupLoading.value = true
    const response = await groupApi.getGroupList({
      skip: 0,
      limit: 100,
      status: 'active'
    })
    
    if (response && response.data) {
      groupList.value = response.data
      console.log(`加载了 ${response.data.length} 个分组`)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取分组列表失败')
    groupList.value = []
  } finally {
    groupLoading.value = false
  }
}

// 分组选择
const handleGroupSelect = (group: Group) => {
  console.log('🔍 选择分组:', group)
  selectedGroup.value = group
  searchForm.group_id = group.id
  pagination.page = 1
  fetchOrderList()
}

// 分组变更
const handleGroupChange = (groupId: number | null) => {
  console.log('🔍 分组变更，分组ID:', groupId)
  if (groupId) {
    const group = groupList.value.find(g => g.id === groupId)
    if (group) {
      console.log('🔍 找到分组:', group)
      selectedGroup.value = group
    } else {
      console.log('❌ 未找到分组，分组ID:', groupId)
    }
  } else {
    console.log('🔍 清空分组选择')
    selectedGroup.value = null
  }
  pagination.page = 1
  fetchOrderList()
}

// 创建分组
const handleCreateGroup = () => {
  ElMessage.info('创建分组功能开发中...')
}

// 分组导入
const handleGroupImport = () => {
  ElMessage.info('分组导入功能开发中...')
}

// 分组批量检测
const handleGroupBatchCheck = async () => {
  console.log('🔍 开始分组批量检测，当前选中分组:', selectedGroup.value)
  
  if (!selectedGroup.value) {
    ElMessage.warning('请先选择一个分组')
    return
  }
  
  try {
    groupCheckLoading.value = true
    console.log('📤 调用批量检测API，分组ID:', selectedGroup.value.id)
    
    const response = await groupApi.batchCheckBlacklist(selectedGroup.value.id, true) // 改为强制重新检测
    
    console.log('📊 批量检测响应:', response)
    
    // 保存检测结果
    detectionStats.value = {
      total_orders: response.total_orders,
      checked_orders: response.checked_orders,
      blacklist_matches: response.blacklist_matches,
      new_matches: response.new_matches
    }
    
    // 获取检测后的订单详情
    await fetchDetectionResults()
    
    ElMessage.success(response.message)
    
    // 刷新分组列表和订单列表
    await fetchGroupList()
    await fetchOrderList()
    
    // 显示检测结果
    showDetectionResults()
  } catch (error: any) {
    console.error('❌ 批量检测失败:', error)
    ElMessage.error(error.message || '批量检测失败')
  } finally {
    groupCheckLoading.value = false
  }
}

// 获取检测结果
const fetchDetectionResults = async () => {
  if (!selectedGroup.value) return
  
  try {
    const response = await orderApi.getOrderList({
      group_id: selectedGroup.value.id,
      skip: 0,
      limit: 1000, // 增加限制以获取更多数据
      group_tour_number: '',
      orderer: '',
      contact_phone: '',
      order_status: '',
      is_blacklist_checked: 'yes' // 只获取已检测的订单
    })
    
    // 过滤出有黑名单匹配的订单（匹配为True的订单）
    const allOrders = response.data || []
    const matchedOrders = allOrders.filter((order: any) => 
      order.blacklist_risk_level && 
      order.blacklist_risk_level !== 'none' &&
      order.blacklist_risk_level !== 'LOW' && // 排除低风险
      order.blacklist_match_info && 
      order.blacklist_match_info !== '未匹配到黑名单'
    )
    
    // 只显示匹配出来的订单数据
    detectionResults.value = matchedOrders
    
    // 初始化筛选结果
    filteredResults.value = detectionResults.value
    currentFilter.value = 'all'
    
    // 在浏览器控制台输出所有匹配为True的订单
    console.log('🔍 所有匹配为True的订单数据:')
    console.log('📊 总匹配订单数:', matchedOrders.length)
    matchedOrders.forEach((order: any, index: number) => {
      console.log(`\n📋 匹配订单 ${index + 1}:`)
      console.log(`   订单ID: ${order.id}`)
      console.log(`   跟团号: ${order.group_tour_number}`)
      console.log(`   下单人: ${order.orderer}`)
      console.log(`   收货人: ${order.consignee}`)
      console.log(`   联系电话: ${order.contact_phone}`)
      console.log(`   详细地址: ${order.detailed_address}`)
      console.log(`   订单金额: ¥${order.order_amount}`)
      console.log(`   风险等级: ${order.blacklist_risk_level}`)
      console.log(`   匹配信息: ${order.blacklist_match_info}`)
      console.log(`   匹配详情: ${order.blacklist_match_details}`)
      console.log(`   创建时间: ${order.created_at}`)
    })
    
    console.log('📊 检测结果统计:')
    console.log('   总订单数:', allOrders.length)
    console.log('   匹配订单数:', matchedOrders.length)
    console.log('   高风险订单:', matchedOrders.filter(o => o.blacklist_risk_level === 'HIGH').length)
    console.log('   中风险订单:', matchedOrders.filter(o => o.blacklist_risk_level === 'MEDIUM').length)
  } catch (error) {
    console.error('❌ 获取检测结果失败:', error)
  }
}

// 显示检测结果
const showDetectionResults = () => {
  if (detectionResults.value.length > 0) {
    detectionModalVisible.value = true
  }
}

// 关闭检测结果弹窗
const closeDetectionModal = () => {
  detectionModalVisible.value = false
}

// 查看订单详情
const viewOrderDetail = (order: any) => {
  console.log('查看订单详情:', order)
  ElMessage.info(`查看订单 ${order.id} 的详细信息`)
  // 这里可以添加查看详情的逻辑
}

// 导出检测结果
const exportDetectionResults = () => {
  if (detectionResults.value.length === 0) {
    ElMessage.warning('没有检测结果可导出')
    return
  }
  
  // 创建CSV内容 - 包含所有字段
  const headers = [
    '订单ID', '跟团号', '下单人', '团员备注', '支付时间', '团长备注', '商品', 
    '订单金额', '退款金额', '订单状态', '自提点', '收货人', '联系电话', '详细地址',
    '黑名单检测状态', '风险等级', '匹配信息', '匹配详情', '创建时间'
  ]
  
  const csvContent = [
    headers.join(','),
    ...detectionResults.value.map(order => [
      order.id,
      order.group_tour_number || '',
      order.orderer || '',
      `"${(order.member_remarks || '').replace(/"/g, '""')}"`,
      order.payment_time ? formatDate(order.payment_time) : '',
      `"${(order.group_leader_remarks || '').replace(/"/g, '""')}"`,
      `"${(order.product || '').replace(/"/g, '""')}"`,
      order.order_amount || 0,
      order.refund_amount || 0,
      order.order_status || '',
      `"${(order.pickup_point || '').replace(/"/g, '""')}"`,
      order.consignee || '',
      order.contact_phone || '',
      `"${(order.detailed_address || '').replace(/"/g, '""')}"`,
      order.is_blacklist_checked || '',
      order.blacklist_risk_level || '',
      `"${(order.blacklist_match_info || '').replace(/"/g, '""')}"`,
      `"${(order.blacklist_match_details || '').replace(/"/g, '""')}"`,
      order.created_at ? formatDate(order.created_at) : ''
    ].join(','))
  ].join('\n')
  
  // 创建下载链接
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `黑名单检测结果_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('检测结果导出成功')
}

// 刷新检测结果
const refreshDetectionResults = async () => {
  await fetchDetectionResults()
  ElMessage.success('检测结果已刷新')
}

// 计算属性 - 各种筛选结果（只显示匹配的订单）
// const matchedResults = computed(() => {
//   return detectionResults.value.filter(order => 
//     order.blacklist_risk_level && 
//     order.blacklist_risk_level !== 'none' &&
//     order.blacklist_risk_level !== 'LOW' && // 排除低风险
//     order.blacklist_match_info && 
//     order.blacklist_match_info !== '未匹配到黑名单'
//   )
// })

const highRiskResults = computed(() => {
  return detectionResults.value.filter(order => 
    order.blacklist_risk_level === 'HIGH'
  )
})

const mediumRiskResults = computed(() => {
  return detectionResults.value.filter(order => 
    order.blacklist_risk_level === 'MEDIUM'
  )
})

// const lowRiskResults = computed(() => {
//   return detectionResults.value.filter(order => 
//     order.blacklist_risk_level === 'LOW'
//   )
// })

// 设置筛选条件
const setFilter = (filterType: string) => {
  currentFilter.value = filterType
  
  switch (filterType) {
    case 'all':
      filteredResults.value = detectionResults.value
      break
    case 'high':
      filteredResults.value = highRiskResults.value
      break
    case 'medium':
      filteredResults.value = mediumRiskResults.value
      break
    default:
      filteredResults.value = detectionResults.value
  }
  
  console.log(`🔍 筛选条件: ${filterType}, 结果数量: ${filteredResults.value.length}`)
  
  // 在控制台输出当前筛选结果
  if (filteredResults.value.length > 0) {
    console.log(`📋 当前筛选结果 (${filterType}):`)
    filteredResults.value.forEach((order: any, index: number) => {
      console.log(`   ${index + 1}. 订单ID: ${order.id}, 风险等级: ${order.blacklist_risk_level}, 匹配信息: ${order.blacklist_match_info}`)
    })
  }
}

// 分组删除
const handleGroupDelete = async (group: Group) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分组 "${group.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await groupApi.deleteGroup(group.id)
    ElMessage.success('分组删除成功')
    
    // 刷新分组列表
    await fetchGroupList()
    
    // 如果删除的是当前选中的分组，清空选择
    if (selectedGroup.value && selectedGroup.value.id === group.id) {
      selectedGroup.value = null
      searchForm.group_id = null
      await fetchOrderList()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除分组失败')
    }
  }
}

// 分组编辑
const handleGroupEdit = (_group: Group) => {
  ElMessage.info('分组编辑功能暂未实现')
}

// 分组黑名单检测
const handleGroupBlacklistCheck = async (group: Group) => {
  try {
    ElMessage.info(`开始检测分组 "${group.name}" 的黑名单...`)
    
    const response = await groupApi.batchCheckBlacklist(group.id, true)
    
    console.log('📊 分组黑名单检测响应:', response)
    
    // 显示检测结果
    if (response.blacklist_matches > 0) {
      ElMessage.warning(`检测完成！发现 ${response.blacklist_matches} 条黑名单匹配记录`)
    } else {
      ElMessage.success('检测完成！未发现黑名单匹配记录')
    }
    
    // 刷新分组列表以获取最新的统计信息
    await fetchGroupList()
    
    // 更新当前选中的分组信息
    if (selectedGroup.value && selectedGroup.value.id === group.id) {
      const updatedGroup = groupList.value.find(g => g.id === group.id)
      if (updatedGroup) {
        selectedGroup.value = updatedGroup
      }
      await fetchOrderList()
    }
    
  } catch (error: any) {
    console.error('分组黑名单检测失败:', error)
    ElMessage.error(error.message || '分组黑名单检测失败')
  }
}

// 获取分组状态类型
const getGroupStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'archived': return 'warning'
    case 'deleted': return 'danger'
    default: return 'info'
  }
}

// 获取分组统计信息描述
const getGroupStatsDescription = (group: Group) => {
  // 如果已检测订单数为0，说明还没有进行过检测，显示0
  if (group.checked_orders === 0) {
    return `订单总数: ${group.total_orders} | 已检测: 0 | 黑名单匹配: 0 (未检测)`
  }
  
  // 如果已检测订单数大于0，显示实际检测结果
  return `订单总数: ${group.total_orders} | 已检测: ${group.checked_orders} | 黑名单匹配: ${group.blacklist_matches}`
}

// 获取分组状态文本
const getGroupStatusText = (status: string) => {
  switch (status) {
    case 'active': return '活跃'
    case 'archived': return '已归档'
    case 'deleted': return '已删除'
    default: return '未知'
  }
}

// 获取订单列表
const fetchOrderList = async () => {
  try {
    loading.value = true
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      ...searchForm,
      group_id: searchForm.group_id || undefined
    }
    
    const response = await orderApi.getOrderList(params)
    console.log('订单API响应:', response)
    
    if (response && response.data) {
      tableData.value = response.data
      pagination.total = response.total || 0
      console.log(`加载了 ${response.data.length} 条记录，总共 ${response.total} 条`)
    } else {
      console.error('API返回格式错误:', response)
      tableData.value = []
      pagination.total = 0
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取订单列表失败')
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchOrderList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    group_id: null,
    group_tour_number: '',
    orderer: '',
    contact_phone: '',
    order_status: '',
    is_blacklist_checked: ''
  })
  selectedGroup.value = null
  pagination.page = 1
  fetchOrderList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  fetchOrderList()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  fetchOrderList()
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
  router.push('/orders/create')
}

const goToEdit = (id: number) => {
  router.push(`/orders/${id}/edit`)
}

// 删除记录
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除订单"${row.group_tour_number || '未知'}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await orderApi.deleteOrder(row.id)
    ElMessage.success('删除成功')
    fetchOrderList()
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
    await orderApi.batchDeleteOrders(ids)
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchOrderList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

// 检测黑名单
const handleCheckBlacklist = async (row: any) => {
  try {
    const result = await orderApi.checkBlacklist(row.id)
    if (result.is_blacklist) {
      ElMessage.warning(`检测到黑名单风险！风险等级：${result.risk_level}`)
    } else {
      ElMessage.success('未检测到黑名单风险')
    }
    fetchOrderList()
  } catch (error: any) {
    ElMessage.error(error.message || '黑名单检测失败')
  }
}

// 批量检测黑名单
const handleBatchCheckBlacklist = async () => {
  try {
    const ids = selectedRows.value.map(row => row.id)
    const result = await orderApi.batchCheckBlacklist(ids)
    
    const blacklistCount = result.results.filter(r => r.is_blacklist).length
    if (blacklistCount > 0) {
      ElMessage.warning(`批量检测完成，发现 ${blacklistCount} 条黑名单风险记录`)
    } else {
      ElMessage.success('批量检测完成，未发现黑名单风险')
    }
    
    selectedRows.value = []
    fetchOrderList()
  } catch (error: any) {
    ElMessage.error(error.message || '批量黑名单检测失败')
  }
}

// 导入功能
const handleImport = () => {
  importDialogVisible.value = true
}

const beforeUpload = (file: File) => {
  // 分组名称验证已移除，允许使用文件名作为默认值
  
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

const handleUploadSuccess = (response: any) => {
  if (response.success) {
    ElMessage.success(`导入成功！创建分组"${response.group_name}"，导入 ${response.imported_count} 条记录，失败 ${response.failed_count} 条`)
    if (response.errors && response.errors.length > 0) {
      console.warn('导入错误:', response.errors)
    }
  } else {
    ElMessage.error(response.message || '导入失败')
  }
  importDialogVisible.value = false
  fileList.value = []
  importGroupName.value = ''
  // 刷新分组列表和订单列表
  fetchGroupList()
  fetchOrderList()
}

const handleUploadError = (error: any) => {
  ElMessage.error('导入失败')
  console.error('Upload error:', error)
}

// 导出功能
const handleExport = async () => {
  try {
    await orderApi.exportOrders(searchForm)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

const handleBatchExport = async () => {
  try {
    const ids = selectedRows.value.map(row => row.id)
    await orderApi.exportOrders({ ids })
    ElMessage.success('批量导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '批量导出失败')
  }
}

// 工具函数
const getOrderStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    paid: 'success',
    shipped: 'primary',
    delivered: 'success',
    cancelled: 'danger',
    refunded: 'info'
  }
  return types[status] || 'info'
}

const getOrderStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    paid: '已支付',
    shipped: '已发货',
    delivered: '已送达',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return texts[status] || '未知'
}

const getBlacklistCheckType = (checked: string) => {
  const types: Record<string, string> = {
    yes: 'success',
    no: 'warning'
  }
  return types[checked] || 'info'
}

const getBlacklistCheckText = (checked: string) => {
  const texts: Record<string, string> = {
    yes: '已检测',
    no: '未检测'
  }
  return texts[checked] || '未知'
}

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
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 组件挂载
onMounted(async () => {
  try {
    if (!authStore.isAuthenticated) {
      console.log('用户未认证，等待认证状态初始化...')
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    console.log('开始获取数据...')
    await fetchGroupList()
    await fetchOrderList()
  } catch (error) {
    console.error('组件挂载时获取数据失败:', error)
  }
})
</script>

<style scoped>
.order-list {
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
  flex-wrap: wrap;
}

.group-management {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  flex-shrink: 0;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.group-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.group-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.group-list {
  margin-bottom: 20px;
  width: 100%;
}

.group-list .el-table {
  width: 100% !important;
}

.selected-group-info {
  margin-top: 15px;
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
  width: 100% !important;
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

.upload-instructions {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.upload-instructions h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.upload-instructions ul {
  margin: 0;
  padding-left: 20px;
}

.upload-instructions li {
  margin-bottom: 5px;
  color: #606266;
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

/* 检测结果样式 */
.detection-results-section {
  margin-top: 20px;
}

.detection-results-card {
  border: 2px solid #e6a23c;
  border-radius: 8px;
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detection-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #e6a23c;
}

.warning-icon {
  font-size: 20px;
  color: #e6a23c;
}

.detection-actions {
  display: flex;
  gap: 10px;
}

.detection-stats {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.stat-item.danger {
  background: #f8d7da;
  border-color: #f5c6cb;
}

.stat-item.warning {
  background: #fff3cd;
  border-color: #ffeaa7;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stat-item.danger .stat-number {
  color: #721c24;
}

.stat-item.warning .stat-number {
  color: #856404;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
}

.detection-preview h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

/* 检测结果弹窗样式 */
.detection-modal .el-dialog__body {
  padding: 20px;
}

.detection-modal-content {
  max-height: 70vh;
  overflow-y: auto;
}

.detection-overview {
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
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
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

.stat-info .stat-number {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-info .stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.filter-buttons {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.filter-buttons .el-button-group {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.filter-buttons .el-button {
  border-radius: 0;
  border: none;
  background: #f5f7fa;
  color: #606266;
  font-weight: 500;
  transition: all 0.3s ease;
}

.filter-buttons .el-button:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.filter-buttons .el-button.is-active,
.filter-buttons .el-button--primary {
  background: #1890ff;
  color: white;
  box-shadow: 0 2px 4px rgba(24, 144, 255, 0.3);
}

.filter-buttons .el-button:first-child {
  border-top-left-radius: 6px;
  border-bottom-left-radius: 6px;
}

.filter-buttons .el-button:last-child {
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
}

.detection-table {
  margin-bottom: 20px;
}

.detection-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.amount {
  font-weight: 600;
  color: #67c23a;
}

.refund-amount {
  font-weight: 600;
  color: #f56c6c;
}

.match-info {
  color: #e6a23c;
  font-weight: 500;
  background: #fdf6ec;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.match-details {
  color: #606266;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  line-height: 1.4;
}

.text-gray-400 {
  color: #c0c4cc;
}
</style>
