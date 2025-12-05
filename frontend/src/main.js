import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import translationService from './services/translationService'
import i18n from './plugins/i18n'
import axios from 'axios'

// Configure axios baseURL and default Authorization header from stored auth
try {
  const storedAuth = sessionStorage.getItem('authData');
  const initialAuth = storedAuth ? JSON.parse(storedAuth) : null;
  
  // Set baseURL for all API calls
  axios.defaults.baseURL = 'http://127.0.0.1:5000';
  
  // Set Authorization header if token exists
  if (initialAuth && initialAuth.token) {
    axios.defaults.headers.common['Authorization'] = initialAuth.token;
  }
  
  // Expose axios for quick debugging in devtools console
  window.axios = axios;
} catch (e) {
  console.error('Error configuring axios:', e);
  axios.defaults.baseURL = 'http://127.0.0.1:5000';
  window.axios = axios;
}

console.log('Main.js loaded');

// Add global error handling
window.addEventListener('error', (e) => {
  console.error('Global error caught:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled promise rejection:', e.reason);
});

try {
  // Create the app instance
  const app = createApp(App)

  console.log('App instance created');

  // Use plugins
  app.use(store)
  app.use(router)
  app.use(i18n)

  console.log('Plugins registered');

  // Mount the app immediately
  app.mount('#app')

  console.log('App mounted to #app');

  // Load translations after mounting
  async function loadTranslations() {
    try {
      console.log('Attempting to load translations');
      // Try to get user's preferred language from store
      const userPreferredLanguage = store.state.userData?.preferred_language || 'en';
      console.log('User preferred language:', userPreferredLanguage);
      
      // Load translations
      await translationService.loadTranslations(userPreferredLanguage);
      console.log('Translations loaded successfully');
    } catch (error) {
      console.error('Error loading translations:', error);
    }
  }

  // Load translations after mounting
  loadTranslations().catch(error => {
    console.error('Error loading translations after mount:', error);
  });
} catch (error) {
  console.error('Error during app initialization:', error);
}