<template>
  <div class="screening-upload">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">上传筛查文件</h1>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
      </div>

      <!-- 上传区域 -->
      <div class="upload-container">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>文件上传</span>
            </div>
          </template>
          
          <el-upload
            ref="uploadRef"
            :before-upload="beforeUpload"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".xlsx,.xls,.csv"
            drag
            :auto-upload="false"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 xlsx/xls/csv 文件，且不超过 10MB
              </div>
            </template>
          </el-upload>
          
          <div class="upload-actions">
            <el-button type="primary" @click="handleUpload" :loading="uploading">
              <el-icon><Upload /></el-icon>
              开始上传
            </el-button>
            <el-button @click="handleClear">
              <el-icon><Delete /></el-icon>
              清空文件
            </el-button>
          </div>
        </el-card>

        <!-- 上传说明 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>上传说明</span>
            </div>
          </template>
          
          <div class="info-content">
            <h4>支持的文件格式：</h4>
            <ul>
              <li>Excel文件：.xlsx, .xls</li>
              <li>CSV文件：.csv</li>
            </ul>
            
            <h4>文件要求：</h4>
            <ul>
              <li>文件大小不超过 10MB</li>
              <li>必须包含姓名和电话号码列</li>
              <li>建议使用UTF-8编码</li>
            </ul>
            
            <h4>处理流程：</h4>
            <ol>
              <li>上传文件后系统会自动解析</li>
              <li>与黑名单数据库进行匹配</li>
              <li>生成筛查结果报告</li>
              <li>可下载详细结果</li>
            </ol>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type UploadUserFile } from 'element-plus'
import {
  ArrowLeft,
  Upload,
  UploadFilled,
  Delete,
  InfoFilled
} from '@element-plus/icons-vue'
import { screeningApi } from '@/api/screening'

const router = useRouter()

// 响应式数据
const uploading = ref(false)
const uploadRef = ref()
const fileList = ref<UploadUserFile[]>([])
const selectedFile = ref<File | null>(null)

// 上传前验证
const beforeUpload = (file: File) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel' ||
                  file.type === 'text/csv'
  
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 或 CSV 文件!')
    return false
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  
  return true
}

// 文件变化处理
const handleFileChange = (file: UploadUserFile) => {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

// 开始上传
const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  
  try {
    uploading.value = true
    const response = await screeningApi.uploadFile(selectedFile.value)
    
    ElMessage.success('文件上传成功')
    uploading.value = false
    fileList.value = []
    selectedFile.value = null
    
    // 跳转到筛查结果页面
    if (response.id) {
      router.push(`/screening/${response.id}/results`)
    } else {
      router.push('/screening')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '文件上传失败')
    uploading.value = false
    console.error('Upload error:', error)
  }
}

// 清空文件
const handleClear = () => {
  fileList.value = []
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

// 返回列表
const goBack = () => {
  router.push('/screening')
}
</script>

<style scoped>
.screening-upload {
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

.upload-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.upload-card,
.info-card {
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

.upload-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.info-content {
  line-height: 1.6;
}

.info-content h4 {
  color: #409eff;
  margin: 15px 0 10px 0;
  font-size: 14px;
}

.info-content ul,
.info-content ol {
  margin: 0 0 15px 20px;
  padding: 0;
}

.info-content li {
  margin: 5px 0;
  font-size: 13px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-container {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .upload-actions {
    flex-direction: column;
  }
}
</style>
