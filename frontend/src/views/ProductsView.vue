<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Product Feed</h4>
      <div v-if="$store.state.isAuthenticated">
        <button class="btn btn-success" @click="$router.push('/add-product')">
          <i class="bi bi-plus-lg"></i> Add Product
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search products..." 
              v-model="searchQuery"
              @keyup.enter="searchProducts"
            >
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="selectedCategory" @change="filterProducts">
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="sortBy" @change="sortProducts">
              <option value="created_at">Newest</option>
              <option value="price">Price Low to High</option>
              <option value="price_desc">Price High to Low</option>
              <option value="views">Most Popular</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Product Grid -->
    <div v-else>
      <div class="row row-cols-1 row-cols-md-3 g-4">
        <div v-for="product in products" :key="product.id" class="col">
          <div class="card h-100 product-card" @click="viewProduct(product.id)">
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
              <p class="card-text flex-grow-1">{{ product.description.substring(0, 100) }}{{ product.description.length > 100 ? '...' : '' }}</p>
              
              <div class="mt-auto">
                <div class="d-flex justify-content-between align-items-center">
                  <h6 class="text-success mb-0">${{ product.price }}</h6>
                  <span v-if="product.is_auction" class="badge bg-warning">Auction</span>
                </div>
                
                <div class="d-flex justify-content-between align-items-center mt-2">
                  <small class="text-muted">{{ product.seller }}</small>
                  <small class="text-muted">
                    <i class="bi bi-star-fill text-warning"></i>
                    {{ product.seller_rating ? product.seller_rating.toFixed(1) : 'N/A' }}
                  </small>
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
import { mapState } from 'vuex';

export default {
  name: 'ProductsView',
  data() {
    return {
      loading: true,
      products: [],
      categories: [],
      searchQuery: '',
      selectedCategory: '',
      sortBy: 'created_at',
      currentPage: 1,
      totalPages: 1,
      totalProducts: 0
    };
  },
  computed: {
    ...mapState(['isAuthenticated'])
  },
  async mounted() {
    await this.loadCategories();
    await this.loadProducts();
  },
  methods: {
    async loadProducts() {
      this.loading = true;
      
      try {
        const params = new URLSearchParams();
        params.append('page', this.currentPage);
        params.append('per_page', 12);
        
        if (this.searchQuery) {
          params.append('search', this.searchQuery);
        }
        
        if (this.selectedCategory) {
          params.append('category_id', this.selectedCategory);
        }
        
        if (this.sortBy) {
          if (this.sortBy === 'price_desc') {
            params.append('sort_by', 'price');
            params.append('sort_order', 'desc');
          } else {
            params.append('sort_by', this.sortBy);
          }
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
    
    async loadCategories() {
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/categories`);
        const data = await response.json();
        this.categories = data.categories.flatMap(cat => {
          // Flatten categories and subcategories
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
    
    searchProducts() {
      this.currentPage = 1;
      this.loadProducts();
    },
    
    filterProducts() {
      this.currentPage = 1;
      this.loadProducts();
    },
    
    sortProducts() {
      this.currentPage = 1;
      this.loadProducts();
    },
    
    changePage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.currentPage = page;
        this.loadProducts();
      }
    },
    
    viewProduct(productId) {
      this.$router.push(`/product/${productId}`);
    }
  }
};
</script>

<style scoped>
.product-card {
  cursor: pointer;
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