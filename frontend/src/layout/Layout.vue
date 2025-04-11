<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo-container">
        <span class="logo-text">数智IT客服</span>
      </div>
      <el-menu
        :router="true"
        :default-active="$route.path"
        class="el-menu-vertical"
      >
        <el-menu-item index="/">
          <el-icon><DataLine /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/work-orders">
          <el-icon><Document /></el-icon>
          <span>工单管理</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><PieChart /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-title">数智IT客服派单平台</div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userStore.fullName }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { DataLine, Document, PieChart, ArrowDown, User, Setting } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background-color: #263445;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}

.el-header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdfe6;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
}

.el-menu-vertical {
  height: calc(100% - 60px);
  border-right: none;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #606266;
}
</style> 