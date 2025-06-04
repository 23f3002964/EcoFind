<template>
  <div class="container my-4">
    <h4>Admin's Dashboard</h4>
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
    name:'AdminDashboard'
}
</script>

<style>

</style>