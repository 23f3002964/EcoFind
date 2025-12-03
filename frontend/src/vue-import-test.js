// Test if Vue can be imported correctly
import { createApp } from 'vue'

console.log('Vue imported successfully');

// Test if we can create a simple app
try {
  const app = createApp({
    template: '<div><h1>Vue Import Test</h1><p>If you see this, Vue import works!</p></div>'
  });
  
  console.log('Vue app created successfully');
  
  // Test if we can mount the app
  app.mount('#app');
  
  console.log('Vue app mounted successfully');
} catch (error) {
  console.error('Error during Vue app creation/mounting:', error);
}