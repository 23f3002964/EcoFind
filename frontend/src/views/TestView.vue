<template>
  <div class="test-page">
    <!-- Simple Test Page -->
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 90vh; background-color: #f8f9fa;">
      <h1 style="color: #28a745; font-size: 2.5rem;">EcoFinds Frontend is Working!</h1>
      <p style="font-size: 1.2rem; margin: 1rem 0;">If you can see this message, the frontend is loading correctly.</p>
      <div style="margin-top: 2rem;">
        <button style="background-color: #28a745; color: white; border: none; padding: 10px 20px; font-size: 1rem; border-radius: 5px; margin-right: 10px; cursor: pointer;" @click="goToProducts">Browse Products</button>
        <button style="background-color: transparent; color: #28a745; border: 1px solid #28a745; padding: 10px 20px; font-size: 1rem; border-radius: 5px; cursor: pointer;" @click="goToLogin">Login</button>
      </div>
      <div style="margin-top: 3rem;">
        <h3>Current Time: {{ currentTime }}</h3>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestView',
  data() {
    return {
      currentTime: new Date().toLocaleTimeString()
    }
  },
  mounted() {
    console.log('TestView component mounted');
    // Update time every second
    this.timer = setInterval(() => {
      this.currentTime = new Date().toLocaleTimeString();
    }, 1000);
  },
  beforeUnmount() {
    console.log('TestView component unmounting');
    if (this.timer) {
      clearInterval(this.timer);
    }
  },
  methods: {
    goToProducts() {
      console.log('Navigating to products');
      this.$router.push('/products');
    },
    goToLogin() {
      console.log('Navigating to login');
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
.test-page {
  min-height: 90vh;
}
</style>