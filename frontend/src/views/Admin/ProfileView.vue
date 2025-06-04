<template>
  <!-- 🔄 Loader -->
  <div v-if="loading" class="container my-4">
    <Loader1 />
  </div>

  <!-- ✅ Success Content -->
  <div v-else-if="user" class="container my-4">
    <h4>User's Profile</h4>
    <div class="row">
      <!-- Profile Sidebar -->
      <div class="col-lg-4 mb-4">
        <div class="card shadow-sm text-center p-4">
          <img :src="user.profile_picture || 'https://via.placeholder.com/150'" alt="Profile"
            class="rounded-circle mb-3 mx-auto" width="120" height="120" />
          <h4 class="fw-bold mb-0">{{ user.first_name }} {{ user.last_name }}</h4>
          <small class="text-muted">@{{ user.email || 'username' }}</small>

          <hr class="my-4" />

          <p class="text-muted">{{ user.bio || 'No bio available' }}</p>

          <div class="d-grid gap-2">
            <button class="btn btn-outline-primary">Edit Profile</button>
            <button class="btn btn-outline-secondary">Change Password</button>
            <hr />
            <button class="btn custom-danger">Logout</button>
          </div>
        </div>
      </div>

      <!-- Profile Details -->
      <div class="col-lg-8">
        <div class="card shadow-sm p-4">
          <h5 class="fw-bold mb-4">Personal Information</h5>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Full Name</div>
            <div class="col-sm-8">{{ user.first_name }} {{ user.last_name }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Email</div>
            <div class="col-sm-8">{{ userEmail }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Date of Birth</div>
            <div class="col-sm-8">{{ user.dob }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Gender</div>
            <div class="col-sm-8">{{ user.gender }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Bio</div>
            <div class="col-sm-8">{{ user.bio }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Joined</div>
            <div class="col-sm-8">{{ formatDate(user.created_at) }}</div>
          </div>

          <div class="row mb-3">
            <div class="col-sm-4 text-muted">Status</div>
            <div class="col-sm-8">
              <span class="badge bg-success">Active</span>
            </div>
          </div>

          <!-- Optional Social Section -->
          <h6 class="fw-bold mt-5">Social Links</h6>
          <div class="d-flex gap-3 mt-2">
            <a href="#" class="text-decoration-none text-primary"><i class="bi bi-twitter"></i> Twitter</a>
            <a href="#" class="text-decoration-none text-primary"><i class="bi bi-linkedin"></i> LinkedIn</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { mapGetters } from 'vuex';
import Loader1 from '@/components/Loader1.vue'

const stored = sessionStorage.getItem('authData');
const authData = stored ? JSON.parse(stored) : {};

export default {
  name: 'AdminProfile',
  data() {
    return {
      loading: true,
      error: null,
    }
  },
  components: {
    Loader1
  },
  computed: {
    ...mapGetters(['userData', 'userEmail']),
    user() {
      return this.$store.state.userData
    }
  },
  mounted() {
    if (!this.user) {
      this.loadUserData();
    } else {
      this.loading = false;
    }
  },
  methods: {
    async loadUserData() {
      this.loading = true;
      try {
        await this.$store.dispatch('fetchUserData');
      } catch (err) {
        this.error = 'Failed to load user data';
      }
      this.loading = false;
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return isNaN(date) ? 'N/A' : date.toLocaleDateString();
    },

  },
}
</script>

<style scoped>
.card {
  border-radius: 1rem;
}

.custom-danger {
  background-color: #dc3545;
  /* Bootstrap danger red */
  color: #fff;
  border: 1px solid #dc3545;
}

.custom-danger:hover {
  background-color: #b81222;
}
</style>
