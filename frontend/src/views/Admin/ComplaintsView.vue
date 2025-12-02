<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Complaints Management</h4>
      <div class="d-flex gap-2">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Search complaints..." 
          v-model="searchQuery"
          @keyup.enter="searchComplaints"
          style="width: 200px;"
        >
        <select class="form-select" v-model="filterStatus" @change="filterComplaints" style="width: 150px;">
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <button class="btn btn-outline-secondary" @click="refreshComplaints">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <h5 class="card-title">Open</h5>
            <h3>{{ statusStats.open || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">In Progress</h5>
            <h3>{{ statusStats.in_progress || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Resolved</h5>
            <h3>{{ statusStats.resolved || 0 }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-secondary text-white">
          <div class="card-body">
            <h5 class="card-title">Closed</h5>
            <h3>{{ statusStats.closed || 0 }}</h3>
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

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredComplaints.length === 0" class="text-center py-5">
      <i class="bi bi-exclamation-circle" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No complaints found</h5>
      <p class="text-muted">There are no complaints matching your current filters.</p>
    </div>

    <!-- Complaints Table -->
    <div v-else class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th @click="sort('id')" style="cursor: pointer;">
                  ID <i class="bi" :class="getSortIcon('id')"></i>
                </th>
                <th>Users Involved</th>
                <th @click="sort('item')" style="cursor: pointer;">
                  Item <i class="bi" :class="getSortIcon('item')"></i>
                </th>
                <th @click="sort('title')" style="cursor: pointer;">
                  Title <i class="bi" :class="getSortIcon('title')"></i>
                </th>
                <th @click="sort('status')" style="cursor: pointer;">
                  Status <i class="bi" :class="getSortIcon('status')"></i>
                </th>
                <th @click="sort('date_reported')" style="cursor: pointer;">
                  Date Reported <i class="bi" :class="getSortIcon('date_reported')"></i>
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="complaint in filteredComplaints" :key="complaint.id">
                <td>#{{ complaint.id }}</td>
                <td>
                  <div class="d-flex flex-column">
                    <div class="d-flex align-items-center mb-1">
                      <span class="badge bg-primary me-2">C</span>
                      <span>{{ complaint.complainant.username }}</span>
                    </div>
                    <div class="d-flex align-items-center">
                      <span class="badge bg-secondary me-2">R</span>
                      <span>{{ complaint.respondent.username }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="d-flex align-items-center" v-if="complaint.product">
                    <img 
                      :src="complaint.product.image || 'https://via.placeholder.com/40'" 
                      class="me-2" 
                      alt="Item"
                      width="40"
                      height="40"
                    >
                    <span>{{ complaint.product.title }}</span>
                  </div>
                  <span v-else>N/A</span>
                </td>
                <td>{{ complaint.title }}</td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(complaint.status)">
                    {{ complaint.status.replace('_', ' ') | capitalize }}
                  </span>
                </td>
                <td>{{ formatDate(complaint.created_at) }}</td>
                <td>
                  <div class="d-flex gap-1">
                    <button 
                      class="btn btn-sm btn-outline-primary" 
                      @click="viewComplaintDetails(complaint.id)"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button 
                      v-if="complaint.status === 'open'" 
                      class="btn btn-sm btn-outline-warning" 
                      @click="assignComplaint(complaint.id)"
                      title="Assign to Me"
                    >
                      <i class="bi bi-person-plus"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-success" 
                      @click="resolveComplaint(complaint.id)"
                      title="Resolve"
                      :disabled="complaint.status === 'resolved' || complaint.status === 'closed'"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger" 
                      @click="closeComplaint(complaint.id)"
                      title="Close"
                      :disabled="complaint.status === 'closed'"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <nav class="mt-4" v-if="totalPages > 1">
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

  <!-- Complaint Detail Modal -->
  <div class="modal fade" :class="{ show: showDetailModal }" tabindex="-1" v-if="showDetailModal">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Complaint Details #{{ selectedComplaint?.id }}</h5>
          <button type="button" class="btn-close" @click="showDetailModal = false"></button>
        </div>
        <div class="modal-body" v-if="selectedComplaint">
          <div class="row">
            <div class="col-md-6">
              <h6>Complaint Information</h6>
              <div class="mb-3">
                <label class="form-label"><strong>Title:</strong></label>
                <p>{{ selectedComplaint.title }}</p>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Status:</strong></label>
                <span class="badge" :class="getStatusBadgeClass(selectedComplaint.status)">
                  {{ selectedComplaint.status.replace('_', ' ') | capitalize }}
                </span>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Date Reported:</strong></label>
                <p>{{ formatDate(selectedComplaint.created_at) }}</p>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Last Updated:</strong></label>
                <p>{{ formatDate(selectedComplaint.updated_at) }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <h6>Parties Involved</h6>
              <div class="mb-3">
                <label class="form-label"><strong>Complainant:</strong></label>
                <p>{{ selectedComplaint.complainant.username }} ({{ selectedComplaint.complainant.email }})</p>
              </div>
              <div class="mb-3">
                <label class="form-label"><strong>Respondent:</strong></label>
                <p>{{ selectedComplaint.respondent.username }} ({{ selectedComplaint.respondent.email }})</p>
              </div>
              <div v-if="selectedComplaint.product">
                <h6>Related Product</h6>
                <div class="d-flex align-items-center">
                  <img 
                    :src="selectedComplaint.product.image || 'https://via.placeholder.com/40'" 
                    class="me-2" 
                    alt="Item"
                    width="40"
                    height="40"
                  >
                  <span>{{ selectedComplaint.product.title }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="mb-3">
            <label class="form-label"><strong>Description:</strong></label>
            <p>{{ selectedComplaint.description }}</p>
          </div>
          
          <div class="mb-3">
            <label class="form-label"><strong>Admin Notes:</strong></label>
            <textarea 
              class="form-control" 
              rows="3" 
              v-model="adminNotes"
              placeholder="Add notes about this complaint..."
            ></textarea>
          </div>
          
          <div class="mb-3">
            <label class="form-label"><strong>Update Status:</strong></label>
            <select class="form-select" v-model="newStatus">
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showDetailModal = false">Close</button>
          <button type="button" class="btn btn-primary" @click="updateComplaint" :disabled="updating">
            <span v-if="!updating">Update</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm" role="status"></span>
              Updating...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Backdrop for modal -->
  <div v-if="showDetailModal" class="modal-backdrop fade show"></div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ComplaintsManagementView',
  data() {
    return {
      complaints: [],
      loading: false,
      updating: false,
      error: null,
      filterStatus: '',
      searchQuery: '',
      sortKey: 'date_reported',
      sortOrder: 'desc',
      currentPage: 1,
      totalPages: 1,
      itemsPerPage: 10,
      statusStats: {}, // Add this for statistics
      
      // Modal data
      showDetailModal: false,
      selectedComplaint: null,
      adminNotes: '',
      newStatus: ''
    };
  },
  
  computed: {
    filteredComplaints() {
      let result = [...this.complaints];
      
      // Apply status filter
      if (this.filterStatus) {
        result = result.filter(complaint => complaint.status === this.filterStatus);
      }
      
      // Apply search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(complaint => 
          complaint.title.toLowerCase().includes(query) ||
          complaint.complainant.username.toLowerCase().includes(query) ||
          complaint.respondent.username.toLowerCase().includes(query) ||
          (complaint.product && complaint.product.title.toLowerCase().includes(query))
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let modifier = this.sortOrder === 'asc' ? 1 : -1;
        
        // Special handling for nested properties
        let aValue, bValue;
        if (this.sortKey === 'item' && a.product) {
          aValue = a.product.title;
          bValue = b.product?.title || '';
        } else if (this.sortKey === 'title') {
          aValue = a.title;
          bValue = b.title;
        } else if (this.sortKey === 'date_reported') {
          aValue = a.created_at;
          bValue = b.created_at;
        } else if (this.sortKey === 'status') {
          aValue = a.status;
          bValue = b.status;
        } else {
          aValue = a[this.sortKey];
          bValue = b[this.sortKey];
        }
        
        if (aValue < bValue) return -1 * modifier;
        if (aValue > bValue) return 1 * modifier;
        return 0;
      });
      
      return result;
    }
  },
  
  filters: {
    capitalize(value) {
      if (!value) return '';
      return value.charAt(0).toUpperCase() + value.slice(1);
    }
  },
  
  mounted() {
    this.fetchComplaints();
    this.fetchStats(); // Fetch statistics when component mounts
  },
  
  methods: {
    async fetchComplaints() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/admin/disputes', {
          params: {
            page: this.currentPage,
            per_page: this.itemsPerPage,
            status: this.filterStatus,
            search: this.searchQuery
          }
        });
        
        this.complaints = response.data.disputes || [];
        this.totalPages = response.data.pages || 1;
      } catch (err) {
        console.error('Error fetching complaints:', err);
        this.error = 'Failed to load complaints. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchStats() {
      try {
        const response = await axios.get('/api/admin/disputes/stats');
        this.statusStats = response.data.status_counts || {};
      } catch (err) {
        console.error('Error fetching stats:', err);
      }
    },
    
    searchComplaints() {
      this.currentPage = 1;
      this.fetchComplaints();
    },
    
    filterComplaints() {
      this.currentPage = 1;
      this.fetchComplaints();
    },
    
    sort(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortOrder = 'asc';
      }
      this.fetchComplaints();
    },
    
    getSortIcon(key) {
      if (this.sortKey !== key) return 'bi-sort';
      return this.sortOrder === 'asc' ? 'bi-sort-up' : 'bi-sort-down';
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
    
    refreshComplaints() {
      this.fetchComplaints();
      this.fetchStats(); // Also refresh stats
    },
    
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchComplaints();
    },
    
    viewComplaintDetails(complaintId) {
      const complaint = this.complaints.find(c => c.id === complaintId);
      if (complaint) {
        this.selectedComplaint = complaint;
        this.adminNotes = complaint.admin_notes || '';
        this.newStatus = complaint.status;
        this.showDetailModal = true;
      }
    },
    
    async updateComplaint() {
      if (!this.selectedComplaint) return;
      
      this.updating = true;
      
      try {
        await axios.put(`/api/admin/disputes/${this.selectedComplaint.id}`, {
          admin_notes: this.adminNotes,
          status: this.newStatus
        });
        
        // Update the complaint in our local data
        const complaint = this.complaints.find(c => c.id === this.selectedComplaint.id);
        if (complaint) {
          complaint.admin_notes = this.adminNotes;
          complaint.status = this.newStatus;
        }
        
        this.showDetailModal = false;
        alert('Complaint updated successfully!');
      } catch (err) {
        console.error('Error updating complaint:', err);
        alert('Failed to update complaint. Please try again.');
      } finally {
        this.updating = false;
      }
    },
    
    async assignComplaint(complaintId) {
      if (!confirm('Are you sure you want to assign this complaint to yourself?')) return;
      
      try {
        await axios.post(`/api/admin/disputes/${complaintId}/assign`);
        
        // Update the complaint status in our local data
        const complaint = this.complaints.find(c => c.id === complaintId);
        if (complaint) {
          complaint.status = 'in_progress';
        }
        
        alert('Complaint assigned to you successfully!');
      } catch (err) {
        console.error('Error assigning complaint:', err);
        alert('Failed to assign complaint. Please try again.');
      }
    },
    
    async resolveComplaint(complaintId) {
      if (!confirm('Are you sure you want to mark this complaint as resolved?')) return;
      
      try {
        await axios.put(`/api/admin/disputes/${complaintId}`, {
          status: 'resolved'
        });
        
        // Update the complaint status in our local data
        const complaint = this.complaints.find(c => c.id === complaintId);
        if (complaint) {
          complaint.status = 'resolved';
        }
        
        alert('Complaint marked as resolved successfully!');
      } catch (err) {
        console.error('Error resolving complaint:', err);
        alert('Failed to resolve complaint. Please try again.');
      }
    },
    
    async closeComplaint(complaintId) {
      if (!confirm('Are you sure you want to close this complaint?')) return;
      
      try {
        await axios.put(`/api/admin/disputes/${complaintId}`, {
          status: 'closed'
        });
        
        // Update the complaint status in our local data
        const complaint = this.complaints.find(c => c.id === complaintId);
        if (complaint) {
          complaint.status = 'closed';
        }
        
        alert('Complaint closed successfully!');
      } catch (err) {
        console.error('Error closing complaint:', err);
        alert('Failed to close complaint. Please try again.');
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.table th {
  user-select: none;
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