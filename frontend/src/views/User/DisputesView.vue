<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>My Disputes</h4>
      <button class="btn btn-primary" @click="showNewDisputeModal = true">
        <i class="bi bi-plus-circle"></i> File New Dispute
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
    <div v-else-if="disputes.length === 0" class="text-center py-5">
      <i class="bi bi-exclamation-circle" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No disputes found</h5>
      <p class="text-muted">You don't have any active or past disputes.</p>
      <button class="btn btn-primary" @click="showNewDisputeModal = true">
        File Your First Dispute
      </button>
    </div>

    <!-- Disputes List -->
    <div v-else>
      <div class="row">
        <div class="col-lg-8">
          <div class="card mb-3" v-for="dispute in disputes" :key="dispute.id">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <h5 class="card-title">{{ dispute.title }}</h5>
                <span class="badge" :class="getStatusBadgeClass(dispute.status)">
                  {{ dispute.status.replace('_', ' ') }}
                </span>
              </div>
              
              <p class="card-text">{{ dispute.description.substring(0, 100) }}{{ dispute.description.length > 100 ? '...' : '' }}</p>
              
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <small class="text-muted">
                    Filed on {{ formatDate(dispute.created_at) }}
                  </small>
                </div>
                <div>
                  <button class="btn btn-sm btn-outline-primary me-2" @click="viewDisputeDetails(dispute)">
                    View Details
                  </button>
                  <button 
                    v-if="dispute.status === 'open' || dispute.status === 'in_progress'" 
                    class="btn btn-sm btn-outline-secondary"
                    @click="showEvidenceModal(dispute)"
                  >
                    Add Evidence
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pagination -->
          <nav v-if="totalPages > 1">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Previous</a>
              </li>
              <li 
                class="page-item" 
                :class="{ active: currentPage === page }"
                v-for="page in totalPages" 
                :key="page"
              >
                <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Next</a>
              </li>
            </ul>
          </nav>
        </div>
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h5>Dispute Statistics</h5>
            </div>
            <div class="card-body">
              <div class="d-flex justify-content-between mb-3">
                <span>Total Disputes:</span>
                <strong>{{ totalDisputes }}</strong>
              </div>
              <div class="d-flex justify-content-between mb-3">
                <span>Open:</span>
                <strong>{{ statusCounts.open || 0 }}</strong>
              </div>
              <div class="d-flex justify-content-between mb-3">
                <span>In Progress:</span>
                <strong>{{ statusCounts.in_progress || 0 }}</strong>
              </div>
              <div class="d-flex justify-content-between mb-3">
                <span>Resolved:</span>
                <strong>{{ statusCounts.resolved || 0 }}</strong>
              </div>
              <div class="d-flex justify-content-between">
                <span>Closed:</span>
                <strong>{{ statusCounts.closed || 0 }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- New Dispute Modal -->
  <div class="modal fade" :class="{ show: showNewDisputeModal }" tabindex="-1" v-if="showNewDisputeModal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">File New Dispute</h5>
          <button type="button" class="btn-close" @click="showNewDisputeModal = false"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitNewDispute">
            <div class="mb-3">
              <label for="title" class="form-label">Title</label>
              <input 
                type="text" 
                class="form-control" 
                id="title" 
                v-model="newDispute.title"
                required
              >
            </div>
            
            <div class="mb-3">
              <label for="respondent" class="form-label">Respondent (User you're disputing with)</label>
              <input 
                type="text" 
                class="form-control" 
                id="respondent" 
                v-model="newDispute.respondent"
                placeholder="Enter username"
                required
              >
            </div>
            
            <div class="mb-3">
              <label for="productId" class="form-label">Related Product (Optional)</label>
              <input 
                type="text" 
                class="form-control" 
                id="productId" 
                v-model="newDispute.productId"
                placeholder="Product ID"
              >
            </div>
            
            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <textarea 
                class="form-control" 
                id="description" 
                rows="4" 
                v-model="newDispute.description"
                required
              ></textarea>
            </div>
            
            <div v-if="disputeError" class="alert alert-danger">
              {{ disputeError }}
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showNewDisputeModal = false">Cancel</button>
          <button type="button" class="btn btn-primary" @click="submitNewDispute" :disabled="submitting">
            <span v-if="!submitting">Submit Dispute</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm" role="status"></span>
              Submitting...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Dispute Detail Modal -->
  <div class="modal fade" :class="{ show: showDetailModal }" tabindex="-1" v-if="showDetailModal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Dispute Details #{{ selectedDispute?.id }}</h5>
          <button type="button" class="btn-close" @click="showDetailModal = false"></button>
        </div>
        <div class="modal-body" v-if="selectedDispute">
          <div class="row">
            <div class="col-md-6">
              <h6>Dispute Information</h6>
              <div class="mb-3">
                <label class="form-label"><strong>Title:</strong></label>
                <p>{{ selectedDispute.title }}</p>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Status:</strong></label>
                <span class="badge" :class="getStatusBadgeClass(selectedDispute.status)">
                  {{ selectedDispute.status.replace('_', ' ') }}
                </span>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Date Filed:</strong></label>
                <p>{{ formatDate(selectedDispute.created_at) }}</p>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Last Updated:</strong></label>
                <p>{{ formatDate(selectedDispute.updated_at) }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <h6>Parties Involved</h6>
              <div class="mb-3">
                <label class="form-label"><strong>Complainant:</strong></label>
                <p>{{ selectedDispute.complainant.username }} ({{ selectedDispute.complainant.email }})</p>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Respondent:</strong></label>
                <p>{{ selectedDispute.respondent.username }} ({{ selectedDispute.respondent.email }})</p>
              </div>
              <div v-if="selectedDispute.product">
                <h6>Related Product</h6>
                <div class="d-flex align-items-center">
                  <img 
                    :src="selectedDispute.product.image || 'https://via.placeholder.com/40'" 
                    class="me-2" 
                    alt="Item"
                    width="40"
                    height="40"
                  >
                  <span>{{ selectedDispute.product.title }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="mb-3">
            <label class="form-label"><strong>Description:</strong></label>
            <p>{{ selectedDispute.description }}</p>
          </div>
          
          <div v-if="selectedDispute.admin_notes">
            <label class="form-label"><strong>Admin Notes:</strong></label>
            <p>{{ selectedDispute.admin_notes }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showDetailModal = false">Close</button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Add Evidence Modal -->
  <div class="modal fade" :class="{ show: showEvidenceModalFlag }" tabindex="-1" v-if="showEvidenceModalFlag">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add Evidence to Dispute #{{ evidenceDispute?.id }}</h5>
          <button type="button" class="btn-close" @click="showEvidenceModalFlag = false"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitEvidence">
            <div class="mb-3">
              <label for="evidence" class="form-label">Evidence Description</label>
              <textarea 
                class="form-control" 
                id="evidence" 
                rows="4" 
                v-model="evidenceText"
                placeholder="Describe any additional evidence or information..."
                required
              ></textarea>
            </div>
            
            <div v-if="evidenceError" class="alert alert-danger">
              {{ evidenceError }}
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showEvidenceModalFlag = false">Cancel</button>
          <button type="button" class="btn btn-primary" @click="submitEvidence" :disabled="evidenceSubmitting">
            <span v-if="!evidenceSubmitting">Submit Evidence</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm" role="status"></span>
              Submitting...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Backdrops for modals -->
  <div v-if="showNewDisputeModal || showDetailModal || showEvidenceModalFlag" class="modal-backdrop fade show"></div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserDisputesView',
  data() {
    return {
      disputes: [],
      loading: false,
      submitting: false,
      evidenceSubmitting: false,
      error: null,
      disputeError: null,
      evidenceError: null,
      currentPage: 1,
      totalPages: 1,
      totalDisputes: 0,
      statusCounts: {},
      
      // Modals
      showNewDisputeModal: false,
      showDetailModal: false,
      showEvidenceModalFlag: false,
      
      // Form data
      newDispute: {
        title: '',
        respondent: '',
        productId: '',
        description: ''
      },
      
      selectedDispute: null,
      evidenceDispute: null,
      evidenceText: ''
    };
  },
  
  mounted() {
    this.fetchDisputes();
  },
  
  methods: {
    async fetchDisputes() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/disputes', {
          params: {
            page: this.currentPage,
            per_page: 10
          }
        });
        
        this.disputes = response.data.disputes || [];
        this.totalPages = response.data.pages || 1;
        this.totalDisputes = response.data.total || 0;
        
        // Calculate status counts
        this.statusCounts = {};
        this.disputes.forEach(dispute => {
          this.statusCounts[dispute.status] = (this.statusCounts[dispute.status] || 0) + 1;
        });
      } catch (err) {
        console.error('Error fetching disputes:', err);
        this.error = 'Failed to load disputes. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    getStatusBadgeClass(status) {
      const statusClasses = {
        'open': 'bg-warning',
        'in_progress': 'bg-primary',
        'resolved': 'bg-success',
        'closed': 'bg-secondary'
      };
      return statusClasses[status] || 'bg-light';
    },
    
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchDisputes();
    },
    
    viewDisputeDetails(dispute) {
      this.selectedDispute = dispute;
      this.showDetailModal = true;
    },
    
    showEvidenceModal(dispute) {
      this.evidenceDispute = dispute;
      this.evidenceText = '';
      this.showEvidenceModalFlag = true;
    },
    
    async submitNewDispute() {
      this.submitting = true;
      this.disputeError = null;
      
      try {
        // In a real implementation, we would look up the user ID by username
        // For now, we'll just submit with placeholder data
        await axios.post('/api/disputes', {
          respondent_id: 2, // Placeholder - in real app, look up by username
          title: this.newDispute.title,
          description: this.newDispute.description,
          product_id: this.newDispute.productId || undefined
        });
        
        // Close modal and reset form
        this.showNewDisputeModal = false;
        this.newDispute = {
          title: '',
          respondent: '',
          productId: '',
          description: ''
        };
        
        // Refresh disputes
        this.fetchDisputes();
        
        // Show success message
        alert('Dispute filed successfully!');
      } catch (err) {
        console.error('Error filing dispute:', err);
        this.disputeError = err.response?.data?.error || 'Failed to file dispute. Please try again.';
      } finally {
        this.submitting = false;
      }
    },
    
    async submitEvidence() {
      if (!this.evidenceDispute) return;
      
      this.evidenceSubmitting = true;
      this.evidenceError = null;
      
      try {
        await axios.put(`/api/disputes/${this.evidenceDispute.id}`, {
          evidence: this.evidenceText
        });
        
        // Close modal and reset form
        this.showEvidenceModalFlag = false;
        this.evidenceText = '';
        
        // Refresh disputes
        this.fetchDisputes();
        
        // Show success message
        alert('Evidence submitted successfully!');
      } catch (err) {
        console.error('Error submitting evidence:', err);
        this.evidenceError = err.response?.data?.error || 'Failed to submit evidence. Please try again.';
      } finally {
        this.evidenceSubmitting = false;
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.badge.bg-warning {
  color: #000;
}

.modal-backdrop {
  z-index: 1050;
}

.modal {
  z-index: 1051;
}
</style>