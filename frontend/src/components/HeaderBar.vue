<template>
  <div class="top-header d-flex justify-content-between align-items-center px-4 py-2 border-bottom bg-white">
    <div class="d-flex align-items-center gap-3">
      <router-link to="/chats" class="btn btn-outline-info btn-sm" v-if="$store.state.isAuthenticated">
        <i class="bi bi-chat-dots"></i> Messages
      </router-link>
      <router-link to="/saved-searches" class="btn btn-outline-primary btn-sm" v-if="$store.state.isAuthenticated">
        <i class="bi bi-bookmark"></i> Saved Searches
      </router-link>
      <router-link to="/price-alerts" class="btn btn-outline-success btn-sm" v-if="$store.state.isAuthenticated">
        <i class="bi bi-bell"></i> Price Alerts
      </router-link>
    </div>
    
    <div class="d-flex align-items-center gap-3">
      <NotificationBell v-if="$store.state.isAuthenticated" />
      
      <div class="d-flex align-items-center gap-2">
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
  }
};
</script>

<style scoped>
.top-header {
  height: 60px;
}
</style>