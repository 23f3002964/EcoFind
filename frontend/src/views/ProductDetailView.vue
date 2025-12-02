<template>
  <div class="container my-4">
    <!-- Loading State - Shown while fetching product details -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State - Shown when product loading fails -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Product Detail - Main content area -->
    <div v-else-if="product" class="row">
      <!-- Left Column - Product Images Gallery -->
      <div class="col-lg-6 mb-4">
        <div class="card">
          <div class="card-body">
            <!-- Main Product Image -->
            <div class="text-center mb-3">
              <img 
                :src="currentImage" 
                class="img-fluid rounded" 
                :alt="product.title"
                style="max-height: 400px; object-fit: contain;"
              >
            </div>

            <!-- Thumbnail Images - Click to change main image -->
            <div v-if="product.images && product.images.length > 1" class="d-flex flex-wrap justify-content-center gap-2">
              <img 
                v-for="(image, index) in product.images" 
                :key="index"
                :src="image" 
                class="img-thumbnail" 
                :alt="`${product.title} ${index + 1}`"
                style="width: 80px; height: 80px; object-fit: cover; cursor: pointer;"
                @click="currentImageIndex = index"
                :class="{ 'border-primary': currentImageIndex === index }"
              >
            </div>

            <!-- No Images Placeholder -->
            <div v-else-if="(!product.images || product.images.length === 0)" class="text-center py-5">
              <i class="bi bi-image text-muted" style="font-size: 5rem;"></i>
              <p class="text-muted mt-2">No images available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Product Details and Actions -->
      <div class="col-lg-6">
        <div class="card">
          <div class="card-body">
            <!-- Product Header - Title, Price, Back Button -->
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h4 class="card-title">{{ product.title }}</h4>
                <div class="d-flex align-items-center mb-2">
                  <span class="h5 text-success me-3">${{ product.price }}</span>
                  <span v-if="product.is_auction" class="badge bg-warning">Auction</span>
                </div>
              </div>
              <!-- Back button to return to product list -->
              <button class="btn btn-outline-secondary" @click="$router.back()">
                <i class="bi bi-arrow-left"></i>
              </button>
            </div>

            <!-- Category Information -->
            <div class="mb-3">
              <small class="text-muted">Category:</small>
              <div>{{ product.category.name }}</div>
            </div>

            <!-- Condition Information -->
            <div class="mb-3">
              <small class="text-muted">Condition:</small>
              <div>{{ product.condition }}</div>
            </div>

            <!-- Seller Information Panel -->
            <div class="mb-3 p-3 bg-light rounded">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>Seller:</strong> {{ product.seller.first_name }} {{ product.seller.last_name }}
                </div>
                <div>
                  <i class="bi bi-star-fill text-warning"></i>
                  {{ product.seller.rating ? product.seller.rating.toFixed(1) : 'N/A' }}
                  ({{ product.seller.total_reviews }} reviews)
                </div>
              </div>
            </div>

            <!-- Product Description -->
            <div class="mb-4">
              <h6>Description</h6>
              <p>{{ product.description }}</p>
            </div>

            <!-- Additional Product Details Grid -->
            <div class="row mb-4">
              <div class="col-md-6 mb-3">
                <small class="text-muted">Brand:</small>
                <div>{{ product.brand || 'Not specified' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <small class="text-muted">Model:</small>
                <div>{{ product.model || 'Not specified' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <small class="text-muted">Material:</small>
                <div>{{ product.material || 'Not specified' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <small class="text-muted">Location:</small>
                <div>{{ product.location || 'Not specified' }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <small class="text-muted">Views:</small>
                <div>{{ product.views }}</div>
              </div>
              <div class="col-md-6 mb-3">
                <small class="text-muted">Posted:</small>
                <div>{{ formatDate(product.created_at) }}</div>
              </div>
            </div>

            <!-- Auction Specific Section - Only shown for auction items -->
            <div v-if="product.is_auction" class="border rounded p-3 mb-4">
              <h6>Auction Details</h6>
              <!-- Auction Information Grid -->
              <div class="row">
                <div class="col-md-6 mb-2">
                  <small class="text-muted">Current Bid:</small>
                  <div class="h5 text-success">${{ product.current_bid }}</div>
                </div>
                <div class="col-md-6 mb-2">
                  <small class="text-muted">Minimum Bid:</small>
                  <div>${{ product.minimum_bid }}</div>
                </div>
                <div class="col-md-6 mb-2">
                  <small class="text-muted">Reserve Price:</small>
                  <div>{{ product.reserve_price ? `$${product.reserve_price}` : 'Not set' }}</div>
                </div>
                <div class="col-md-6 mb-2">
                  <small class="text-muted">Time Remaining:</small>
                  <div :class="getTimeRemainingClass()">{{ auctionTimeRemaining }}</div>
                </div>
              </div>
              
              <!-- Bid Placement Form - Only for non-sellers and active auctions -->
              <div v-if="product.seller.id !== currentUser?.id && !isAuctionEnded" class="mt-3">
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="bidAmount"
                    :min="product.current_bid + 1"
                    placeholder="Enter your bid"
                  >
                  <!-- Place Bid Button -->
                  <button 
                    type="button" 
                    class="btn btn-success" 
                    @click="placeBid"
                    :disabled="placingBid"
                  >
                    <span v-if="placingBid" class="spinner-border spinner-border-sm me-1"></span>
                    Place Bid
                  </button>
                </div>
                <!-- Bid Error Messages -->
                <div v-if="bidError" class="text-danger small mt-1">{{ bidError }}</div>
              </div>
              
              <!-- Auction Ended Message - Shown when auction has finished -->
              <div v-if="isAuctionEnded" class="alert alert-info mt-3 mb-0">
                <strong>This auction has ended.</strong>
                <div v-if="product.current_bid > 0">
                  Winning bid: ${{ product.current_bid }}
                </div>
              </div>
            </div>

            <!-- Action Buttons Section -->
            <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
              <!-- Contact Seller Button (visible to all except seller) -->
              <button 
                v-if="product.seller.id !== currentUser?.id" 
                class="btn btn-primary btn-lg me-md-2"
                @click="contactSeller"
              >
                <i class="bi bi-chat-dots"></i> Chat with Seller
              </button>
              
              <!-- Add to Cart Button (for non-auction items) -->
              <button 
                v-if="!product.is_auction && product.seller.id !== currentUser?.id && !product.is_sold" 
                class="btn btn-success btn-lg me-md-2" 
                @click="addToCart"
                :disabled="addingToCart"
              >
                <span v-if="!addingToCart">
                  <i class="bi bi-cart-plus"></i> Add to Cart
                </span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm" role="status"></span>
                  Adding...
                </span>
              </button>
              
              <!-- Create Price Alert Button (for non-auction items) -->
              <button 
                v-if="!product.is_auction && product.seller.id !== currentUser?.id && $store.state.isAuthenticated" 
                class="btn btn-warning btn-lg"
                @click="createPriceAlert"
              >
                <i class="bi bi-bell"></i> Create Price Alert
              </button>
              
              <!-- Edit Product Button (visible only to seller) -->
              <button 
                v-if="product.seller.id === currentUser?.id" 
                class="btn btn-outline-primary btn-lg me-md-2"
                @click="editProduct"
              >
                <i class="bi bi-pencil-square"></i> Edit Product
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'ProductDetailView',
  data() {
    return {
      loading: true,
      error: '',
      product: null,
      currentImageIndex: 0,
      bidAmount: '',
      placingBid: false,
      bidError: '',
      addingToCart: false
    };
  },
  computed: {
    ...mapState(['isAuthenticated', 'authData']),
    // Current user information from store
    currentUser() {
      return this.authData ? { id: this.authData.id } : null;
    },
    // Current image to display in main viewer
    currentImage() {
      if (!this.product || !this.product.images || this.product.images.length === 0) {
        return ''; // Will show placeholder
      }
      return this.product.images[this.currentImageIndex] || this.product.images[0];
    },
    // Calculate and format time remaining for auctions
    auctionTimeRemaining() {
      if (!this.product || !this.product.auction_end_time) return '';
      
      const endTime = new Date(this.product.auction_end_time);
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
    },
    // Check if auction has ended
    isAuctionEnded() {
      if (!this.product || !this.product.auction_end_time) return false;
      
      const endTime = new Date(this.product.auction_end_time);
      const now = new Date();
      return now > endTime;
    }
  },
  async mounted() {
    // Load product when component mounts
    const productId = this.$route.params.id;
    if (productId) {
      await this.loadProduct(productId);
    } else {
      this.error = 'Product not found';
      this.loading = false;
    }
  },
  methods: {
    // Fetch product details from API
    async loadProduct(productId) {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/products/${productId}`);
        
        if (response.ok) {
          const data = await response.json();
          this.product = data;
        } else {
          this.error = 'Product not found';
        }
      } catch (error) {
        console.error('Error loading product:', error);
        this.error = 'Failed to load product details';
      } finally {
        this.loading = false;
      }
    },
    
    // Get CSS class for time remaining based on urgency
    getTimeRemainingClass() {
      if (!this.product || !this.product.auction_end_time) return '';
      
      const endTime = new Date(this.product.auction_end_time);
      const now = new Date();
      const diff = endTime - now;
      const hours = diff / (1000 * 60 * 60);
      
      if (hours < 1) {
        return 'text-danger fw-bold'; // Critical - less than 1 hour
      } else if (hours < 24) {
        return 'text-warning'; // Warning - less than 24 hours
      } else {
        return 'text-success'; // Safe - more than 24 hours
      }
    },
    
    // Place a bid on an auction item
    async placeBid() {
      // Require authentication to place bids
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      // Validate bid amount
      if (!this.bidAmount || this.bidAmount <= this.product.current_bid) {
        this.bidError = `Bid must be higher than $${this.product.current_bid}`;
        return;
      }
      
      this.placingBid = true;
      this.bidError = '';
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/products/${this.product.id}/bid`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.authData?.token
          },
          body: JSON.stringify({ amount: parseFloat(this.bidAmount) })
        });
        
        if (response.ok) {
          const result = await response.json();
          // Update product with new bid information
          this.product.current_bid = parseFloat(this.bidAmount);
          this.bidAmount = '';
          alert('Bid placed successfully!');
        } else {
          const error = await response.json();
          this.bidError = error.error || 'Failed to place bid';
        }
      } catch (error) {
        console.error('Error placing bid:', error);
        this.bidError = 'Network error. Please try again.';
      } finally {
        this.placingBid = false;
      }
    },
    
    // Add product to user's cart
    async addToCart() {
      // Require authentication to add to cart
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      this.addingToCart = true;
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/cart`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.authData?.token
          },
          body: JSON.stringify({ product_id: this.product.id })
        });
        
        if (response.ok) {
          // Show success message
          alert('Product added to cart!');
        } else {
          const error = await response.json();
          alert(error.error || 'Failed to add product to cart');
        }
      } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Network error. Please try again.');
      } finally {
        this.addingToCart = false;
      }
    },
    
    // Initiate chat with seller
    async contactSeller() {
      // Require authentication to contact seller
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      try {
        // Create or get existing chat with seller
        const response = await fetch(`${this.$store.state.backendUrl}/api/chats`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.authData?.token
          },
          body: JSON.stringify({
            receiver_id: this.product.seller.id,
            product_id: this.product.id,
            message: `Hi, I'm interested in your product "${this.product.title}".`
          })
        });
        
        if (response.ok) {
          // Open chat view
          this.$router.push(`/chat/${this.product.seller.id}?product_id=${this.product.id}`);
        } else {
          const error = await response.json();
          alert(error.error || 'Failed to initiate chat');
        }
      } catch (error) {
        console.error('Error initiating chat:', error);
        alert('Network error. Please try again.');
      }
    },
    
    // Create a price alert for this product
    async createPriceAlert() {
      // Require authentication to create price alerts
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      // Prompt user for target price
      const targetPrice = prompt(`Enter your target price for "${this.product.title}":`, this.product.price);
      if (!targetPrice || isNaN(targetPrice) || parseFloat(targetPrice) <= 0) {
        alert('Please enter a valid target price.');
        return;
      }
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/price-alerts`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.authData?.token
          },
          body: JSON.stringify({
            product_id: this.product.id,
            target_price: parseFloat(targetPrice)
          })
        });
        
        if (response.ok) {
          const result = await response.json();
          alert('Price alert created successfully! You will be notified when the price drops to your target.');
        } else {
          const error = await response.json();
          alert(error.error || 'Failed to create price alert');
        }
      } catch (error) {
        console.error('Error creating price alert:', error);
        alert('Network error. Please try again.');
      }
    },
    
    // Navigate to edit product page
    editProduct() {
      this.$router.push(`/edit-product/${this.product.id}`);
    },
    
    // Format date for display
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
  }
};
</script>

<style scoped>
/* Thumbnail image hover effect */
.img-thumbnail {
  transition: border-color 0.2s;
}

.img-thumbnail:hover {
  border-color: #0d6efd;
}
</style>