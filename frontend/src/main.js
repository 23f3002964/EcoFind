import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import translationService from './services/translationService'
import i18n from './plugins/i18n'

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