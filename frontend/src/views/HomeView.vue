<template>
  <div class="home container-fluid p-0">
    <!-- Hero Section -->
    <header class="bg-success text-white py-5">
      <div class="container text-center">
        <h1 class="display-4 fw-bold">Discover Local Eco-Friendly Shops</h1>
        <p class="lead">EcoFinds helps you find sustainable businesses around you.</p>
        <router-link to="/products" class="btn btn-light btn-lg mt-3">
          <i class="bi bi-search me-2"></i>Explore Sustainable Products
        </router-link>
      </div>
    </header>

    <!-- Features Section -->
    <section id="features" class="py-5 bg-light">
      <div class="container">
        <h2 class="text-center mb-4">Why Use EcoFinds?</h2>
        <div class="row text-center">
          <div class="col-md-4">
            <i class="bi bi-globe2 fs-1 text-success mb-2"></i>
            <h5>Eco-Friendly Focus</h5>
            <p>We list only verified sustainable and eco-conscious businesses.</p>
          </div>
          <div class="col-md-4">
            <i class="bi bi-geo-alt fs-1 text-success mb-2"></i>
            <h5>Local Discovery</h5>
            <p>Find green shops, cafes, and services in your neighborhood.</p>
          </div>
          <div class="col-md-4">
            <i class="bi bi-heart fs-1 text-success mb-2"></i>
            <h5>Support Good Causes</h5>
            <p>Your purchases make a difference for the planet and people.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="py-5 bg-primary text-white">
      <div class="container text-center">
        <h2 class="mb-3">Ready to Make a Difference?</h2>
        <p class="lead mb-4">Join thousands of eco-conscious shoppers today.</p>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/signup" class="btn btn-light btn-lg">
            <i class="bi bi-person-plus me-2"></i>Create Account
          </router-link>
          <router-link to="/products" class="btn btn-outline-light btn-lg">
            <i class="bi bi-box-seam me-2"></i>Browse Products
          </router-link>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-5">
      <div class="container text-center">
        <h2>About EcoFinds</h2>
        <p class="lead">We're on a mission to connect eco-conscious consumers with sustainable businesses worldwide.</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white text-center py-3">
      <div class="container">
        &copy; 2025 EcoFinds. All rights reserved.
      </div>
    </footer>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'

export default {
  name: 'HomeView',
  components: {
    HelloWorld
  }
}
</script>

<style scoped>
.home {
  min-height: 90vh;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>