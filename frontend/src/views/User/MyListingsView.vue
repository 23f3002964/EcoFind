<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>My Listings</h4>
      <button class="btn btn-success" @click="$router.push('/add-product')">
        <i class="bi bi-plus-lg"></i> Add New Product
      </button>
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
    <div v-else-if="products.length === 0" class="text-center py-5">
      <i class="bi bi-tag text-muted" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No listings yet</h5>
      <p class="text-muted">Create your first product listing to get started.</p>
      <button class="btn btn-success" @click="$router.push('/add-product')">
        <i class="bi bi-plus-lg"></i> Add Your First Product
      </button>
    </div>

    <!-- Products List -->
    <div v-else>
      <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        <div v-for="product in products" :key="product.id" class="col">
          <div class="card h-100 product-card">
            <div v-if="product.images && product.images.length > 0" class="card-img-top-wrapper">
              <img 
                :src="product.images[0]" 
                class="card-img-top" 
                :alt="product.title"
                style="height: 200px; object-fit: cover;"
              >
            </div>
            <div v-else class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
              <i class="bi bi-image text-muted" style="font-size: 3rem;"></i>
            </div>
            
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">{{ product.title }}</h5>
              
              <div class="mt-auto">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="text-success mb-0">${{ product.price }}</h6>
                  <span v-if="product.is_auction" class="badge bg-warning">Auction</span>
                  <span v-else-if="product.is_sold" class="badge bg-secondary">Sold</span>
                  <span v-else-if="!product.is_active" class="badge bg-danger">Inactive</span>
                </div>
                
                <!-- Auction Info -->
                <div v-if="product.is_auction" class="mb-2">
                  <div class="d-flex justify-content-between small">
                    <span>Current Bid:</span>
                    <span class="fw-bold">${{ product.current_bid }}</span>
                  </div>
                  <div class="d-flex justify-content-between small">
                    <span>Time Left:</span>
                    <span :class="{ 'text-danger': isAuctionEndingSoon(product) }">
                      {{ auctionTimeRemaining(product) }}
                    </span>
                  </div>
                </div>
                
                <!-- Stats -->
                <div class="d-flex justify-content-between small text-muted mb-3">
                  <span>
                    <i class="bi bi-eye me-1"></i>
                    {{ product.views }}
                  </span>
                  <span>
                    {{ formatDate(product.created_at) }}
                  </span>
                </div>
                
                <!-- Action Buttons -->
                <div class="d-flex gap-2">
                  <button 
                    class="btn btn-sm btn-outline-primary flex-fill" 
                    @click="editProduct(product.id)"
                  >
                    <i class="bi bi-pencil"></i> Edit
                  </button>
                  
                  <button 
                    v-if="product.is_auction && isAuctionEnded(product) && !product.is_sold" 
                    class="btn btn-sm btn-outline-success flex-fill" 
                    @click="confirmAuctionSale(product.id)"
                  >
                    <i class="bi bi-check-circle"></i> Confirm Sale
                  </button>
                  
                  <button 
                    v-else-if="product.is_active && !product.is_sold" 
                    class="btn btn-sm btn-outline-danger flex-fill" 
                    @click="toggleProductStatus(product, false)"
                  >
                    <i class="bi bi-eye-slash"></i> Hide
                  </button>
                  
                  <button 
                    v-else-if="!product.is_active && !product.is_sold" 
                    class="btn btn-sm btn-outline-success flex-fill" 
                    @click="toggleProductStatus(product, true)"
                  >
                    <i class="bi bi-eye"></i> Show
                  </button>
                  
                  <button 
                    v-if="!product.is_sold" 
                    class="btn btn-sm btn-outline-secondary flex-fill" 
                    @click="deleteProduct(product.id)"
                  >
                    <i class="bi bi-trash"></i> Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <nav aria-label="Product pagination" class="mt-4">
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
export default {
  name: 'MyListingsView',
  data() {
    return {
      loading: true,
      error: '',
      products: [],
      currentPage: 1,
      totalPages: 1,
      totalProducts: 0
    };
  },
  async mounted() {
    await this.loadProducts();
  },
  methods: {
    async loadProducts() {
      this.loading = true;
      this.error = '';
      
      try {
        const params = new URLSearchParams();
        params.append('page', this.currentPage);
        params.append('per_page', 12);
        
        const response = await fetch(`${this.$store.state.backendUrl}/api/my-products?${params.toString()}`, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.products = data.products;
          this.totalPages = data.pages;
          this.totalProducts = data.total;
        } else {
          this.error = 'Failed to load your products';
        }
      } catch (error) {
        console.error('Error loading products:', error);
        this.error = 'Network error. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    auctionTimeRemaining(product) {
      if (!product.auction_end_time) return '';
      
      const endTime = new Date(product.auction_end_time);
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
    
    isAuctionEndingSoon(product) {
      if (!product.auction_end_time) return false;
      
      const endTime = new Date(product.auction_end_time);
      const now = new Date();
      const diff = endTime - now;
      
      // Less than 24 hours remaining
      return diff > 0 && diff < (24 * 60 * 60 * 1000);
    },
    
    isAuctionEnded(product) {
      if (!product.auction_end_time) return false;
      
      const endTime = new Date(product.auction_end_time);
      const now = new Date();
      return now > endTime;
    },
    
    editProduct(productId) {
      // Redirect to the edit product page
      this.$router.push(`/edit-product/${productId}`);
    },
    
    confirmAuctionSale(auctionId) {
      // Redirect to the confirm auction sale page
      this.$router.push(`/confirm-auction-sale/${auctionId}`);
    },
    
    async toggleProductStatus(product, isActive) {
      if (!confirm(`Are you sure you want to ${isActive ? 'activate' : 'deactivate'} this product?`)) {
        return;
      }
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/products/${product.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.$store.state.authData?.token
          },
          body: JSON.stringify({ is_active: isActive })
        });
        
        if (response.ok) {
          // Update the product in the list
          product.is_active = isActive;
          // Show success message
          alert(`Product ${isActive ? 'activated' : 'deactivated'} successfully!`);
        } else {
          const error = await response.json();
          alert(error.error || `Failed to ${isActive ? 'activate' : 'deactivate'} product`);
        }
      } catch (error) {
        console.error('Error toggling product status:', error);
        alert('Network error. Please try again.');
      }
    },
    
    async deleteProduct(productId) {
      if (!confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
        return;
      }
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/products/${productId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        if (response.ok) {
          // Remove the product from the list
          this.products = this.products.filter(p => p.id !== productId);
          // Show success message
          alert('Product deleted successfully!');
        } else {
          const error = await response.json();
          alert(error.error || 'Failed to delete product');
        }
      } catch (error) {
        console.error('Error deleting product:', error);
        alert('Network error. Please try again.');
      }
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page;
        this.loadProducts();
      }
    }
  }
};
</script>

<style scoped>
.product-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.card-img-top-wrapper {
  overflow: hidden;
}

.card-img-top {
  transition: transform 0.3s;
}

.product-card:hover .card-img-top {
  transform: scale(1.05);
}
</style>