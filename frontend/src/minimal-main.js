import { createApp } from 'vue'

console.log('Minimal main.js loaded');

// Create a simple app component
const MinimalApp = {
  template: `
    <div>
      <h1>Minimal Vue App</h1>
      <p>If you can see this, Vue is working!</p>
      <button @click="count++">Clicked {{ count }} times</button>
    </div>
  `,
  data() {
    return {
      count: 0
    }
  },
  mounted() {
    console.log('Minimal app mounted');
  }
}

// Create the app instance
const app = createApp(MinimalApp)

console.log('Minimal app instance created');

// Mount the app
app.mount('#app')

console.log('Minimal app mounted to #app');