<template>
  <div class="container my-4">
    <div class="d-flex align-items-center mb-4">
      <button class="btn btn-outline-secondary me-3" @click="$router.back()">
        <i class="bi bi-arrow-left"></i>
      </button>
      <div>
        <h4 class="mb-0">{{ chatPartnerName }}</h4>
        <small class="text-muted" v-if="otherUser">
          {{ otherUser.online ? 'Online' : 'Offline' }}
        </small>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Chat Interface -->
    <div v-else class="card">
      <div class="card-body d-flex flex-column" style="height: 70vh;">
        <!-- Product Info -->
        <div v-if="product" class="border-bottom pb-3 mb-3">
          <div class="d-flex align-items-center">
            <img 
              :src="getProductImage(product)" 
              class="img-fluid rounded" 
              :alt="product.title"
              style="width: 60px; height: 60px; object-fit: cover;"
            >
            <div class="ms-3">
              <h6 class="mb-0">{{ product.title }}</h6>
              <p class="text-muted mb-0">${{ product.price }}</p>
            </div>
          </div>
        </div>
        
        <!-- Messages Area -->
        <div class="flex-grow-1 overflow-auto mb-3" ref="messagesContainer">
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="mb-3"
            :class="{ 'text-end': message.is_from_me }"
          >
            <div 
              class="d-inline-block p-2 rounded"
              :class="message.is_from_me ? 'bg-primary text-white' : 'bg-light'"
              style="max-width: 75%;"
            >
              <div>{{ message.message }}</div>
              <small 
                class="text-muted" 
                :class="{ 'text-white-50': message.is_from_me }"
              >
                {{ formatTime(message.created_at) }}
              </small>
            </div>
          </div>
        </div>
        
        <!-- Message Input -->
        <div class="mt-auto">
          <div class="input-group">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Type your message..." 
              v-model="newMessage"
              @keyup.enter="sendMessage"
              :disabled="sending"
            >
            <button 
              class="btn btn-primary" 
              type="button" 
              @click="sendMessage"
              :disabled="!newMessage.trim() || sending"
            >
              <span v-if="!sending">Send</span>
              <span v-else>
                <span class="spinner-border spinner-border-sm" role="status"></span>
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ChatView',
  data() {
    return {
      messages: [],
      otherUser: null,
      product: null,
      newMessage: '',
      loading: false,
      sending: false,
      error: null,
      pollingInterval: null
    };
  },
  
  computed: {
    chatPartnerName() {
      return this.otherUser ? `${this.otherUser.username}` : 'Chat';
    }
  },
  
  async mounted() {
    await this.fetchChatData();
    this.setupPolling();
  },
  
  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  },
  
  methods: {
    getProductImage(product) {
      if (product.images && product.images.length > 0) {
        return product.images[0];
      }
      return 'https://via.placeholder.com/80';
    },
    
    async fetchChatData() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get route parameters
        const otherUserId = this.$route.params.other_user_id || this.$route.params.chatId;
        const productId = this.$route.query.product_id;
        
        // Fetch messages
        const messagesResponse = await axios.get(`/api/chats/${otherUserId}?product_id=${productId}`);
        this.messages = messagesResponse.data.messages || [];
        
        // Fetch other user info
        const userResponse = await axios.get(`/api/users/${otherUserId}`);
        this.otherUser = userResponse.data;
        
        // Fetch product info if productId is provided
        if (productId) {
          const productResponse = await axios.get(`/api/products/${productId}`);
          this.product = productResponse.data;
        }
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      } catch (err) {
        console.error('Error fetching chat data:', err);
        this.error = 'Failed to load chat. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async sendMessage() {
      if (!this.newMessage.trim()) return;
      
      this.sending = true;
      
      try {
        const otherUserId = this.$route.params.other_user_id || this.$route.params.chatId;
        const productId = this.$route.query.product_id;
        
        const response = await axios.post('/api/chats', {
          receiver_id: otherUserId,
          product_id: productId,
          message: this.newMessage.trim()
        });
        
        // Add message to local list
        this.messages.push({
          id: response.data.message_id || Date.now(),
          message: this.newMessage.trim(),
          is_from_me: true,
          created_at: new Date().toISOString()
        });
        
        this.newMessage = '';
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      } catch (err) {
        console.error('Error sending message:', err);
        this.error = 'Failed to send message. Please try again.';
      } finally {
        this.sending = false;
      }
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    setupPolling() {
      // Poll for new messages every 5 seconds
      this.pollingInterval = setInterval(this.fetchNewMessages, 5000);
    },
    
    async fetchNewMessages() {
      try {
        const otherUserId = this.$route.params.other_user_id || this.$route.params.chatId;
        const productId = this.$route.query.product_id;
        
        const response = await axios.get(`/api/chats/${otherUserId}?product_id=${productId}`);
        const newMessages = response.data.messages || [];
        
        // Check if there are new messages
        if (newMessages.length > this.messages.length) {
          this.messages = newMessages;
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }
      } catch (err) {
        console.error('Error fetching new messages:', err);
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.overflow-auto {
  overflow-y: auto;
  max-height: 500px;
}
</style>