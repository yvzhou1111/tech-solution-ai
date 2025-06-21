<template>
  <div class="home">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="container text-center">
        <h1 class="display-4">技术方案生成AI</h1>
        <p class="lead">基于学术论文与AI大模型，自动生成详细的技术方案</p>
      </div>
    </header>

    <!-- 主要内容 -->
    <div class="container">
      <!-- 表单卡片 -->
      <div class="row justify-content-center mb-5">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-body">
              <h2 class="card-title text-center mb-4">创建技术方案</h2>
              
              <form @submit.prevent="submitForm">
                <!-- 标题输入 -->
                <div class="mb-3">
                  <label for="title" class="form-label">项目标题</label>
                  <input
                    type="text"
                    class="form-control"
                    id="title"
                    v-model="formData.title"
                    placeholder="为您的技术方案起一个标题"
                    required
                  >
                </div>
                
                <!-- 主题输入 -->
                <div class="mb-3">
                  <label for="topic" class="form-label">技术主题</label>
                  <textarea
                    class="form-control"
                    id="topic"
                    v-model="formData.topic"
                    placeholder="输入您感兴趣的技术主题，例如：量子计算在金融领域的应用"
                    rows="3"
                    required
                  ></textarea>
                  <div class="form-text">支持中文输入，系统将自动翻译为适合学术搜索的英文关键词</div>
                </div>
                
                <!-- 描述输入(可选) -->
                <div class="mb-3">
                  <label for="description" class="form-label">补充说明（可选）</label>
                  <textarea
                    class="form-control"
                    id="description"
                    v-model="formData.description"
                    placeholder="添加更多关于您需求的细节，有助于生成更精准的技术方案"
                    rows="2"
                  ></textarea>
                </div>
                
                <!-- 高级选项 -->
                <details class="mb-4">
                  <summary class="form-label text-primary">高级选项</summary>
                  
                  <div class="card card-body bg-light mt-2">
                    <!-- 模型选择 -->
                    <div class="mb-3">
                      <label class="form-label">模型类型</label>
                      <div class="form-check">
                        <input class="form-check-input" type="radio" id="modelDefault" value="default" v-model="formData.model_type">
                        <label class="form-check-label" for="modelDefault">
                          豆包思维专业版（默认，最强大）
                        </label>
                      </div>
                      <div class="form-check">
                        <input class="form-check-input" type="radio" id="modelPro" value="pro" v-model="formData.model_type">
                        <label class="form-check-label" for="modelPro">
                          豆包专业版（平衡性能）
                        </label>
                      </div>
                      <div class="form-check">
                        <input class="form-check-input" type="radio" id="modelLite" value="lite" v-model="formData.model_type">
                        <label class="form-check-label" for="modelLite">
                          豆包轻量版（更快响应）
                        </label>
                      </div>
                    </div>
                    
                    <!-- 最大论文数量 -->
                    <div class="mb-3">
                      <label for="maxPapers" class="form-label">最大论文数量</label>
                      <input
                        type="number"
                        class="form-control"
                        id="maxPapers"
                        v-model.number="formData.max_papers"
                        min="1"
                        max="10"
                      >
                      <div class="form-text">系统将搜索和分析的arXiv论文数量（1-10篇）</div>
                    </div>
                    
                    <!-- 自定义关键词 -->
                    <div class="mb-3">
                      <label for="keywords" class="form-label">自定义搜索关键词（可选）</label>
                      <input
                        type="text"
                        class="form-control"
                        id="keywords"
                        v-model="keywordsInput"
                        placeholder="输入关键词，用逗号分隔"
                      >
                      <div class="form-text">填写可以更精准地控制论文搜索方向</div>
                    </div>
                  </div>
                </details>
                
                <!-- 提交按钮 -->
                <div class="d-grid">
                  <button type="submit" class="btn btn-primary btn-lg" :disabled="isSubmitting">
                    <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ isSubmitting ? '正在生成中...' : '生成技术方案' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 功能介绍 -->
      <div class="row mb-5">
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <div class="mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="#6c63ff" class="bi bi-search" viewBox="0 0 16 16">
                  <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                </svg>
              </div>
              <h4>arXiv论文检索</h4>
              <p>自动搜索与技术主题相关的最新研究论文，提供学术支持</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <div class="mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="#6c63ff" class="bi bi-robot" viewBox="0 0 16 16">
                  <path fill-rule="evenodd" d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2V1.866ZM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5Zm-8 5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5ZM3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.58 26.58 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219V8.062Zm4.542-.827a.25.25 0 0 1 .182.135l.842 1.7.754-.785a.25.25 0 0 1 .166-.076 24.85 24.85 0 0 0 1.98-.19.25.25 0 0 1 .068.496 25.29 25.29 0 0 1-1.922.188.25.25 0 0 1-.181-.135l-.842-1.7-.754.785a.25.25 0 0 1-.182.076 24.8 24.8 0 0 0-1.979.19.25.25 0 0 1-.068-.496c.639-.09 1.289-.159 1.978-.19a.25.25 0 0 1 .04 0Z"/>
                </svg>
              </div>
              <h4>AI方案生成</h4>
              <p>基于豆包系列大模型，根据学术资料生成详细可行的技术方案</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-body text-center">
              <div class="mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="#6c63ff" class="bi bi-diagram-3" viewBox="0 0 16 16">
                  <path fill-rule="evenodd" d="M6 3.5A1.5 1.5 0 0 1 7.5 2h1A1.5 1.5 0 0 1 10 3.5v1A1.5 1.5 0 0 1 8.5 6v1H14a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-1 0V8h-5v.5a.5.5 0 0 1-1 0V8h-5v.5a.5.5 0 0 1-1 0v-1A.5.5 0 0 1 2 7h5.5V6A1.5 1.5 0 0 1 6 4.5v-1zM8.5 5a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1zM0 11.5A1.5 1.5 0 0 1 1.5 10h1A1.5 1.5 0 0 1 4 11.5v1A1.5 1.5 0 0 1 2.5 14h-1A1.5 1.5 0 0 1 0 12.5v-1zm1.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1zm4.5.5A1.5 1.5 0 0 1 7.5 10h1a1.5 1.5 0 0 1 1.5 1.5v1A1.5 1.5 0 0 1 8.5 14h-1A1.5 1.5 0 0 1 6 12.5v-1zm1.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1zm4.5.5a1.5 1.5 0 0 1 1.5-1.5h1a1.5 1.5 0 0 1 1.5 1.5v1a1.5 1.5 0 0 1-1.5 1.5h-1a1.5 1.5 0 0 1-1.5-1.5v-1zm1.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1z"/>
                </svg>
              </div>
              <h4>流程图可视化</h4>
              <p>使用Mermaid自动生成架构图和流程图，让技术方案更直观</p>
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
  name: 'HomeView',
  
  data() {
    return {
      // 表单数据
      formData: {
        title: '',
        topic: '',
        description: '',
        model_type: 'default',
        max_papers: 5,
        custom_keywords: []
      },
      
      // 关键词输入
      keywordsInput: '',
      
      // 提交状态
      isSubmitting: false,
      
      // 错误信息
      errorMessage: ''
    }
  },
  
  watch: {
    // 监听关键词输入变化
    keywordsInput(val) {
      if (val) {
        this.formData.custom_keywords = val.split(',').map(k => k.trim()).filter(k => k)
      } else {
        this.formData.custom_keywords = []
      }
    }
  },
  
  methods: {
    // 提交表单
    async submitForm() {
      try {
        this.isSubmitting = true
        this.errorMessage = ''
        
        // 调用API创建项目
        const response = await api.projects.create(this.formData)
        
        // 跳转到项目详情页
        this.$router.push({ name: 'project', params: { id: response.data.project_id } })
      } catch (error) {
        console.error('提交表单时出错', error)
        this.errorMessage = error.response?.data?.detail || '创建项目时出错，请重试'
        alert(this.errorMessage)
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100%;
}

/* 自定义样式 */
summary {
  cursor: pointer;
  font-weight: bold;
}

summary:focus {
  outline: none;
}
</style> 