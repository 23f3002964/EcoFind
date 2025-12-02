<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Saved Searches</h4>
      <button class="btn btn-success" @click="showCreateModal = true">
        <i class="bi bi-plus-lg"></i> Save Current Search
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
    <div v-else-if="savedSearches.length === 0" class="text-center py-5">
      <i class="bi bi-search text-muted" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No saved searches yet</h5>
      <p class="text-muted">Save your favorite search filters for quick access.</p>
    </div>

    <!-- Saved Searches List -->
    <div v-else>
      <div class="row row-cols-1 g-3">
        <div v-for="search in savedSearches" :key="search.id" class="col">
          <div class="card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h5 class="card-title">{{ search.name }}</h5>
                  <p class="card-text text-muted mb-2">
                    "{{ search.search_query }}"
                  </p>
                  <div class="d-flex flex-wrap gap-2">
                    <span v-for="(value, key) in search.filters" :key="key" class="badge bg-secondary">
                      {{ formatFilterLabel(key) }}: {{ value }}
                    </span>
                  </div>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn btn-sm btn-outline-primary" @click="applySearch(search)">
                    <i class="bi bi-play-btn"></i> Apply
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteSearch(search.id)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
              <small class="text-muted">
                Saved on {{ formatDate(search.created_at) }}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Saved Search Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Save Current Search</h5>
            <button type="button" class="btn-close" @click="showCreateModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Search Name</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="newSearchName"
                placeholder="e.g., Electronics under $100"
              >
            </div>
            <div class="alert alert-info">
              <small>
                This will save your current search filters. You can apply them later with one click.
              </small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateModal = false">Cancel</button>
            <button type="button" class="btn btn-success" @click="saveCurrentSearch" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ saving ? 'Saving...' : 'Save Search' }}
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
  name: 'SavedSearchesView',
  data() {
    return {
      loading: false,
      saving: false,
      error: '',
      savedSearches: [],
      showCreateModal: false,
      newSearchName: ''
    };
  },
  async mounted() {
    await this.loadSavedSearches();
  },
  methods: {
    // Load all saved searches for the current user
    async loadSavedSearches() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/saved-searches`, {
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.savedSearches = data.saved_searches;
        } else {
          this.error = 'Failed to load saved searches';
        }
      } catch (error) {
        console.error('Error loading saved searches:', error);
        this.error = 'Network error. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    // Save the current search filters
    async saveCurrentSearch() {
      if (!this.newSearchName.trim()) {
        alert('Please enter a name for your saved search');
        return;
      }
      
      this.saving = true;
      
      try {
        // Get current search parameters from URL or store
        const urlParams = new URLSearchParams(window.location.search);
        const searchQuery = urlParams.get('search') || '';
        const filters = {};
        
        // Extract common filter parameters
        const filterKeys = ['category_id', 'condition', 'min_price', 'max_price', 'location', 'sort_by'];
        filterKeys.forEach(key => {
          const value = urlParams.get(key);
          if (value) {
            filters[key] = value;
          }
        });
        
        const response = await fetch(`${this.$store.state.backendUrl}/api/saved-searches`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': this.$store.state.authData?.token
          },
          body: JSON.stringify({
            name: this.newSearchName,
            search_query: searchQuery,
            filters: filters
          })
        });
        
        if (response.ok) {
          // Close modal and reset form
          this.showCreateModal = false;
          this.newSearchName = '';
          
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
      } finally {
        this.saving = false;
      }
    },
    
    // Apply a saved search by navigating to the products page with filters
    applySearch(search) {
      // Build query parameters from saved search
      const params = new URLSearchParams();
      
      if (search.search_query) {
        params.append('search', search.search_query);
      }
      
      // Add filters
      Object.entries(search.filters).forEach(([key, value]) => {
        params.append(key, value);
      });
      
      // Navigate to products page with these filters
      this.$router.push(`/products?${params.toString()}`);
    },
    
    // Delete a saved search
    async deleteSearch(searchId) {
      if (!confirm('Are you sure you want to delete this saved search?')) {
        return;
      }
      
      try {
        const response = await fetch(`${this.$store.state.backendUrl}/api/saved-searches/${searchId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': this.$store.state.authData?.token
          }
        });
        
        if (response.ok) {
          // Remove from local list
          this.savedSearches = this.savedSearches.filter(s => s.id !== searchId);
          alert('Saved search deleted successfully!');
        } else {
          const error = await response.json();
          alert(error.error || 'Failed to delete saved search');
        }
      } catch (error) {
        console.error('Error deleting saved search:', error);
        alert('Network error. Please try again.');
      }
    },
    
    // Format filter labels for display
    formatFilterLabel(key) {
      const labels = {
        'category_id': 'Category',
        'condition': 'Condition',
        'min_price': 'Min Price',
        'max_price': 'Max Price',
        'location': 'Location',
        'sort_by': 'Sort By'
      };
      
      return labels[key] || key;
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