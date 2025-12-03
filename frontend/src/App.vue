<template>
  <div id="app">
    <HeaderBar />
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
import HeaderBar from './components/HeaderBar.vue';

export default {
  name: 'App',
  components:{
    HeaderBar,
  },
  mounted() {
    console.log('App component mounted with HeaderBar and router-view');
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
</style>