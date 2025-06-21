import axios from 'axios'

// 创建API客户端
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '/api',
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 在这里可以添加认证令牌等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// API服务对象
export default {
  // 项目相关API
  projects: {
    // 创建新项目
    create(projectData) {
      return apiClient.post('/projects', projectData)
    },
    
    // 获取项目详情
    get(id) {
      return apiClient.get(`/projects/${id}`)
    },
    
    // 获取项目列表
    list(limit = 10) {
      return apiClient.get('/projects', { params: { limit } })
    }
  },
  
  // 文件上传API
  upload: {
    // 上传文件
    file(file, projectId = null) {
      const formData = new FormData()
      formData.append('file', file)
      
      if (projectId) {
        formData.append('project_id', projectId)
      }
      
      return apiClient.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
  },
  
  // URL分析API
  url: {
    // 分析URL内容
    analyze(url) {
      const formData = new FormData()
      formData.append('url', url)
      
      return apiClient.post('/analyze-url', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
  },
  
  // 健康检查
  health() {
    return apiClient.get('/health')
  }
} 