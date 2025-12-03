// Debug main file to trace execution
console.log('Debug main file loading');

// Import Vue
import { createApp } from 'vue'
console.log('Vue imported successfully');

// Create a simple component
const TestComponent = {
  template: `
    <div>
      <h1>Debug Test</h1>
      <p>If you can see this, the debug test is working!</p>
    </div>
  `,
  mounted() {
    console.log('Test component mounted');
  }
}

console.log('Test component created');

// Create app
console.log('Creating app...');
const app = createApp(TestComponent)
console.log('App created successfully');

// Mount app
console.log('Mounting app to #app...');
try {
  app.mount('#app')
  console.log('App mounted successfully');
} catch (error) {
  console.error('Error mounting app:', error);
}