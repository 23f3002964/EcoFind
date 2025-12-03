import { createApp } from 'vue'
import TestComponent from './TestComponent.vue'

console.log('Component test loading');

const app = createApp(TestComponent)

console.log('App created with component, mounting...');
app.mount('#app')
console.log('App mounted');