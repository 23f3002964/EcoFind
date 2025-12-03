<template>
  <div class="top-header d-flex justify-content-between align-items-center px-4 py-2 border-bottom bg-white">
    <div class="d-flex align-items-center gap-3">
      <router-link to="/chats" class="btn btn-outline-info btn-sm" v-if="$store.state.isAuthenticated">
        <i class="bi bi-chat-dots"></i> {{ $t('messages') }}
      </router-link>
      <router-link to="/saved-searches" class="btn btn-outline-primary btn-sm" v-if="$store.state.isAuthenticated">
        <i class="bi bi-bookmark"></i> {{ $t('saved_searches') }}
      </router-link>
      <router-link to="/price-alerts" class="btn btn-outline-success btn-sm" v-if="$store.state.isAuthenticated">
        <i class="bi bi-bell"></i> {{ $t('price_alerts') }}
      </router-link>
    </div>
    
    <div class="d-flex align-items-center gap-3">
      <!-- Language Selector -->
      <div class="dropdown" v-if="$store.state.isAuthenticated">
        <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown">
          <i class="bi bi-globe"></i> {{ getCurrentLanguageName() }}
        </button>
        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="#" @click.prevent="setLanguage('en')">English</a></li>
          <li><a class="dropdown-item" href="#" @click.prevent="setLanguage('hi')">हिंदी</a></li>
          <li><a class="dropdown-item" href="#" @click.prevent="setLanguage('gu')">ગુજરાતી</a></li>
        </ul>
      </div>
      
      <NotificationBell v-if="$store.state.isAuthenticated" />
      
      <div class="d-flex align-items-center gap-2" v-if="$store.state.isAuthenticated">
        <img
          :src="userProfileImage"
          alt="User"
          class="rounded-circle"
          width="36"
          height="36"
        />
        <span class="fw-medium">{{ userData?.first_name }}</span>
      </div>
    </div>
  </div>
</template>


<script>
import { mapGetters } from 'vuex';
import NotificationBell from './NotificationBell.vue';

export default {
  name: 'HeaderBar',
  components: {
    NotificationBell
  },
  computed: {
    ...mapGetters(['userData']),
    userProfileImage() {
      return this.userData?.profile_image || 'https://via.placeholder.com/40';
    }
  },
  methods: {
    getCurrentLanguageName() {
      const lang = this.$store.state.userData?.preferred_language || 'en';
      const languages = {
        'en': 'English',
        'hi': 'हिंदी',
        'gu': 'ગુજરાતી'
      };
      return languages[lang] || 'English';
    },
    async setLanguage(lang) {
      // Update store
      if (this.$store.state.userData) {
        this.$store.commit('SET_USER_DATA', {
          ...this.$store.state.userData,
          preferred_language: lang
        });
      }
      
      // Save to backend
      if (this.$store.state.authData?.id) {
        try {
          const response = await fetch(`${this.$store.state.backendUrl}/api/user/language`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': this.$store.state.authData.token
            },
            body: JSON.stringify({ preferred_language: lang })
          });
          
          if (!response.ok) {
            console.error('Failed to save language preference');
          }
        } catch (error) {
          console.error('Error saving language preference:', error);
        }
      }
      
      // Load new translations
      await this.$setLanguage(lang);
      
      // Reload page to apply translations
      window.location.reload();
    }
  }
};
</script>

<style scoped>
.top-header {
  height: 60px;
}
</style>