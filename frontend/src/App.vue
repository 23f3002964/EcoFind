<template>
  <div id="app" class="d-flex">
    <!-- Sidebar -->
    <NavBar v-if="componentsLoaded.navbar" />

    <!-- Right section: header + content -->
    <div class="flex-grow-1 d-flex flex-column" style="min-height: 100vh;">
      <!-- Header Component -->
      <HeaderBar v-if="componentsLoaded.headerbar" />

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
  data() {
    return {
      componentsLoaded: {
        navbar: true,
        headerbar: true
      }
    }
  },
  mounted() {
    console.log('App mounted');
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