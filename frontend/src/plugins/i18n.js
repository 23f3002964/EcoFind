import translationService from '@/services/translationService';

const i18n = {
  install(app) {
    // Add global $t method for translations
    app.config.globalProperties.$t = (key) => {
      return translationService.t(key);
    };
    
    // Add global $setLanguage method
    app.config.globalProperties.$setLanguage = async (lang) => {
      await translationService.loadTranslations(lang);
    };
    
    // Add global $getCurrentLanguage method
    app.config.globalProperties.$getCurrentLanguage = () => {
      return translationService.getCurrentLanguage();
    };
    
    // Also make it available in provide/inject
    app.provide('$t', (key) => translationService.t(key));
    app.provide('$setLanguage', async (lang) => {
      await translationService.loadTranslations(lang);
    });
    app.provide('$getCurrentLanguage', () => translationService.getCurrentLanguage());
  }
};

export default i18n;