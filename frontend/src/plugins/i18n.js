const i18n = {
  install(app) {
    // Add simple global $t method for translations
    app.config.globalProperties.$t = (key) => {
      console.log('Translation requested for key:', key);
      return key; // Just return the key as-is for now
    };
    
    // Add simple global $setLanguage method
    app.config.globalProperties.$setLanguage = async (lang) => {
      console.log('Setting language to:', lang);
    };
    
    // Add simple global $getCurrentLanguage method
    app.config.globalProperties.$getCurrentLanguage = () => {
      console.log('Getting current language');
      return 'en';
    };
    
    // Also make it available in provide/inject
    app.provide('$t', (key) => key);
    app.provide('$setLanguage', async (lang) => {});
    app.provide('$getCurrentLanguage', () => 'en');
  }
};

export default i18n;