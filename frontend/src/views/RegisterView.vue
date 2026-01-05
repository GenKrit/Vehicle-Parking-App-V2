<template>
  <div class="auth-wrapper">
    <!-- Background shapes -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>

    <div class="auth-card shadow-lg">
      
      <!-- Left Side: Sign Up Form -->
      <div class="auth-form-panel">
        <div class="form-header text-center">
          <h2 class="form-title">Create Account</h2>
          <p class="text-muted">Start booking your spots today</p>
        </div>

        <form @submit.prevent="register" class="login-form">
          
          <!-- Full Name -->
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <div class="input-wrapper">
              <input
                v-model="username"
                type="text"
                class="form-control custom-input"
                placeholder="Your Name"
                required
              />
              <span class="input-icon">👤</span>
            </div>
          </div>

          <!-- Email -->
          <div class="mb-3">
            <label class="form-label">Email Address</label>
            <div class="input-wrapper">
              <input
                v-model="email"
                type="email"
                class="form-control custom-input"
                placeholder="name@company.com"
                required
              />
              <span class="input-icon">✉</span>
            </div>
          </div>

          <!-- Password -->
          <div class="mb-3">
            <label class="form-label">Password</label>
            <div class="input-wrapper">
              <input
                v-model="password"
                type="password"
                class="form-control custom-input"
                placeholder="Choose a strong password"
                required
              />
              <span class="input-icon">🔒</span>
            </div>
          </div>

          <!-- Optional Field -->
          <div class="row g-2 mb-4">
            <div class="col-8">
              <label class="form-label">Address <span class="text-muted small">(Optional)</span></label>
              <div class="input-wrapper">
                <input
                  v-model="address"
                  type="text"
                  class="form-control custom-input"
                  placeholder="City, Street..."
                />
                <span class="input-icon">🏠</span>
              </div>
            </div>
            <div class="col-4">
              <label class="form-label">Pin Code</label>
              <div class="input-wrapper">
                <input
                  v-model="pinCode"
                  type="text"
                  class="form-control custom-input"
                  placeholder="000000"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            class="btn btn-primary w-100 btn-lg auth-btn"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <span v-if="loading">Creating Account...</span>
            <span v-else>Register</span>
          </button>

          <!-- Success/Error Message -->
          <div 
            v-if="message" 
            class="alert mt-3 custom-alert text-center"
            :class="messageClass === 'text-success' ? 'alert-success-custom' : 'alert-danger-custom'"
          >
            {{ message }}
          </div>

          <div class="mt-4 text-center">
            <span class="text-muted">Already registered?</span>
            <router-link to="/login" class="auth-link ms-2">
              Login here
            </router-link>
          </div>
        </form>
      </div>

      <!-- Right Side: Information Panel -->
      <div class="auth-side-panel d-none d-md-flex">
        <div class="panel-content">
          <h1 class="app-title mb-3">Join Us Today</h1>
          <p class="panel-description mb-4">
            Create a user account to unlock full access to the Vehicle Parking System.
          </p>
          
          <div class="features-list">
            <div class="feature-item">
              <div class="feature-icon">📅</div>
              <div class="feature-text">
                <strong>Pre-booking</strong>
                <span>Reserve spots before you arrive</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📜</div>
              <div class="feature-text">
                <strong>History Tracking</strong>
                <span>View all your past parking logs</span>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">💸</div>
              <div class="feature-text">
                <strong>Easy Exports</strong>
                <span>Download records for reimbursement</span>
              </div>
            </div>
          </div>

          <div class="mt-5 pt-3 border-top border-secondary border-opacity-25 text-center">
            <small class="text-white-50 fst-italic">
              Note: Admin accounts are pre-configured by the system.
            </small>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // Import router
import { apiFetch } from '../api';

const email = ref('');
const password = ref('');
const username = ref('');
const address = ref('');
const pinCode = ref('');

const message = ref('');
const messageClass = ref('');
const loading = ref(false);

const router = useRouter(); // Initialize router

const register = async () => {
  message.value = '';
  loading.value = true;

  try {
    const response = await apiFetch('/register', {
      method: 'POST',
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        username: username.value,
        address: address.value,
        pinCode: pinCode.value
      }),
    });

    const data = await response.json();

    if (response.ok) {
      message.value = 'Registration successful! Redirecting to login...';
      messageClass.value = 'text-success';
      
      // Clear sensitive fields
      password.value = '';

      // wait and redirect
      setTimeout(() => {
        router.push('/login');
      }, 1500); // 1.5 sec

    } else {
      message.value = data.message || 'Registration failed.';
      messageClass.value = 'text-danger';
    }
  } catch (err) {
    message.value = 'Error connecting to server.';
    messageClass.value = 'text-danger';
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
  
  overflow: hidden;
  
  background-color: #0f172a;
  background-image: 
    radial-gradient(at 100% 100%, hsla(253,16%,7%,1) 0, transparent 50%), 
    radial-gradient(at 0% 0%, hsla(225,39%,30%,1) 0, transparent 50%);
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.4;
}
.shape-1 { width: 400px; height: 400px; background: #ea580c; top: -50px; right: -50px; } /* Orange on right top */
.shape-2 { width: 300px; height: 300px; background: #3b82f6; bottom: -50px; left: -50px; }

/* --- Main Card --- */
.auth-card {
  display: flex;
  flex-direction: column; 
  width: 90%;
  max-width: 1000px;
  max-height: 90vh; /* Contain height */
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  overflow: hidden; /* Prevent content spill */
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  z-index: 1;
}

/* Desktop: Side-by-Side */
@media (min-width: 768px) {
  .auth-card {
    flex-direction: row; 
  }
  
  /* Form on Left */
  .auth-form-panel {
    width: 50%;
  }

  /* Info on Right */
  .auth-side-panel {
    width: 50%;
    border-left: 1px solid rgba(255, 255, 255, 0.1); /* Left border for separation */
  }
}

/* --- Panels --- */
.auth-form-panel {
  padding: 3rem;
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.auth-side-panel {
  background: rgba(15, 23, 42, 0.6);
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.panel-content {
  max-width: 400px;
  margin: 0 auto;
}

/* --- Typography & Elements --- */
.app-title {
  font-family: system-ui, sans-serif;
  font-weight: 800;
  font-size: 2.2rem;
  background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.panel-description {
  color: #94a3b8;
  font-size: 1.1rem;
  line-height: 1.6;
}

.form-title {
  color: #fff;
  font-weight: 700;
  font-size: 1.75rem;
}

/* --- Features List --- */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1.5rem;
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

.feature-text strong { font-size: 1rem; color: #fff; }
.feature-text span { font-size: 0.85rem; color: #94a3b8; }

/* --- Inputs --- */
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
  margin-bottom: 0.4rem;
  display: block;
}

/* --- Buttons & Links --- */
.auth-btn {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border: none;
  padding: 0.9rem;
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.3);
  margin-top: 0.5rem;
}

.auth-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.4);
}

.auth-link {
  color: #f97316;
  text-decoration: none;
  font-weight: 500;
}
.auth-link:hover {
  color: #fbbf24;
  text-decoration: underline;
}

/* --- Alerts --- */
.custom-alert {
  border-radius: 8px;
  font-size: 0.9rem;
  border: 1px solid;
}
.alert-danger-custom {
  background: rgba(220, 38, 38, 0.1);
  border-color: rgba(220, 38, 38, 0.2);
  color: #fca5a5;
}
.alert-success-custom {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

/* Mobile Tweaks */
@media (max-width: 767.98px) {
  .auth-form-panel {
    padding: 2rem 1.5rem;
  }
}
</style>