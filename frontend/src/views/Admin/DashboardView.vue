<template>
  <div class="container my-4">
    <h4>Admin Dashboard</h4>
    
    <!-- Stats Overview -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card bg-primary text-white h-100">
          <div class="card-body">
            <h5 class="card-title">Total Users</h5>
            <h3>{{ dashboardData.user_stats?.total || 0 }}</h3>
            <p class="mb-0">{{ dashboardData.user_stats?.active || 0 }} Active</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card bg-success text-white h-100">
          <div class="card-body">
            <h5 class="card-title">Total Products</h5>
            <h3>{{ dashboardData.product_stats?.total || 0 }}</h3>
            <p class="mb-0">{{ dashboardData.product_stats?.active || 0 }} Active</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card bg-warning text-dark h-100">
          <div class="card-body">
            <h5 class="card-title">Open Disputes</h5>
            <h3>{{ dashboardData.dispute_stats?.open || 0 }}</h3>
            <p class="mb-0">Needs Attention</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card bg-info text-white h-100">
          <div class="card-body">
            <h5 class="card-title">Recent Activity</h5>
            <h3>{{ dashboardData.recent_disputes_count || 0 }}</h3>
            <p class="mb-0">Disputes (30 days)</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-people fs-1 text-primary"></i>
            <h5 class="card-title mt-2">User Management</h5>
            <p class="card-text">Manage user accounts and permissions</p>
            <router-link :to="`/admin/${userId}/users`" class="btn btn-primary">Manage Users</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-exclamation-circle fs-1 text-warning"></i>
            <h5 class="card-title mt-2">Complaints</h5>
            <p class="card-text">Handle user complaints and disputes</p>
            <router-link :to="`/admin/${userId}/complaints`" class="btn btn-warning">Manage Complaints</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <i class="bi bi-graph-up fs-1 text-success"></i>
            <h5 class="card-title mt-2">Reports</h5>
            <p class="card-text">View platform analytics and reports</p>
            <button class="btn btn-success">View Reports</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Recent Users</h5>
          </div>
          <div class="card-body">
            <ul class="list-group list-group-flush">
              <li 
                class="list-group-item d-flex justify-content-between align-items-center" 
                v-for="user in dashboardData.recent_users" 
                :key="user.id"
              >
                <div>
                  <strong>{{ user.username }}</strong>
                  <br>
                  <small class="text-muted">{{ user.email }}</small>
                </div>
                <small>{{ formatDate(user.created_at) }}</small>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Recent Products</h5>
          </div>
          <div class="card-body">
            <ul class="list-group list-group-flush">
              <li 
                class="list-group-item d-flex justify-content-between align-items-center" 
                v-for="product in dashboardData.recent_products" 
                :key="product.id"
              >
                <div>
                  <strong>{{ product.title }}</strong>
                  <br>
                  <small class="text-muted">${{ product.price }}</small>
                </div>
                <small>{{ formatDate(product.created_at) }}</small>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      userId: null,
      dashboardData: {
        user_stats: {},
        product_stats: {},
        dispute_stats: {},
        recent_users: [],
        recent_products: [],
        recent_disputes_count: 0
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
        const response = await axios.get('/api/admin/dashboard');
        this.dashboardData = response.data;
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}
</style>