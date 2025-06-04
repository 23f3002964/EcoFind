<template>
  <div id="login" class="d-flex justify-content-center align-items-center">
    <div class="card shadow p-4" style="width: 100%; max-width: 400px;">
      <h4 class="mb-4 fw-semibold">Sign in to your account</h4>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="email" class="form-label">Your email</label>
          <input v-model="email" type="email" class="form-control" id="email" placeholder="name@company.com" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input v-model="password" type="password" class="form-control" id="password" placeholder="••••••••" required>
        </div>

       <div class="d-flex justify-content-between align-items-center mb-3">
          <div class="form-check">
            <input type="checkbox" class="form-check-input" id="remember" />
            <label class="form-check-label" for="remember">Remember me</label>
          </div>
          <a href="/forgot-password" class="text-decoration-none">Forgot password?</a>
        </div>

        <button type="submit" class="btn btn-primary w-100">Login</button>
        
        <div class="mt-2">
        <small>Don’t have an account yet? <a href="/signup" class="text-primary">Sign up</a></small>
      </div>
        <div class="mt-1 fw-bold text-danger">{{ errorMessage }}</div>
      </form>
    </div>
  </div>
</template>



<script>
import { mapState } from 'vuex';


// If You Customize This Login Page, Please be sure :-
// 1. <form @submit.prevent="handleLogin">
// 2. v-model="inputName" for all Inputs
// 3. Please add inputNmae in data property for reactive
// 4. and update handleLogin in methods as your need

export default {
  name:"LoginView",

  // Reactive data
  data(){
    return{
      errorMessage: null,
      email: null,
      password: null,
    }
  },

  // Methods (event handlers, helpers, etc.)
  methods: {
    async handleLogin() {
      const url = `${this.$store.state.backendUrl}/login`;
      const userData = { 'email': this.email, 'password': this.password };

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userData)
        });

        this.email = null;
        this.password = null;

        if(response.ok){

          const authData = await response.json();
          this.$store.dispatch('login', authData);
          if(authData.role === 'User'){
            this.$router.push({name:'userProfile', params:{userId: authData.id}})
          }else if(authData.role === 'Admin'){
            this.$router.push({name:'adminProfile', params:{userId: authData.id}})
          }else{
            console.error(`Unknown role: ${data.role}`);
            this.$router.push({ name: 'Unauthorized' });
          } 

        } else {
          const errorData = await response.json();
          this.errorMessage = errorData.message
          console.error('Error:', errorData);

          setTimeout(() => {
            this.errorMessage = null;
          }, 2000)
        }
        
      } catch (error) {
        console.error('An error occurred:', error);
        alert(error);
      }
    }
  },

  // Computed properties
  computed: {

  },

}
</script>

<style scoped>
#login{
  min-height: 95vh;
}
</style>