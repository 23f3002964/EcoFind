<template>
  <div class="card shadow-sm text-center p-4">
    <img :src="profileImage" alt="Profile" class="rounded-circle mb-3 mx-auto" width="120" height="120" />
    <h4 class="fw-bold mb-0">{{ fullName }}</h4>
    <small class="text-muted">@{{ username }}</small>

    <hr class="my-4" />

    <p class="text-muted">{{ bio || 'No bio available' }}</p>

    <div class="d-grid gap-2">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileCard',
  props: {
    profileImage: {
      type: String,
      default: 'https://via.placeholder.com/150'
    },
    firstName: {
      type: String,
      default: ''
    },
    lastName: {
      type: String,
      default: ''
    },
    username: {
      type: String,
      default: 'username'
    },
    bio: {
      type: String,
      default: null
    }
  },
  computed: {
    fullName() {
      return `${this.firstName} ${this.lastName}`.trim() || 'User';
    }
  }
};
</script>

<style scoped>
/* Component styles if needed */
</style>