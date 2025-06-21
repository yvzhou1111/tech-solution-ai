<template>
  <div class="history-view">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="container">
        <h1>历史记录</h1>
        <p class="lead">查看您之前生成的技术方案</p>
        <router-link to="/" class="btn btn-outline-light">返回首页</router-link>
      </div>
    </header>

    <div class="container py-4">
      <!-- 加载中状态 -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <p class="mt-2">正在加载历史记录...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="alert alert-danger">
        <h4 class="alert-heading">加载失败</h4>
        <p>{{ error }}</p>
        <button class="btn btn-outline-danger" @click="fetchProjects">重试</button>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="projects.length === 0" class="text-center py-5">
        <div class="mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#6c757d" class="bi bi-inbox" viewBox="0 0 16 16">
            <path d="M4.98 4a.5.5 0 0 0-.39.188L1.54 8H6a.5.5 0 0 1 .5.5 1.5 1.5 0 1 0 3 0A.5.5 0 0 1 10 8h4.46l-3.05-3.812A.5.5 0 0 0 11.02 4H4.98zm-1.17-.437A1.5 1.5 0 0 1 4.98 3h6.04a1.5 1.5 0 0 1 1.17.563l3.7 4.625a.5.5 0 0 1 .106.374l-.39 3.124A1.5 1.5 0 0 1 14.117 13H1.883a1.5 1.5 0 0 1-1.489-1.314l-.39-3.124a.5.5 0 0 1 .106-.374l3.7-4.625z"/>
          </svg>
        </div>
        <h3>暂无历史记录</h3>
        <p class="text-muted mb-4">您还没有生成过技术方案</p>
        <router-link to="/" class="btn btn-primary">创建第一个技术方案</router-link>
      </div>
      
      <!-- 项目列表 -->
      <div v-else>
        <div class="mb-4 d-flex justify-content-between align-items-center">
          <h2>历史技术方案</h2>
          <div>
            <div class="input-group">
              <input
                type="number"
                class="form-control"
                placeholder="显示数量"
                v-model.number="limit"
                min="1"
                max="50"
              >
              <button class="btn btn-outline-secondary" type="button" @click="fetchProjects">
                刷新
              </button>
            </div>
          </div>
        </div>
        
        <div class="row">
          <div v-for="project in projects" :key="project.id" class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
              <div class="card-body">
                <h5 class="card-title">{{ project.title }}</h5>
                <p class="card-text text-truncate">{{ project.topic }}</p>
                <div class="mb-3">
                  <span v-if="project.status === 'pending'" class="badge bg-secondary">等待处理</span>
                  <span v-else-if="project.status === 'processing'" class="badge bg-warning text-dark">处理中</span>
                  <span v-else-if="project.status === 'completed'" class="badge bg-success">已完成</span>
                  <span v-else-if="project.status === 'failed'" class="badge bg-danger">失败</span>
                  <small class="text-muted ms-2">{{ formatDate(project.created_at) }}</small>
                </div>
              </div>
              <div class="card-footer bg-transparent border-top-0">
                <router-link :to="`/project/${project.id}`" class="btn btn-primary">
                  查看详情
                </router-link>
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

export default {
  name: 'HistoryView',
  
  data() {
    return {
      projects: [],
      isLoading: false,
      error: null,
      limit: 20
    }
  },
  
  async created() {
    await this.fetchProjects()
  },
  
  methods: {
    async fetchProjects() {
      try {
        this.isLoading = true
        this.error = null
        
        const response = await api.projects.list(this.limit)
        this.projects = response.data || []
      } catch (error) {
        console.error('获取项目列表失败', error)
        this.error = error.response?.data?.detail || '加载历史记录失败，请重试'
      } finally {
        this.isLoading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN')
      } catch (e) {
        return dateString
      }
    }
  },
  
  watch: {
    limit(newLimit) {
      // 如果限制大小变化，重新加载项目列表
      if (newLimit > 0 && newLimit <= 50) {
        this.fetchProjects()
      }
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
</style> 