<template>
  <div>
    <h1>Test Component</h1>
    <p>If you can see this, Vue components are working!</p>
  </div>
</template>

<script>
export default {
  name: 'TestComponent',
  mounted() {
    console.log('TestComponent mounted');
  }
}
</script>