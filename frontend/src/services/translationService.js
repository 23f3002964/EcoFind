import store from '@/store';

class TranslationService {
  constructor() {
    this.translations = {};
    this.currentLanguage = 'en';
  }

  async loadTranslations(lang = 'en') {
    try {
      const response = await fetch(`${store.state.backendUrl}/api/translations?lang=${lang}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.translations = await response.json();
      this.currentLanguage = lang;
      return this.translations;
    } catch (error) {
      console.error('Error loading translations:', error);
      // Return English translations as fallback
      return this.getFallbackTranslations();
    }
  }

  t(key) {
    return this.translations[key] || key;
  }

  getCurrentLanguage() {
    return this.currentLanguage;
  }

  getFallbackTranslations() {
    return {
      // Header and Navigation
      'welcome': 'Welcome to EcoFinds',
      'search_placeholder': 'Search for products...',
      'categories': 'Categories',
      'my_account': 'My Account',
      'cart': 'Cart',
      'messages': 'Messages',
      'saved_items': 'Saved Items',
      'dashboard': 'Dashboard',
      'profile': 'Profile',
      'logout': 'Logout',
      'language': 'Language',
      
      // Common Actions
      'save': 'Save',
      'cancel': 'Cancel',
      'delete': 'Delete',
      'edit': 'Edit',
      'view': 'View',
      'close': 'Close',
      'submit': 'Submit',
      'update': 'Update',
      
      // Dashboard
      'my_dashboard': 'My Dashboard',
      'total_listings': 'Total Listings',
      'active_listings': 'Active Listings',
      'sold_items': 'Sold Items',
      'total_purchases': 'Total Purchases',
      'total_sales': 'Total Sales',
      'unread_messages': 'Unread Messages',
      'user_rating': 'User Rating',
      'total_reviews': 'Total Reviews',
      
      // Product Related
      'products': 'Products',
      'add_product': 'Add Product',
      'my_listings': 'My Listings',
      'browse_products': 'Browse Products',
      'product_details': 'Product Details',
      'price': 'Price',
      'condition': 'Condition',
      'location': 'Location',
      'description': 'Description',
      'seller': 'Seller',
      'contact_seller': 'Contact Seller',
      
      // User Profile
      'personal_information': 'Personal Information',
      'full_name': 'Full Name',
      'email': 'Email',
      'date_of_birth': 'Date of Birth',
      'gender': 'Gender',
      'bio': 'Bio',
      'joined': 'Joined',
      'status': 'Status',
      'active': 'Active',
      'rating': 'Rating',
      'no_bio_available': 'No bio available',
      
      // Reviews
      'reviews': 'Reviews',
      'leave_review': 'Leave Review',
      'review_comment': 'Review Comment',
      'submit_review': 'Submit Review',
      
      // Disputes
      'disputes': 'Disputes',
      'file_dispute': 'File Dispute',
      'dispute_title': 'Dispute Title',
      'dispute_description': 'Dispute Description',
      'submit_dispute': 'Submit Dispute',
      
      // Notifications
      'notifications': 'Notifications',
      'mark_all_read': 'Mark All Read',
      'unread_notifications': 'unread notifications',
      'loading': 'Loading',
      'no_notifications': 'No notifications',
      'related_product': 'Related product',
      'view_all_notifications': 'View all notifications',
      'failed_mark_all_read': 'Failed to mark all notifications as read',
      'days_ago': 'd ago',
      'hours_ago': 'h ago',
      'minutes_ago': 'm ago',
      'just_now': 'Just now',
      
      // Chats/Messages
      'no_conversations_yet': 'No conversations yet',
      'conversations_will_appear_here': 'Your conversations with other users will appear here.',
      'general_conversation': 'General conversation',
      'failed_load_conversations': 'Failed to load conversations. Please try again.',
      
      // Saved Searches
      'saved_searches': 'Saved Searches',
      'save_search': 'Save Search',
      
      // Price Alerts
      'price_alerts': 'Price Alerts',
      'create_alert': 'Create Alert',
      'target_price': 'Target Price',
      
      // Authentication
      'login': 'Login',
      'signup': 'Sign Up',
      'forgot_password': 'Forgot Password',
      'reset_password': 'Reset Password',
      'verify_email': 'Verify Email',
      'verify_phone': 'Verify Phone',
      'i_accept_terms': 'I accept the',
      'terms_and_conditions': 'Terms and Conditions',
      
      // Form Labels
      'username': 'Username',
      'password': 'Password',
      'confirm_password': 'Confirm Password',
      'first_name': 'First Name',
      'last_name': 'Last Name',
      'phone_number': 'Phone Number',
      'address': 'Address',
      
      // Status Labels
      'open': 'Open',
      'in_progress': 'In Progress',
      'resolved': 'Resolved',
      'closed': 'Closed',
      
      // Home Page
      'why_use_ecofinds': 'Why Use EcoFinds?',
      'eco_friendly_focus': 'Eco-Friendly Focus',
      'eco_friendly_description': 'We list only verified sustainable and eco-conscious businesses.',
      'local_discovery': 'Local Discovery',
      'local_discovery_description': 'Find green shops, cafes, and services in your neighborhood.',
      'support_good_causes': 'Support Good Causes',
      'support_good_causes_description': 'Your purchases make a difference for the planet and people.',
      'ready_to_make_difference': 'Ready to Make a Difference?',
      'join_eco_conscious_shoppers': 'Join thousands of eco-conscious shoppers today.',
      'about_ecofinds': 'About EcoFinds',
      'mission_statement': "We're on a mission to connect eco-conscious consumers with sustainable businesses worldwide.",
      'all_rights_reserved': 'All rights reserved.',
      
      // NavBar
      'home': 'Home',
      'browse': 'Browse',
      'about': 'About',
      'users': 'Users',
      'expand_sidebar': 'Expand Sidebar',
      'collapse_sidebar': 'Collapse Sidebar',
      'confirm_logout': 'Are you sure you want to logout?'
    };
  }
}

// Export a singleton instance
export default new TranslationService();