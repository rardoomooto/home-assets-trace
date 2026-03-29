import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { guest: true }
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { auth: true }
    },
    {
      path: '/items',
      name: 'Items',
      component: () => import('@/views/Items.vue'),
      meta: { auth: true }
    },
    {
      path: '/items/new',
      name: 'NewItem',
      component: () => import('@/views/ItemForm.vue'),
      meta: { auth: true }
    },
    {
      path: '/items/:id/edit',
      name: 'EditItem',
      component: () => import('@/views/ItemForm.vue'),
      meta: { auth: true }
    },
    {
      path: '/categories',
      name: 'Categories',
      component: () => import('@/views/Categories.vue'),
      meta: { auth: true }
    },
    {
      path: '/rooms',
      name: 'Rooms',
      component: () => import('@/views/Rooms.vue'),
      meta: { auth: true }
    },
    {
      path: '/families',
      name: 'Families',
      component: () => import('@/views/Families.vue'),
      meta: { auth: true }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.auth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
