<template>
  <div class="profile-page">
    <!-- Top header -->
    <section class="profile-header">
      <h2 class="profile-title">My Profile</h2>
      <p class="profile-subtitle">
        View and update your account details. Changes apply to both dashboard and bookings.
      </p>
    </section>

    <div class="profile-layout">
      <!-- LEFT: Overview -->
      <section class="profile-left card-soft">
        <div class="profile-left-inner">
          <div class="avatar-wrapper">
            <div class="avatar-circle">
              {{ avatarInitial }}
            </div>
          </div>

          <div class="text-center">
            <div class="display-name">
              {{ profile.username || 'Unnamed User' }}
            </div>
            <div class="email-text">
              {{ profile.email }}
            </div>
            <div class="role-pill">
              {{ (profile.role || 'USER').toUpperCase() }}
            </div>
          </div>

          <div class="divider"></div>

          <p class="hint-text">
            This account is used for logging in and managing your parking activity.
          </p>
        </div>
      </section>

      <!-- Forms -->
      <section class="profile-right">
        <!-- Account details -->
        <div class="card-soft section-card">
          <div class="section-header">
            <div>
              <h5 class="section-title">Account Details</h5>
              <p class="section-subtitle">Basic information about your account.</p>
            </div>
          </div>

          <div class="section-body">
            <form @submit.prevent="saveProfile" class="form-stack">
              <div class="field-group">
                <label class="form-label">Email (login ID)</label>
                <input
                  v-model="profile.email"
                  type="email"
                  class="form-control soft-input"
                  readonly
                />
              </div>

              <div class="field-group">
                <label class="form-label">Display Name</label>
                <input
                  v-model="profile.username"
                  type="text"
                  class="form-control soft-input"
                  placeholder="What should we call you?"
                  required
                />
                <div class="helper-text">
                  This is shown on dashboards instead of your email.
                </div>
              </div>

              <div class="actions-row">
                <button
                  type="button"
                  class="btn btn-outline-light rounded-pill px-3"
                  @click="resetProfile"
                >
                  Reset
                </button>
                <button
                  type="submit"
                  class="btn btn-primary rounded-pill px-4"
                  :disabled="savingProfile"
                >
                  {{ savingProfile ? 'Saving…' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Security -->
        <div class="card-soft section-card">
          <div class="section-header">
            <div>
              <h5 class="section-title">Security</h5>
              <p class="section-subtitle">Change your password to keep your account safe.</p>
            </div>
          </div>

          <div class="section-body">
            <form @submit.prevent="changePassword" class="form-stack">
              <div class="field-row">
                <div class="field-group">
                  <label class="form-label">Current Password</label>
                  <input
                    v-model="passwordForm.current_password"
                    type="password"
                    class="form-control soft-input"
                    autocomplete="current-password"
                    required
                  />
                </div>
                <div class="field-group">
                  <label class="form-label">New Password</label>
                  <input
                    v-model="passwordForm.new_password"
                    type="password"
                    class="form-control soft-input"
                    autocomplete="new-password"
                    required
                  />
                </div>
                <div class="field-group">
                  <label class="form-label">Confirm New Password</label>
                  <input
                    v-model="passwordForm.confirm_password"
                    type="password"
                    class="form-control soft-input"
                    autocomplete="new-password"
                    required
                  />
                </div>
              </div>

              <div class="helper-text mb-2">
                Choose a strong password you don’t use elsewhere.
              </div>

              <div class="actions-row">
                <button
                  type="button"
                  class="btn btn-outline-light rounded-pill px-3"
                  @click="resetPasswordForm"
                >
                  Clear
                </button>
                <button
                  type="submit"
                  class="btn btn-success rounded-pill px-4"
                  :disabled="changingPassword"
                >
                  {{ changingPassword ? 'Updating…' : 'Update Password' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const API_BASE = 'http://127.0.0.1:5000/api';

const profile = ref({
  email: '',
  username: '',
  role: ''
});

const originalProfile = ref(null);

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
});

const savingProfile = ref(false);
const changingPassword = ref(false);

const avatarInitial = computed(() =>
  profile.value.email ? profile.value.email.charAt(0).toUpperCase() : '?'
);

const loadProfile = async () => {
  const email = localStorage.getItem('user_email');
  if (!email) {
    alert('Not logged in. Please login again.');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.message || 'Failed to load profile');
      return;
    }

    profile.value = {
      email: data.email,
      username: data.username,
      role: data.role
    };
    originalProfile.value = { ...profile.value };
  } catch (err) {
    console.error(err);
    alert('Error loading profile');
  }
};

const resetProfile = () => {
  if (originalProfile.value) {
    profile.value = { ...originalProfile.value };
  }
};

const saveProfile = async () => {
  savingProfile.value = true;
  try {
    const res = await fetch(`${API_BASE}/profile/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: profile.value.email,
        username: profile.value.username
      })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.message || 'Failed to update profile');
      return;
    }

    localStorage.setItem('username', profile.value.username || '');
    originalProfile.value = { ...profile.value };
    alert('Profile updated successfully.');
  } catch (err) {
    console.error(err);
    alert('Error updating profile');
  } finally {
    savingProfile.value = false;
  }
};

const resetPasswordForm = () => {
  passwordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  };
};

const changePassword = async () => {
  if (
    passwordForm.value.new_password !== passwordForm.value.confirm_password
  ) {
    alert('New password and confirmation do not match.');
    return;
  }

  changingPassword.value = true;
  try {
    const res = await fetch(`${API_BASE}/profile/change-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: profile.value.email,
        current_password: passwordForm.value.current_password,
        new_password: passwordForm.value.new_password
      })
    });
    const data = await res.json();
    if (!res.ok) {
      alert(data.message || 'Failed to change password');
      return;
    }

    alert('Password updated successfully.');
    resetPasswordForm();
  } catch (err) {
    console.error(err);
    alert('Error updating password');
  } finally {
    changingPassword.value = false;
  }
};

onMounted(loadProfile);
</script>

<style scoped>
.profile-page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1.8rem 1.25rem 2.5rem;
  animation: pageFadeUp 0.5s ease-out;
}

/* Header */
.profile-header {
  margin-bottom: 1.5rem;
}

.profile-title {
  font-weight: 600;
  letter-spacing: 0.02em;
  margin-bottom: 0.25rem;
}

.profile-subtitle {
  font-size: 0.9rem;
  color: #9ca3af;
}

/* Layout */
.profile-layout {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.6fr);
  gap: 1.5rem;
}

@media (max-width: 992px) {
  .profile-layout {
    grid-template-columns: minmax(0, 1fr);
  }
}

/* Soft cards */
.card-soft {
  border-radius: 24px;
  background: radial-gradient(circle at 0% 0%, #111827, #020617);
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.85);
  padding: 1.4rem 1.5rem;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.card-soft:hover {
  transform: translateY(-3px);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.95);
  border-color: rgba(96, 165, 250, 0.45);
}

/* LEFT PANEL */
.profile-left-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;   /* center vertically */
  gap: 0.6rem;
  min-height: 280px;
  text-align: center;
}

.avatar-wrapper {
  margin-bottom: 0.5rem;
}

.avatar-circle {
  width: 86px;
  height: 86px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 30% 20%, #22c55e, #0ea5e9);
  color: #ecfeff;
  font-size: 2.3rem;
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(8, 47, 73, 0.9);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.avatar-circle:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 18px 40px rgba(8, 47, 73, 1);
}

.display-name {
  font-size: 1.15rem;
  font-weight: 600;
}

.email-text {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-top: 0.15rem;
}

.role-pill {
  margin-top: 0.4rem;
  padding: 0.25rem 1.1rem;
  border-radius: 999px;
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  background: rgba(37, 99, 235, 0.18);
  border: 1px solid rgba(59, 130, 246, 0.7);
  color: #e5e7eb;
}

.divider {
  width: 100%;
  height: 1px;
  margin: 0.9rem 0 0.7rem;
  background: linear-gradient(
    to right,
    transparent,
    rgba(75, 85, 99, 0.8),
    transparent
  );
}

.hint-text {
  font-size: 0.8rem;
  color: #9ca3af;
}

/* RIGHT PANEL */
.profile-right {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.section-card {
  padding: 1.2rem 1.4rem 1.3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.1rem;
}

.section-subtitle {
  font-size: 0.8rem;
  color: #9ca3af;
}

.section-body {
  margin-top: 0.3rem;
}

/* Form layout */
.form-stack {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
}

@media (max-width: 992px) {
  .field-row {
    grid-template-columns: minmax(0, 1fr);
  }
}

/* Inputs */
.soft-input {
  background-color: #020617;
  border-radius: 14px;
  border: 1px solid rgba(55, 65, 81, 0.95);
  color: #e5e7eb;
  padding: 0.5rem 0.8rem;
  font-size: 0.9rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
}

.soft-input:focus {
  background-color: #020617;
  border-color: #2563eb;
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.55);
}

/* Helpers & actions */
.helper-text {
  font-size: 0.78rem;
  color: #9ca3af;
}

.actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

/* BUTTONS */
.btn-primary {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  border: none;
  color: #e5e7eb;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.45);
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(30, 64, 175, 0.65);
}

.btn-outline-light {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.8);
  color: #e5e7eb;
  background: transparent;
  transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease;
}

.btn-outline-light:hover {
  background: rgba(31, 41, 55, 0.9);
  border-color: rgba(209, 213, 219, 0.9);
  transform: translateY(-1px);
}

.btn-success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  border: none;
  color: #022c22;
  box-shadow: 0 10px 20px rgba(34, 197, 94, 0.4);
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.btn-success:hover {
  background: linear-gradient(135deg, #16a34a, #15803d);
  transform: translateY(-1px);
  box-shadow: 0 14px 26px rgba(22, 163, 74, 0.7);
}

/* Page animation */
@keyframes pageFadeUp {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
