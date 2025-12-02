<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>My Bids</h4>
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
    <div v-else-if="bids.length === 0" class="text-center py-5">
      <i class="bi bi-gavel text-muted" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No bids yet</h5>
      <p class="text-muted">You haven't placed any bids on auctions.</p>
      <router-link to="/products" class="btn btn-success">
        <i class="bi bi-search"></i> Browse Auctions
      </router-link>
    </div>

    <!-- Bids List -->
    <div v-else>
      <div class="row row-cols-1 g-4">
        <div v-for="bid in bids" :key="bid.id" class="col">
          <div class="card h-100">
            <div class="card-body">
              <div class="d-flex">
                <div class="flex-shrink-0 me-3">
                  <img 
                    :src="bid.product.images[0] || 'https://via.placeholder.com/100'" 
                    class="img-fluid rounded" 
                    :alt="bid.product.title"
                    style="width: 100px; height: 100px; object-fit: cover;"
                  >
                </div>
                <div class="flex-grow-1">
                  <h5 class="card-title">
                    <router-link :to="`/auction/${bid.product.id}`" class="text-decoration-none">
                      {{ bid.product.title }}
                    </router-link>
                  </h5>
                  
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                      <span class="h5 text-success mb-0">${{ bid.amount }}</span>
                      <span v-if="bid.is_winning" class="badge bg-success ms-2">Winning Bid</span>
                    </div>
                    <div>
                      <span v-if="bid.product.is_sold" class="badge bg-secondary">Sold</span>
                      <span v-else-if="isAuctionEnded(bid.product)" class="badge bg-info">Ended</span>
                      <span v-else class="badge bg-warning">Active</span>
                    </div>
                  </div>
                  
                  <div class="d-flex justify-content-between text-muted small">
                    <span>Placed: {{ formatDate(bid.created_at) }}</span>
                    <span v-if="bid.product.auction_end_time">
                      Ends: {{ formatDate(bid.product.auction_end_time) }}
                    </span>
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
  name: 'MyBidsView',
  data() {
    return {
      loading: true,
      error: '',
      bids: []
    };
  },
  
  async mounted() {
    await this.loadBids();
  },
  
  methods: {
    async loadBids() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await axios.get('/api/my-bids', {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.bids = data.bids;
        } else {
          this.error = 'Failed to load your bids';
        }
      } catch (error) {
        console.error('Error loading bids:', error);
        this.error = 'Network error. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },
    
    isAuctionEnded(product) {
      if (!product.auction_end_time) return false;
      
      const endTime = new Date(product.auction_end_time);
      const now = new Date();
      return now > endTime;
    }
  }
};
</script>

<style scoped>
.card-title a:hover {
  color: #0d6efd !important;
}
</style>