<template>
  <div class="auth-wrapper">
    <!-- Background shapes -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>

    <div class="auth-card shadow-lg">
      <!-- Left Side: Information Panel -->
      <div class="auth-side-panel d-none d-md-flex">
        <div class="panel-content">
          
          <h1 class="app-title mb-3"> PAVE Parking</h1>
          <h3 class="panel-description mb-4">Vehicle Parking Management System</h3>
          <p class="panel-description mb-4">
            Experience the next generation of parking management. <br />
            Seamless, secure, and smart.
          </p>
          
          <div class="features-list">
            <div class="feature-item">
              <div class="feature-icon">🅿️</div>
              <div class="feature-text">
                <strong>Real-time Availability</strong>
                <span>Check spots instantly</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🛡️</div>
              <div class="feature-text">
                <strong>Secure Access</strong>
                <span>Encrypted user data</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <div class="feature-text">
                <strong>Smart Reporting</strong>
                <span>Automated history export</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side: Login Form -->
      <div class="auth-form-panel">
        <div class="form-header text-center">
          <h2 class="form-title">Welcome Back</h2>
          <p class="text-muted">Please enter your details</p>
        </div>

        <form @submit.prevent="login" class="login-form">
          <div class="mb-4">
            <label class="form-label">Email Address</label>
            <div class="input-wrapper">
              <input
                v-model="email"
                type="email"
                class="form-control custom-input"
                placeholder="name@company.com"
                required
              />
              <span class="input-icon">✉️</span>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label">Password</label>
            <div class="input-wrapper">
              <input
                v-model="password"
                type="password"
                class="form-control custom-input"
                placeholder="••••••••"
                required
              />
              <span class="input-icon">🔒</span>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center mb-4 text-sm">
            <small class="text-white-50">Admin login available</small>
            <!-- To be added later:-  <a href="#" class="forgot-link">Forgot password?</a> -->
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100 btn-lg auth-btn"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <span v-if="loading">Verifying...</span>
            <span v-else>Login</span>
          </button>

          <div class="alert alert-danger mt-3 custom-alert" v-if="error">
            {{ error }}
          </div>

          <div class="mt-4 text-center">
            <span class="text-muted">Don't have an account?</span>
            <router-link to="/register" class="auth-link ms-2">
              Sign up
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { apiFetch } from '../api';

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const router = useRouter();

const login = async () => {
  error.value = '';
  loading.value = true;

  try {
    const response = await apiFetch('/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.value, password: password.value }),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('user_email', data.email);
      
      if (data.role === 'admin') {
        router.push('/admin-dashboard');
      } else {
        router.push('/dashboard');
      }
    } else {
      error.value = data.message || 'Invalid credentials';
    }
  } catch (err) {
    console.error(err);
    error.value = 'Service unavailable. Is the backend running?';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* --- Layout Container --- */
.auth-wrapper {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 9999; 
  
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* Disable scrollbars */
  overflow: hidden; 
  
  background-color: #0f172a;
  background-image: 
    radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.4;
}
.shape-1 { width: 400px; height: 400px; background: #f97316; top: -100px; left: -100px; }
.shape-2 { width: 300px; height: 300px; background: #3b82f6; bottom: -50px; right: -50px; }

/* --- Main Card Layout --- */
.auth-card {
  display: flex;
  flex-direction: column; 
  width: 90%; /* Responsive width */
  max-width: 1000px;
  max-height: 90vh; 
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  overflow: hidden; 
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  z-index: 1;
}

/* Desktop: Force Side-by-Side */
@media (min-width: 768px) {
  .auth-card {
    flex-direction: row; 
  }
  
  .auth-side-panel {
    width: 50%;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: none;
  }
  
  .auth-form-panel {
    width: 50%;
  }
}

/* --- Left Side Panel --- */
.auth-side-panel {
  background: rgba(15, 23, 42, 0.6);
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.panel-content {
  max-width: 400px;
  margin: 0 auto;
}

.app-title {
  font-family: system-ui, sans-serif;
  font-weight: 800;
  font-size: 2.5rem;
  background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  
}

.panel-description {
  color: #94a3b8;
  font-size: 1.1rem;
  line-height: 1.6;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #e2e8f0;
}

.feature-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.feature-text {
  display: flex;
  flex-direction: column;
}

.feature-text strong {
  font-size: 1rem;
  color: #fff;
}

.feature-text span {
  font-size: 0.85rem;
  color: #94a3b8;
}

/* --- Right Form Panel --- */
.auth-form-panel {
  padding: 3rem;
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  margin-bottom: 2rem;
}

.form-title {
  color: #fff;
  font-weight: 700;
  font-size: 1.75rem;
}
.custom-input {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #fff;
  padding: 0.8rem 1rem 0.8rem 2.8rem;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.custom-input:focus {
  background: rgba(15, 23, 42, 0.9);
  border-color: #f97316;
  box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.1);
}

.input-wrapper { position: relative; }
.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.form-label {
  color: #cbd5e1;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  display: block;
}

.forgot-link, .auth-link {
  color: #f97316;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.forgot-link:hover, .auth-link:hover {
  color: #fbbf24;
  text-decoration: underline;
}

.auth-btn {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  padding: 0.9rem;
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.3);
  margin-top: 1rem;
}

.auth-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4);
}

.custom-alert {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.2);
  color: #fca5a5;
  border-radius: 8px;
  font-size: 0.9rem;
}

/* Responsive Tweaks */
@media (max-width: 767.98px) {
  .auth-form-panel {
    padding: 2rem 1.5rem;
  }
}
</style>