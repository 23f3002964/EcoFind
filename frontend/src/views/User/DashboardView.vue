<template>
  <!-- Loader -->
  <div v-if="loading" class="container my-4">
    <Loader1 />
  </div>

  <div v-else class="container my-4">
    <h4>User Dashboard</h4>

    <!-- Quick Links Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Quick Actions</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-3 col-sm-6 mb-3">
                <router-link to="/products" class="btn btn-primary w-100">
                  <i class="bi bi-search me-1"></i> Browse Products
                </router-link>
              </div>
              <div class="col-md-3 col-sm-6 mb-3">
                <router-link to="/add-product" class="btn btn-success w-100">
                  <i class="bi bi-plus-lg me-1"></i> Add Product
                </router-link>
              </div>
              <div class="col-md-3 col-sm-6 mb-3">
                <router-link to="/user/1/listings" class="btn btn-info w-100">
                  <i class="bi bi-list-ul me-1"></i> My Listings
                </router-link>
              </div>
              <div class="col-md-3 col-sm-6 mb-3">
                <router-link to="/user/1/cart" class="btn btn-warning w-100">
                  <i class="bi bi-cart me-1"></i> My Cart
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3 col-sm-6 mb-3" v-for="(card, index) in cards" :key="index">
        <div class="card text-white bg-primary h-100">
          <div class="card-body d-flex flex-column justify-content-between">
            <h5 class="card-title">{{ card.title }}</h5>
            <h3>{{ card.value }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity Table -->
    <div class="card">
      <div class="card-header">Recent Activity</div>
      <div class="card-body p-0">
        <table class="table mb-0">
          <thead class="table-light">
            <tr>
              <th>Date</th>
              <th>Activity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in tableData" :key="index">
              <td>{{ row.date }}</td>
              <td>{{ row.activity }}</td>
              <td><span class="badge bg-success">{{ row.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import Loader1 from '@/components/Loader1.vue';
export default {
  name: 'Dashboard',
  data() {
    return {
      userId: this.$route.params.userId || 1,
      loading: false,
      cards: [
        { title: 'My Listings', value: 5 },
        { title: 'Purchases', value: 12 },
        { title: 'Messages', value: 3 },
        { title: 'Saved Items', value: 8 },
      ],
      tableData: [
        { date: '2025-05-18', activity: 'Added new product', status: 'Success' },
        { date: '2025-05-17', activity: 'Placed bid on auction', status: 'Success' },
        { date: '2025-05-16', activity: 'Updated profile', status: 'Success' },
      ],
    }
  },

  components: {
    Loader1
  },

  computed: {

  }
}
</script>

<style scoped>
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}
</style>