<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>My Cart</h4>
      <button 
        v-if="cartItems.length > 0" 
        class="btn btn-success" 
        @click="checkout"
        :disabled="processing"
      >
        <span v-if="!processing">Checkout</span>
        <span v-else>
          <span class="spinner-border spinner-border-sm" role="status"></span>
          Processing...
        </span>
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

    <!-- Empty Cart -->
    <div v-else-if="cartItems.length === 0" class="text-center py-5">
      <i class="bi bi-cart-x" style="font-size: 3rem;"></i>
      <h5 class="mt-3">Your cart is empty</h5>
      <p class="text-muted">Add some products to your cart!</p>
      <button class="btn btn-primary" @click="$router.push('/products')">
        Browse Products
      </button>
    </div>

    <!-- Cart Items -->
    <div v-else>
      <div class="row">
        <div class="col-lg-8">
          <div class="card mb-3" v-for="item in cartItems" :key="item.id">
            <div class="card-body">
              <div class="d-flex">
                <div class="flex-shrink-0">
                  <img 
                    :src="item.product.image_url || 'https://via.placeholder.com/100'" 
                    class="img-fluid rounded" 
                    alt="Product image"
                    style="width: 100px; height: 100px; object-fit: cover;"
                  >
                </div>
                <div class="flex-grow-1 ms-3">
                  <h5 class="card-title">{{ item.product.name }}</h5>
                  <p class="card-text text-muted">{{ item.product.description }}</p>
                  
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>${{ item.product.price }}</strong>
                    </div>
                    
                    <div class="d-flex align-items-center">
                      <button 
                        class="btn btn-sm btn-outline-secondary"
                        @click="updateQuantity(item.id, item.quantity - 1)"
                        :disabled="item.quantity <= 1"
                      >
                        -
                      </button>
                      <span class="mx-2">{{ item.quantity }}</span>
                      <button 
                        class="btn btn-sm btn-outline-secondary"
                        @click="updateQuantity(item.id, item.quantity + 1)"
                      >
                        +
                      </button>
                      
                      <button 
                        class="btn btn-sm btn-danger ms-3"
                        @click="removeFromCart(item.id)"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h5>Order Summary</h5>
            </div>
            <div class="card-body">
              <div class="d-flex justify-content-between mb-2">
                <span>Subtotal</span>
                <span>${{ subtotal.toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span>Shipping</span>
                <span>Free</span>
              </div>
              <hr>
              <div class="d-flex justify-content-between fw-bold">
                <span>Total</span>
                <span>${{ total.toFixed(2) }}</span>
              </div>
              
              <button 
                class="btn btn-success w-100 mt-3" 
                @click="checkout"
                :disabled="processing || cartItems.length === 0"
              >
                <span v-if="!processing">Proceed to Checkout</span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm" role="status"></span>
                  Processing...
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
  name: 'CartView',
  data() {
    return {
      cartItems: [],
      loading: false,
      processing: false,
      error: null
    };
  },
  
  computed: {
    subtotal() {
      return this.cartItems.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
    },
    
    total() {
      return this.subtotal; // Free shipping
    }
  },
  
  mounted() {
    this.fetchCart();
  },
  
  methods: {
    async fetchCart() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/cart');
        this.cartItems = response.data.items || [];
      } catch (err) {
        console.error('Error fetching cart:', err);
        this.error = 'Failed to load cart items. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async updateQuantity(cartItemId, newQuantity) {
      if (newQuantity < 1) return;
      
      try {
        await axios.put(`/api/cart/${cartItemId}`, { quantity: newQuantity });
        const item = this.cartItems.find(item => item.id === cartItemId);
        if (item) {
          item.quantity = newQuantity;
        }
      } catch (err) {
        console.error('Error updating quantity:', err);
        this.error = 'Failed to update item quantity. Please try again.';
      }
    },
    
    async removeFromCart(cartItemId) {
      try {
        await axios.delete(`/api/cart/${cartItemId}`);
        this.cartItems = this.cartItems.filter(item => item.id !== cartItemId);
      } catch (err) {
        console.error('Error removing item:', err);
        this.error = 'Failed to remove item from cart. Please try again.';
      }
    },
    
    async checkout() {
      this.processing = true;
      this.error = null;
      
      try {
        const response = await axios.post('/api/cart/checkout');
        // Redirect to success page or order confirmation
        this.$router.push(`/order-confirmation/${response.data.orderId}`);
      } catch (err) {
        console.error('Error during checkout:', err);
        this.error = 'Checkout failed. Please try again.';
      } finally {
        this.processing = false;
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}
</style>