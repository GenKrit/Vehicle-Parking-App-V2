<template>
  <div class="app-shell">
    <!-- Animated Bg Mesh -->
    <div class="bg-mesh"></div>

    <!-- NAVBAR -->
    <header v-if="showNavbar" class="app-navbar">
      <div class="nav-container">
        <!-- LEFT: Brand -->
        <div class="nav-left" @click="goToDashboard">
          <div class="logo-wrapper">
            <img
              src="https://raw.githubusercontent.com/GenKrit/Content/main/EmailTemplate/Images/Parkinglogo.png"
              alt="Logo"
              class="brand-logo"
              @error="$event.target.style.display='none'" 
            />
            <!-- IMage fallback -->
            <div class="logo-fallback">P</div>
          </div>
          <div class="brand-text">
            <h1 class="brand-title">PAVE <span class="highlight">Parking</span></h1>
            <span class="brand-subtitle">Vehicle Parking System</span>
          </div>
        </div>

        <!-- CENTER: Admin tabs -->
        <nav class="nav-center" v-if="isLoggedIn && role === 'admin'">
          <div class="glass-dock">
            <button
              v-for="tab in ['home', 'users', 'search', 'summary']"
              :key="tab"
              type="button"
              class="dock-item"
              :class="{ active: adminTab === tab }"
              @click="goAdminTab(tab)"
            >
              {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
              <span class="active-dot" v-if="adminTab === tab"></span>
            </button>
          </div>
        </nav>

        <!-- CENTER: User tabs (Home & Summary) -->
        <nav class="nav-center" v-if="isLoggedIn && role === 'user'">
          <div class="glass-dock">
            <button
              type="button"
              class="dock-item"
              :class="{ active: adminTab === 'home' }"
              @click="goUserTab('home')"
            >
              Home
              <span class="active-dot" v-if="adminTab === 'home'"></span>
            </button>

            <button
              type="button"
              class="dock-item"
              :class="{ active: adminTab === 'summary' }"
              @click="goUserTab('summary')"
            >
              Summary
              <span class="active-dot" v-if="adminTab === 'summary'"></span>
            </button>
          </div>
        </nav>

        <!-- RIGHT: user controls -->
        <div class="nav-right">
          <!-- Not logged in -->
          <template v-if="!isLoggedIn">
            <router-link class="nav-link" to="/login">Login</router-link>
            <router-link class="btn-primary-glow" to="/register">
              <span>Register</span>
            </router-link>
          </template>

          <!-- Logged in -->
          <template v-else>
            <button class="nav-link dashboard-link" type="button" @click="goToDashboard">
              {{ role === 'admin' ? 'Dashboard' : 'Dashboard' }}
            </button>

            <button
              v-if="isLoggedIn"
              type="button"
              class="user-chip"
              @click="goToProfile">
              <div class="user-avatar">
                {{ userInitial }}
              </div>
              <div class="user-meta">
                <span class="user-email" :title="userEmail">{{ userEmail }}</span>
                <span class="user-badge" :class="role">{{ role || 'user' }}</span>
              </div>
            </button>

            <button class="btn-icon-logout" type="button" @click="logout" title="Logout">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
            </button>
          </template>
        </div>
      </div>
    </header>

    <!-- MAIN CONTENT and Transition -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeMount } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const isLoggedIn = ref(false);
const userEmail = ref('');
const role = ref('');
const adminTab = ref(route.query.tab || 'home');

const goToProfile = () => {
  router.push({ name: 'profile' });
};

const updateAuthState = () => {
  const token = localStorage.getItem('token');
  isLoggedIn.value = !!token;
  userEmail.value = localStorage.getItem('user_email') || '';
  role.value = localStorage.getItem('role') || '';
};

onBeforeMount(() => {
  updateAuthState();
});

// update after every navigation
router.afterEach((to) => {
  updateAuthState();
  adminTab.value = to.query.tab || 'home';
});

// hide navbar 
const showNavbar = computed(() => {
  const path = router.currentRoute.value.path;
  return !(path === '/login' || path === '/register');
});

const userInitial = computed(() => {
  if (!userEmail.value) return '?';
  return userEmail.value.trim().charAt(0).toUpperCase();
});

const goToDashboard = () => {
  if (!isLoggedIn.value) {
    router.push('/login');
    return;
  }
  if (role.value === 'admin') {
    router.push({ name: 'admin-dashboard', query: { tab: adminTab.value || 'home' } });
  } else {
    router.push('/dashboard');
  }
};

const goAdminTab = (tab) => {
  adminTab.value = tab;
  router.push({ name: 'admin-dashboard', query: { tab } });
};

// user tab handler (keeps other functions intact)
const goUserTab = (tab) => {
  adminTab.value = tab; // reuse same state so active styling matches route
  router.push({ name: 'user-dashboard', query: { tab } });
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('user_email');
  updateAuthState();
  router.push('/login');
};
</script>

<style scoped>
/* --- VARIABLES & RESET --- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

.app-shell {
  font-family: 'Plus Jakarta Sans', sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  background-color: #0f172a; /* Fallback */
  color: #e2e8f0;
}

/* --- ANIMATED BACKGROUND --- */
.bg-mesh {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  background: 
    radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
  background-size: 200% 200%;
  animation: bg-shift 15s ease infinite;
  pointer-events: none;
}

@keyframes bg-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* --- NAVBAR --- */
.app-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

/* LEFT: Brand */
.nav-left {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 0.75rem;
  transition: transform 0.2s ease;
}

.nav-left:hover {
  transform: scale(1.02);
}

.logo-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
}

.brand-logo {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  object-fit: cover;
  position: relative;
  z-index: 2;
}

.logo-fallback {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  color: white;
  z-index: 1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  margin: 0;
  font-weight: 700;
  font-size: 1.1rem;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.highlight {
  background: linear-gradient(to right, #818cf8, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* CENTER: (Admin Tabs) */
.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.glass-dock {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.25rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.dock-item {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.4rem 1.2rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.dock-item:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}

.dock-item.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.active-dot {
  width: 4px;
  height: 4px;
  background-color: #38bdf8;
  border-radius: 50%;
  position: absolute;
  bottom: 4px;
  box-shadow: 0 0 8px #38bdf8;
}

/* RIGHT: User Controls */
.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Links */
.nav-link {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s ease;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.nav-link:hover, .dashboard-link:hover {
  color: #fff;
}

/* Register Button */
.btn-primary-glow {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  text-decoration: none;
  padding: 0.5rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4);
  position: relative;
  overflow: hidden;
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6);
}

/* User Chip */
.user-chip {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.25rem 0.25rem 0.25rem 0.75rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  transition: border-color 0.2s ease;
}

.user-chip:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0ea5e9, #3b82f6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.user-meta {
  display: flex;
  flex-direction: column;
  padding-right: 0.75rem;
}

.user-email {
  font-size: 0.8rem;
  font-weight: 500;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #e2e8f0;
}

.user-badge {
  font-size: 0.65rem;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #94a3b8;
}
.user-badge.admin { color: #f43f5e; } /* Rose for admin */

/* Logout Button */
.btn-icon-logout {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon-logout:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg);
}

/* MAIN CONTENT & TRANSITIONS */
.app-main {
  flex: 1;
  position: relative;
  z-index: 10;
  padding-top: 1rem; 
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Transition: Fade & Slide Up */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

/* RESPONSIVE */
@media (max-width: 1024px) {
  .nav-center {
    position: static;
    transform: none;
    order: 3;
    width: 100%;
    margin-top: 1rem;
    display: flex;
    justify-content: center;
  }
  
  .nav-container {
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .brand-text { display: none; }
  .user-email { display: none; }
  .user-chip { padding: 0.25rem; border: none; background: transparent; }
  .user-meta { display: none; }
  .nav-right { gap: 0.5rem; }
  
  .dock-item {
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
  }
}
</style>
