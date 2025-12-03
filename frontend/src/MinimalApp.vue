<template>
  <div id="app">
    <h1>Minimal App</h1>
    <p>If you can see this, Vue is working!</p>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'MinimalApp',
  mounted() {
    console.log('Minimal App mounted successfully');
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