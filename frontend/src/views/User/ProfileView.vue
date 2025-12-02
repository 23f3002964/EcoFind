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
        <ProfileCard 
          :profile-image="user.profile_picture || 'https://via.placeholder.com/150'"
          :first-name="user.first_name"
          :last-name="user.last_name"
          :username="user.email || 'username'"
          :bio="user.bio"
        >
          <template #actions>
            <button class="btn btn-outline-primary">Edit Profile</button>
            <button class="btn btn-outline-secondary">Change Password</button>
            <hr />
            <button class="btn custom-danger" @click="handleLogout">Logout</button>
          </template>
        </ProfileCard>
      </div>

      <!-- Profile Details -->
      <div class="col-lg-8">
        <ProfileInfo 
          title="Personal Information"
          :fields="[
            { label: 'Full Name', value: `${user.first_name} ${user.last_name}` },
            { label: 'Email', value: userEmail },
            { label: 'Date of Birth', value: user.dob },
            { label: 'Gender', value: user.gender },
            { label: 'Bio', value: user.bio },
            { label: 'Joined', value: formatDate(user.created_at) }
          ]"
        >
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
        </ProfileInfo>
      </div>
    </div>
  </div>
</template>


<script>
import { mapGetters } from 'vuex';
import Loader1 from '@/components/Loader1.vue'
import ProfileCard from '@/components/ProfileCard.vue'
import ProfileInfo from '@/components/ProfileInfo.vue'

const stored = sessionStorage.getItem('authData');
const authData = stored ? JSON.parse(stored) : {};

export default {
  name: 'UserProfile',
  data() {
    return {
      loading: true,
      error: null,
    }
  },
  components: {
    Loader1,
    ProfileCard,
    ProfileInfo
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
    handleLogout() {
      if (confirm('Are you sure you want to logout?')) {
        this.$store.dispatch('logout');
        this.$router.push({ name: 'login' });
      }
    }
  },
}
</script>

<style scoped>
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
