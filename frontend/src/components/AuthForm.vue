<template>
  <div class="card shadow p-4" :style="{ width: '100%', maxWidth: maxWidth }">
    <h4 class="mb-4 fw-semibold">{{ title }}</h4>
    <form @submit.prevent="onSubmit">
      <slot></slot>
      
      <!-- Terms and Conditions Checkbox (optional) -->
      <div v-if="showTerms" class="form-check mb-3">
        <input v-model="acceptTerms" type="checkbox" class="form-check-input" id="term" required />
        <label class="form-check-label" for="term">I accept the <a href="#" class="">Terms and Conditions</a></label>
      </div>

      <!-- Submit Button -->
      <button type="submit" :class="submitButtonClass">{{ submitButtonText }}</button>

      <!-- Links -->
      <div class="mt-2">
        <small>
          <slot name="links"></slot>
        </small>
      </div>

      <!-- Messages -->
      <div v-if="successMessage" class="mt-3 fw-bold text-success">{{ successMessage }}</div>
      <div v-if="errorMessage" class="mt-2 fw-bold text-danger">{{ errorMessage }}</div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AuthForm',
  props: {
    title: {
      type: String,
      required: true
    },
    onSubmit: {
      type: Function,
      required: true
    },
    maxWidth: {
      type: String,
      default: '400px'
    },
    submitButtonText: {
      type: String,
      default: 'Submit'
    },
    submitButtonClass: {
      type: String,
      default: 'btn btn-primary w-100'
    },
    showTerms: {
      type: Boolean,
      default: false
    },
    successMessage: {
      type: String,
      default: null
    },
    errorMessage: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      acceptTerms: false
    };
  }
};
</script>

<style scoped>
/* Component styles if needed */
</style>