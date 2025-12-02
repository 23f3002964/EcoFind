<template>
  <div class="container my-4">
    <div class="d-flex align-items-center mb-4">
      <button class="btn btn-outline-secondary me-3" @click="$router.back()">
        <i class="bi bi-arrow-left"></i>
      </button>
      <h4>Add New Product</h4>
    </div>

    <div class="card">
      <div class="card-body">
        <form @submit.prevent="submitProduct">
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

          <!-- Auction Options -->
          <div class="border rounded p-3 mb-4">
            <div class="form-check mb-3">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isAuction" 
                v-model="product.is_auction"
              >
              <label class="form-check-label" for="isAuction">
                List as Auction Item
              </label>
            </div>

            <div v-if="product.is_auction">
              <!-- Minimum Bid -->
              <div class="mb-3">
                <label for="minimumBid" class="form-label">Minimum Bid ($) *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="minimumBid" 
                  v-model="product.minimum_bid" 
                  min="0" 
                  step="0.01"
                  :required="product.is_auction"
                  placeholder="0.00"
                >
              </div>

              <!-- Reserve Price -->
              <div class="mb-3">
                <label for="reservePrice" class="form-label">Reserve Price ($)</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="reservePrice" 
                  v-model="product.reserve_price" 
                  min="0" 
                  step="0.01"
                  placeholder="0.00 (Optional)"
                >
                <div class="form-text">
                  The minimum price you're willing to sell for. If not met, the item won't be sold.
                </div>
              </div>

              <!-- Auction Duration -->
              <div class="mb-3">
                <label for="auctionDuration" class="form-label">Auction Duration (Days) *</label>
                <select 
                  class="form-select" 
                  id="auctionDuration" 
                  v-model="product.auction_duration" 
                  :required="product.is_auction"
                >
                  <option value="1">1 Day</option>
                  <option value="3">3 Days</option>
                  <option value="5">5 Days</option>
                  <option value="7" selected>7 Days</option>
                  <option value="14">14 Days</option>
                  <option value="30">30 Days</option>
                </select>
              </div>
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
              {{ submitting ? 'Submitting...' : 'Submit Listing' }}
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
  name: 'AddProductView',
  data() {
    return {
      submitting: false,
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
        auction_duration: 7
      }
    };
  },
  async mounted() {
    await this.loadCategories();
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
    
    async submitProduct() {
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
          images: this.product.images,
          is_auction: this.product.is_auction
        };
        
        // Add auction-specific fields if needed
        if (this.product.is_auction) {
          productData.minimum_bid = parseFloat(this.product.minimum_bid);
          productData.reserve_price = this.product.reserve_price ? parseFloat(this.product.reserve_price) : null;
          productData.auction_duration = parseInt(this.product.auction_duration);
        }
        
        const response = await fetch(`${this.$store.state.backendUrl}/api/products`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.$store.state.authData?.token
          },
          body: JSON.stringify(productData)
        });
        
        if (response.ok) {
          const result = await response.json();
          // Redirect to the newly created product or back to products list
          this.$router.push(`/product/${result.product_id}`);
        } else {
          const error = await response.json();
          this.errorMessage = error.error || 'Failed to create product. Please check your inputs and try again.';
        }
      } catch (error) {
        console.error('Error submitting product:', error);
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