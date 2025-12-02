<template>
  <div class="container my-4">
    <!-- Page header with title and mark all as read button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Notifications</h4>
      <!-- Mark all as read button (only shown when there are unread notifications) -->
      <button 
        v-if="unreadCount > 0" 
        class="btn btn-outline-primary" 
        @click="markAllAsRead"
        :disabled="markingAllRead"
      >
        <span v-if="markingAllRead" class="spinner-border spinner-border-sm me-2" role="status"></span>
        <span v-else><i class="bi bi-check-all me-1"></i></span>
        Mark all as read
      </button>
    </div>

    <!-- Loading State - Shown while fetching notifications -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State - Shown when notification loading fails -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Empty State - Shown when user has no notifications -->
    <div v-else-if="notifications.length === 0" class="text-center py-5">
      <i class="bi bi-bell-slash text-muted" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No notifications</h5>
      <p class="text-muted">You don't have any notifications at the moment.</p>
    </div>

    <!-- Notifications List - Display all notifications -->
    <div v-else>
      <div class="list-group">
        <!-- Individual notification items -->
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="list-group-item list-group-item-action"
          :class="{ 'bg-light': !notification.is_read }"
          @click="viewNotification(notification)"
          style="cursor: pointer;"
        >
          <!-- Notification header with title and date -->
          <div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">{{ notification.title }}</h5>
            <small class="text-muted">{{ formatDate(notification.created_at) }}</small>
          </div>
          <!-- Notification message content -->
          <p class="mb-1">{{ notification.message }}</p>
          <!-- Footer with time and badges -->
          <div class="d-flex justify-content-between align-items-center">
            <small class="text-muted">{{ formatTime(notification.created_at) }}</small>
            <div>
              <!-- Unread status badge -->
              <span v-if="!notification.is_read" class="badge bg-danger">Unread</span>
              <!-- Related product badge -->
              <span v-if="notification.related_product_id" class="badge bg-primary ms-2">
                <i class="bi bi-box me-1"></i> Product
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination Controls - Navigate between notification pages -->
      <nav aria-label="Notifications pagination" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Previous</a>
          </li>
          
          <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Next</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'NotificationsView',
  data() {
    return {
      notifications: [],        // List of all notifications
      loading: false,           // Loading state flag
      markingAllRead: false,    // Mark all as read operation state
      error: '',                // Error message
      currentPage: 1,           // Current pagination page
      totalPages: 1,            // Total number of pages
      totalNotifications: 0,    // Total number of notifications
      unreadCount: 0            // Count of unread notifications
    };
  },
  
  async mounted() {
    // Load notifications when component mounts
    await this.loadNotifications();
  },
  
  methods: {
    // Load notifications with pagination
    async loadNotifications() {
      this.loading = true;
      this.error = '';
      
      try {
        // Build query parameters for API request
        const params = new URLSearchParams();
        params.append('page', this.currentPage);
        params.append('per_page', 10);
        params.append('include_read', true);
        
        const response = await axios.get(`/api/notifications?${params.toString()}`, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        this.notifications = response.data.notifications;
        this.totalPages = response.data.pages;
        this.totalNotifications = response.data.total;
        this.unreadCount = this.notifications.filter(n => !n.is_read).length;
      } catch (error) {
        console.error('Error loading notifications:', error);
        this.error = 'Failed to load notifications. Please try again.';
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
        alert('Failed to mark all notifications as read');
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
    
    // Format date for display (e.g., "May 15, 2023")
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    // Format time for display (e.g., "2:30 PM")
    formatTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    // Navigate to a specific page of notifications
    async changePage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page;
        await this.loadNotifications();
      }
    }
  }
};
</script>

<style scoped>
/* Hover effect for notification items */
.list-group-item:hover {
  background-color: #f8f9fa !important;
}
</style>