<template>
  <div class="container my-4">
    <h4>User Dashboard</h4>
    
    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-box fs-1 text-primary"></i>
            <h5 class="card-title mt-2">My Listings</h5>
            <p class="card-text">Manage your product listings</p>
            <router-link :to="`/user/${userId}/listings`" class="btn btn-primary">View</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-cart fs-1 text-success"></i>
            <h5 class="card-title mt-2">My Cart</h5>
            <p class="card-text">View and manage your shopping cart</p>
            <router-link :to="`/user/${userId}/cart`" class="btn btn-success">View</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-currency-dollar fs-1 text-warning"></i>
            <h5 class="card-title mt-2">My Purchases</h5>
            <p class="card-text">View your purchase history</p>
            <router-link :to="`/user/${userId}/purchases`" class="btn btn-warning">View</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-chat-dots fs-1 text-info"></i>
            <h5 class="card-title mt-2">My Messages</h5>
            <p class="card-text">Check your messages</p>
            <router-link :to="`/chats`" class="btn btn-info">View</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Additional Features -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-star fs-1 text-purple"></i>
            <h5 class="card-title mt-2">My Reviews</h5>
            <p class="card-text">View and manage your reviews</p>
            <router-link :to="`/user/${userId}/reviews`" class="btn btn-outline-purple">View</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-exclamation-circle fs-1 text-orange"></i>
            <h5 class="card-title mt-2">My Disputes</h5>
            <p class="card-text">Manage your disputes</p>
            <router-link :to="`/user/${userId}/disputes`" class="btn btn-outline-orange">View</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-search fs-1 text-teal"></i>
            <h5 class="card-title mt-2">Saved Searches</h5>
            <p class="card-text">Manage your saved searches</p>
            <router-link :to="`/saved-searches`" class="btn btn-outline-teal">View</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-bell fs-1 text-pink"></i>
            <h5 class="card-title mt-2">Price Alerts</h5>
            <p class="card-text">Manage your price alerts</p>
            <router-link :to="`/price-alerts`" class="btn btn-outline-pink">View</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Stats Overview -->
    <div class="card">
      <div class="card-header">
        <h5>Overview</h5>
      </div>
      <div class="card-body">
        <div class="row text-center">
          <div class="col-md-3 mb-3">
            <h3>{{ stats.total_listings }}</h3>
            <p class="text-muted">Total Listings</p>
          </div>
          <div class="col-md-3 mb-3">
            <h3>{{ stats.active_listings }}</h3>
            <p class="text-muted">Active Listings</p>
          </div>
          <div class="col-md-3 mb-3">
            <h3>{{ stats.total_purchases }}</h3>
            <p class="text-muted">Total Purchases</p>
          </div>
          <div class="col-md-3 mb-3">
            <h3>{{ stats.unread_messages }}</h3>
            <p class="text-muted">Unread Messages</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserDashboard',
  data() {
    return {
      userId: null,
      stats: {
        total_listings: 0,
        active_listings: 0,
        total_purchases: 0,
        unread_messages: 0
      }
    };
  },
  
  mounted() {
    this.userId = this.$route.params.userId;
    this.fetchDashboardData();
  },
  
  methods: {
    async fetchDashboardData() {
      try {
        const response = await axios.get('/api/dashboard');
        this.stats = response.data.stats;
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    }
  }
};
</script>

<style scoped>
.text-purple {
  color: #6f42c1;
}

.text-orange {
  color: #fd7e14;
}

.text-teal {
  color: #20c997;
}

.text-pink {
  color: #d63384;
}

.btn-outline-purple {
  color: #6f42c1;
  border-color: #6f42c1;
}

.btn-outline-purple:hover {
  background-color: #6f42c1;
  border-color: #6f42c1;
}

.btn-outline-orange {
  color: #fd7e14;
  border-color: #fd7e14;
}

.btn-outline-orange:hover {
  background-color: #fd7e14;
  border-color: #fd7e14;
}

.btn-outline-teal {
  color: #20c997;
  border-color: #20c997;
}

.btn-outline-teal:hover {
  background-color: #20c997;
  border-color: #20c997;
}

.btn-outline-pink {
  color: #d63384;
  border-color: #d63384;
}

.btn-outline-pink:hover {
  background-color: #d63384;
  border-color: #d63384;
}
</style>