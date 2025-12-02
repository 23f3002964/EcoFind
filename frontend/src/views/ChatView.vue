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
        <!-- Messages Area -->
        <div class="flex-grow-1 overflow-auto mb-3" ref="messagesContainer">
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="mb-3"
            :class="{ 'text-end': message.sender_id === currentUser.id }"
          >
            <div 
              class="d-inline-block p-2 rounded"
              :class="message.sender_id === currentUser.id ? 'bg-primary text-white' : 'bg-light'"
              style="max-width: 75%;"
            >
              <div>{{ message.content }}</div>
              <small 
                class="text-muted" 
                :class="{ 'text-white-50': message.sender_id === currentUser.id }"
              >
                {{ formatTime(message.timestamp) }}
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
  props: {
    chatId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      chat: null,
      messages: [],
      otherUser: null,
      newMessage: '',
      loading: false,
      sending: false,
      error: null,
      currentUser: {
        id: 1 // This would come from auth state
      }
    };
  },
  
  computed: {
    chatPartnerName() {
      return this.otherUser ? `${this.otherUser.first_name} ${this.otherUser.last_name}` : 'Chat';
    }
  },
  
  mounted() {
    this.fetchChat();
    this.setupWebSocket(); // In a real app, we'd use WebSocket for real-time messaging
  },
  
  beforeUnmount() {
    if (this.websocket) {
      this.websocket.close();
    }
  },
  
  methods: {
    async fetchChat() {
      this.loading = true;
      this.error = null;
      
      try {
        // Fetch chat details
        const chatResponse = await axios.get(`/api/chats/${this.chatId}`);
        this.chat = chatResponse.data;
        
        // Fetch messages
        const messagesResponse = await axios.get(`/api/chats/${this.chatId}/messages`);
        this.messages = messagesResponse.data.messages || [];
        
        // Get other user info
        const otherUserId = this.chat.participants.find(id => id !== this.currentUser.id);
        const userResponse = await axios.get(`/api/users/${otherUserId}`);
        this.otherUser = userResponse.data;
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      } catch (err) {
        console.error('Error fetching chat:', err);
        this.error = 'Failed to load chat. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async sendMessage() {
      if (!this.newMessage.trim()) return;
      
      this.sending = true;
      
      try {
        const response = await axios.post(`/api/chats/${this.chatId}/messages`, {
          content: this.newMessage.trim()
        });
        
        this.messages.push(response.data);
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
    
    setupWebSocket() {
      // In a real implementation, we would connect to a WebSocket server
      // For now, we'll simulate real-time updates with periodic polling
      this.messagePolling = setInterval(this.fetchNewMessages, 5000);
    },
    
    async fetchNewMessages() {
      try {
        const response = await axios.get(`/api/chats/${this.chatId}/messages?since=${this.getLastMessageTimestamp()}`);
        if (response.data.messages && response.data.messages.length > 0) {
          this.messages = [...this.messages, ...response.data.messages];
          
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }
      } catch (err) {
        console.error('Error fetching new messages:', err);
      }
    },
    
    getLastMessageTimestamp() {
      if (this.messages.length === 0) return null;
      return this.messages[this.messages.length - 1].timestamp;
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