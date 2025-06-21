const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  
  // 输出目录配置
  outputDir: 'dist',
  assetsDir: 'static',
  
  // 生产环境配置
  productionSourceMap: false
}) 