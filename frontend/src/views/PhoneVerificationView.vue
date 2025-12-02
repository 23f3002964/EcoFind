<template>
  <div id="phone-verification" class="d-flex justify-content-center align-items-center">
    <div class="card" style="width: 100%; max-width: 500px;">
      <div class="card-body p-4">
        <div class="text-center mb-4">
          <h3>Verify Your Phone Number</h3>
          <p class="text-muted">
            Enter the 6-digit code sent to {{ phoneNumber }}
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          {{ errorMessage }}
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="alert alert-success" role="alert">
          {{ successMessage }}
        </div>

        <!-- Verification Form -->
        <form v-if="!isVerified" @submit.prevent="verifyOtp">
          <div class="mb-3">
            <label for="otp" class="form-label">Verification Code</label>
            <input 
              v-model="otp" 
              type="text" 
              class="form-control" 
              id="otp" 
              placeholder="Enter 6-digit code"
              maxlength="6"
              required
            >
          </div>

          <div class="d-grid gap-2">
            <button 
              type="submit" 
              class="btn btn-success" 
              :disabled="verifying || !otp || otp.length !== 6"
            >
              <span v-if="verifying" class="spinner-border spinner-border-sm" role="status"></span>
              {{ verifying ? 'Verifying...' : 'Verify Phone Number' }}
            </button>
          </div>
        </form>

        <!-- Resend OTP -->
        <div class="mt-3 text-center">
          <p v-if="!isVerified" class="text-muted">
            Didn't receive the code?
            <a href="#" @click.prevent="resendOtp" class="text-primary">
              Resend OTP
            </a>
          </p>
          <p v-else class="text-success">
            <i class="bi bi-check-circle-fill"></i> Phone number verified successfully!
          </p>
        </div>

        <!-- Continue Button -->
        <div v-if="isVerified" class="d-grid gap-2 mt-3">
          <router-link to="/login" class="btn btn-primary">
            Continue to Login
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PhoneVerificationView',
  data() {
    return {
      phoneNumber: '+1 (555) 123-4567', // This would come from the registration process
      otp: '',
      verifying: false,
      errorMessage: null,
      successMessage: null,
      isVerified: false
    };
  },
  methods: {
    async verifyOtp() {
      this.verifying = true;
      this.errorMessage = null;
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/verify-phone`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone_number: this.phoneNumber,
            otp: this.otp
          })
        });
        
        const result = await response.json();
        
        if (response.ok) {
          this.isVerified = true;
          this.successMessage = result.msg;
        } else {
          this.errorMessage = result.msg;
        }
      } catch (error) {
        console.error('Verification error:', error);
        this.errorMessage = 'Something went wrong. Please try again.';
      } finally {
        this.verifying = false;
      }
    },
    
    async resendOtp() {
      // TODO: Add cooldown period to prevent spamming OTP requests
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/resend-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone_number: this.phoneNumber
          })
        });
        
        const result = await response.json();
        
        if (response.ok) {
          this.successMessage = result.msg;
          this.errorMessage = null;
        } else {
          this.errorMessage = result.msg;
          this.successMessage = null;
        }
      } catch (error) {
        console.error('Resend OTP error:', error);
        this.errorMessage = 'Failed to resend OTP. Please try again.';
      }
    }
  }
};
</script>

<style scoped>
#phone-verification {
  min-height: 95vh;
}

.card {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>