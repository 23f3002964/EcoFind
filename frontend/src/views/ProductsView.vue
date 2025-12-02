<template>
  <div class="container my-4">
    <!-- Page header with title and add product button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Product Feed</h4>
      <div v-if="$store.state.isAuthenticated">
        <button class="btn btn-success" @click="$router.push('/add-product')">
          <i class="bi bi-plus-lg"></i> Add Product
        </button>
      </div>
    </div>

    <!-- Personalized Recommendations Section - Shows recommended products for authenticated users -->
    <div v-if="$store.state.isAuthenticated && recommendations.length > 0" class="mb-4">
      <h5>Recommended for You</h5>
      <div class="row row-cols-1 row-cols-md-4 g-3">
        <div v-for="product in recommendations.slice(0, 4)" :key="product.id" class="col">
          <div class="card h-100 product-card" @click="viewProduct(product.id)">
            <div v-if="product.images && product.images.length > 0" class="card-img-top-wrapper">
              <img 
                :src="product.images[0]" 
                class="card-img-top" 
                :alt="product.title"
                style="height: 150px; object-fit: cover;"
              >
            </div>
            <div v-else class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 150px;">
              <i class="bi bi-image text-muted" style="font-size: 2rem;"></i>
            </div>
            
            <div class="card-body p-2">
              <h6 class="card-title mb-1">{{ product.title }}</h6>
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-success fw-bold">${{ product.price }}</span>
                <span v-if="product.is_auction" class="badge bg-warning">Auction</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters Section - Advanced filtering options for products -->
    <div class="card mb-4">
      <div class="card-body">
        <!-- Main filters row: search, category, condition, sort, reset -->
        <div class="row g-3">
          <div class="col-md-4">
            <!-- Search input with enter key support -->
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search products..." 
              v-model="searchQuery"
              @keyup.enter="searchProducts"
            >
          </div>
          <div class="col-md-2">
            <!-- Category filter dropdown -->
            <select class="form-select" v-model="selectedCategory" @change="filterProducts">
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <!-- Condition filter dropdown -->
            <select class="form-select" v-model="conditionFilter" @change="filterProducts">
              <option value="">All Conditions</option>
              <option value="New">New</option>
              <option value="Like New">Like New</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
              <option value="Used">Used</option>
            </select>
          </div>
          <div class="col-md-2">
            <!-- Sort order dropdown -->
            <select class="form-select" v-model="sortBy" @change="sortProducts">
              <option value="created_at">Newest</option>
              <option value="price">Price Low to High</option>
              <option value="price_desc">Price High to Low</option>
              <option value="views">Most Popular</option>
            </select>
          </div>
          <div class="col-md-2">
            <!-- Reset all filters button -->
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-circle"></i> Reset
            </button>
          </div>
        </div>
        
        <!-- Additional filters row: price range and auction type -->
        <div class="row g-3 mt-2">
          <div class="col-md-3">
            <!-- Minimum price filter -->
            <label class="form-label">Min Price</label>
            <input 
              type="number" 
              class="form-control" 
              placeholder="0" 
              v-model="minPrice"
              @change="filterProducts"
            >
          </div>
          <div class="col-md-3">
            <!-- Maximum price filter -->
            <label class="form-label">Max Price</label>
            <input 
              type="number" 
              class="form-control" 
              placeholder="Any" 
              v-model="maxPrice"
              @change="filterProducts"
            >
          </div>
          <div class="col-md-3">
            <!-- Auction type filter -->
            <label class="form-label">Auction Items</label>
            <select class="form-select" v-model="auctionFilter" @change="filterProducts">
              <option value="">All Items</option>
              <option value="true">Auction Only</option>
              <option value="false">Fixed Price Only</option>
            </select>
          </div>
          <div class="col-md-3">
            <!-- Location filter -->
            <label class="form-label">Location</label>
            <input 
              type="text" 
              class="form-control" 
              placeholder="City or State" 
              v-model="locationFilter"
              @change="filterProducts"
            >
          </div>
        </div>
        
        <!-- Saved Searches Section -->
        <div v-if="$store.state.isAuthenticated" class="mt-3 pt-3 border-top">
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Saved Searches</h6>
            <button class="btn btn-sm btn-outline-primary" @click="saveCurrentSearch">
              <i class="bi bi-bookmark"></i> Save This Search
            </button>
          </div>
          <div class="d-flex flex-wrap gap-2 mt-2">
            <button 
              v-for="savedSearch in savedSearches" 
              :key="savedSearch.id"
              class="btn btn-sm btn-outline-secondary"
              @click="applySavedSearch(savedSearch)"
            >
              {{ savedSearch.name }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State - Shown while fetching products -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Product Grid - Displays products in a responsive grid -->
    <div v-else>
      <div class="row row-cols-1 row-cols-md-3 g-4">
        <div v-for="product in products" :key="product.id" class="col">
          <div class="card h-100 product-card" @click="viewProduct(product.id)">
            <!-- Product image with fallback placeholder -->
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
              <!-- Product title and description preview -->
              <h5 class="card-title">{{ product.title }}</h5>
              <p class="card-text flex-grow-1">{{ product.description.substring(0, 100) }}{{ product.description.length > 100 ? '...' : '' }}</p>
              
              <div class="mt-auto">
                <!-- Price and auction badge -->
                <div class="d-flex justify-content-between align-items-center">
                  <h6 class="text-success mb-0">${{ product.price }}</h6>
                  <span v-if="product.is_auction" class="badge bg-warning">Auction</span>
                </div>
                
                <!-- Seller info and rating -->
                <div class="d-flex justify-content-between align-items-center mt-2">
                  <small class="text-muted">{{ product.seller }}</small>
                  <small class="text-muted">
                    <i class="bi bi-star-fill text-warning"></i>
                    {{ product.seller_rating ? product.seller_rating.toFixed(1) : 'N/A' }}
                  </small>
                </div>
                
                <!-- Auction-specific info (current bid and time remaining) -->
                <div v-if="product.is_auction" class="mt-2">
                  <div class="d-flex justify-content-between small">
                    <span>Current Bid:</span>
                    <span class="fw-bold">${{ product.current_bid }}</span>
                  </div>
                  <div class="d-flex justify-content-between small">
                    <span>Ends:</span>
                    <span>{{ formatAuctionEndTime(product.auction_end_time) }}</span>
                  </div>
                </div>
                
                <!-- Location info -->
                <div v-if="product.location" class="mt-2">
                  <small class="text-muted">
                    <i class="bi bi-geo-alt"></i> {{ product.location }}
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State - Shown when no products match the filters -->
      <div v-if="products.length === 0" class="text-center py-5">
        <i class="bi bi-search text-muted" style="font-size: 3rem;"></i>
        <h5 class="mt-3">No products found</h5>
        <p class="text-muted">Try adjusting your search or filter criteria</p>
        <button class="btn btn-outline-primary" @click="resetFilters">Reset Filters</button>
      </div>

      <!-- Pagination Controls - Navigate between product pages -->
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
import { mapState } from 'vuex';

export default {
  name: 'ProductsView',
  data() {
    return {
      loading: true,
      products: [],
      categories: [],
      recommendations: [],
      savedSearches: [],
      searchQuery: '',
      selectedCategory: '',
      conditionFilter: '',
      sortBy: 'created_at',
      minPrice: '',
      maxPrice: '',
      auctionFilter: '',
      locationFilter: '',
      currentPage: 1,
      totalPages: 1,
      totalProducts: 0
    };
  },
  computed: {
    ...mapState(['isAuthenticated'])
  },
  async mounted() {
    // Load categories first
    await this.loadCategories();
    // Load personalized recommendations for authenticated users
    if (this.isAuthenticated) {
      await this.loadRecommendations();
      await this.loadSavedSearches();
    }
    // Load products with current filters
    await this.loadProducts();
  },
  methods: {
    // Load products with current filters and pagination
    async loadProducts() {
      this.loading = true;
      
      try {
        const params = new URLSearchParams();
        params.append('page', this.currentPage);
        params.append('per_page', 12);
        
        // Add filters to API request
        if (this.searchQuery) params.append('search', this.searchQuery);
        if (this.selectedCategory) params.append('category_id', this.selectedCategory);
        if (this.conditionFilter) params.append('condition', this.conditionFilter);
        if (this.minPrice) params.append('min_price', this.minPrice);
        if (this.maxPrice) params.append('max_price', this.maxPrice);
        if (this.auctionFilter) params.append('is_auction', this.auctionFilter);
        if (this.locationFilter) params.append('location', this.locationFilter);
        
        // Handle sorting parameters
        if (this.sortBy === 'price_desc') {
          params.append('sort_by', 'price');
          params.append('sort_order', 'desc');
        } else if (this.sortBy === 'price') {
          params.append('sort_by', 'price');
          params.append('sort_order', 'asc');
        } else {
          params.append('sort_by', this.sortBy);
        }
        
        const response = await fetch(`${this.$store.state.backendUrl}/api/products?${params.toString()}`);
        const data = await response.json();
        
        this.products = data.products;
        this.totalPages = data.pages;
        this.totalProducts = data.total;
      } catch (error) {
        console.error('Error loading products:', error);
      } finally {
        this.loading = false;
      }
    },
    
    // Load all available categories for filtering
    async loadCategories() {
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/categories`);
        const data = await response.json();
        // Flatten categories and subcategories for easier selection
        this.categories = data.categories.flatMap(cat => {
          const result = [cat];
          if (cat.subcategories) {
            result.push(...cat.subcategories);
          }
          return result;
        });
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    },
    
    // Load personalized product recommendations for authenticated users
    async loadRecommendations() {
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/recommendations`, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        const data = await response.json();
        this.recommendations = data.recommendations || [];
      } catch (error) {
        console.error('Error loading recommendations:', error);
      }
    },
    
    // Load saved searches for authenticated users
    async loadSavedSearches() {
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/saved-searches`, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        const data = await response.json();
        this.savedSearches = data.saved_searches || [];
      } catch (error) {
        console.error('Error loading saved searches:', error);
      }
    },
    
    // Trigger product search when user presses enter in search box
    searchProducts() {
      this.currentPage = 1;
      this.loadProducts();
    },
    
    // Apply filters when any filter dropdown is changed
    filterProducts() {
      this.currentPage = 1;
      this.loadProducts();
    },
    
    // Apply sorting when sort dropdown is changed
    sortProducts() {
      this.currentPage = 1;
      this.loadProducts();
    },
    
    // Reset all filters to default values
    resetFilters() {
      this.searchQuery = '';
      this.selectedCategory = '';
      this.conditionFilter = '';
      this.minPrice = '';
      this.maxPrice = '';
      this.auctionFilter = '';
      this.locationFilter = '';
      this.sortBy = 'created_at';
      this.currentPage = 1;
      this.loadProducts();
    },
    
    // Navigate to a specific page of products
    changePage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page;
        this.loadProducts();
      }
    },
    
    // Navigate to product detail page
    viewProduct(productId) {
      this.$router.push(`/product/${productId}`);
    },
    
    // Format auction end time for display (e.g., "2d 4h" or "Ended")
    formatAuctionEndTime(endTime) {
      if (!endTime) return '';
      
      const end = new Date(endTime);
      const now = new Date();
      const diff = end - now;
      
      if (diff <= 0) {
        return 'Ended';
      }
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      
      if (days > 0) {
        return `${days}d ${hours}h`;
      } else {
        return `${hours}h`;
      }
    },
    
    // Save current search filters
    async saveCurrentSearch() {
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      const searchName = prompt('Enter a name for this saved search:');
      if (!searchName) return;
      
      try {
        // Prepare filters object
        const filters = {};
        if (this.selectedCategory) filters.category_id = this.selectedCategory;
        if (this.conditionFilter) filters.condition = this.conditionFilter;
        if (this.minPrice) filters.min_price = this.minPrice;
        if (this.maxPrice) filters.max_price = this.maxPrice;
        if (this.auctionFilter) filters.is_auction = this.auctionFilter;
        if (this.locationFilter) filters.location = this.locationFilter;
        if (this.sortBy) filters.sort_by = this.sortBy;
        
        const response = await fetch(`${this.$store.state.backendUrl}/api/saved-searches`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.$store.state.authData?.token
          },
          body: JSON.stringify({
            name: searchName,
            search_query: this.searchQuery,
            filters: filters
          })
        });
        
        if (response.ok) {
          // Reload saved searches
          await this.loadSavedSearches();
          alert('Search saved successfully!');
        } else {
          const error = await response.json();
          alert(error.error || 'Failed to save search');
        }
      } catch (error) {
        console.error('Error saving search:', error);
        alert('Network error. Please try again.');
      }
    },
    
    // Apply a saved search
    applySavedSearch(savedSearch) {
      // Reset all filters first
      this.resetFilters();
      
      // Apply search query
      this.searchQuery = savedSearch.search_query || '';
      
      // Apply filters
      const filters = savedSearch.filters || {};
      this.selectedCategory = filters.category_id || '';
      this.conditionFilter = filters.condition || '';
      this.minPrice = filters.min_price || '';
      this.maxPrice = filters.max_price || '';
      this.auctionFilter = filters.is_auction || '';
      this.locationFilter = filters.location || '';
      this.sortBy = filters.sort_by || 'created_at';
      
      // Load products with these filters
      this.currentPage = 1;
      this.loadProducts();
    }
  }
};
</script>

<style scoped>
/* Product card hover effects */
.product-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Image container styling */
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