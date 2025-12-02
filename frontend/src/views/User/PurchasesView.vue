<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>My Purchases</h4>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="purchases.length === 0" class="text-center py-5">
      <i class="bi bi-bag-x" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No purchases yet</h5>
      <p class="text-muted">Your purchased items will appear here.</p>
      <button class="btn btn-primary" @click="$router.push('/products')">
        Browse Products
      </button>
    </div>

    <!-- Purchases List -->
    <div v-else>
      <div class="row">
        <div class="col-12" v-for="purchase in purchases" :key="purchase.id">
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div>
                <strong>Order #{{ purchase.id }}</strong>
                <small class="text-muted ms-2">{{ formatDate(purchase.created_at) }}</small>
              </div>
              <span class="badge" :class="getStatusBadgeClass(purchase.status)">
                {{ purchase.status }}
              </span>
            </div>
            
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <div v-for="item in purchase.items" :key="item.id" class="d-flex mb-3">
                    <div class="flex-shrink-0">
                      <img 
                        :src="item.product.image_url || 'https://via.placeholder.com/80'" 
                        class="img-fluid rounded" 
                        alt="Product image"
                        style="width: 80px; height: 80px; object-fit: cover;"
                      >
                    </div>
                    <div class="flex-grow-1 ms-3">
                      <h6 class="mb-1">{{ item.product.name }}</h6>
                      <p class="text-muted small mb-1">{{ item.product.description }}</p>
                      <div class="d-flex justify-content-between">
                        <span>Qty: {{ item.quantity }}</span>
                        <strong>${{ (item.product.price * item.quantity).toFixed(2) }}</strong>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-4">
                  <div class="card bg-light">
                    <div class="card-body">
                      <h6 class="card-title">Order Summary</h6>
                      <div class="d-flex justify-content-between mb-1">
                        <span>Subtotal</span>
                        <span>${{ purchase.total_amount.toFixed(2) }}</span>
                      </div>
                      <div class="d-flex justify-content-between mb-1">
                        <span>Shipping</span>
                        <span>Free</span>
                      </div>
                      <hr>
                      <div class="d-flex justify-content-between fw-bold">
                        <span>Total</span>
                        <span>${{ purchase.total_amount.toFixed(2) }}</span>
                      </div>
                      
                      <div class="mt-3">
                        <button 
                          class="btn btn-sm btn-outline-primary w-100 mb-2"
                          @click="viewProduct(item.product.id)"
                          v-for="item in purchase.items" 
                          :key="item.id"
                        >
                          View Product
                        </button>
                        
                        <button 
                          v-if="canReview(purchase)" 
                          class="btn btn-sm btn-success w-100"
                          @click="leaveReview(purchase)"
                        >
                          Leave Review
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PreviousPurchasesView',
  data() {
    return {
      purchases: [],
      loading: false,
      error: null
    };
  },
  
  mounted() {
    this.fetchPurchases();
  },
  
  methods: {
    async fetchPurchases() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/purchases');
        this.purchases = response.data.purchases || [];
      } catch (err) {
        console.error('Error fetching purchases:', err);
        this.error = 'Failed to load purchase history. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    getStatusBadgeClass(status) {
      const statusClasses = {
        'completed': 'bg-success',
        'pending': 'bg-warning',
        'shipped': 'bg-info',
        'delivered': 'bg-primary',
        'cancelled': 'bg-danger'
      };
      return statusClasses[status] || 'bg-secondary';
    },
    
    viewProduct(productId) {
      this.$router.push(`/product/${productId}`);
    },
    
    canReview(purchase) {
      // Can review if purchase is completed and no review has been submitted yet
      return purchase.status === 'completed' && !purchase.has_review;
    },
    
    leaveReview(purchase) {
      // Navigate to review page or open review modal
      // For now, we'll just show an alert
      alert('Review functionality would be implemented here');
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.badge.bg-warning {
  color: #000;
}
</style>