<template>
  <div class="not-found">
    <div class="container py-5 text-center">
      <div class="mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" fill="#6c63ff" class="bi bi-question-circle" viewBox="0 0 16 16">
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
          <path d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"/>
        </svg>
      </div>
      
      <h1 class="display-1 fw-bold">404</h1>
      <h2 class="mb-4">页面未找到</h2>
      <p class="lead mb-5">您访问的页面不存在或已被移除</p>
      
      <div class="d-flex justify-content-center">
        <router-link to="/" class="btn btn-primary me-2">
          返回首页
        </router-link>
        <button @click="goBack" class="btn btn-outline-secondary">
          返回上一页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView',
  
  methods: {
    goBack() {
      window.history.length > 1 
        ? this.$router.go(-1) 
        : this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.not-found {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 