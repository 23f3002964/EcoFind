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

    <!-- Product Detail -->
    <div v-else-if="product" class="row">
      <!-- Left Column - Images -->
      <div class="col-lg-6 mb-4">
        <div class="card">
          <div class="card-body">
            <!-- Main Image -->
            <div class="text-center mb-3">
              <img 
                :src="currentImage" 
                class="img-fluid rounded" 
                :alt="product.title"
                style="max-height: 400px; object-fit: contain;"
              >
            </div>

            <!-- Thumbnail Images -->
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

            <div v-else-if="(!product.images || product.images.length === 0)" class="text-center py-5">
              <i class="bi bi-image text-muted" style="font-size: 5rem;"></i>
              <p class="text-muted mt-2">No images available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Details -->
      <div class="col-lg-6">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h4 class="card-title">{{ product.title }}</h4>
                <div class="d-flex align-items-center mb-2">
                  <span class="h5 text-success me-3">${{ product.price }}</span>
                  <span v-if="product.is_auction" class="badge bg-warning">Auction</span>
                </div>
              </div>
              <button class="btn btn-outline-secondary" @click="$router.back()">
                <i class="bi bi-arrow-left"></i>
              </button>
            </div>

            <!-- Category -->
            <div class="mb-3">
              <small class="text-muted">Category:</small>
              <div>{{ product.category.name }}</div>
            </div>

            <!-- Condition -->
            <div class="mb-3">
              <small class="text-muted">Condition:</small>
              <div>{{ product.condition }}</div>
            </div>

            <!-- Seller Info -->
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

            <!-- Description -->
            <div class="mb-4">
              <h6>Description</h6>
              <p>{{ product.description }}</p>
            </div>

            <!-- Additional Details -->
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
            </div>

            <!-- Auction Specific Info -->
            <div v-if="product.is_auction" class="border rounded p-3 mb-4">
              <h6>Auction Details</h6>
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
                  <div>${{ product.reserve_price || 'Not set' }}</div>
                </div>
                <div class="col-md-6 mb-2">
                  <small class="text-muted">Time Remaining:</small>
                  <div :class="{ 'text-danger': isAuctionEndingSoon }">
                    {{ auctionTimeRemaining }}
                  </div>
                </div>
              </div>

              <!-- Place Bid Form -->
              <div class="mt-3">
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="bidAmount" 
                    :min="product.current_bid + 1"
                    step="1"
                    placeholder="Enter your bid"
                  >
                  <button 
                    class="btn btn-primary" 
                    type="button" 
                    @click="placeBid"
                    :disabled="placingBid"
                  >
                    <span v-if="placingBid" class="spinner-border spinner-border-sm me-1"></span>
                    Place Bid
                  </button>
                </div>
                <div v-if="bidError" class="text-danger small mt-1">{{ bidError }}</div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-grid gap-2">
              <button 
                v-if="!product.is_auction && !product.is_sold && product.seller.id !== currentUser.id"
                class="btn btn-success btn-lg" 
                @click="addToCart"
                :disabled="addingToCart"
              >
                <span v-if="addingToCart" class="spinner-border spinner-border-sm me-2"></span>
                <i class="bi bi-cart me-2"></i>
                {{ addingToCart ? 'Adding...' : 'Add to Cart' }}
              </button>

              <button 
                v-if="product.seller.id !== currentUser.id"
                class="btn btn-outline-primary btn-lg" 
                @click="contactSeller"
              >
                <i class="bi bi-chat-dots me-2"></i>
                Chat with Seller
              </button>

              <button 
                v-if="product.seller.id === currentUser.id"
                class="btn btn-outline-secondary btn-lg" 
                @click="editProduct"
              >
                <i class="bi bi-pencil me-2"></i>
                Edit Product
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
    currentUser() {
      return this.authData ? { id: this.authData.id } : null;
    },
    currentImage() {
      if (!this.product || !this.product.images || this.product.images.length === 0) {
        return ''; // Will show placeholder
      }
      return this.product.images[this.currentImageIndex] || this.product.images[0];
    },
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
        return `${days} day${days !== 1 ? 's' : ''} ${hours} hour${hours !== 1 ? 's' : ''}`;
      } else if (hours > 0) {
        return `${hours} hour${hours !== 1 ? 's' : ''} ${minutes} minute${minutes !== 1 ? 's' : ''}`;
      } else {
        return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
      }
    },
    isAuctionEndingSoon() {
      if (!this.product || !this.product.auction_end_time) return false;
      
      const endTime = new Date(this.product.auction_end_time);
      const now = new Date();
      const diff = endTime - now;
      
      // Less than 24 hours remaining
      return diff > 0 && diff < (24 * 60 * 60 * 1000);
    }
  },
  async mounted() {
    const productId = this.$route.params.id;
    if (productId) {
      await this.loadProduct(productId);
    } else {
      this.error = 'Product not found';
      this.loading = false;
    }
  },
  methods: {
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
    
    async placeBid() {
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
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
            'Authorization': this.authData.token
          },
          body: JSON.stringify({ amount: parseFloat(this.bidAmount) })
        });
        
        if (response.ok) {
          // Update the current bid in the UI
          this.product.current_bid = parseFloat(this.bidAmount);
          this.bidAmount = '';
          // Reload product to get updated info
          await this.loadProduct(this.product.id);
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
    
    async addToCart() {
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
            'Authorization': this.authData.token
          },
          body: JSON.stringify({ product_id: this.product.id })
        });
        
        if (response.ok) {
          // Show success message or redirect to cart
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
    
    contactSeller() {
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      // For now, we'll just show an alert. In a full implementation, this would open a chat
      alert('Contact seller functionality would open a chat window here.');
    },
    
    editProduct() {
      this.$router.push(`/edit-product/${this.product.id}`);
    }
  }
};
</script>

<style scoped>
.img-thumbnail {
  transition: border-color 0.2s;
}

.img-thumbnail:hover {
  border-color: #0d6efd;
}
</style>