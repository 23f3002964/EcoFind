<template>
  <div class="card shadow-sm p-4">
    <h5 class="fw-bold mb-4">{{ title }}</h5>
    
    <div v-for="(field, index) in fields" :key="index" class="row mb-3">
      <div class="col-sm-4 text-muted">{{ field.label }}</div>
      <div class="col-sm-8">{{ field.value }}</div>
    </div>
    
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'ProfileInfo',
  props: {
    title: {
      type: String,
      default: 'Information'
    },
    fields: {
      type: Array,
      default: () => [],
      validator: (fields) => {
        return fields.every(field => 
          typeof field === 'object' && 
          typeof field.label === 'string' && 
          (typeof field.value === 'string' || typeof field.value === 'number')
        );
      }
    }
  }
};
</script>

<style scoped>
/* Component styles if needed */
</style>