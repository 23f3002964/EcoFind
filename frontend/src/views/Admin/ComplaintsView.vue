<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>Complaints Management</h4>
      <div class="d-flex gap-2">
        <select class="form-select" v-model="filterStatus" @change="filterComplaints">
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
                <th @click="sort('users_involved')" style="cursor: pointer;">
                  Users Involved <i class="bi" :class="getSortIcon('users_involved')"></i>
                </th>
                <th @click="sort('item')" style="cursor: pointer;">
                  Item <i class="bi" :class="getSortIcon('item')"></i>
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
                  <div v-for="user in complaint.users_involved" :key="user.id" class="d-flex align-items-center mb-1">
                    <img 
                      :src="user.avatar || 'https://via.placeholder.com/30'" 
                      class="rounded-circle me-2" 
                      alt="User"
                      width="30"
                      height="30"
                    >
                    <span>{{ user.name }}</span>
                  </div>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <img 
                      :src="complaint.item.image || 'https://via.placeholder.com/40'" 
                      class="me-2" 
                      alt="Item"
                      width="40"
                      height="40"
                    >
                    <span>{{ complaint.item.name }}</span>
                  </div>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(complaint.status)">
                    {{ complaint.status.replace('_', ' ') | capitalize }}
                  </span>
                </td>
                <td>{{ formatDate(complaint.date_reported) }}</td>
                <td>
                  <div class="btn-group" role="group">
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="viewComplaintDetails(complaint.id)"
                    >
                      <i class="bi bi-eye"></i> View
                    </button>
                    <button 
                      v-if="complaint.status !== 'resolved' && complaint.status !== 'closed'"
                      class="btn btn-sm btn-outline-success"
                      @click="resolveComplaint(complaint.id)"
                    >
                      <i class="bi bi-check-circle"></i> Resolve
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
</template>

<script>
import axios from 'axios';

export default {
  name: 'ComplaintsManagementView',
  data() {
    return {
      complaints: [],
      loading: false,
      error: null,
      filterStatus: '',
      sortKey: 'date_reported',
      sortOrder: 'desc',
      currentPage: 1,
      totalPages: 1,
      itemsPerPage: 10
    };
  },
  
  computed: {
    filteredComplaints() {
      let result = [...this.complaints];
      
      // Apply status filter
      if (this.filterStatus) {
        result = result.filter(complaint => complaint.status === this.filterStatus);
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let modifier = this.sortOrder === 'asc' ? 1 : -1;
        if (a[this.sortKey] < b[this.sortKey]) return -1 * modifier;
        if (a[this.sortKey] > b[this.sortKey]) return 1 * modifier;
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
  },
  
  methods: {
    async fetchComplaints() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/admin/complaints', {
          params: {
            page: this.currentPage,
            limit: this.itemsPerPage
          }
        });
        
        this.complaints = response.data.complaints || [];
        this.totalPages = response.data.total_pages || 1;
      } catch (err) {
        console.error('Error fetching complaints:', err);
        this.error = 'Failed to load complaints. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    filterComplaints() {
      // Filtering is handled by computed property
      this.currentPage = 1; // Reset to first page when filtering
    },
    
    sort(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortOrder = 'asc';
      }
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
    },
    
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchComplaints();
    },
    
    viewComplaintDetails(complaintId) {
      // Navigate to complaint detail view
      this.$router.push(`/admin/complaints/${complaintId}`);
    },
    
    async resolveComplaint(complaintId) {
      if (!confirm('Are you sure you want to mark this complaint as resolved?')) return;
      
      try {
        await axios.patch(`/api/admin/complaints/${complaintId}`, {
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
</style>