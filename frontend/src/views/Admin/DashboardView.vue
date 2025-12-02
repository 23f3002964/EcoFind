<template>
  <div class="container my-4">
    <h4>Admin Dashboard</h4>
    
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
                <router-link to="/admin/1/users" class="btn btn-primary w-100">
                  <i class="bi bi-people me-1"></i> Manage Users
                </router-link>
              </div>
              <div class="col-md-3 col-sm-6 mb-3">
                <router-link to="/admin/1/complaints" class="btn btn-warning w-100">
                  <i class="bi bi-exclamation-triangle me-1"></i> Complaints
                </router-link>
              </div>
              <div class="col-md-3 col-sm-6 mb-3">
                <router-link to="/admin/1/profile" class="btn btn-info w-100">
                  <i class="bi bi-person me-1"></i> My Profile
                </router-link>
              </div>
              <div class="col-md-3 col-sm-6 mb-3">
                <button class="btn btn-outline-secondary w-100" @click="refreshData">
                  <i class="bi bi-arrow-clockwise me-1"></i> Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <h5 class="card-title">Users</h5>
            <p class="card-text display-6">1,230</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Active Sessions</h5>
            <p class="card-text display-6">87</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <h5 class="card-title">Reports</h5>
            <p class="card-text display-6">56</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-danger">
          <div class="card-body">
            <h5 class="card-title">Errors</h5>
            <p class="card-text display-6">12</p>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        Recent User Activity
      </div>
      <table class="table mb-0">
        <thead>
          <tr>
            <th scope="col">User</th>
            <th scope="col">Activity</th>
            <th scope="col">Time</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>alice@example.com</td>
            <td>Logged in</td>
            <td>10:45 AM</td>
          </tr>
          <tr>
            <td>bob@example.com</td>
            <td>Viewed report</td>
            <td>10:42 AM</td>
          </tr>
          <tr>
            <td>carol@example.com</td>
            <td>Updated profile</td>
            <td>10:30 AM</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
    name:'AdminDashboard',
    methods: {
      refreshData() {
        // Reload the page to refresh data
        window.location.reload();
      }
    }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>