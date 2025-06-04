<template>
  <div class="top-header d-flex justify-content-end align-items-center px-4 py-2 border-bottom bg-white">
    <div class="d-flex align-items-center gap-2">
      <img
        :src="userProfileImage"
        alt="User"
        class="rounded-circle"
        width="36"
        height="36"
      />
      <span class="fw-medium">{{ userData?.first_name }}</span>
    </div>
  </div>
</template>


<script>
import { mapGetters } from 'vuex';

export default {
  name: 'HeaderBar',
  computed: {
    ...mapGetters(['userData']),
    userProfileImage() {
      return this.userData?.profile_image || 'https://via.placeholder.com/40';
    }
  }
};
</script>

<style scoped>
.top-header {
  height: 60px;
}
</style>
