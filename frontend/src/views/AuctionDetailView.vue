<template>
  <div class="container my-4">
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

    <!-- Auction Detail -->
    <div v-else-if="auction" class="row">
      <!-- Left Column - Images -->
      <div class="col-lg-6 mb-4">
        <div class="card">
          <div class="card-body">
            <!-- Main Image -->
            <div class="text-center mb-3">
              <img 
                :src="currentImage" 
                class="img-fluid rounded" 
                alt="Product image"
                style="max-height: 400px; object-fit: cover;"
              >
            </div>
            
            <!-- Thumbnail Images -->
            <div class="d-flex overflow-auto gap-2">
              <img 
                v-for="(image, index) in auction.product.images" 
                :key="index"
                :src="image" 
                class="img-thumbnail" 
                alt="Product thumbnail"
                style="width: 80px; height: 80px; object-fit: cover; cursor: pointer;"
                @click="currentImage = image"
              >
            </div>
          </div>
        </div>
      </div>
      
      <!-- Right Column - Details -->
      <div class="col-lg-6">
        <div class="card">
          <div class="card-body">
            <h3 class="card-title">{{ auction.product.name }}</h3>
            <p class="text-muted">{{ auction.product.category }}</p>
            
            <div class="mb-3">
              <p class="card-text">{{ auction.product.description }}</p>
            </div>
            
            <div class="border-top pt-3 mt-3">
              <h5>Auction Details</h5>
              
              <div class="row mb-2">
                <div class="col-sm-4 text-muted">Starting Price</div>
                <div class="col-sm-8">${{ auction.starting_price }}</div>
              </div>
              
              <div class="row mb-2">
                <div class="col-sm-4 text-muted">Minimum Bid</div>
                <div class="col-sm-8">${{ auction.minimum_bid }}</div>
              </div>
              
              <div class="row mb-2">
                <div class="col-sm-4 text-muted">Reserve Price</div>
                <div class="col-sm-8">{{ auction.reserve_price ? `$${auction.reserve_price}` : 'Not set' }}</div>
              </div>
              
              <div class="row mb-2">
                <div class="col-sm-4 text-muted">Current Highest Bid</div>
                <div class="col-sm-8">
                  <strong v-if="auction.current_highest_bid">${{ auction.current_highest_bid }}</strong>
                  <span v-else>No bids yet</span>
                </div>
              </div>
              
              <div class="row mb-2">
                <div class="col-sm-4 text-muted">Number of Bids</div>
                <div class="col-sm-8">{{ auction.bid_count }}</div>
              </div>
              
              <div class="row mb-2">
                <div class="col-sm-4 text-muted">Time Remaining</div>
                <div class="col-sm-8">
                  <span :class="getTimeRemainingClass()">{{ timeRemaining }}</span>
                </div>
              </div>
            </div>
            
            <div class="border-top pt-3 mt-3">
              <h5>Seller Information</h5>
              
              <div class="d-flex align-items-center mb-3">
                <img 
                  :src="auction.seller.profile_picture || 'https://via.placeholder.com/50'" 
                  class="rounded-circle me-3" 
                  alt="Seller"
                  width="50"
                  height="50"
                >
                <div>
                  <div>{{ auction.seller.first_name }} {{ auction.seller.last_name }}</div>
                  <div class="text-muted">Rating: {{ auction.seller.rating }}/5</div>
                </div>
              </div>
            </div>
            
            <!-- Bid Form -->
            <div class="border-top pt-3 mt-3" v-if="isAuctionActive">
              <h5>Place a Bid</h5>
              
              <div class="mb-3">
                <label for="bidAmount" class="form-label">Bid Amount ($)</label>
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="bidAmount"
                    v-model="bidAmount"
                    :min="minimumNextBid"
                    step="0.01"
                    :placeholder="`Minimum bid: $${minimumNextBid}`"
                  >
                </div>
                <div class="form-text">
                  Next minimum bid: ${{ minimumNextBid }}
                </div>
              </div>
              
              <button 
                class="btn btn-success w-100" 
                @click="placeBid"
                :disabled="!isValidBid || placingBid"
              >
                <span v-if="!placingBid">Place Bid</span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm" role="status"></span>
                  Placing Bid...
                </span>
              </button>
              
              <div v-if="bidError" class="alert alert-danger mt-2 mb-0">
                {{ bidError }}
              </div>
            </div>
            
            <!-- Auction Ended Message -->
            <div class="border-top pt-3 mt-3" v-else>
              <div class="alert alert-info">
                <strong>This auction has ended.</strong>
                <div v-if="auction.winning_bid">
                  Winning bid: ${{ auction.winning_bid.amount }} by {{ auction.winning_bid.bidder.first_name }}
                </div>
                <div v-else>
                  No winning bid.
                </div>
              </div>
            </div>
            
            <!-- Watch Auction Button -->
            <div class="mt-3">
              <button 
                class="btn" 
                :class="isWatching ? 'btn-danger' : 'btn-outline-primary'"
                @click="toggleWatchAuction"
                :disabled="togglingWatch"
              >
                <span v-if="!togglingWatch">
                  <i class="bi" :class="isWatching ? 'bi-eye-slash' : 'bi-eye'"></i>
                  {{ isWatching ? 'Unwatch Auction' : 'Watch Auction' }}
                </span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm" role="status"></span>
                </span>
              </button>
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
  name: 'AuctionDetailView',
  props: {
    auctionId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      auction: null,
      currentImage: '',
      bidAmount: '',
      loading: false,
      placingBid: false,
      togglingWatch: false,
      error: null,
      bidError: null,
      timeRemainingInterval: null
    };
  },
  
  computed: {
    minimumNextBid() {
      if (!this.auction) return 0;
      // Minimum next bid is current highest bid + minimum increment
      const increment = 1.00; // Could be dynamic based on auction rules
      return this.auction.current_highest_bid ? 
        (parseFloat(this.auction.current_highest_bid) + increment).toFixed(2) : 
        parseFloat(this.auction.minimum_bid).toFixed(2);
    },
    
    isValidBid() {
      if (!this.bidAmount) return false;
      return parseFloat(this.bidAmount) >= parseFloat(this.minimumNextBid);
    },
    
    isWatching() {
      // In a real app, this would check if the current user is watching the auction
      return false;
    },
    
    isAuctionActive() {
      return this.auction && this.auction.status === 'active';
    },
    
    timeRemaining() {
      if (!this.auction) return '';
      
      const endTime = new Date(this.auction.end_time);
      const now = new Date();
      const diff = endTime - now;
      
      if (diff <= 0) {
        return 'Ended';
      }
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      
      if (days > 0) {
        return `${days}d ${hours}h`;
      } else if (hours > 0) {
        return `${hours}h ${minutes}m`;
      } else {
        return `${minutes}m`;
      }
    }
  },
  
  mounted() {
    this.fetchAuction();
    // Update time remaining every minute
    this.timeRemainingInterval = setInterval(() => {
      this.$forceUpdate();
    }, 60000);
  },
  
  beforeUnmount() {
    if (this.timeRemainingInterval) {
      clearInterval(this.timeRemainingInterval);
    }
  },
  
  methods: {
    async fetchAuction() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/api/auctions/${this.auctionId}`);
        this.auction = response.data;
        this.currentImage = this.auction.product.images[0] || 'https://via.placeholder.com/400';
      } catch (err) {
        console.error('Error fetching auction:', err);
        this.error = 'Failed to load auction details. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    getTimeRemainingClass() {
      if (!this.auction) return '';
      
      const endTime = new Date(this.auction.end_time);
      const now = new Date();
      const diff = endTime - now;
      const hours = diff / (1000 * 60 * 60);
      
      if (hours < 1) {
        return 'text-danger fw-bold';
      } else if (hours < 24) {
        return 'text-warning';
      } else {
        return 'text-success';
      }
    },
    
    async placeBid() {
      if (!this.isValidBid) return;
      
      this.placingBid = true;
      this.bidError = null;
      
      try {
        const response = await axios.post(`/api/auctions/${this.auctionId}/bids`, {
          amount: parseFloat(this.bidAmount)
        });
        
        // Update auction with new bid information
        this.auction.current_highest_bid = response.data.amount;
        this.auction.bid_count = response.data.bid_count;
        this.bidAmount = '';
        
        // Show success message
        alert('Bid placed successfully!');
      } catch (err) {
        console.error('Error placing bid:', err);
        this.bidError = err.response?.data?.error || 'Failed to place bid. Please try again.';
      } finally {
        this.placingBid = false;
      }
    },
    
    async toggleWatchAuction() {
      this.togglingWatch = true;
      
      try {
        if (this.isWatching) {
          await axios.delete(`/api/auctions/${this.auctionId}/watch`);
        } else {
          await axios.post(`/api/auctions/${this.auctionId}/watch`);
        }
        
        // Refresh auction data
        await this.fetchAuction();
      } catch (err) {
        console.error('Error toggling watch:', err);
        alert('Failed to update watch status. Please try again.');
      } finally {
        this.togglingWatch = false;
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.img-thumbnail {
  cursor: pointer;
  transition: border-color 0.2s;
}

.img-thumbnail:hover {
  border-color: #0d6efd;
}
</style>