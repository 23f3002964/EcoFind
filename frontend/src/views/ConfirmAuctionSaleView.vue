<template>
  <div class="container my-4">
    <!-- Page header with back button -->
    <div class="d-flex align-items-center mb-4">
      <button class="btn btn-outline-secondary me-3" @click="$router.back()">
        <i class="bi bi-arrow-left"></i>
      </button>
      <h4>Confirm Auction Sale</h4>
    </div>

    <!-- Loading State - Shown while fetching auction details -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State - Shown when auction loading fails -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Success State - Shown after successful sale confirmation -->
    <div v-else-if="saleConfirmed" class="alert alert-success">
      <h5>Sale Confirmed Successfully!</h5>
      <p>The auction has been marked as sold and the winning bidder has been notified.</p>
      <button class="btn btn-primary" @click="$router.push('/my-listings')">Back to My Listings</button>
    </div>

    <!-- Confirm Sale Form - Main interface for seller to confirm sale -->
    <div v-else-if="auction" class="card">
      <div class="card-body">
        <!-- Product title -->
        <h5 class="card-title">{{ auction.product.name }}</h5>
        
        <!-- Product information grid -->
        <div class="row mb-4">
          <!-- Product image -->
          <div class="col-md-6">
            <img 
              :src="auction.product.images[0] || 'https://via.placeholder.com/300'" 
              class="img-fluid rounded" 
              :alt="auction.product.name"
              style="max-height: 200px; object-fit: cover;"
            >
          </div>
          <!-- Auction details -->
          <div class="col-md-6">
            <!-- Auction status -->
            <div class="mb-3">
              <label class="form-label">Auction Status</label>
              <div class="badge bg-info">Ended</div>
            </div>
            
            <!-- Winning bid information -->
            <div class="mb-3">
              <label class="form-label">Winning Bid</label>
              <div class="h5 text-success">${{ auction.current_highest_bid }}</div>
            </div>
            
            <!-- Winning bidder information -->
            <div class="mb-3">
              <label class="form-label">Winning Bidder</label>
              <div>{{ auction.winning_bid.bidder.first_name }} {{ auction.winning_bid.bidder.last_name }}</div>
            </div>
            
            <!-- Reserve price status -->
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
        
        <!-- Important information alert -->
        <div class="alert alert-warning">
          <h6><i class="bi bi-exclamation-triangle"></i> Important</h6>
          <p>By confirming this sale, you agree to:</p>
          <ul>
            <li>Sell this item to the winning bidder for ${{ auction.current_highest_bid }}</li>
            <li>Package and ship the item according to platform guidelines</li>
            <li>Communicate with the buyer through the platform's messaging system</li>
          </ul>
        </div>
        
        <!-- Action buttons -->
        <div class="d-grid gap-2">
          <!-- Confirm sale button -->
          <button 
            class="btn btn-success btn-lg" 
            @click="confirmSale"
            :disabled="confirmingSale || !canConfirmSale"
          >
            <span v-if="confirmingSale" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ confirmingSale ? 'Processing...' : 'Confirm Sale' }}
          </button>
          
          <!-- Cancel button -->
          <button class="btn btn-outline-secondary" @click="$router.back()">Cancel</button>
        </div>
        
        <!-- Error message for sale confirmation -->
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
      auction: null,          // Auction details
      loading: false,         // Loading state flag
      confirmingSale: false,   // Sale confirmation operation state
      saleConfirmed: false,    // Sale confirmation success state
      error: null,            // Error message for loading
      saleError: null         // Error message for sale confirmation
    };
  },
  
  computed: {
    // Determine if sale can be confirmed based on various conditions
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
    // Load auction details when component mounts
    await this.fetchAuction();
  },
  
  methods: {
    // Fetch auction details from the API
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
    
    // Confirm the auction sale
    async confirmSale() {
      // Prevent confirmation if conditions aren't met
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
/* Form label styling */
.form-label {
  font-weight: 500;
}
</style>