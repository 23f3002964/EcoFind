<template>
  <div class="dropdown">
    <button 
      class="btn btn-link text-decoration-none position-relative" 
      type="button" 
      id="notificationDropdown" 
      data-bs-toggle="dropdown" 
      aria-expanded="false"
    >
      <i class="bi bi-bell" style="font-size: 1.5rem;"></i>
      <span 
        v-if="unreadCount > 0" 
        class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
        style="font-size: 0.6rem;"
      >
        {{ unreadCount }}
        <span class="visually-hidden">unread notifications</span>
      </span>
    </button>
    
    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="notificationDropdown" style="width: 350px; max-height: 400px; overflow-y: auto;">
      <li class="dropdown-header d-flex justify-content-between align-items-center">
        <span>Notifications</span>
        <button 
          v-if="unreadCount > 0" 
          class="btn btn-sm btn-outline-primary" 
          @click="markAllAsRead"
          :disabled="markingAllRead"
        >
          <span v-if="markingAllRead" class="spinner-border spinner-border-sm" role="status"></span>
          <span v-else>Mark all as read</span>
        </button>
      </li>
      
      <li v-if="loading" class="dropdown-item-text text-center">
        <div class="spinner-border spinner-border-sm" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </li>
      
      <li v-else-if="notifications.length === 0" class="dropdown-item-text text-center text-muted">
        No notifications
      </li>
      
      <li v-else>
        <div class="list-group list-group-flush">
          <a 
            v-for="notification in notifications" 
            :key="notification.id"
            href="#" 
            class="list-group-item list-group-item-action border-0"
            :class="{ 'bg-light': !notification.is_read }"
            @click.prevent="viewNotification(notification)"
          >
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1">{{ notification.title }}</h6>
              <small class="text-muted">{{ formatTime(notification.created_at) }}</small>
            </div>
            <p class="mb-1">{{ notification.message }}</p>
            <small v-if="notification.related_product_id" class="text-primary">
              <i class="bi bi-box"></i> Related product
            </small>
          </a>
        </div>
      </li>
      
      <li v-if="notifications.length > 0" class="dropdown-item-text text-center border-top">
        <router-link to="/notifications" class="text-decoration-none">
          View all notifications
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'NotificationBell',
  data() {
    return {
      notifications: [],
      unreadCount: 0,
      loading: false,
      markingAllRead: false
    };
  },
  
  async mounted() {
    await this.fetchNotifications();
    // Set up polling for new notifications every 30 seconds
    this.notificationInterval = setInterval(this.fetchNotifications, 30000);
  },
  
  beforeUnmount() {
    if (this.notificationInterval) {
      clearInterval(this.notificationInterval);
    }
  },
  
  methods: {
    async fetchNotifications() {
      if (!this.$store.state.isAuthenticated) return;
      
      try {
        this.loading = true;
        const response = await axios.get('/api/notifications?per_page=5', {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        this.notifications = response.data.notifications;
        this.unreadCount = response.data.notifications.filter(n => !n.is_read).length;
      } catch (error) {
        console.error('Error fetching notifications:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async markAllAsRead() {
      if (this.markingAllRead) return;
      
      try {
        this.markingAllRead = true;
        await axios.put('/api/notifications/read-all', {}, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        // Update local state
        this.notifications.forEach(n => n.is_read = true);
        this.unreadCount = 0;
      } catch (error) {
        console.error('Error marking all as read:', error);
        alert('Failed to mark all notifications as read');
      } finally {
        this.markingAllRead = false;
      }
    },
    
    async viewNotification(notification) {
      // Mark as read
      if (!notification.is_read) {
        try {
          await axios.put(`/api/notifications/${notification.id}/read`, {}, {
            headers: {
              'Authorization': this.$store.state.authData?.token
            }
          });
          
          // Update local state
          notification.is_read = true;
          this.unreadCount--;
        } catch (error) {
          console.error('Error marking notification as read:', error);
        }
      }
      
      // If notification is related to a product, navigate to it
      if (notification.related_product_id) {
        this.$router.push(`/product/${notification.related_product_id}`);
      }
    },
    
    formatTime(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / 86400000);
      const diffHours = Math.floor((diffMs % 86400000) / 3600000);
      const diffMinutes = Math.floor(((diffMs % 86400000) % 3600000) / 60000);
      
      if (diffDays > 0) {
        return `${diffDays}d ago`;
      } else if (diffHours > 0) {
        return `${diffHours}h ago`;
      } else if (diffMinutes > 0) {
        return `${diffMinutes}m ago`;
      } else {
        return 'Just now';
      }
    }
  }
};
</script>

<style scoped>
.dropdown-menu {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.list-group-item:hover {
  background-color: #f8f9fa !important;
}
</style>