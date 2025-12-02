<template>
  <div id="email-verification" class="d-flex justify-content-center align-items-center">
    <div class="card" style="width: 100%; max-width: 500px;">
      <div class="card-body p-4">
        <div class="text-center mb-4">
          <h3>Email Verification</h3>
          <p class="text-muted">
            Verifying your email address...
          </p>
        </div>

        <!-- Loading State -->
        <div v-if="verifying" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Please wait while we verify your email address</p>
        </div>

        <!-- Success Message -->
        <div v-else-if="success" class="text-center">
          <div class="text-success mb-3">
            <i class="bi bi-check-circle-fill" style="font-size: 3rem;"></i>
          </div>
          <h4 class="text-success">Email Verified Successfully!</h4>
          <p class="text-muted">
            Your email address has been verified. You can now log in to your account.
          </p>
          <div class="d-grid gap-2 mt-4">
            <router-link to="/login" class="btn btn-primary">
              Continue to Login
            </router-link>
          </div>
        </div>

        <!-- Error Message -->
        <div v-else class="text-center">
          <div class="text-danger mb-3">
            <i class="bi bi-x-circle-fill" style="font-size: 3rem;"></i>
          </div>
          <h4 class="text-danger">Verification Failed</h4>
          <p class="text-muted">
            {{ errorMessage || 'The verification link is invalid or has expired.' }}
          </p>
          <div class="d-grid gap-2 mt-4">
            <router-link to="/signup" class="btn btn-outline-primary">
              Create New Account
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmailVerificationView',
  data() {
    return {
      verifying: true,
      success: false,
      errorMessage: null
    };
  },
  async mounted() {
    const token = this.$route.params.token;
    
    if (!token) {
      this.verifying = false;
      return;
    }
    
    try {
      const response = await fetch(`${this.$store.state.backendUrl}/verify-email/${token}`);
      const result = await response.json();
      
      if (response.ok) {
        this.success = true;
      } else {
        this.errorMessage = result.msg;
      }
    } catch (error) {
      console.error('Verification error:', error);
      this.errorMessage = 'Something went wrong during verification. Please try again.';
    } finally {
      this.verifying = false;
    }
  }
};
</script>

<style scoped>
#email-verification {
  min-height: 95vh;
}

.card {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>