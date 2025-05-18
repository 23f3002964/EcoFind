<template>
  <nav>
    <router-link to="/">Home</router-link> |
    <router-link to="/about">About</router-link> | 
    <router-link to="/singup">Singup</router-link> |
    <router-link to="/login">Login</router-link>
      <div class="p-4">

    <!-- Your login form section goes here -->
  </div>
  </nav>
  <router-view/>
</template>

<script>
export default {
  data() {
    return {
      isDark: false
    }
  },
  mounted() {
    // On initial load, check localStorage or system preference
    const savedTheme = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    this.isDark = savedTheme === 'dark' || (!savedTheme && prefersDark)
    this.applyTheme()
  },
  methods: {
    toggleDark() {
      this.isDark = !this.isDark
      this.applyTheme()
    },
    applyTheme() {
      const html = document.documentElement
      if (this.isDark) {
        html.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        html.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 3px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
