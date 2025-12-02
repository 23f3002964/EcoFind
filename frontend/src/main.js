import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import translationService from './services/translationService'
import i18n from './plugins/i18n'

// Simplified initialization for debugging
createApp(App).use(store).use(router).use(i18n).mount('#app')

// Load translations based on user's preferred language
async function initApp() {
  // Try to get user's preferred language from store
  const userPreferredLanguage = store.state.userData?.preferred_language || 'en';
  
  // Load translations
  await translationService.loadTranslations(userPreferredLanguage);
  
  // Create and mount the app
  createApp(App).use(store).use(router).use(i18n).mount('#app')
}

initApp().catch(error => {
  console.error('Error initializing app:', error);
  // Fallback to English if there's an error
  translationService.loadTranslations('en').then(() => {
    createApp(App).use(store).use(router).use(i18n).mount('#app')
  });
})