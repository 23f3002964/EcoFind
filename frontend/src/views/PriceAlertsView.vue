<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Price Alerts</h4>
      <button class="btn btn-success" @click="showCreateModal = true">
        <i class="bi bi-plus-lg"></i> Create Price Alert
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
    <div v-else-if="priceAlerts.length === 0" class="text-center py-5">
      <i class="bi bi-bell text-muted" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No price alerts yet</h5>
      <p class="text-muted">Create price alerts to get notified when items drop to your target price.</p>
    </div>

    <!-- Price Alerts List -->
    <div v-else>
      <div class="row row-cols-1 g-3">
        <div v-for="alert in priceAlerts" :key="alert.id" class="col">
          <div class="card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h5 class="card-title">{{ alert.product.title }}</h5>
                  <div class="d-flex align-items-center mb-2">
                    <span class="h5 text-success me-3">${{ alert.target_price }}</span>
                    <span class="text-muted">Current: ${{ alert.product.price }}</span>
                  </div>
                  <div class="d-flex flex-wrap gap-2">
                    <span class="badge bg-info">Price Alert</span>
                    <span :class="alert.status === 'active' ? 'badge bg-success' : 'badge bg-secondary'">
                      {{ alert.status }}
                    </span>
                  </div>
                </div>
                <div class="d-flex gap-2">
                  <button 
                    class="btn btn-sm btn-outline-danger" 
                    @click="deleteAlert(alert.id)"
                    :disabled="deletingAlert === alert.id"
                  >
                    <span v-if="deletingAlert === alert.id" class="spinner-border spinner-border-sm" role="status"></span>
                    <span v-else><i class="bi bi-trash"></i></span>
                  </button>
                </div>
              </div>
              <small class="text-muted">
                Created on {{ formatDate(alert.created_at) }}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Price Alert Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Price Alert</h5>
            <button type="button" class="btn-close" @click="showCreateModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Product URL or ID</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="newAlert.productId"
                placeholder="Enter product URL or ID"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Target Price ($)</label>
              <input 
                type="number" 
                class="form-control" 
                v-model="newAlert.targetPrice"
                placeholder="Enter your target price"
                min="0"
                step="0.01"
              >
            </div>
            <div class="alert alert-info">
              <small>
                You'll receive a notification when the product's price drops to or below your target price.
              </small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
            <button type="button" class="btn btn-success" @click="createPriceAlert" :disabled="creating">
              <span v-if="creating" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ creating ? 'Creating...' : 'Create Alert' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Overlay for modal -->
    <div v-if="showCreateModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
export default {
  name: 'PriceAlertsView',
  data() {
    return {
      loading: false,
      creating: false,
      deletingAlert: null,
      error: '',
      priceAlerts: [],
      showCreateModal: false,
      newAlert: {
        productId: '',
        targetPrice: ''
      }
    };
  },
  async mounted() {
    await this.loadPriceAlerts();
  },
  methods: {
    // Load all price alerts for the current user
    async loadPriceAlerts() {
      this.loading = true;
      this.error = '';
      
      try {
        // TODO: Implement backend endpoint for price alerts
        // For now, we'll simulate with mock data
        this.priceAlerts = [];
        
        // In a real implementation, you would fetch from:
        // const response = await fetch(`${this.$store.state.backendUrl}/api/price-alerts`, {
        //   headers: {
        //     'Authorization': this.$store.state.authData?.token
        //   }
        // });
        // 
        // if (response.ok) {
        //   const data = await response.json();
        //   this.priceAlerts = data.price_alerts;
        // } else {
        //   this.error = 'Failed to load price alerts';
        // }
      } catch (error) {
        console.error('Error loading price alerts:', error);
        this.error = 'Network error. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    // Create a new price alert
    async createPriceAlert() {
      if (!this.newAlert.productId.trim() || !this.newAlert.targetPrice) {
        alert('Please enter both product and target price');
        return;
      }
      
      this.creating = true;
      
      try {
        // TODO: Implement backend endpoint for creating price alerts
        // For now, we'll simulate the creation
        alert('Price alert functionality would be implemented in a full version. In a real application, this would create an alert that monitors the product price and notifies you when it drops to your target price.');
        this.showCreateModal = false;
        this.newAlert = { productId: '', targetPrice: '' };
        
        // In a real implementation:
        // const response = await fetch(`${this.$store.state.backendUrl}/api/price-alerts`, {
        //   method: 'POST',
        //   headers: {
        //     'Content-Type': 'application/json',
        //     'Authorization': this.$store.state.authData?.token
        //   },
        //   body: JSON.stringify({
        //     product_id: this.newAlert.productId,
        //     target_price: parseFloat(this.newAlert.targetPrice)
        //   })
        // });
        // 
        // if (response.ok) {
        //   // Close modal and reset form
        //   this.showCreateModal = false;
        //   this.newAlert = { productId: '', targetPrice: '' };
        //   
        //   // Reload price alerts
        //   await this.loadPriceAlerts();
        //   
        //   alert('Price alert created successfully!');
        // } else {
        //   const error = await response.json();
        //   alert(error.error || 'Failed to create price alert');
        // }
      } catch (error) {
        console.error('Error creating price alert:', error);
        alert('Network error. Please try again.');
      } finally {
        this.creating = false;
      }
    },
    
    // Delete a price alert
    async deleteAlert(alertId) {
      if (!confirm('Are you sure you want to delete this price alert?')) {
        return;
      }
      
      this.deletingAlert = alertId;
      
      try {
        // TODO: Implement backend endpoint for deleting price alerts
        // For now, we'll simulate the deletion
        this.priceAlerts = this.priceAlerts.filter(a => a.id !== alertId);
        
        // In a real implementation:
        // const response = await fetch(`${this.$store.state.backendUrl}/api/price-alerts/${alertId}`, {
        //   method: 'DELETE',
        //   headers: {
        //     'Authorization': this.$store.state.authData?.token
        //   }
        // });
        // 
        // if (response.ok) {
        //   // Remove from local list
        //   this.priceAlerts = this.priceAlerts.filter(a => a.id !== alertId);
        //   alert('Price alert deleted successfully!');
        // } else {
        //   const error = await response.json();
        //   alert(error.error || 'Failed to delete price alert');
        // }
      } catch (error) {
        console.error('Error deleting price alert:', error);
        alert('Network error. Please try again.');
      } finally {
        this.deletingAlert = null;
      }
    },
    
    // Format date for display
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    }
  }
};
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.badge {
  font-size: 0.75em;
}
</style>