import { createRouter, createWebHistory } from 'vue-router'

import store from '@/store'

import NotFound from '@/components/NotFound.vue'

import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import ForgotPassword from '../views/ForgotPassword.vue';
import ResetPassword from '../views/ResetPassword.vue';
import PhoneVerificationView from '@/views/PhoneVerificationView.vue';
import EditProductView from '@/views/EditProductView.vue';
import ConfirmAuctionSaleView from '@/views/ConfirmAuctionSaleView.vue';
import MyBidsView from '@/views/MyBidsView.vue';
import NotificationsView from '@/views/NotificationsView.vue';
import SavedSearchesView from '@/views/SavedSearchesView.vue';
import PriceAlertsView from '@/views/PriceAlertsView.vue';

// Products
import ProductsView from '@/views/ProductsView.vue'
import AddProductView from '@/views/AddProductView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'
import AuctionDetailView from '@/views/AuctionDetailView.vue'

// Chat
import ChatView from '@/views/ChatView.vue'
import ChatsView from '@/views/ChatsView.vue'

// User
import UserDashboardView from '@/views/User/DashboardView.vue'
import UserProfileView from '@/views/User/ProfileView.vue'
import MyListingsView from '@/views/User/MyListingsView.vue'
import CartView from '@/views/User/CartView.vue'
import PurchasesView from '@/views/User/PurchasesView.vue'
import Unauthorized from '@/components/Unauthorized.vue'

// Admin 
import AdminDashboardView from '@/views/Admin/DashboardView.vue'
import AdminProfileView from '@/views/Admin/ProfileView.vue'
import AdminUserView from '@/views/Admin/UserView.vue'
import ComplaintsView from '@/views/Admin/ComplaintsView.vue'


const routes = [

  // Error Routes
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: Unauthorized
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
  },


  // App Routes 
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/products',
    name: 'products',
    component: ProductsView
  },
  {
    path: '/add-product',
    name: 'addProduct',
    component: AddProductView,
    meta: { requiresAuth: true }
  },
  {
    path: '/edit-product/:id',
    name: 'editProduct',
    component: EditProductView,
    meta: { requiresAuth: true }
  },
  {
    path: '/confirm-auction-sale/:id',
    name: 'confirmAuctionSale',
    component: ConfirmAuctionSaleView,
    meta: { requiresAuth: true }
  },
  {
    path: '/my-bids',
    name: 'myBids',
    component: MyBidsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/saved-searches',
    name: 'savedSearches',
    component: SavedSearchesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/price-alerts',
    name: 'priceAlerts',
    component: PriceAlertsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/product/:id',
    name: 'productDetail',
    component: ProductDetailView
  },
  {
    path: '/auction/:id',
    name: 'auctionDetail',
    component: AuctionDetailView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: function () {
      return import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
    }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignupView
  },
  {
    path: '/phone-verification',
    name: 'phoneVerification',
    component: PhoneVerificationView
  },
  {
    path: '/verify-email/:token',
    name: 'emailVerification',
    component: () => import('../views/EmailVerificationView.vue')
  },

  { path: '/forgot-password', component: ForgotPassword },
  { path: '/reset-password/:token', component: ResetPassword },
  {
    path: '/chats',
    name: 'chats',
    component: ChatsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/chat/:other_user_id',
    name: 'chat',
    component: ChatView,
    meta: { requiresAuth: true }
  },


  // ROle: User's Routes
  {
    path: '/user/:userId/dashboard',
    name: 'userDashboard',
    component: UserDashboardView
  },
  {
    path: '/user/:userId/profile',
    name: 'userProfile',
    component: UserProfileView
  },
  {
    path: '/user/:userId/listings',
    name: 'myListings',
    component: MyListingsView
  },
  {
    path: '/user/:userId/cart',
    name: 'cart',
    component: CartView
  },
  {
    path: '/user/:userId/purchases',
    name: 'purchases',
    component: PurchasesView
  },


  // Role: Admin's Routes
  {
    path: '/admin/:userId/dashboard',
    name: 'adminDashboard',
    component: AdminDashboardView
  },
  {
    path: '/admin/:userId/users',
    name: 'adminUsers',
    component: AdminUserView
  },
  {
    path: '/admin/:userId/profile',
    name: 'adminProfile',
    component: AdminProfileView
  },
  {
    path: '/admin/:userId/complaints',
    name: 'adminComplaints',
    component: ComplaintsView
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});


router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;
  const requiredRole = to.meta.requiredRole;

  const isAuthenticated = store.state.isAuthenticated;
  const userRole = store.state.userRole;

  if (requiresAuth) {
    if (!isAuthenticated) {
      // Not logged in — redirect to login
      return next({ name: 'login' });
    }

    if (requiredRole && userRole !== requiredRole) {
      // Logged in but not the right role — redirect to unauthorized page
      return next({ name: 'Unauthorized' });
    }
  }

  // All good, proceed
  next();
});

export default router