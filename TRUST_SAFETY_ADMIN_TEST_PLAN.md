# Trust, Safety & Administration Features Test Plan

## Overview
This document outlines the test plan for verifying the implementation of Trust, Safety & Administration features in the EcoFind application.

## Features to Test

### 1. User Ratings & Reviews System

#### 1.1 Review Creation
- [ ] Users can only review other users they have transacted with
- [ ] Users can provide star-based ratings (1-5 stars)
- [ ] Users can add textual comments to reviews
- [ ] Reviews are publicly displayed on user profiles
- [ ] Average rating is calculated and displayed correctly

#### 1.2 Review Reporting
- [ ] Users can report inappropriate reviews
- [ ] Reported reviews trigger notifications to admins
- [ ] Admins can delete reported reviews
- [ ] Regular users cannot delete reviews, only report them

#### 1.3 Review Display
- [ ] Reviews are displayed with star ratings visualization
- [ ] Reviews show product information when applicable
- [ ] Reviews are sorted by date (newest first)
- [ ] Pagination works correctly for reviews

### 2. Dispute Resolution Mechanism

#### 2.1 Dispute Creation
- [ ] Users can file disputes against other users
- [ ] Disputes require title and description
- [ ] Disputes can be linked to specific products
- [ ] Disputes automatically notify the respondent

#### 2.2 Dispute Management
- [ ] Users can view their filed disputes
- [ ] Users can add evidence to open disputes
- [ ] Dispute status updates are reflected in real-time
- [ ] Users receive notifications about dispute updates

#### 2.3 Dispute Lifecycle
- [ ] Disputes can have statuses: open, in_progress, resolved, closed
- [ ] Status transitions work correctly
- [ ] Only involved parties can update disputes
- [ ] Evidence submission updates dispute timestamps

### 3. Admin Complaints Management

#### 3.1 Dashboard & Statistics
- [ ] Admin dashboard displays key metrics
- [ ] Dispute statistics show counts by status
- [ ] Recent activity is displayed correctly
- [ ] Charts and visualizations render properly

#### 3.2 Complaint Listing
- [ ] Admins can view all complaints
- [ ] Complaints display involved parties
- [ ] Complaints show related products when applicable
- [ ] Complaints are sortable by various criteria

#### 3.3 Complaint Filtering
- [ ] Filter by status works correctly
- [ ] Search functionality finds complaints by keywords
- [ ] Combined filters work as expected
- [ ] Pagination works with filtered results

#### 3.4 Complaint Actions
- [ ] Admins can assign complaints to themselves
- [ ] Admins can update complaint status
- [ ] Admins can add notes to complaints
- [ ] Status changes notify involved parties
- [ ] Admins can resolve or close complaints

## Test Scenarios

### Scenario 1: User Reviews Flow
1. Complete a transaction between two users
2. Have buyer rate seller with 4-star rating and comment
3. Have seller rate buyer with 5-star rating and comment
4. Verify ratings appear on both user profiles
5. Verify average ratings are calculated correctly
6. Report one review as inappropriate
7. Verify admin receives notification
8. Log in as admin and delete the reported review
9. Verify review is removed from user profile

### Scenario 2: Dispute Resolution Flow
1. User A files dispute against User B
2. User B receives notification about dispute
3. User B adds evidence to the dispute
4. Admin assigns dispute to themselves
5. Admin reviews evidence and updates status to "in_progress"
6. Both users receive status update notifications
7. Admin resolves dispute after investigation
8. Both users receive resolution notification
9. Verify dispute history is maintained

### Scenario 3: Admin Management Flow
1. Admin logs in and views dashboard
2. Verifies statistics display correctly
3. Navigates to complaints management
4. Filters complaints by "open" status
5. Assigns an open complaint to themselves
6. Updates complaint with notes and changes status
7. Searches for specific complaint by keyword
8. Resolves complaint and verifies status change
9. Checks that involved parties received notifications

## API Endpoints to Test

### Reviews Endpoints
- `POST /api/reviews` - Create review
- `GET /api/users/{user_id}/reviews` - Get user reviews
- `GET /api/my-reviews` - Get current user's reviews
- `DELETE /api/reviews/{review_id}` - Report/delete review

### Disputes Endpoints
- `POST /api/disputes` - Create dispute
- `GET /api/disputes` - Get user's disputes
- `PUT /api/disputes/{dispute_id}` - Update dispute

### Admin Endpoints
- `GET /api/admin/disputes` - Get all disputes
- `GET /api/admin/disputes/stats` - Get dispute statistics
- `GET /api/admin/dashboard` - Get admin dashboard data
- `PUT /api/admin/disputes/{dispute_id}` - Update dispute
- `POST /api/admin/disputes/{dispute_id}/assign` - Assign dispute

## Frontend Components to Test

### User Components
- ReviewsView.vue - Display and submit reviews
- DisputesView.vue - Manage disputes
- ProfileView.vue - Display ratings and reviews
- DashboardView.vue - Quick access to features

### Admin Components
- ComplaintsView.vue - Manage complaints
- DashboardView.vue - Admin overview
- AdminProfileView.vue - Admin profile management

## Expected Outcomes
All tests should pass with:
- Correct data displayed in UI components
- Proper API responses for all endpoints
- Accurate notifications sent to users
- Valid state transitions for disputes
- Secure access controls for admin features

## Test Data Requirements
- Multiple user accounts with verified transactions
- Various products for linking to disputes
- Sample reviews with different ratings
- Test admin account with proper permissions