<template>
  <div class="container my-5">
  <h3 class="mb-4">User Management</h3>

  <table class="table table-hover">
    <thead class="table-light">
      <tr>
        <th scope="col">#</th>
        <th scope="col">Name</th>
        <th scope="col">Email</th>
        <th scope="col">Role</th>
        <th scope="col">Status</th>
        <th scope="col">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">1</th>
        <td>John Doe</td>
        <td>john@example.com</td>
        <td>Admin</td>
        <td><span class="badge bg-success">Active</span></td>
        <td>
          <button class="btn btn-sm btn-primary">Edit</button>
          <button class="btn btn-sm btn-danger">Delete</button>
        </td>
      </tr>
      <tr>
        <th scope="row">2</th>
        <td>Jane Smith</td>
        <td>jane@example.com</td>
        <td>User</td>
        <td><span class="badge bg-secondary">Inactive</span></td>
        <td>
          <button class="btn btn-sm btn-primary">Edit</button>
          <button class="btn btn-sm btn-danger">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
</template>

<script>
export default {
    name:'UserManagement'
}
</script>

<style>

</style>