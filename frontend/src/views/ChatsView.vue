<template>
  <div class="container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4>{{ $t('messages') }}</h4>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">{{ $t('loading') }}...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="conversations.length === 0" class="text-center py-5">
      <i class="bi bi-chat-dots" style="font-size: 3rem;"></i>
      <h5 class="mt-3">{{ $t('no_conversations_yet') }}</h5>
      <p class="text-muted">{{ $t('conversations_will_appear_here') }}</p>
    </div>

    <!-- Conversations List -->
    <div v-else>
      <div class="list-group">
        <div 
          v-for="conversation in conversations" 
          :key="`${conversation.other_user.id}-${conversation.product?.id || 0}`"
          class="list-group-item list-group-item-action"
          @click="openChat(conversation)"
        >
          <div class="d-flex">
            <div class="flex-shrink-0">
              <img 
                :src="getProductImage(conversation.product)" 
                class="img-fluid rounded" 
                :alt="conversation.product?.title || 'Product'"
                style="width: 60px; height: 60px; object-fit: cover;"
                v-if="conversation.product"
              >
              <div 
                class="bg-secondary rounded d-flex align-items-center justify-content-center" 
                style="width: 60px; height: 60px;"
                v-else
              >
                <i class="bi bi-person-fill text-white"></i>
              </div>
            </div>
            <div class="flex-grow-1 ms-3">
              <div class="d-flex justify-content-between">
                <h6 class="mb-1">{{ conversation.other_user.username }}</h6>
                <small class="text-muted">{{ formatTime(conversation.last_message.created_at) }}</small>
              </div>
              <p class="mb-1">{{ conversation.last_message.message }}</p>
              <div class="d-flex justify-content-between">
                <small class="text-muted">{{ conversation.product?.title || $t('general_conversation') }}</small>
                <span 
                  v-if="conversation.unread_count > 0" 
                  class="badge bg-primary rounded-pill"
                >
                  {{ conversation.unread_count }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ChatsView',
  data() {
    return {
      conversations: [],
      loading: false,
      error: null
    };
  },
  
  mounted() {
    this.fetchChats();
  },
  
  methods: {
    getProductImage(product) {
      if (product && product.images && product.images.length > 0) {
        return product.images[0];
      }
      return 'https://via.placeholder.com/60';
    },
    
    async fetchChats() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get('/api/chats');
        this.conversations = response.data.conversations || [];
      } catch (err) {
        console.error('Error fetching chats:', err);
        this.error = this.$t('failed_load_conversations');
      } finally {
        this.loading = false;
      }
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInHours = (now - date) / (1000 * 60 * 60);
      
      if (diffInHours < 24) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }
    },
    
    openChat(conversation) {
      const productId = conversation.product?.id ? `?product_id=${conversation.product.id}` : '';
      this.$router.push(`/chat/${conversation.other_user.id}${productId}`);
    }
  }
};
</script>

<style scoped>
.list-group-item:hover {
  background-color: #f8f9fa;
  cursor: pointer;
}

.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}
</style>