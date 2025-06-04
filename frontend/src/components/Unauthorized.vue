<template>
    <div id="unauthorized" class="d-flex flex-column justify-content-center align-items-center text-center bg-light">
        <div class="mb-4">
            <i class="bi bi-shield-lock-fill text-danger" style="font-size: 4rem;"></i>
        </div>
        <h1 class="display-4 text-danger">403 - Unauthorized</h1>
        <p class="lead mb-4">You do not have permission to access this page.</p>
        <a href="/" class="btn btn-outline-primary">
            <i class="bi bi-house-door-fill me-2"></i>Return to Home
        </a>
    </div>
</template>

<script>
export default {

}
</script>
export default {
  name: 'Unauthorized'
}
<style scoped>
#unauthorized{
    min-height: 90vh;
}
</style>