<template>
  <div class="project-view">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
      <p class="mt-2">正在加载项目数据...</p>
    </div>
    
    <!-- 加载错误 -->
    <div v-else-if="error" class="container py-5">
      <div class="alert alert-danger">
        <h4 class="alert-heading">加载失败</h4>
        <p>{{ error }}</p>
        <hr>
        <router-link to="/" class="btn btn-outline-danger">返回首页</router-link>
      </div>
    </div>
    
    <!-- 项目内容 -->
    <div v-else-if="project">
      <!-- 页面头部 -->
      <header class="page-header">
        <div class="container">
          <h1>{{ project.title }}</h1>
          <p class="lead">
            状态: 
            <span v-if="project.status === 'pending'" class="badge bg-secondary">等待处理</span>
            <span v-else-if="project.status === 'processing'" class="badge bg-warning text-dark">处理中</span>
            <span v-else-if="project.status === 'completed'" class="badge bg-success">已完成</span>
            <span v-else-if="project.status === 'failed'" class="badge bg-danger">失败</span>
            <span v-else class="badge bg-secondary">{{ project.status }}</span>
          </p>
          <div class="mt-3">
            <router-link to="/" class="btn btn-outline-light">返回首页</router-link>
            <router-link to="/history" class="btn btn-outline-light ms-2">历史记录</router-link>
          </div>
        </div>
      </header>
      
      <div class="container py-4">
        <!-- 项目信息卡片 -->
        <div class="card mb-4">
          <div class="card-header">
            <h3>项目信息</h3>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>主题:</strong> {{ project.topic }}</p>
                <p v-if="project.description"><strong>补充说明:</strong> {{ project.description }}</p>
                <p><strong>创建时间:</strong> {{ formatDate(project.created_at) }}</p>
              </div>
              <div class="col-md-6">
                <p v-if="project.result && project.result.translated_topic">
                  <strong>英文搜索关键词:</strong> {{ project.result.translated_topic }}
                </p>
                <p v-if="project.status_message">
                  <strong>状态信息:</strong> {{ project.status_message }}
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 处理中状态 -->
        <div v-if="project.status === 'processing'" class="card mb-4">
          <div class="card-body text-center">
            <h3 class="mb-3">正在生成技术方案...</h3>
            <div class="progress mb-3">
              <div 
                class="progress-bar progress-bar-striped progress-bar-animated" 
                role="progressbar" 
                :style="{width: processingProgress + '%'}"
              ></div>
            </div>
            <p>{{ project.status_message || '系统正在处理您的请求，请稍候...' }}</p>
            <small class="text-muted">生成技术方案通常需要1-3分钟，取决于论文数量和内容复杂度</small>
          </div>
        </div>
        
        <!-- 失败状态 -->
        <div v-if="project.status === 'failed'" class="alert alert-danger">
          <h4>处理失败</h4>
          <p>{{ project.error || '技术方案生成过程中出现错误，请重试或联系管理员。' }}</p>
        </div>
        
        <!-- 技术方案内容 (仅在完成状态下显示) -->
        <div v-if="project.status === 'completed' && project.result" class="mb-4">
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h3 class="mb-0">技术方案</h3>
              <button class="btn btn-sm btn-outline-secondary" @click="printProposal">
                <i class="bi bi-printer"></i> 打印/导出
              </button>
            </div>
            <div class="card-body">
              <!-- Markdown渲染 -->
              <div class="markdown-body" ref="markdownContent" v-html="renderedMarkdown"></div>
            </div>
          </div>
          
          <!-- 参考资料 -->
          <div v-if="project.result.references && project.result.references.length > 0" class="card">
            <div class="card-header">
              <h3>参考资料</h3>
            </div>
            <div class="card-body">
              <div v-for="(paper, index) in project.result.references" :key="paper.id" class="mb-4 border-bottom pb-3">
                <h5>{{ index + 1 }}. {{ paper.title }}</h5>
                <p><strong>作者:</strong> {{ paper.authors.join(', ') }}</p>
                <p><strong>摘要:</strong> {{ truncateText(paper.summary, 200) }}</p>
                <p><strong>发布日期:</strong> {{ formatDate(paper.published) }}</p>
                <div>
                  <a :href="`/api/papers/${paper.id}/pdf`" class="btn btn-sm btn-primary" target="_blank">
                    下载PDF
                  </a>
                  <a :href="paper.pdf_url" class="btn btn-sm btn-outline-secondary ms-1" target="_blank">
                    访问原始链接
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { marked } from 'marked'
import mermaid from 'mermaid'

export default {
  name: 'ProjectView',
  
  data() {
    return {
      project: null,
      isLoading: true,
      error: null,
      renderedMarkdown: '',
      processingProgress: 20,
      pollTimer: null
    }
  },
  
  async created() {
    await this.fetchProject()
    
    // 如果项目状态是处理中，开始轮询更新
    if (this.project && this.project.status === 'processing') {
      this.startPolling()
    }
  },
  
  methods: {
    // 获取项目数据
    async fetchProject() {
      try {
        this.isLoading = true
        this.error = null
        
        const response = await api.projects.get(this.$route.params.id)
        this.project = response.data
        
        // 如果有技术方案，渲染Markdown
        if (this.project.result && this.project.result.technical_proposal) {
          this.renderMarkdown()
        }
      } catch (error) {
        console.error('获取项目详情失败', error)
        this.error = error.response?.data?.detail || '获取项目信息失败，请重试'
      } finally {
        this.isLoading = false
      }
    },
    
    // 渲染Markdown内容
    renderMarkdown() {
      if (this.project.result && this.project.result.technical_proposal) {
        this.renderedMarkdown = marked(this.project.result.technical_proposal)
        
        // 使用nextTick确保DOM已更新
        this.$nextTick(() => {
          // 初始化Mermaid图表
          try {
            mermaid.init(undefined, document.querySelectorAll('.markdown-body .mermaid'))
          } catch (e) {
            console.error('Mermaid初始化失败', e)
          }
        })
      }
    },
    
    // 开始轮询更新
    startPolling() {
      // 先清除可能存在的定时器
      this.stopPolling()
      
      // 更新进度条
      this.updateProgress()
      
      // 创建新的轮询定时器
      this.pollTimer = setInterval(async () => {
        await this.fetchProject()
        
        // 如果项目状态不再是处理中，停止轮询
        if (this.project && this.project.status !== 'processing') {
          this.stopPolling()
        }
        
        // 更新进度条
        this.updateProgress()
      }, 5000) // 每5秒更新一次
    },
    
    // 停止轮询
    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    },
    
    // 更新进度条
    updateProgress() {
      if (!this.project || this.project.status !== 'processing') return
      
      // 根据状态消息估计进度
      let progress = 20 // 默认进度
      const statusMsg = this.project.status_message || ''
      
      if (statusMsg.includes('翻译主题')) {
        progress = 30
      } else if (statusMsg.includes('搜索相关论文')) {
        progress = 40
      } else if (statusMsg.includes('下载论文')) {
        progress = 50
      } else if (statusMsg.includes('提取论文内容')) {
        progress = 60
      } else if (statusMsg.includes('生成技术方案')) {
        progress = 80
      }
      
      this.processingProgress = progress
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN')
      } catch (e) {
        return dateString
      }
    },
    
    // 截断文本
    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substr(0, maxLength) + '...' : text
    },
    
    // 打印技术方案
    printProposal() {
      window.print()
    }
  },
  
  // 组件销毁时停止轮询
  beforeUnmount() {
    this.stopPolling()
  },
  
  // 监听路由参数变化，重新获取数据
  watch: {
    '$route.params.id': {
      handler: async function(newId) {
        if (newId) {
          await this.fetchProject()
        }
      },
      immediate: true
    }
  }
}
</script>

<style>
/* 打印样式 */
@media print {
  nav, footer, .page-header, .card-header, button {
    display: none !important;
  }
  
  .container {
    width: 100% !important;
    max-width: none !important;
    padding: 0 !important;
  }
  
  .markdown-body {
    padding: 0 !important;
  }
}

/* Markdown样式 */
.markdown-body {
  padding: 1rem;
}

.markdown-body img {
  max-width: 100%;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1rem;
}

.markdown-body table, .markdown-body th, .markdown-body td {
  border: 1px solid #dee2e6;
  padding: 0.5rem;
}

.markdown-body th {
  background-color: #f8f9fa;
}

/* Mermaid图表样式 */
.markdown-body .mermaid {
  margin: 1.5rem 0;
}
</style> 