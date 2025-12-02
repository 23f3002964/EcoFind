# Search, Filtering & Personalization Features

## Overview
This document describes the enhanced search, filtering, and personalization features implemented for the EcoFinds sustainable marketplace application.

## Features Implemented

### 1. Advanced Search & Filtering

#### Enhanced Search Capabilities
- **Keyword Search**: Search products by title, description, brand, and model
- **Category Filtering**: Filter by specific categories and subcategories
- **Condition Filtering**: Filter by product condition (New, Like New, Good, Fair, Used)
- **Price Range Filtering**: Set minimum and maximum price limits
- **Auction vs Fixed-Price Filtering**: Filter specifically for auction or fixed-price items
- **Location-Based Filtering**: Filter by geographic location
- **Sorting Options**: Sort by newest, price (low to high), price (high to low), and popularity

#### User Interface Enhancements
- Improved filter layout with organized sections
- Real-time filtering as users adjust parameters
- "Reset Filters" button to clear all applied filters
- Visual indicators for active filters
- Responsive design that works on all device sizes

### 2. Saved Searches

#### Functionality
- Users can save their current search filters with a custom name
- Saved searches are accessible from the user dashboard and product browsing page
- One-click application of saved searches
- Ability to delete unwanted saved searches

#### Implementation Details
- **Backend**: 
  - New API endpoints for managing saved searches (`/api/saved-searches`)
  - SavedSearch model to store user search preferences
- **Frontend**:
  - SavedSearchesView component for managing saved searches
  - Integration with ProductsView to show and apply saved searches
  - Quick save option directly from the product browsing page

### 3. Price Alerts

#### Functionality
- Users can create price alerts for specific products
- System monitors product prices and notifies users when prices drop to or below target prices
- Notifications delivered through the existing notification system
- Users can manage (view/delete) their price alerts

#### Implementation Details
- **Backend**:
  - New PriceAlert model to track user price preferences
  - API endpoints for managing price alerts (`/api/price-alerts`)
  - Background scheduler job to check for price drops
  - Notification system integration for alert delivery
- **Frontend**:
  - PriceAlertsView component for managing price alerts
  - "Create Price Alert" button on product detail pages
  - Integration with notification system

### 4. Enhanced Personalized Recommendations

#### Improved Algorithm
- **Multi-Factor Analysis**:
  - User's saved items and purchase history
  - User's search history
  - User's preferred product conditions
  - Recently added products
  - Popular items (by view count)
  - Highly-rated sellers
- **Dynamic Updates**: Recommendations update based on user behavior
- **Fallback System**: Popular products shown when insufficient data exists

#### Implementation Details
- Enhanced `/api/recommendations` endpoint with improved algorithm
- Cached results for performance (3-minute cache)
- Featured prominently on the product browsing page

## Technical Implementation

### Backend Components
1. **Models**:
   - PriceAlert model for tracking price preferences
   - Enhanced SavedSearch model relationships

2. **API Endpoints**:
   - `/api/price-alerts` (GET, POST, DELETE)
   - Enhanced `/api/recommendations` with improved algorithm
   - `/api/saved-searches` (existing, with UI enhancements)

3. **Background Jobs**:
   - Price alert checker runs every 2 hours
   - Integrated with existing auction notification system

4. **Utilities**:
   - Enhanced notification system to handle price alert notifications
   - Improved recommendation algorithm

### Frontend Components
1. **New Views**:
   - SavedSearchesView.vue: Manage saved searches
   - PriceAlertsView.vue: Manage price alerts

2. **Enhanced Views**:
   - ProductsView.vue: Added location filter, saved searches section
   - ProductDetailView.vue: Added "Create Price Alert" button

3. **Navigation**:
   - NavBar.vue: Added links to saved searches and price alerts
   - HeaderBar.vue: Added quick access buttons for authenticated users

## User Benefits

### Search & Filtering
- **Time Savings**: Quickly find desired products with advanced filters
- **Precision**: Exact matches with keyword and category filtering
- **Flexibility**: Multiple sorting options to view products in preferred order

### Saved Searches
- **Convenience**: No need to recreate complex filter combinations
- **Efficiency**: One-click access to frequently used searches
- **Organization**: Named searches for easy identification

### Price Alerts
- **Deal Notification**: Never miss price drops on wanted items
- **Passive Monitoring**: System watches prices while users focus on other tasks
- **Competitive Advantage**: Early awareness of price reductions

### Personalization
- **Relevant Content**: Products matched to user interests and behaviors
- **Increased Engagement**: Higher likelihood of finding interesting items
- **Repeat Visits**: Personalized experience encourages return visits

## Future Enhancements

1. **AI-Powered Recommendations**: Machine learning algorithms for smarter suggestions
2. **Advanced Filtering**: Custom attribute filters based on product categories
3. **Search History**: Quick access to recent searches
4. **Email Notifications**: Price alert notifications via email
5. **Mobile Push Notifications**: Native mobile app integration for alerts
6. **Social Features**: "Trending" and "Recently Viewed" sections