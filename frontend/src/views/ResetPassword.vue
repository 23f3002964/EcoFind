<template>
  <div id="reset-password" class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="card shadow p-4" style="width: 100%; max-width: 400px;">
      <h4 class="mb-4 fw-semibold">Reset Your Password</h4>
      <form @submit.prevent="submitReset">
        <div class="mb-3">
          <label for="password" class="form-label">New Password</label>
          <input
            v-model="password"
            type="password"
            class="form-control"
            id="password"
            placeholder="••••••••"
            required
            :disabled="loading || success"
          />
        </div>

        <div class="mb-3">
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="form-control"
            id="confirmPassword"
            placeholder="••••••••"
            required
            :disabled="loading || success"
          />
        </div>

        <div v-if="validationError" class="mb-2 text-danger small">
          {{ validationError }}
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading || success">
          <span v-if="loading">Resetting...</span>
          <span v-else-if="success">Password Reset</span>
          <span v-else>Reset Password</span>
        </button>

        <div v-if="msg" class="mt-3 text-success fw-medium">
          {{ msg }}
        </div>
        <div v-if="error" class="mt-3 text-danger fw-medium">
          {{ error }}
        </div>

        <!-- Success actions -->
        <div v-if="success" class="mt-4 text-center">
          <p class="text-muted mb-1">
            You can now log in with your new password.
          </p>
          <p class="text-muted small">
            Redirecting to login in {{ countdown }} seconds...
          </p>
          <a href="/login" class="text-decoration-none">Back to Login</a>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      password: '',
      confirmPassword: '',
      token: '',
      msg: '',
      error: '',
      validationError: '',
      loading: false,
      success: false,
      countdown: 10,
      countdownInterval: null
    };
  },
  mounted() {
    this.token = this.$route.params.token;
  },
  methods: {
    async submitReset() {
      this.msg = '';
      this.error = '';
      this.validationError = '';
      this.success = false;

      if (this.password !== this.confirmPassword) {
        this.validationError = "Passwords do not match.";
        return;
      }

      this.loading = true;
      const url = `${this.$store.state.backendUrl}/reset_password`;

      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: this.token,
            password: this.password
          })
        });

        const data = await res.json();
        if (res.ok) {
          this.msg = data.msg || "Password has been reset successfully.";
          this.success = true;
          this.startCountdown();
        } else {
          this.error = data.msg || "Failed to reset password.";
        }
      } catch (err) {
        this.error = "Network error while resetting password.";
      } finally {
        this.loading = false;
      }
    },
    startCountdown() {
      this.countdownInterval = setInterval(() => {
        if (this.countdown > 0) {
          this.countdown--;
        } else {
          clearInterval(this.countdownInterval);
          this.$router.push('/login');
        }
      }, 1000);
    }
  },
  beforeDestroy() {
    if (this.countdownInterval) clearInterval(this.countdownInterval);
  }
};
</script>

