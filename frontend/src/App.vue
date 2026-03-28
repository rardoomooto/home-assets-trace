<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <nav v-if="authStore.isAuthenticated" class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <router-link to="/" class="flex items-center text-xl font-bold text-gray-900">
              家庭物品跟踪
            </router-link>
            <div class="hidden sm:flex sm:ml-6 sm:space-x-8">
              <router-link
                to="/items"
                class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                active-class="border-b-2 border-indigo-500"
              >
                物品管理
              </router-link>
              <router-link
                to="/categories"
                class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                active-class="border-b-2 border-indigo-500"
              >
                分类管理
              </router-link>
              <!-- Add Rooms navigation -->
              <router-link
                to="/rooms"
                class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900"
                active-class="border-b-2 border-indigo-500"
              >
                房间管理
              </router-link>
            </div>
          </div>
          <div class="flex items-center">
            <span class="text-sm text-gray-500 mr-4">{{ authStore.user?.username }}</span>
            <button
              @click="handleLogout"
              class="text-sm text-gray-500 hover:text-gray-700"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>
