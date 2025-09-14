<template>
  <div class="blacklist-form">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="title-section">
          <h1 class="page-title">
            {{ isEdit ? '编辑黑名单' : '添加黑名单' }}
          </h1>
          <div v-if="hasUnsavedChanges" class="save-status">
            <el-tag type="warning" size="small">
              <el-icon><Clock /></el-icon>
              有未保存的更改
            </el-tag>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="saveDraft" :disabled="!hasUnsavedChanges" size="small">
            <el-icon><Document /></el-icon>
            保存草稿
          </el-button>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>
      </div>

      <!-- 表单 -->
      <div class="form-container">
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="120px"
          class="blacklist-form-content"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="KTT名字" prop="ktt_name">
                <el-input
                  v-model="formData.ktt_name"
                  placeholder="请输入KTT名字"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="微信名字" prop="wechat_name">
                <el-input
                  v-model="formData.wechat_name"
                  placeholder="请输入微信名字"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="微信号" prop="wechat_id">
                <el-input
                  v-model="formData.wechat_id"
                  placeholder="请输入微信号"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="风险等级" prop="risk_level">
                <el-select v-model="formData.risk_level" placeholder="选择风险等级">
                  <el-option label="高风险" value="high" />
                  <el-option label="中风险" value="medium" />
                  <el-option label="低风险" value="low" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="下单人姓名" prop="order_name">
                <el-input
                  v-model="formData.order_name"
                  placeholder="请输入下单人姓名"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="主要电话号码" prop="phone">
                <el-input
                  v-model="formData.phone"
                  placeholder="请输入手机号码"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="原始数据" prop="order_name_phone">
            <el-input
              v-model="formData.order_name_phone"
              type="textarea"
              :rows="2"
              placeholder="请输入下单名字和电话（原始数据）"
            />
            <div class="form-tip">
              提示：可以输入"姓名+电话号码"格式，系统会自动分离
            </div>
          </el-form-item>

          <el-form-item label="下单地址1" prop="order_address1">
            <el-input
              v-model="formData.order_address1"
              type="textarea"
              :rows="2"
              placeholder="请输入主要收货地址"
            />
          </el-form-item>

          <el-form-item label="下单地址2" prop="order_address2">
            <el-input
              v-model="formData.order_address2"
              type="textarea"
              :rows="2"
              placeholder="请输入备用收货地址"
            />
          </el-form-item>

          <el-form-item label="入黑原因" prop="blacklist_reason">
            <el-input
              v-model="formData.blacklist_reason"
              type="textarea"
              :rows="3"
              placeholder="请详细说明入黑名单的原因"
            />
          </el-form-item>

          <!-- 电话号码列表 -->
          <el-form-item label="电话号码列表" v-if="phoneNumbers.length > 0">
            <div class="phone-list">
              <el-tag
                v-for="(phone, index) in phoneNumbers"
                :key="index"
                type="info"
                closable
                @close="removePhone(index)"
                class="phone-tag"
              >
                {{ phone }}
              </el-tag>
              <el-button
                type="primary"
                size="small"
                @click="showAddPhoneDialog = true"
                class="add-phone-btn"
              >
                <el-icon><Plus /></el-icon>
                添加电话
              </el-button>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              {{ isEdit ? '更新' : '创建' }}
            </el-button>
            <el-button @click="goBack">取消</el-button>
            <el-button v-if="isEdit" type="danger" @click="handleDelete">
              删除
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 添加电话号码对话框 -->
    <el-dialog
      v-model="showAddPhoneDialog"
      title="添加电话号码"
      width="400px"
    >
      <el-form :model="phoneForm" :rules="phoneRules" ref="phoneFormRef">
        <el-form-item label="电话号码" prop="phone">
          <el-input
            v-model="phoneForm.phone"
            placeholder="请输入手机号码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPhoneDialog = false">取消</el-button>
        <el-button type="primary" @click="addPhone">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowLeft, Plus, Clock, Document } from '@element-plus/icons-vue'
import { blacklistApi } from '@/api/blacklist'

const route = useRoute()
const router = useRouter()

// 表单引用
const formRef = ref<FormInstance>()
const phoneFormRef = ref<FormInstance>()

// 响应式数据
const submitting = ref(false)
const showAddPhoneDialog = ref(false)
const phoneNumbers = ref<string[]>([])
const hasUnsavedChanges = ref(false)
const autoSaveTimer = ref<NodeJS.Timeout | null>(null)

// 是否为编辑模式
const isEdit = computed(() => !!route.params.id)

// 表单数据
const formData = reactive({
  ktt_name: '',
  wechat_name: '',
  wechat_id: '',
  order_name: '',
  phone: '',
  order_name_phone: '',
  order_address1: '',
  order_address2: '',
  blacklist_reason: '',
  risk_level: 'medium'
})

// 电话号码表单
const phoneForm = reactive({
  phone: ''
})

// 表单验证规则（已取消所有必填项）
const formRules: FormRules = {}

// 电话号码验证规则（已取消必填校验）
const phoneRules: FormRules = {}

// 监听原始数据变化，自动分离姓名和电话
watch(() => formData.order_name_phone, (newValue) => {
  if (newValue) {
    const { name, phone } = extractNameAndPhone(newValue)
    if (name) formData.order_name = name
    if (phone) formData.phone = phone
  }
})

// 监听表单数据变化，标记为有未保存更改
watch(formData, () => {
  hasUnsavedChanges.value = true
  // 自动保存草稿（延迟3秒）
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
  }
  autoSaveTimer.value = setTimeout(() => {
    saveDraft()
  }, 3000)
}, { deep: true })

// 监听电话号码变化
watch(phoneNumbers, () => {
  hasUnsavedChanges.value = true
}, { deep: true })

// 提取姓名和电话号码
const extractNameAndPhone = (text: string) => {
  const phonePattern = /1[3-9]\d{9}/g
  const phones = text.match(phonePattern) || []
  const phone = phones[0] || ''
  
  const name = text.replace(/[0-9\s\-\+\(\)]+/g, '').trim()
  
  return { name, phone }
}

// 保存草稿
const saveDraft = () => {
  try {
    const draftData = {
      ...formData,
      phone_numbers: phoneNumbers.value,
      saved_at: new Date().toISOString()
    }
    localStorage.setItem('blacklist_draft', JSON.stringify(draftData))
    console.log('草稿已保存')
  } catch (error) {
    console.error('保存草稿失败:', error)
  }
}

// 加载草稿
const loadDraft = () => {
  try {
    const draftData = localStorage.getItem('blacklist_draft')
    if (draftData) {
      const parsed = JSON.parse(draftData)
      Object.assign(formData, parsed)
      if (parsed.phone_numbers) {
        phoneNumbers.value = parsed.phone_numbers
      }
      hasUnsavedChanges.value = false
      console.log('草稿已加载')
    }
  } catch (error) {
    console.error('加载草稿失败:', error)
  }
}

// 清除草稿
const clearDraft = () => {
  localStorage.removeItem('blacklist_draft')
  hasUnsavedChanges.value = false
}

// 清空所有数据
const clearAllData = () => {
  // 清空表单数据
  Object.assign(formData, {
    ktt_name: '',
    wechat_name: '',
    wechat_id: '',
    order_name: '',
    phone: '',
    order_name_phone: '',
    order_address1: '',
    order_address2: '',
    blacklist_reason: '',
    risk_level: 'medium'
  })
  
  // 清空电话号码列表
  phoneNumbers.value = []
  
  // 清空草稿
  clearDraft()
  
  console.log('所有数据已清空，页面完全干净')
}

// 获取黑名单详情
const fetchBlacklistDetail = async (id: string) => {
  try {
    console.log('开始获取黑名单详情，ID:', id)
    const response = await blacklistApi.getBlacklistDetail(parseInt(id))
    console.log('API响应状态:', response ? '成功' : '失败')
    console.log('获取到的详情数据:', response)
    
    if (!response) {
      throw new Error('获取数据失败')
    }
    
    // 映射数据到表单
    console.log('开始映射数据到表单...')
    
    // 使用Object.assign确保响应式更新
    Object.assign(formData, {
      ktt_name: response.ktt_name || '',
      wechat_name: response.wechat_name || '',
      wechat_id: response.wechat_id || '',
      order_name_phone: response.order_name_phone || '',
      order_address1: response.order_address1 || '',
      order_address2: response.order_address2 || '',
      blacklist_reason: response.blacklist_reason || '',
      risk_level: response.risk_level || 'medium'
    })
    
    console.log('基础字段映射完成')
    
    // 从order_name_phone中提取姓名和电话
    if (response.order_name_phone) {
      console.log('提取姓名和电话，原始数据:', response.order_name_phone)
      const { name, phone } = extractNameAndPhone(response.order_name_phone)
      
      // 使用Object.assign确保响应式更新
      Object.assign(formData, {
        order_name: name,
        phone: phone
      })
      
      console.log('提取结果 - 姓名:', name, '电话:', phone)
    }
    
    // 处理电话号码列表
    if (response.phone_numbers) {
      console.log('处理电话号码列表，原始数据:', response.phone_numbers)
      phoneNumbers.value = Array.isArray(response.phone_numbers) 
        ? response.phone_numbers 
        : JSON.parse(response.phone_numbers)
      console.log('处理后的电话号码列表:', phoneNumbers.value)
    }
    
    console.log('数据映射完成，最终表单数据:', formData)
    console.log('最终电话号码列表:', phoneNumbers.value)
    
    // 使用nextTick确保DOM更新
    await nextTick()
    
    // 强制更新响应式数据
    hasUnsavedChanges.value = false
    
    console.log('数据回显完成，表单应该已更新')
    
  } catch (error: any) {
    console.error('获取黑名单详情失败:', error)
    ElMessage.error(error.message || '获取黑名单详情失败')
    goBack()
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    submitting.value = true
    
    const submitData = {
      ...formData,
      phone_numbers: phoneNumbers.value
    }
    
    if (isEdit.value) {
      await blacklistApi.updateBlacklist(parseInt(route.params.id as string), submitData)
      ElMessage.success('更新成功')
    } else {
      await blacklistApi.createBlacklist(submitData)
      ElMessage.success('创建成功')
    }
    
    // 清除草稿
    clearDraft()
    goBack()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 删除记录
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条黑名单记录吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await blacklistApi.deleteBlacklist(parseInt(route.params.id as string))
    ElMessage.success('删除成功')
    goBack()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 添加电话号码
const addPhone = async () => {
  if (!phoneFormRef.value) return
  
  try {
    const valid = await phoneFormRef.value.validate()
    if (!valid) return
    
    if (phoneNumbers.value.includes(phoneForm.phone)) {
      ElMessage.warning('该电话号码已存在')
      return
    }
    
    phoneNumbers.value.push(phoneForm.phone)
    phoneForm.phone = ''
    showAddPhoneDialog.value = false
    ElMessage.success('添加成功')
  } catch (error: any) {
    ElMessage.error('添加失败')
  }
}

// 移除电话号码
const removePhone = (index: number) => {
  phoneNumbers.value.splice(index, 1)
}

// 返回列表
const goBack = () => {
  router.push('/blacklist')
}

// 组件挂载
onMounted(() => {
  console.log('组件挂载，编辑模式:', isEdit.value)
  console.log('路由参数ID:', route.params.id)
  
  if (isEdit.value) {
    console.log('开始获取黑名单详情...')
    fetchBlacklistDetail(route.params.id as string)
  } else {
    // 新建模式，确保页面完全干净
    console.log('新建模式，清空所有数据...')
    clearAllData()
  }
})

// 页面离开前确认
onBeforeUnmount(() => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
  }
})

// 路由离开前确认
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    ElMessageBox.confirm(
      '您有未保存的更改，确定要离开吗？',
      '确认离开',
      {
        confirmButtonText: '确定离开',
        cancelButtonText: '继续编辑',
        type: 'warning'
      }
    ).then(() => {
      next()
    }).catch(() => {
      next(false)
    })
  } else {
    next()
  }
})
</script>

<style scoped>
.blacklist-form {
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.save-status {
  margin-left: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.form-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.blacklist-form-content {
  max-width: 800px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.phone-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.phone-tag {
  margin: 0;
}

.add-phone-btn {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .form-container {
    padding: 20px;
  }
  
  .phone-list {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
