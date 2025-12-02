<template>
  <div class="container my-4">
    <div class="d-flex align-items-center mb-4">
      <button class="btn btn-outline-secondary me-3" @click="$router.back()">
        <i class="bi bi-arrow-left"></i>
      </button>
      <h4>Confirm Auction Sale</h4>
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

    <!-- Success State -->
    <div v-else-if="saleConfirmed" class="alert alert-success">
      <h5>Sale Confirmed Successfully!</h5>
      <p>The auction has been marked as sold and the winning bidder has been notified.</p>
      <button class="btn btn-primary" @click="$router.push('/my-listings')">Back to My Listings</button>
    </div>

    <!-- Confirm Sale Form -->
    <div v-else-if="auction" class="card">
      <div class="card-body">
        <h5 class="card-title">{{ auction.product.name }}</h5>
        
        <div class="row mb-4">
          <div class="col-md-6">
            <img 
              :src="auction.product.images[0] || 'https://via.placeholder.com/300'" 
              class="img-fluid rounded" 
              :alt="auction.product.name"
              style="max-height: 200px; object-fit: cover;"
            >
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label">Auction Status</label>
              <div class="badge bg-info">Ended</div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Winning Bid</label>
              <div class="h5 text-success">${{ auction.current_highest_bid }}</div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Winning Bidder</label>
              <div>{{ auction.winning_bid.bidder.first_name }} {{ auction.winning_bid.bidder.last_name }}</div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Reserve Price Status</label>
              <div v-if="auction.reserve_price">
                <span v-if="auction.current_highest_bid >= auction.reserve_price" class="text-success">
                  <i class="bi bi-check-circle"></i> Reserve Met
                </span>
                <span v-else class="text-danger">
                  <i class="bi bi-x-circle"></i> Reserve Not Met
                </span>
              </div>
              <div v-else>
                <span class="text-muted">No reserve price set</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="alert alert-warning">
          <h6><i class="bi bi-exclamation-triangle"></i> Important</h6>
          <p>By confirming this sale, you agree to:</p>
          <ul>
            <li>Sell this item to the winning bidder for ${{ auction.current_highest_bid }}</li>
            <li>Package and ship the item according to platform guidelines</li>
            <li>Communicate with the buyer through the platform's messaging system</li>
          </ul>
        </div>
        
        <div class="d-grid gap-2">
          <button 
            class="btn btn-success btn-lg" 
            @click="confirmSale"
            :disabled="confirmingSale || !canConfirmSale"
          >
            <span v-if="confirmingSale" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ confirmingSale ? 'Processing...' : 'Confirm Sale' }}
          </button>
          
          <button class="btn btn-outline-secondary" @click="$router.back()">Cancel</button>
        </div>
        
        <div v-if="saleError" class="alert alert-danger mt-3 mb-0">
          {{ saleError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ConfirmAuctionSaleView',
  props: {
    auctionId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      auction: null,
      loading: false,
      confirmingSale: false,
      saleConfirmed: false,
      error: null,
      saleError: null
    };
  },
  
  computed: {
    canConfirmSale() {
      if (!this.auction) return false;
      
      // Check if auction has ended
      const endTime = new Date(this.auction.end_time);
      const now = new Date();
      if (now < endTime) return false;
      
      // Check if there's a winning bid
      if (!this.auction.current_highest_bid) return false;
      
      // Check if reserve price is met (if set)
      if (this.auction.reserve_price && this.auction.current_highest_bid < this.auction.reserve_price) {
        return false;
      }
      
      return true;
    }
  },
  
  async mounted() {
    await this.fetchAuction();
  },
  
  methods: {
    async fetchAuction() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/api/auctions/${this.auctionId}`);
        this.auction = response.data;
      } catch (err) {
        console.error('Error fetching auction:', err);
        this.error = 'Failed to load auction details. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async confirmSale() {
      if (!this.canConfirmSale) return;
      
      this.confirmingSale = true;
      this.saleError = null;
      
      try {
        const response = await axios.post(`/api/auctions/${this.auctionId}/confirm-sale`);
        this.saleConfirmed = true;
        
        // Show success notification
        alert('Sale confirmed successfully!');
      } catch (err) {
        console.error('Error confirming sale:', err);
        this.saleError = err.response?.data?.error || 'Failed to confirm sale. Please try again.';
      } finally {
        this.confirmingSale = false;
      }
    }
  }
};
</script>

<style scoped>
.form-label {
  font-weight: 500;
}
</style>