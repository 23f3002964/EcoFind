<template>
  <!-- Notification dropdown menu -->
  <div class="dropdown">
    <!-- Notification bell button with unread count badge -->
    <button 
      class="btn btn-link text-decoration-none position-relative" 
      type="button" 
      id="notificationDropdown" 
      data-bs-toggle="dropdown" 
      aria-expanded="false"
    >
      <!-- Bell icon -->
      <i class="bi bi-bell" style="font-size: 1.5rem;"></i>
      <!-- Unread notification count badge -->
      <span 
        v-if="unreadCount > 0" 
        class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
        style="font-size: 0.6rem;"
      >
        {{ unreadCount }}
        <span class="visually-hidden">{{ $t('unread_notifications') }}</span>
      </span>
    </button>
    
    <!-- Dropdown menu with notifications -->
    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="notificationDropdown" style="width: 350px; max-height: 400px; overflow-y: auto;">
      <!-- Header with title and mark all as read button -->
      <li class="dropdown-header d-flex justify-content-between align-items-center">
        <span>{{ $t('notifications') }}</span>
        <!-- Mark all as read button (only shown when there are unread notifications) -->
        <button 
          v-if="unreadCount > 0" 
          class="btn btn-sm btn-outline-primary" 
          @click="markAllAsRead"
          :disabled="markingAllRead"
        >
          <span v-if="markingAllRead" class="spinner-border spinner-border-sm" role="status"></span>
          <span v-else>{{ $t('mark_all_read') }}</span>
        </button>
      </li>
      
      <!-- Loading state indicator -->
      <li v-if="loading" class="dropdown-item-text text-center">
        <div class="spinner-border spinner-border-sm" role="status">
          <span class="visually-hidden">{{ $t('loading') }}...</span>
        </div>
      </li>
      
      <!-- Empty state message -->
      <li v-else-if="notifications.length === 0" class="dropdown-item-text text-center text-muted">
        {{ $t('no_notifications') }}
      </li>
      
      <!-- Notification list -->
      <li v-else>
        <div class="list-group list-group-flush">
          <!-- Individual notification items -->
          <a 
            v-for="notification in notifications" 
            :key="notification.id"
            href="#" 
            class="list-group-item list-group-item-action border-0"
            :class="{ 'bg-light': !notification.is_read }"
            @click.prevent="viewNotification(notification)"
          >
            <!-- Notification header with title and timestamp -->
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1">{{ notification.title }}</h6>
              <small class="text-muted">{{ formatTime(notification.created_at) }}</small>
            </div>
            <!-- Notification message content -->
            <p class="mb-1">{{ notification.message }}</p>
            <!-- Related product indicator -->
            <small v-if="notification.related_product_id" class="text-primary">
              <i class="bi bi-box"></i> {{ $t('related_product') }}
            </small>
          </a>
        </div>
      </li>
      
      <!-- Footer with link to full notifications page -->
      <li v-if="notifications.length > 0" class="dropdown-item-text text-center border-top">
        <router-link to="/notifications" class="text-decoration-none">
          {{ $t('view_all_notifications') }}
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
      notifications: [],       // List of recent notifications
      unreadCount: 0,          // Count of unread notifications
      loading: false,          // Loading state flag
      markingAllRead: false    // Mark all as read operation state
    };
  },
  
  async mounted() {
    // Load initial notifications when component mounts
    await this.fetchNotifications();
    // Set up polling to refresh notifications every 30 seconds
    this.notificationInterval = setInterval(this.fetchNotifications, 30000);
  },
  
  beforeUnmount() {
    // Clean up polling interval when component is destroyed
    if (this.notificationInterval) {
      clearInterval(this.notificationInterval);
    }
  },
  
  methods: {
    // Fetch the 5 most recent notifications from the API
    async fetchNotifications() {
      // Only fetch if user is authenticated
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
    
    // Mark all notifications as read
    async markAllAsRead() {
      // Prevent multiple simultaneous requests
      if (this.markingAllRead) return;
      
      try {
        this.markingAllRead = true;
        await axios.put('/api/notifications/read-all', {}, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        // Update local state to reflect all notifications as read
        this.notifications.forEach(n => n.is_read = true);
        this.unreadCount = 0;
      } catch (error) {
        console.error('Error marking all as read:', error);
        alert(this.$t('failed_mark_all_read'));
      } finally {
        this.markingAllRead = false;
      }
    },
    
    // Handle clicking on a notification
    async viewNotification(notification) {
      // Mark as read if it's currently unread
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
      
      // If notification is related to a product, navigate to that product
      if (notification.related_product_id) {
        this.$router.push(`/product/${notification.related_product_id}`);
      }
    },
    
    // Format timestamp for display (e.g., "5m ago", "2h ago")
    formatTime(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / 86400000);
      const diffHours = Math.floor((diffMs % 86400000) / 3600000);
      const diffMinutes = Math.floor(((diffMs % 86400000) % 3600000) / 60000);
      
      if (diffDays > 0) {
        return `${diffDays}${this.$t('days_ago')}`;
      } else if (diffHours > 0) {
        return `${diffHours}${this.$t('hours_ago')}`;
      } else if (diffMinutes > 0) {
        return `${diffMinutes}${this.$t('minutes_ago')}`;
      } else {
        return this.$t('just_now');
      }
    }
  }
};
</script>

<style scoped>
/* Dropdown menu styling */
.dropdown-menu {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

/* Hover effect for notification items */
.list-group-item:hover {
  background-color: #f8f9fa !important;
}
</style>