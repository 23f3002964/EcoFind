import { createRouter, createWebHistory } from 'vue-router'

import store from '@/store'

import NotFound from '@/components/NotFound.vue'

import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import ForgotPassword from '../views/ForgotPassword.vue';
import ResetPassword from '../views/ResetPassword.vue';

// User
import UserDashboardView from '@/views/User/DashboardView.vue'
import UserProfileView from '@/views/User/ProfileView.vue'
import Unauthorized from '@/components/Unauthorized.vue'

// Admin 
import AdminDashboardView from '@/views/Admin/DashboardView.vue'
import AdminProfileView from '@/views/Admin/ProfileView.vue'
import AdminUserView from '@/views/Admin/UserView.vue'


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

  { path: '/forgot-password', component: ForgotPassword },
  { path: '/reset-password/:token', component: ResetPassword },


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
