import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import UserDashboard from '../views/UserDashboard.vue';
import ProfileView from '../views/ProfileView.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/admin-dashboard',
      name: 'admin-dashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, requiresRole: 'admin' },
    },

    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true } // both user & admin
    },


    {
      path: '/dashboard',
      name: 'user-dashboard',
      component: UserDashboard,
      meta: { requiresAuth: true, requiresRole: 'user' },
    },
  ],
});

// Global navigation protection
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiredRole = to.meta.requiresRole;
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (requiresAuth && !token) {
    // Needs auth but not logged in
    next('/login');
  } else if (requiresAuth && token && requiredRole && role !== requiredRole) {
    // Logged in but wrong role
    if (role === 'admin') {
      next('/admin-dashboard');
    } else {
      next('/dashboard');
    }
  } else if (token && to.path === '/login') {
    // Already logged in, don't show login
    if (role === 'admin') {
      next('/admin-dashboard');
    } else {
      next('/dashboard');
    }
  } else {
    next();
  }
});

export default router;
