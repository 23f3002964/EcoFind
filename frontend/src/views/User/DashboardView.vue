<template>
  <!-- Loader -->
  <div v-if="loading" class="container my-4">
    <Loader1 />
  </div>

  <div v-else class="container my-4">
    <h4>User's Dashboard</h4>

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
  <div>{{ }}</div>
</template>

<script>
import Loader1 from '@/components/Loader1.vue';
export default {
  name: 'Dashboard',
  data() {
    return {
      userId: this.$route.params,
      loading: false,
      cards: [
        { title: 'Logins', value: 25 },
        { title: 'Tasks Completed', value: 42 },
        { title: 'Messages', value: 12 },
        { title: 'Notifications', value: 5 },
      ],
      tableData: [
        { date: '2025-05-18', activity: 'Logged in', status: 'Success' },
        { date: '2025-05-17', activity: 'Updated Profile', status: 'Success' },
        { date: '2025-05-16', activity: 'Password Change', status: 'Success' },
      ],
    }
  },

  components: {
    Loader1
  },

  computed: {

  },

}

</script>


<style scoped></style>
