<template>
  <div id="forgot-password" class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="card shadow p-4" style="width: 100%; max-width: 400px;">
      <h4 class="mb-4 fw-semibold">Forgot your password?</h4>
      <form @submit.prevent="submitRequest">
        <div class="mb-3">
          <label for="email" class="form-label">Enter your email</label>
          <input
            v-model="email"
            type="email"
            class="form-control"
            id="email"
            placeholder="name@company.com"
            required
            :disabled="loading"
          />

<div class="mt-2 p-2 rounded" style="background-color: #f8f9fa; font-size: 0.88rem;">
  <ul class="mb-0 ps-3 text-muted">
    <li>Enter the email linked to your account.</li>
    <li>Use a valid, accessible email.</li>
    <li>Reset link expires in 5 minutes.</li>
  </ul>
</div>
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading">Sending...</span>
          <span v-else>Send Reset Link</span>
        </button>

        <div v-if="msg" class="mt-3 text-success fw-medium">
          {{ msg }}
        </div>
        <div v-if="error" class="mt-3 text-danger fw-medium">
          {{ error }}
        </div>
      </form>

      <div class="mt-4 text-center">
        <a href="/login" class="text-decoration-none">Back to Login</a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      msg: '',
      error: '',
      loading: false
    };
  },
  methods: {
    async submitRequest() {
      this.msg = '';
      this.error = '';
      this.loading = true;
      const url = `${this.$store.state.backendUrl}/forgot_password`;

      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email })
        });

        const data = await res.json();

        if (res.ok) {
          this.msg = data.msg || "Reset email sent successfully.";
        } else {
          this.error = data.error || "Failed to send reset email.";
        }
      } catch (err) {
        this.error = "Network error while sending reset email.";
      } finally {
        this.loading = false;
        this.email = ''
      }
    }
  }
};
</script>
