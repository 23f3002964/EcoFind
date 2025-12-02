<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>User Reviews</h4>
      <div v-if="currentUser && currentUser.id !== userId" class="d-flex gap-2">
        <button 
          class="btn btn-primary" 
          @click="showReviewModal = true"
          v-if="canReview"
        >
          <i class="bi bi-star"></i> Leave Review
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
    <div v-else-if="reviews.length === 0" class="text-center py-5">
      <i class="bi bi-star" style="font-size: 3rem;"></i>
      <h5 class="mt-3">No reviews yet</h5>
      <p class="text-muted">This user doesn't have any reviews yet.</p>
      <button 
        v-if="currentUser && currentUser.id !== userId && canReview" 
        class="btn btn-primary" 
        @click="showReviewModal = true"
      >
        Be the first to leave a review
      </button>
    </div>

    <!-- Reviews List -->
    <div v-else>
      <div class="row">
        <div class="col-lg-8">
          <div class="card mb-3" v-for="review in reviews" :key="review.id">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <div class="d-flex align-items-center">
                  <div class="me-3">
                    <strong>{{ review.reviewer.username }}</strong>
                    <div class="text-muted small">
                      <i class="bi bi-star-fill text-warning"></i>
                      {{ review.reviewer.rating ? review.reviewer.rating.toFixed(1) : 'N/A' }}
                    </div>
                  </div>
                </div>
                <div>
                  <div class="d-flex">
                    <i 
                      v-for="i in 5" 
                      :key="i" 
                      class="bi" 
                      :class="i <= review.rating ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                    ></i>
                  </div>
                  <div class="text-muted small text-end">
                    {{ formatDate(review.created_at) }}
                  </div>
                </div>
              </div>
              
              <div class="mt-3">
                <p class="mb-0">{{ review.comment }}</p>
              </div>
              
              <div v-if="review.product_title" class="mt-2">
                <small class="text-muted">For: {{ review.product_title }}</small>
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
              <h5>Rating Summary</h5>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <div class="display-4">{{ averageRating.toFixed(1) }}</div>
                <div class="d-flex justify-content-center">
                  <i 
                    v-for="i in 5" 
                    :key="i" 
                    class="bi" 
                    :class="i <= Math.round(averageRating) ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                  ></i>
                </div>
                <div class="text-muted">{{ totalReviews }} reviews</div>
              </div>
              
              <hr>
              
              <div class="d-flex justify-content-between align-items-center mb-2" v-for="star in [5, 4, 3, 2, 1]" :key="star">
                <div class="d-flex align-items-center">
                  <span>{{ star }}</span>
                  <i class="bi bi-star-fill text-warning ms-1"></i>
                </div>
                <div class="flex-grow-1 mx-2">
                  <div class="progress" style="height: 8px;">
                    <div 
                      class="progress-bar bg-warning" 
                      role="progressbar" 
                      :style="{ width: getStarPercentage(star) + '%' }"
                      :aria-valuenow="getStarPercentage(star)" 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                    ></div>
                  </div>
                </div>
                <div>{{ getStarCount(star) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Review Modal -->
  <div class="modal fade" :class="{ show: showReviewModal }" tabindex="-1" v-if="showReviewModal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Leave a Review</h5>
          <button type="button" class="btn-close" @click="showReviewModal = false"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitReview">
            <div class="mb-3">
              <label class="form-label">Rating</label>
              <div class="d-flex">
                <i 
                  v-for="i in 5" 
                  :key="i" 
                  class="bi bi-star fs-3" 
                  :class="i <= rating ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                  @click="rating = i"
                  style="cursor: pointer;"
                ></i>
              </div>
            </div>
            
            <div class="mb-3">
              <label for="comment" class="form-label">Comment</label>
              <textarea 
                class="form-control" 
                id="comment" 
                rows="4" 
                v-model="comment"
                placeholder="Share your experience with this user..."
              ></textarea>
            </div>
            
            <div v-if="reviewError" class="alert alert-danger">
              {{ reviewError }}
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showReviewModal = false">Cancel</button>
          <button type="button" class="btn btn-primary" @click="submitReview" :disabled="submitting">
            <span v-if="!submitting">Submit Review</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm" role="status"></span>
              Submitting...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Backdrop for modal -->
  <div v-if="showReviewModal" class="modal-backdrop fade show"></div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';

export default {
  name: 'UserReviewsView',
  props: {
    userId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      reviews: [],
      loading: false,
      submitting: false,
      error: null,
      reviewError: null,
      currentPage: 1,
      totalPages: 1,
      totalReviews: 0,
      averageRating: 0,
      ratingDistribution: {},
      canReview: false,
      
      // Review modal
      showReviewModal: false,
      rating: 0,
      comment: ''
    };
  },
  
  computed: {
    ...mapState(['isAuthenticated', 'authData']),
    currentUser() {
      return this.authData ? { id: this.authData.id } : null;
    }
  },
  
  mounted() {
    this.fetchReviews();
    this.checkReviewEligibility();
  },
  
  methods: {
    async fetchReviews() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`/api/users/${this.userId}/reviews`, {
          params: {
            page: this.currentPage,
            per_page: 10
          }
        });
        
        this.reviews = response.data.reviews || [];
        this.totalPages = response.data.pages || 1;
        this.totalReviews = response.data.total || 0;
        
        // Calculate average rating and distribution
        if (this.reviews.length > 0) {
          const totalRating = this.reviews.reduce((sum, review) => sum + review.rating, 0);
          this.averageRating = totalRating / this.reviews.length;
          
          // Calculate rating distribution
          this.ratingDistribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
          this.reviews.forEach(review => {
            this.ratingDistribution[review.rating]++;
          });
        } else {
          this.averageRating = 0;
        }
      } catch (err) {
        console.error('Error fetching reviews:', err);
        this.error = 'Failed to load reviews. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async checkReviewEligibility() {
      if (!this.isAuthenticated || this.currentUser.id === this.userId) {
        return;
      }
      
      try {
        // In a full implementation, this would check if the current user has transacted with the user
        // For now, we'll assume they can review if they're authenticated and not the same user
        this.canReview = true;
      } catch (err) {
        console.error('Error checking review eligibility:', err);
        this.canReview = false;
      }
    },
    
    async submitReview() {
      if (this.rating === 0) {
        this.reviewError = 'Please select a rating';
        return;
      }
      
      this.submitting = true;
      this.reviewError = null;
      
      try {
        await axios.post('/api/reviews', {
          reviewee_id: this.userId,
          rating: this.rating,
          comment: this.comment
        });
        
        // Close modal and reset form
        this.showReviewModal = false;
        this.rating = 0;
        this.comment = '';
        
        // Refresh reviews
        this.fetchReviews();
        
        // Show success message
        alert('Review submitted successfully!');
      } catch (err) {
        console.error('Error submitting review:', err);
        this.reviewError = err.response?.data?.error || 'Failed to submit review. Please try again.';
      } finally {
        this.submitting = false;
      }
    },
    
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    getStarCount(star) {
      return this.ratingDistribution[star] || 0;
    },
    
    getStarPercentage(star) {
      if (this.totalReviews === 0) return 0;
      return ((this.ratingDistribution[star] || 0) / this.totalReviews) * 100;
    },
    
    changePage(page) {
      if (page < 1 || page > this.totalPages) return;
      this.currentPage = page;
      this.fetchReviews();
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.progress {
  border-radius: 4px;
}

.modal-backdrop {
  z-index: 1050;
}

.modal {
  z-index: 1051;
}
</style>