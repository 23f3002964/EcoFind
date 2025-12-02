<template>
  <div class="home container-fluid p-0">
    <!-- Hero Section -->
    <header class="bg-success text-white py-5">
      <div class="container text-center">
        <h1 class="display-4 fw-bold">{{ $t('welcome') }}</h1>
        <p class="lead">{{ $t('browse_products') }}</p>
        <router-link to="/products" class="btn btn-light btn-lg mt-3">
          <i class="bi bi-search me-2"></i>{{ $t('browse_products') }}
        </router-link>
      </div>
    </header>

    <!-- Features Section -->
    <section id="features" class="py-5 bg-light">
      <div class="container">
        <h2 class="text-center mb-4">{{ $t('why_use_ecofinds') }}</h2>
        <div class="row text-center">
          <div class="col-md-4">
            <i class="bi bi-globe2 fs-1 text-success mb-2"></i>
            <h5>{{ $t('eco_friendly_focus') }}</h5>
            <p>{{ $t('eco_friendly_description') }}</p>
          </div>
          <div class="col-md-4">
            <i class="bi bi-geo-alt fs-1 text-success mb-2"></i>
            <h5>{{ $t('local_discovery') }}</h5>
            <p>{{ $t('local_discovery_description') }}</p>
          </div>
          <div class="col-md-4">
            <i class="bi bi-heart fs-1 text-success mb-2"></i>
            <h5>{{ $t('support_good_causes') }}</h5>
            <p>{{ $t('support_good_causes_description') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="py-5 bg-primary text-white">
      <div class="container text-center">
        <h2 class="mb-3">{{ $t('ready_to_make_difference') }}</h2>
        <p class="lead mb-4">{{ $t('join_eco_conscious_shoppers') }}</p>
        <div class="d-flex justify-content-center gap-3">
          <router-link to="/signup" class="btn btn-light btn-lg">
            <i class="bi bi-person-plus me-2"></i>{{ $t('signup') }}
          </router-link>
          <router-link to="/products" class="btn btn-outline-light btn-lg">
            <i class="bi bi-box-seam me-2"></i>{{ $t('browse_products') }}
          </router-link>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-5">
      <div class="container text-center">
        <h2>{{ $t('about_ecofinds') }}</h2>
        <p class="lead">{{ $t('mission_statement') }}</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white text-center py-3">
      <div class="container">
        &copy; 2025 EcoFinds. {{ $t('all_rights_reserved') }}
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