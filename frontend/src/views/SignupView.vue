<template>
  <div id="signup" class="d-flex justify-content-center align-items-center">
    <div class="card shadow p-4" style="width: 100%; max-width: 600px;">
      <h4 class="mb-4 fw-semibold">Create an account</h4>
      <form @submit.prevent="handleSignup">
        <!-- First and Last Name -->
        <div class="row mb-3">
          <div class="col">
            <label for="firstName" class="form-label">First Name</label>
            <input v-model="firstName" type="text" class="form-control" id="firstName" placeholder="John" required>
          </div>
          <div class="col">
            <label for="lastName" class="form-label">Last Name</label>
            <input v-model="lastName" type="text" class="form-control" id="lastName" placeholder="Doe">
          </div>
        </div>

        <!-- Email -->
        <div class="mb-3">
          <label for="email" class="form-label">Your email</label>
          <input v-model="email" type="email" class="form-control" id="email" placeholder="name@company.com" required>
        </div>

        <!-- Password and Confirm Password -->
        <div class="row mb-3">
          <div class="col">
            <label for="password" class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" id="password" placeholder="••••••••"
              required>
          </div>
          <div class="col">
            <label for="confirmPassword" class="form-label">Confirm Password</label>
            <input v-model="confirmPassword" type="password" class="form-control" id="confirmPassword"
              placeholder="••••••••" required>
          </div>
        </div>

        <!-- Bio -->
        <div class="mb-3">
          <label for="bio" class="form-label">Bio</label>
          <textarea v-model="bio" id="bio" class="form-control" rows="2"
            placeholder="Tell us about yourself"></textarea>
        </div>

        <div class="row mb-3">
          <!-- Date of Birth -->
          <div class="col">
            <label for="dob" class="form-label">Date of Birth</label>
            <input v-model="dob" type="date" class="form-control" id="dob" placeholder="yyyy-mm-dd" required>
          </div>

          <!-- Gender -->
          <div class="col">
            <label class="form-label d-block">Gender</label>
            <div class="form-check form-check-inline">
              <input v-model="gender" class="form-check-input" type="radio" name="gender" id="male" value="male">
              <label class="form-check-label" for="male">Male</label>
            </div>
            <div class="form-check form-check-inline">
              <input v-model="gender" class="form-check-input" type="radio" name="gender" id="female" value="female">
              <label class="form-check-label" for="female">Female</label>
            </div>
            <div class="form-check form-check-inline">
              <input v-model="gender" class="form-check-input" type="radio" name="gender" id="other" value="other">
              <label class="form-check-label" for="other">Other</label>
            </div>
          </div>
        </div>


        <!-- Terms -->
        <div class="form-check mb-3">
          <input v-model="acceptTerms" type="checkbox" class="form-check-input" id="term" required />
          <label class="form-check-label" for="term">I accept the <a href="#" class="">Terms and Conditions</a></label>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="btn btn-success w-100">Create Account</button>

        <div class="mt-2">
          <small>Already have an account? <a href="/login" class="text-primary">Login here</a></small>
        </div>

        <!-- Success/Error Message -->
        <div class="mt-3 fw-bold text-success" v-if="successMessage">{{ successMessage }}</div>
        <div class="mt-2 fw-bold text-danger" v-if="errorMessage">{{ errorMessage }}</div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignupView',
  data() {
    return {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      dob: '',
      bio: '',
      gender: '',
      acceptTerms: false,
      successMessage: null,
      errorMessage: null
    };
  },
  methods: {
    async handleSignup() {
      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match.";
        this.successMessage = null;
        return;
      }

      const userData = {
        email: this.email,
        first_name: this.firstName,
        last_name: this.lastName,
        gender: this.gender || null,
        dob: this.dob || null,               // yyyy-mm-dd format from date input
        bio: this.bio || null,
        profile_picture: null,               // add upload later if needed
        password: this.password,
        confirm_password: this.confirmPassword
      };

      const url = `${this.$store.state.backendUrl}/register`;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userData)
        });

        const result = await response.json();

        if (response.ok) {
          this.successMessage = result.message || "Registration successful! You can now log in.";
          this.errorMessage = null;

          // Reset form
          this.firstName = '';
          this.lastName = '';
          this.email = '';
          this.password = '';
          this.confirmPassword = '';
          this.dob = '';
          this.bio = '';
          this.gender = '';
          this.acceptTerms = false;

        } else {
          this.errorMessage = result.message || "Registration failed.";
          this.successMessage = null;
        }

      } catch (error) {
        console.error("Signup error:", error);
        this.errorMessage = "Something went wrong. Please try again.";
        this.successMessage = null;
      }
    }
  }
};
</script>

<style scoped>
#signup {
  min-height: 95vh;
}
</style>
