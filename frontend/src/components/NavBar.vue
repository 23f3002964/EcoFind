<template>

  <div
    :class="['d-flex flex-column bg-light shadow-sm position-relative', isCollapsed ? 'sidebar-collapsed' : 'sidebar-expanded']"
    style="min-height: 100vh; transition: all 0.3s;"
  >
    <!-- Collapse Button -->
    <div class="collapse-btn">
      <button
        class="btn btn-sm btn-outline-secondary"
        @click="toggleSidebar"
        :title="isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
        aria-label="Toggle sidebar"
      >
        <i :class="isCollapsed ? 'bi bi-chevron-double-right' : 'bi bi-chevron-double-left'"></i>
      </button>
    </div>

      <!-- Brand Section -->
      <div class="d-flex align-items-center justify-content-center py-2 border-bottom">
        <i class="bi bi-box me-2 fs-4"></i>
        <span v-if="!isCollapsed" class="fw-bold fs-5">EcoFinds</span>
      </div>


    <!-- Navigation Links -->
    <nav class="nav flex-column mt-3">
      <!-- Admin Links -->
      <template v-if="isAuthenticated && userRole === 'Admin'">
        <router-link :to="`/admin/${userId}/dashboard`" class="nav-link d-flex align-items-center">
          <i class="bi bi-speedometer2 me-2"></i>
          <span v-if="!isCollapsed">Dashboard</span>
        </router-link>
        <router-link :to="`/admin/${userId}/users`" class="nav-link d-flex align-items-center">
          <i class="bi bi-people me-2"></i>
          <span v-if="!isCollapsed">Users</span>
        </router-link>
        <router-link :to="`/admin/${userId}/profile`" class="nav-link d-flex align-items-center">
          <i class="bi bi-person me-2"></i>
          <span v-if="!isCollapsed">Profile</span>
        </router-link>
      </template>

      <!-- User Links -->
      <template v-else-if="isAuthenticated && userRole === 'User'">
        <router-link :to="`/user/${userId}/dashboard`" class="nav-link d-flex align-items-center">
          <i class="bi bi-house-door me-2"></i>
          <span v-if="!isCollapsed">Dashboard</span>
        </router-link>
        <router-link to="/products" class="nav-link d-flex align-items-center">
          <i class="bi bi-search me-2"></i>
          <span v-if="!isCollapsed">Browse</span>
        </router-link>
        <router-link to="/chats" class="nav-link d-flex align-items-center">
          <i class="bi bi-chat-dots me-2"></i>
          <span v-if="!isCollapsed">Messages</span>
        </router-link>
        <router-link to="/saved-searches" class="nav-link d-flex align-items-center">
          <i class="bi bi-bookmark me-2"></i>
          <span v-if="!isCollapsed">Saved Searches</span>
        </router-link>
        <router-link to="/price-alerts" class="nav-link d-flex align-items-center">
          <i class="bi bi-bell me-2"></i>
          <span v-if="!isCollapsed">Price Alerts</span>
        </router-link>
        <router-link :to="`/user/${userId}/profile`" class="nav-link d-flex align-items-center">
          <i class="bi bi-person me-2"></i>
          <span v-if="!isCollapsed">Profile</span>
        </router-link>
      </template>

      <!-- Guest Links -->
      <template v-else>
        <router-link to="/" class="nav-link d-flex align-items-center">
          <i class="bi bi-house me-2"></i>
          <span v-if="!isCollapsed">Home</span>
        </router-link>
        <router-link to="/products" class="nav-link d-flex align-items-center">
          <i class="bi bi-search me-2"></i>
          <span v-if="!isCollapsed">Browse</span>
        </router-link>
        <router-link to="/about" class="nav-link d-flex align-items-center">
          <i class="bi bi-info-circle me-2"></i>
          <span v-if="!isCollapsed">About</span>
        </router-link>
        <router-link to="/signup" class="nav-link d-flex align-items-center">
          <i class="bi bi-person-plus me-2"></i>
          <span v-if="!isCollapsed">SignUp</span>
        </router-link>
        <router-link to="/login" class="nav-link d-flex align-items-center">
          <i class="bi bi-box-arrow-in-right me-2"></i>
          <span v-if="!isCollapsed">LogIn</span>
        </router-link>
      </template>
    </nav>

    <!-- Logout at Bottom -->
    <div class="mt-auto mb-3 px-3">
      <div
        class="nav-link d-flex align-items-center text-danger"
        style="cursor: pointer;"
        @click="handleLogout"
      >
        <i class="bi bi-box-arrow-right me-2"></i>
        <span v-if="!isCollapsed">Logout</span>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'NavBar',
  data() {
    return {
      isCollapsed: false
    };
  },
  computed: {
    ...mapState(['authData', 'isAuthenticated']),
    ...mapGetters(['userData']),
    userRole() {
      return this.authData?.role;
    },
    userId() {
      return this.authData?.id;
    },
    userProfileImage() {
      // Replace this with actual dynamic image path if available
      return this.userData?.profile_image || 'https://via.placeholder.com/40';
    }
  },
  methods: {
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    },
    handleLogout() {
      if (confirm('Are you sure you want to logout?')) {
        this.$store.dispatch('logout');
        this.$router.push({ name: 'login' });
      }
    }
  }
};
</script>

<style scoped>
.sidebar-expanded {
  width: 240px;
}

.sidebar-collapsed {
  width: 70px;
}

.nav-link {
  padding: 10px 20px;
  font-size: 0.95rem;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #e9ecef;
  border-radius: 5px;
}

.bi {
  font-size: 1.2rem;
}

.collapse-btn {
  position: absolute;
  top: 50%;
  right: -14px;
  transform: translateY(-50%);
  z-index: 1000;
}

.collapse-btn button {
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.1);
}
</style>