import { createApp } from 'vue'

console.log('Pure minimal app loading');

const app = createApp({
  template: `
    <div>
      <h1>Pure Minimal Vue App</h1>
      <p>If you can see this, Vue is working without any dependencies!</p>
    </div>
  `,
  mounted() {
    console.log('Pure minimal app mounted');
  }
})

console.log('App created, mounting...');
app.mount('#app')
console.log('App mounted');