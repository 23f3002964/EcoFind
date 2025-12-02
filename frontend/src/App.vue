<template>
  <div id="app" class="d-flex">
    <!-- Debug info -->
    <div v-if="false" style="position: fixed; top: 0; left: 0; background: red; color: white; z-index: 9999; padding: 10px;">
      Debug: Store Loaded - {{ $store ? 'Yes' : 'No' }}
    </div>
    
    <!-- Sidebar -->
    <NavBar />

    <!-- Right section: header + content -->
    <div class="flex-grow-1 d-flex flex-column" style="min-height: 100vh;">
      <!-- Header Component -->
      <HeaderBar />

      <!-- Main Content -->
      <div class="flex-grow-1 p-4" style="background-color: #f8f9fa;">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';
import HeaderBar from './components/HeaderBar.vue';
export default {
    name: 'App',
    components:{
      NavBar,
      HeaderBar,
  },
  mounted() {
    console.log('App mounted');
    console.log('Store:', this.$store);
    console.log('Router:', this.$router);
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}


</style>