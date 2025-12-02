<template>
  <div class="container my-4">
    <div class="d-flex align-items-center mb-4">
      <button class="btn btn-outline-secondary me-3" @click="$router.back()">
        <i class="bi bi-arrow-left"></i>
      </button>
      <h4>Edit Product</h4>
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

    <!-- Product Form -->
    <div v-else class="card">
      <div class="card-body">
        <form @submit.prevent="updateProduct">
          <!-- Product Title -->
          <div class="mb-3">
            <label for="title" class="form-label">Product Title *</label>
            <input 
              type="text" 
              class="form-control" 
              id="title" 
              v-model="product.title" 
              required
              placeholder="Enter product title"
            >
          </div>

          <!-- Category -->
          <div class="mb-3">
            <label for="category" class="form-label">Category *</label>
            <select 
              class="form-select" 
              id="category" 
              v-model="product.category_id" 
              required
            >
              <option value="">Select a category</option>
              <optgroup 
                v-for="category in categories" 
                :key="category.id" 
                :label="category.name"
              >
                <option :value="category.id">{{ category.name }}</option>
                <option 
                  v-for="subcategory in category.subcategories" 
                  :key="subcategory.id" 
                  :value="subcategory.id"
                >
                  &nbsp;&nbsp;{{ subcategory.name }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Description -->
          <div class="mb-3">
            <label for="description" class="form-label">Description *</label>
            <textarea 
              class="form-control" 
              id="description" 
              rows="4" 
              v-model="product.description" 
              required
              placeholder="Describe your product in detail"
            ></textarea>
          </div>

          <!-- Price -->
          <div class="mb-3">
            <label for="price" class="form-label">Price ($) *</label>
            <input 
              type="number" 
              class="form-control" 
              id="price" 
              v-model="product.price" 
              min="0" 
              step="0.01"
              required
              placeholder="0.00"
            >
          </div>

          <!-- Condition -->
          <div class="mb-3">
            <label for="condition" class="form-label">Condition *</label>
            <select 
              class="form-select" 
              id="condition" 
              v-model="product.condition" 
              required
            >
              <option value="">Select condition</option>
              <option value="New">New</option>
              <option value="Like New">Like New</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
              <option value="Used">Used</option>
            </select>
          </div>

          <!-- Location -->
          <div class="mb-3">
            <label for="location" class="form-label">Location</label>
            <input 
              type="text" 
              class="form-control" 
              id="location" 
              v-model="product.location" 
              placeholder="City, State or Address"
            >
          </div>

          <!-- Brand -->
          <div class="mb-3">
            <label for="brand" class="form-label">Brand</label>
            <input 
              type="text" 
              class="form-control" 
              id="brand" 
              v-model="product.brand" 
              placeholder="Brand name"
            >
          </div>

          <!-- Model -->
          <div class="mb-3">
            <label for="model" class="form-label">Model</label>
            <input 
              type="text" 
              class="form-control" 
              id="model" 
              v-model="product.model" 
              placeholder="Model number"
            >
          </div>

          <!-- Material -->
          <div class="mb-3">
            <label for="material" class="form-label">Material</label>
            <input 
              type="text" 
              class="form-control" 
              id="material" 
              v-model="product.material" 
              placeholder="Material composition"
            >
          </div>

          <!-- Images -->
          <div class="mb-3">
            <label class="form-label">Product Images</label>
            <div class="border rounded p-3">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <div 
                  v-for="(image, index) in product.images" 
                  :key="index" 
                  class="position-relative"
                  style="width: 100px; height: 100px;"
                >
                  <img 
                    :src="image" 
                    class="img-thumbnail w-100 h-100" 
                    style="object-fit: cover;"
                  >
                  <button 
                    type="button" 
                    class="btn btn-danger btn-sm position-absolute top-0 end-0" 
                    @click="removeImage(index)"
                  >
                    <i class="bi bi-x"></i>
                  </button>
                </div>
                
                <div 
                  v-if="product.images.length < 5"
                  class="border rounded d-flex align-items-center justify-content-center" 
                  style="width: 100px; height: 100px; cursor: pointer;"
                  @click="triggerFileInput"
                >
                  <i class="bi bi-plus-lg text-muted" style="font-size: 2rem;"></i>
                </div>
              </div>
              
              <input 
                type="file" 
                ref="fileInput" 
                class="d-none" 
                accept="image/*" 
                @change="handleImageUpload"
                multiple
              >
              <small class="text-muted">Upload up to 5 images (Click the + to add images)</small>
            </div>
          </div>

          <!-- Auction Options (readonly for existing auctions) -->
          <div v-if="product.is_auction" class="border rounded p-3 mb-4">
            <h5>Auction Settings</h5>
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Minimum Bid</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    :value="product.minimum_bid" 
                    disabled
                  >
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Reserve Price</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    :value="product.reserve_price || 'Not set'" 
                    disabled
                  >
                </div>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Auction End Time</label>
              <input 
                type="text" 
                class="form-control" 
                :value="formatDateTime(product.auction_end_time)" 
                disabled
              >
            </div>
          </div>

          <!-- Submit Button -->
          <div class="d-grid">
            <button 
              type="submit" 
              class="btn btn-success btn-lg" 
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ submitting ? 'Updating...' : 'Update Listing' }}
            </button>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="alert alert-danger mt-3 mb-0">
            {{ errorMessage }}
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EditProductView',
  props: {
    productId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      submitting: false,
      error: '',
      errorMessage: '',
      categories: [],
      product: {
        title: '',
        category_id: '',
        description: '',
        price: '',
        condition: '',
        location: '',
        brand: '',
        model: '',
        material: '',
        images: [],
        is_auction: false,
        minimum_bid: '',
        reserve_price: '',
        auction_end_time: ''
      }
    };
  },
  async mounted() {
    await this.loadCategories();
    await this.loadProduct();
  },
  methods: {
    async loadCategories() {
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/categories`);
        const data = await response.json();
        this.categories = data.categories;
      } catch (error) {
        console.error('Error loading categories:', error);
        this.errorMessage = 'Failed to load categories. Please try again.';
      }
    },
    
    async loadProduct() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/products/${this.productId}`, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.product = {
            title: data.title,
            category_id: data.category.id,
            description: data.description,
            price: data.price,
            condition: data.condition,
            location: data.location || '',
            brand: data.brand || '',
            model: data.model || '',
            material: data.material || '',
            images: data.images || [],
            is_auction: data.is_auction,
            minimum_bid: data.minimum_bid,
            reserve_price: data.reserve_price,
            auction_end_time: data.auction_end_time
          };
        } else {
          this.error = 'Failed to load product details';
        }
      } catch (error) {
        console.error('Error loading product:', error);
        this.error = 'Network error. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    
    handleImageUpload(event) {
      const files = event.target.files;
      if (!files || files.length === 0) return;
      
      // Limit to 5 images total
      const remainingSlots = 5 - this.product.images.length;
      const filesToProcess = Array.from(files).slice(0, remainingSlots);
      
      filesToProcess.forEach(file => {
        if (!file.type.startsWith('image/')) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
          this.product.images.push(e.target.result);
        };
        reader.readAsDataURL(file);
      });
      
      // Clear the input
      event.target.value = '';
    },
    
    removeImage(index) {
      this.product.images.splice(index, 1);
    },
    
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      const date = new Date(dateTimeString);
      return date.toLocaleString();
    },
    
    async updateProduct() {
      if (this.submitting) return;
      
      this.submitting = true;
      this.errorMessage = '';
      
      try {
        // Prepare the data
        const productData = {
          title: this.product.title,
          category_id: parseInt(this.product.category_id),
          description: this.product.description,
          price: parseFloat(this.product.price),
          condition: this.product.condition,
          location: this.product.location || null,
          brand: this.product.brand || null,
          model: this.product.model || null,
          material: this.product.material || null,
          images: this.product.images
        };
        
        const response = await fetch(`${this.$store.state.backendUrl}/api/products/${this.productId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.$store.state.authData?.token
          },
          body: JSON.stringify(productData)
        });
        
        if (response.ok) {
          // Redirect to the product detail page
          this.$router.push(`/product/${this.productId}`);
        } else {
          const error = await response.json();
          this.errorMessage = error.error || 'Failed to update product. Please check your inputs and try again.';
        }
      } catch (error) {
        console.error('Error updating product:', error);
        this.errorMessage = 'Network error. Please check your connection and try again.';
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style scoped>
.form-label {
  font-weight: 500;
}

.border.rounded {
  border: 1px solid #dee2e6 !important;
}
</style>