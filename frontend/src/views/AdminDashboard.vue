<template>
  <div class="admin-container">
    <header class="admin-header glass-panel">
      <div class="header-content">
        <h2 class="admin-title">
          <span class="gradient-text">Admin Dashboard</span>
        </h2>
        <p class="admin-subtitle">
          Manage parking lots, users, search, and analytics.
        </p>
      </div>
    </header>

    <main class="admin-content">
      <transition name="fade-slide" mode="out-in">

        <!-- Home Tab Section  -->
        <section v-if="currentTab === 'home'" key="home" class="tab-section">
          <div class="section-header">
            <h3 class="section-title">Parking Locations</h3>
            <button 
              type="button" 
              class="btn-primary-glow"
              @click="openAddModal"
            >
              <i class="fas fa-plus me-2"></i> Add New Lot
            </button>
          </div>

          <div class="grid-layout">
            <article
              v-for="lot in lots"
              :key="lot.id"
              class="lot-card glass-panel interactive"
              :class="{ 'is-expanded': expandedLotId === lot.id }"
              @click="toggleExpanded(lot.id)"
            >
              <div class="card-top">
                <div class="lot-info">
                  <h4 class="lot-name">{{ lot.name }}</h4>
                  <div class="lot-badges">
                    <span class="badge-pin"><i class="fas fa-map-pin"></i> {{ lot.pin_code }}</span>
                    <span class="badge-price">₹{{ lot.price_per_hour }}/hr</span>
                  </div>
                </div>
                
                <div class="lot-actions" @click.stop>
                  
                  <button class="icon-btn edit" @click="handleEditLot(lot)" title="Edit">
                    <i class="fas fa-pen"></i>
                  </button>

                  <button class="icon-btn delete" @click="openDeleteModal(lot)" title="Delete">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <div class="card-body">
                <p class="address-text">{{ lot.address }}</p>
                
                <div class="occupancy-wrapper">
                  <div class="occupancy-labels">
                    <span class="label-text">Occupancy</span>
                    <span class="label-value">{{ lot.occupied }} / {{ lot.capacity }}</span>
                  </div>
                  <div class="progress-track">
                    <div 
                      class="progress-fill"
                      :class="getOccupancyColorClass(lot)"
                      :style="{ width: occupancyPercent(lot) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>

              <transition name="accordion">
                <div v-if="expandedLotId === lot.id" class="lot-details" @click.stop>
                  <div class="details-divider"></div>
                  <div class="details-header">
                    <h6>Live Spot View</h6>
                    <div class="legend">
                      <span class="legend-dot available"></span> Free
                      <span style="margin-left: 0.4rem" class="legend-dot occupied ms-2"></span> Taken
                    </div>
                  </div>
                  
                  <div class="spot-grid-container">
                    <div
                      v-for="(status, idx) in buildSpotsArray(lot)"
                      :key="idx"
                      class="spot-indicator"
                      :class="status === 'A' ? 'is-available' : 'is-occupied'"
                      :title="`Spot ${idx + 1} - ${status === 'A' ? 'Free' : 'Occupied'}`"
                      @click="handleSpotClick(lot, idx)"
                    ></div>
                  </div>
                </div>
              </transition>
            </article>

            <div v-if="lots.length === 0" class="lots-empty glass-panel">
              <div class="empty-content">
                <i class="fas fa-warehouse empty-icon"></i>
                <h3>No Parking Lots Yet</h3>
                <p>Get started by adding your first parking location.</p>
              </div>
            </div>
          </div>
        </section>


        <!-- Users tab section  -->
        <section v-else-if="currentTab === 'users'" key="users" class="tab-section">
          <div class="glass-panel table-container">
            <div class="panel-header">
              <div class="header-left">
                <h3>Registered Users</h3>
                <span class="badge-count">{{ filteredUsers.length }} Users</span>
              </div>
              <div class="header-right">
                <div class="search-input-wrapper small">
                  <i class="fas fa-search search-icon"></i>
                  <input 
                    v-model="userSearchQuery" 
                    type="text" 
                    class="modern-input compact" 
                    placeholder="Search users..." 
                  />
                </div>
              </div>
            </div>
            <div class="table-responsive">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User Details</th>
                    <th>Role</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="user in filteredUsers" 
                    :key="user.id"
                    @click="openUserModal(user.id)"
                    style="cursor: pointer"
                    class="interactive-row"
                  >
                    <td class="id-col">#{{ user.id }}</td>
                    <td>
                      <div class="user-cell">
                        <div class="user-avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
                        <div class="user-info">
                          <span class="username">{{ user.username }}</span>
                          <span class="email">{{ user.email }}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="role-badge" :class="user.role">{{ user.role }}</span>
                    </td>
                    <td><span class="status-dot active">Active</span></td>
                  </tr>
                  <tr v-if="filteredUsers.length === 0">
                    <td colspan="4" class="text-center py-5 text-muted">
                      {{ users.length === 0 ? 'No users found in database.' : 'No users match your search.' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
        
        <!-- Search Tab Srction -->
        <section v-else-if="currentTab === 'search'" key="search" class="tab-section">
          <div class="search-hero glass-panel">
            <h3>Find a Location</h3>
            <div class="search-bar-wrapper">
              <div class="select-wrapper">
                <select v-model="searchField" class="custom-select">
                  <option value="name">Name</option>
                  <option value="address">Address</option>
                  <option value="pin_code">Pin Code</option>
                </select>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="Type to search..."
              />
              <button class="search-btn"><i class="fas fa-search"></i></button>
            </div>
          </div>

          <div class="grid-layout mt-4">
            <article
              v-for="lot in filteredLots"
              :key="lot.id"
              class="lot-card glass-panel interactive"
              :class="{ 'is-expanded': expandedLotId === lot.id }"
              @click="toggleExpanded(lot.id)"
            >
              <div class="card-top">
                <div class="lot-info">
                  <h4 class="lot-name">{{ lot.name }}</h4>
                  <small class="text-muted">{{ lot.address }}</small>
                </div>
                <div class="lot-badges">
                    <span class="badge-price">₹{{ lot.price_per_hour }}/hr</span>
                </div>
                <div class="lot-actions" @click.stop>
                  <button class="icon-btn edit" @click="handleEditLot(lot)" title="Edit">
                    <i class="fas fa-pen"></i>
                  </button>
                  <button class="icon-btn delete" @click="openDeleteModal(lot)" title="Delete">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
              
              <div class="card-body">
                <div class="occupancy-wrapper mt-3">
                  <div class="progress-track">
                      <div 
                        class="progress-fill"
                        :class="getOccupancyColorClass(lot)"
                        :style="{ width: occupancyPercent(lot) + '%' }"
                      ></div>
                    </div>
                    <small class="text-muted mt-1 d-block text-end">
                      {{ lot.occupied }} / {{ lot.capacity }} spots filled
                    </small>
                </div>
              </div>

              <transition name="accordion">
                <div v-if="expandedLotId === lot.id" class="lot-details" @click.stop>
                  <div class="details-divider"></div>
                  <div class="details-header">
                    <h6>Live Spot View</h6>
                    <div class="legend">
                      <span class="legend-dot available"></span> Free
                      <span style="margin-left: 0.4rem" class="legend-dot occupied ms-2"></span> Taken
                    </div>
                  </div>
                  
                  <div class="spot-grid-container">
                    <div
                      v-for="(status, idx) in buildSpotsArray(lot)"
                      :key="idx"
                      class="spot-indicator"
                      :class="status === 'A' ? 'is-available' : 'is-occupied'"
                      :title="`Spot ${idx + 1} - ${status === 'A' ? 'Free' : 'Occupied'}`"
                      @click="handleSpotClick(lot, idx)"
                    ></div>
                  </div>
                </div>
              </transition>
            </article>

             <div v-if="filteredLots.length === 0" class="empty-state glass-panel">
              <div class="empty-content">
                <i class="fas fa-search empty-icon"></i>
                <h3>No Results Found</h3>
                <p>Try adjusting your search terms.</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Summary and analytics section  -->
        <section v-else-if="currentTab === 'summary'" key="summary" class="tab-section summary-wrapper">
          
          <div class="analytics-grid">
            <div class="stat-card glass-panel revenue-card animate-fade-up" style="--delay: 0s">
              <div class="stat-content">
                <div class="stat-icon-wrapper">
                  <i class="fas fa-wallet"></i>
                </div>
                <div class="stat-text">
                  <p class="stat-label">Total Revenue</p>
                  <h2 class="stat-value">₹{{ revenueSummary.total_revenue.toLocaleString() }}</h2>
                  <div class="stat-trend positive">
                    <i class="fas fa-arrow-trend-up"></i>
                    <span>Lifetime Earnings</span>
                  </div>
                </div>
              </div>
              <div class="stat-glow"></div>
            </div>

            <div class="chart-card glass-panel animate-fade-up" style="--delay: 0.1s">
              <div class="panel-header-simple">
                <h3>Occupancy Rate</h3>
                <span class="header-badge">Real-time</span>
              </div>
              <div class="chart-flex-wrapper">
                <div class="chart-container-summary">
                  <div v-if="occupancySummary.total > 0" class="chart-wrapper">
                    <Doughnut :data="chartData" :options="chartOptions" />
                  </div>
                  <div v-else class="chart-empty">
                    <p>No data</p>
                  </div>
                </div>
                <div class="chart-legend-vertical">
                  <div class="legend-row">
                    <span class="legend-dot occupied"></span>
                    <div class="legend-info">
                      <span class="legend-val">{{ occupancySummary.occupied }}</span>
                      <span class="legend-lbl">Occupied</span>
                    </div>
                  </div>
                  <div class="legend-row">
                    <span class="legend-dot available"></span>
                    <div class="legend-info">
                      <span class="legend-val">{{ occupancySummary.available }}</span>
                      <span class="legend-lbl">Available</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="lots-analytics-section mt-5">
            <h4 class="section-subtitle animate-fade-up" style="--delay: 0.2s">Performance by Location</h4>

            <div class="lots-analytics-grid">
              <article
                v-for="(lot, index) in lotsSummary"
                :key="lot.id"
                class="lot-analytics-card glass-panel animate-fade-up"
                :style="{ '--delay': `${0.2 + (index * 0.05)}s` }"
              >
                <div class="la-header">
                  <div class="la-title-group">
                    <h5 class="la-name">{{ lot.name }}</h5>
                    <span class="la-id">ID: {{ lot.id }}</span>
                  </div>
                  <div class="la-revenue-badge">
                    ₹{{ lot.total_revenue.toLocaleString() }}
                  </div>
                </div>

                <div class="la-divider"></div>

                <div class="la-stats-row">
                  <div class="la-stat-item">
                    <i class="fas fa-car-side stat-icon"></i>
                    <span class="stat-num">{{ lot.occupied }}</span>
                    <span class="stat-lbl">Occupied</span>
                  </div>
                  <div class="la-stat-item">
                    <i class="fas fa-parking stat-icon"></i>
                    <span class="stat-num">{{ lot.available }}</span>
                    <span class="stat-lbl">Free</span>
                  </div>
                  <div class="la-stat-item">
                    <i class="fas fa-layer-group stat-icon"></i>
                    <span class="stat-num">{{ lot.capacity }}</span>
                    <span class="stat-lbl">Total</span>
                  </div>
                </div>

                <div class="la-progress-mini">
                    <div class="track">
                       <div class="fill" :style="{ width: ((lot.occupied / lot.capacity) * 100) + '%' }"></div>
                    </div>
                 </div>

                <button class="btn-analytics-ghost" @click="openLotAnalytics(lot.id)">
                  View Analytics <i class="fas fa-arrow-right"></i>
                </button>
              </article>
              
              <div v-if="lotsSummary.length === 0" class="empty-placeholder animate-fade-up">
                 No parking lots data available.
              </div>
            </div>
          </div>
        </section>

      </transition>
    </main>

    <transition name="modal-fade">
      <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
        <div class="modal-content glass-panel" style="max-width: 600px;">
          
          <div class="modal-header">
            <h3>User Profile</h3>
            <button class="close-btn" @click="closeUserModal">&times;</button>
          </div>

          <div class="modal-body">
            <div v-if="loadingUser" class="text-center py-5">
              <i class="fas fa-spinner fa-spin fa-2x text-muted"></i>
            </div>

            <div v-else-if="userDetails">
              <div class="d-flex align-items-center mb-4 gap-3">
                <div class="user-avatar-large">
                  {{ userDetails.username.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h4 class="mb-0">{{ userDetails.username }}</h4>
                  <p class="text-muted mb-1">{{ userDetails.email }}</p>
                  <span class="role-badge" :class="userDetails.role">
                    {{ userDetails.role }}
                  </span>
                </div>
              </div>

              <div class="details-divider"></div>

              <h5 class="mb-3">Booking History</h5>
              
              <div v-if="userDetails.reservations.length === 0" class="text-muted text-center py-3">
                No bookings found for this user.
              </div>

              <div v-else class="history-list">
                <div 
                  v-for="res in userDetails.reservations" 
                  :key="res.id" 
                  class="history-item glass-panel"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <div class="fw-bold text-white">{{ res.lot_name }}</div>
                      <div class="text-muted small">Spot: <span class="text-accent">{{ res.spot_number }}</span></div>
                    </div>
                    <span 
                      class="status-badge" 
                      :class="res.active ? 'occupied' : 'free'"
                    >
                      {{ res.active ? 'Active' : 'Completed' }}
                    </span>
                  </div>
                  
                  <div class="mt-2 d-flex justify-content-between small text-muted">
                    <span>{{ new Date(res.start_time).toLocaleDateString() }} {{ new Date(res.start_time).toLocaleTimeString() }}</span>
                    <span v-if="!res.active">₹{{ res.total_cost }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-actions center">
            <button class="btn-secondary" @click="closeUserModal">Close</button>
          </div>
          
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
        <div class="modal-content glass-panel">
          <div class="modal-header">
            <h3>Add New Lot</h3>
            <button class="close-btn" @click="closeAddModal">&times;</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createLot">
              <div class="form-group">
                <label>Location Name</label>
                <input v-model="newLot.name" class="modern-input" placeholder="e.g. Downtown Plaza" required />
              </div>
              <div class="form-group">
                <label>Address</label>
                <textarea v-model="newLot.address" class="modern-input" rows="2" placeholder="Street, City..." required></textarea>
              </div>
              <div class="form-row">
                <div class="form-group half">
                  <label>Pin Code</label>
                  <input v-model="newLot.pin_code" class="modern-input" placeholder="600001" required />
                </div>
                <div class="form-group half">
                  <label>Price/Hr (₹)</label>
                  <input v-model="newLot.price_per_hour" type="number" step="0.5" class="modern-input" placeholder="50" required />
                </div>
              </div>
              <div class="form-group">
                <label>Capacity (Spots)</label>
                <input v-model="newLot.capacity" type="number" min="1" class="modern-input" placeholder="100" required  />
              </div>
              <div class="modal-actions">
                <button type="button" class="btn-text" @click="closeAddModal">Cancel</button>
                <button type="submit" class="btn-primary-glow" :disabled="creatingLot">
                  {{ creatingLot ? 'Creating...' : 'Create Lot' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="showEditModal && editLotTarget" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content glass-panel">
          <div class="modal-header">
            <h3>Edit Lot</h3>
            <button class="close-btn" @click="closeEditModal">&times;</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveLotEdits">
              <div class="form-group">
                <label>Location Name</label>
                <input
                  v-model="editLotForm.name"
                  class="modern-input"
                  placeholder="Location name"
                  required
                />
              </div>
              <div class="form-group">
                <label>Address</label>
                <textarea
                  v-model="editLotForm.address"
                  class="modern-input"
                  rows="2"
                  placeholder="Street, City..."
                  required
                ></textarea>
              </div>
              <div class="form-row">
                <div class="form-group half">
                  <label>Pin Code</label>
                  <input
                    v-model="editLotForm.pin_code"
                    class="modern-input"
                    placeholder="600001"
                    required
                    @keydown = "blockInvalidKeys"
                  />
                </div>
                <div class="form-group half">
                  <label>Price/Hr (₹)</label>
                  <input
                    v-model="editLotForm.price_per_hour"
                    type="number"
                    step="0.5"
                    min = "0"
                    class="modern-input"
                    required
                    
                  />
                </div>
              </div>
              <div class="form-group">
                <label>Capacity (Spots)</label>
                <input
                  v-model="editLotForm.capacity"
                  type="number"
                  min="1"
                  class="modern-input"
                  required
                />
                <small class="text-muted">
                  You cannot reduce capacity below currently occupied spots.  
                  Backend will block it and show a message if you try.
                </small>
              </div>
              <div class="modal-actions">
                <button type="button" class="btn-secondary" @click="closeEditModal">
                  Cancel
                </button>
                <button type="submit" class="btn-primary-glow" :disabled="editingLot">
                  {{ editingLot ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>


    <transition name="modal-fade">
      <div v-if="showDeleteModal && lotToDelete" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-content glass-panel mini">
          <div class="modal-icon warning">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <h3 class="text-center">Delete Location?</h3>
          <p class="text-center text-muted">
            Are you sure you want to delete <strong>{{ lotToDelete.name }}</strong>? This action cannot be undone.
          </p>
          <div class="modal-actions center">
            <button class="btn-secondary" @click="closeDeleteModal">Cancel</button>
            <button class="btn-danger" @click="confirmDelete">
              Delete Lot
            </button>
          </div>


        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div
        v-if="showSpotModal && selectedSpot"
        class="modal-overlay"
        @click.self="closeSpotModal"
      >
        <div class="modal-content glass-panel mini">
          <div class="modal-header">
            <h3>Spot Details</h3>
            <button class="close-btn" @click="closeSpotModal">&times;</button>
          </div>
          <div class="modal-body">
            <p><strong>Spot:</strong> {{ selectedSpot.spot_number }}</p>
            <div class="d-flex align-items-center mb-3">
              <strong class="me-2">Status:</strong>
              <span 
                v-if="selectedSpot.is_occupied" 
                class="status-badge occupied clickable"
                @click="viewReservationDetails"
                title="View Reservation Details"
              >
                Occupied<i class="fas fa-info-circle ms-1">  </i>
              </span>
              <span v-else class="status-badge free">Free</span>
            </div>

            <div v-if="selectedSpot.reservation">
              <p class="text-muted small">ID: #{{ selectedSpot.reservation.id }}</p>
              <p>
                <strong>Started:</strong>
                {{ new Date(selectedSpot.reservation.start_time).toLocaleString() }}
              </p>
            </div>
            <p v-else class="text-muted">No active reservation.</p>
          </div>

          <div class="modal-actions center">
            <button class="btn-secondary" @click="closeSpotModal">Close</button>

            <button
              v-if="selectedSpot.is_occupied"
              class="btn-primary-glow"
              @click="buildReleasePreview"
              :disabled="releasingSpot"
            >
              {{ releasingSpot ? 'Releasing...' : 'Release Spot' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div
        v-if="showReservationInfoModal && reservationInfo"
        class="modal-overlay"
        @click.self="closeReservationInfoModal"
      >
        <div class="modal-content glass-panel mini">
          <div class="modal-header">
            <h3>Reservation Details</h3>
            <button class="close-btn" @click="closeReservationInfoModal">&times;</button>
          </div>

          <div class="modal-body">
            <div class="detail-row">
              <strong>Reservation ID:</strong>
              <span>#{{ reservationInfo.reservationId }}</span>
            </div>

            <div class="detail-row">
              <strong>User ID:</strong>
              <span>{{ reservationInfo.userId }}</span>
            </div>

            <div class="detail-row">
              <strong>User Email:</strong>
              <span>{{ reservationInfo.userEmail }}</span>
            </div>

            <div class="detail-row">
              <strong>Started:</strong>
              <span>{{ reservationInfo.start.toLocaleString() }}</span>
            </div>

            <div class="detail-row">
              <strong>Duration:</strong>
              <span>
                {{ reservationInfo.hours }}h
                <template v-if="reservationInfo.minutes"> {{ reservationInfo.minutes }}m</template>
              </span>
            </div>

            <div class="detail-row">
              <strong>Current Rate:</strong>
              <span>₹{{ reservationInfo.rate }}/hour</span>
            </div>

            <div class="detail-row">
              <strong>Est. Cost:</strong>
              <span class="text-accent">
                ≈ ₹{{ reservationInfo.approxCost }}
              </span>
            </div>
          </div>

          <div class="modal-actions center">
            <button class="btn-primary-glow" @click="closeReservationInfoModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div
        v-if="showReleaseConfirm && releasePreview"
        class="modal-overlay"
        @click.self="showReleaseConfirm = false"
      >
        <div class="modal-content glass-panel mini">
          <div class="modal-header">
            <h3>Confirm Release</h3>
            <button class="close-btn" @click="showReleaseConfirm = false">&times;</button>
          </div>

          <div class="modal-body">
            <p class="text-muted mb-3">
              You are about to release this spot and close the active booking.
            </p>

            <div class="detail-row">
              <strong>Reservation ID:</strong>
              <span>#{{ releasePreview.reservationId }}</span>
            </div>

            <div class="detail-row">
              <strong>User ID:</strong>
              <span>{{ releasePreview.userId }}</span>
            </div>

            <div class="detail-row">
              <strong>User Email:</strong>
              <span>{{ releasePreview.userEmail }}</span>
            </div>


            <div class="detail-row">
              <strong>Started:</strong>
              <span>{{ releasePreview.start.toLocaleString() }}</span>
            </div>

            <div class="detail-row">
              <strong>Duration so far:</strong>
              <span>
                {{ releasePreview.hours }}h
                <template v-if="releasePreview.minutes"> {{ releasePreview.minutes }}m</template>
              </span>
            </div>

            <div class="detail-row">
              <strong>Rate:</strong>
              <span>₹{{ releasePreview.rate }}/hour</span>
            </div>

            <div class="detail-row">
              <strong>Approx. Cost:</strong>
              <span class="text-accent">
                ≈ ₹{{ releasePreview.approxCost }}
              </span>
            </div>

            <p class="text-xs text-muted mt-3">
              This amount is an approximation based on the current time and lot’s hourly rate.
              The backend will compute the final bill when you release the spot.
            </p>
          </div>

          <div class="modal-actions center">
            <button class="btn-secondary" @click="showReleaseConfirm = false">
              Cancel
            </button>

            <button class="btn-primary-glow" @click="handleConfirmRelease">
              Release Spot
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="showLotAnalyticsModal && lotAnalyticsData" class="modal-overlay" @click.self="closeLotAnalytics">
        <div class="modal-content glass-panel" style="max-width:850px;">
          <div class="modal-header">
            <h3><i class="fas fa-chart-line me-2 text-accent"></i> {{ lotAnalyticsData.lot_name }}</h3>
            <button class="close-btn" @click="closeLotAnalytics">&times;</button>
          </div>

          <div class="modal-body">
            
            <div class="analytics-grid-modal">
              <div class="stat-box animate-slide-up" style="--delay: 0.05s">
                <div class="icon-circle revenue"><i class="fas fa-wallet"></i></div>
                <div class="stat-content-mini">
                  <span class="label">Revenue</span>
                  <span class="value">₹{{ lotAnalyticsData.total_revenue.toLocaleString() }}</span>
                </div>
              </div>

              <div class="stat-box animate-slide-up" style="--delay: 0.1s">
                 <div class="icon-circle bookings"><i class="fas fa-ticket-alt"></i></div>
                 <div class="stat-content-mini">
                   <span class="label">Today's Bookings</span>
                   <span class="value">{{ lotAnalyticsData.todays_bookings }}</span>
                 </div>
              </div>

              <div class="stat-box animate-slide-up" style="--delay: 0.15s">
                 <div class="icon-circle month"><i class="fas fa-calendar-check"></i></div>
                 <div class="stat-content-mini">
                   <span class="label">This Month</span>
                   <span class="value">{{ lotAnalyticsData.months_bookings }}</span>
                 </div>
              </div>

              <div class="stat-box animate-slide-up" style="--delay: 0.2s">
                 <div class="icon-circle duration"><i class="fas fa-clock"></i></div>
                 <div class="stat-content-mini">
                   <span class="label">Avg Duration</span>
                   <span class="value">{{ lotAnalyticsData.avg_duration_minutes }}m</span>
                 </div>
              </div>
            </div>

            <div class="chart-section animate-slide-up" style="--delay: 0.3s">
               <div class="chart-header-row">
                  <h4>Revenue Trend (30 Days)</h4>
                  <div class="chart-badge">Daily Income</div>
               </div>
               <div class="chart-modal-inner">
                  <Line v-if="lotChartData" :data="lotChartData" :options="lotChartOptions" />
               </div>
            </div>

          </div>

          <div class="modal-actions center">
            <button class="btn-secondary" @click="closeLotAnalytics">Close Report</button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { apiFetch } from '../api';
import { Doughnut, Line } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, Filler } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, Filler);

// Route & Tabs
const route = useRoute();
const currentTab = computed(() => route.query.tab || 'home');

// Watch tab to reset expansion state so user starts fresh on new tab
watch(currentTab, () => {
  expandedLotId.value = null;
});

const blockInvalidKeys = (event) => {
  const invalidkeys = [ '-', '+', '=', 'e', 'E' ]
  if (invalidkeys.includes(event.key)){
    event.preventDefault();
  }
};


// Data
const lots = ref([]);
const users = ref([]);
const occupancySummary = ref({ total: 0, occupied: 0, available: 0 });
const revenueSummary = ref({ total_revenue: 0 });

// UI State
const expandedLotId = ref(null);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const showEditModal = ref(false);          
const editingLot = ref(false);               
const editLotTarget = ref(null);             
const editLotForm = ref({                   
  name: '',
  address: '',
  pin_code: '',
  capacity: '',
  price_per_hour: ''
});
const lotToDelete = ref(null);
const creatingLot = ref(false);

const lotSpots = ref({});        
const showSpotModal = ref(false);
const selectedSpot = ref(null);
const releasingSpot = ref(false);
const loadingSpotLotId = ref(null); 


const showReleaseConfirm = ref(false);
const releasePreview = ref(null);

// Reservation Detail View
const showReservationInfoModal = ref(false);
const reservationInfo = ref(null);

// per-lot analytics
const lotsSummary = ref([]);
const showLotAnalyticsModal = ref(false);
const lotAnalyticsData = ref(null);
const lotChartData = ref(null);

// User Modal State ===
const showUserModal = ref(false);
const userDetails = ref(null);
const loadingUser = ref(false);

// Auto Refresh Interval ID
let autoRefreshInterval = null;

// Refined Chart Options for Modal
const lotChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { display: false }, 
    tooltip: { 
      mode: 'index', 
      intersect: false,
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      titleColor: '#e2e8f0',
      bodyColor: '#cbd5e1',
      borderColor: 'rgba(148, 163, 184, 0.2)',
      borderWidth: 1,
      padding: 10,
      displayColors: false,
      callbacks: {
        label: (context) => `Revenue: ₹${context.parsed.y.toLocaleString()}`
      }
    } 
  },
  scales: {
    x: { 
      grid: { display: false, drawBorder: false },
      ticks: { color: '#64748b', font: { size: 10 }, maxRotation: 45, minRotation: 0 }
    },
    y: { 
      beginAtZero: true,
      grid: { color: 'rgba(148, 163, 184, 0.08)', borderDash: [5, 5], drawBorder: false },
      ticks: { color: '#64748b', callback: (val) => '₹' + val, font: { size: 10 } }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  },
  elements: {
    line: { tension: 0.4 },
    point: { radius: 0, hitRadius: 20, hoverRadius: 5, hoverBorderWidth: 2 }
  }
};


// Forms
const newLot = ref({ name: '', address: '', pin_code: '', capacity: '', price_per_hour: '' });
const searchQuery = ref('');
const searchField = ref('name');
const userSearchQuery = ref('');

// Computed - Lots
const filteredLots = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return lots.value;
  return lots.value.filter((lot) => 
    String(lot[searchField.value] || '').toLowerCase().includes(q)
  );
});

// Computed - Users
const filteredUsers = computed(() => {
  const q = userSearchQuery.value.trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter(user => 
    user.username.toLowerCase().includes(q) || 
    user.email.toLowerCase().includes(q)
  );
});

// Chart Config
const chartData = ref({
  labels: ['Occupied', 'Available'],
  datasets: [{ backgroundColor: ['#ef4444', '#10b981'], data: [0, 0], borderWidth: 0 }]
});
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  cutout: '75%' 
};



// --- LOGIC ---

const fetchData = async () => {
  try {
    const [resLots, resUsers, resAnalytics] = await Promise.all([
      apiFetch('/parking-lots'),
      apiFetch('/users'),
      apiFetch('/analytics')
    ]);

    const rawLots = await resLots.json();

    lots.value = rawLots.map((lot) => {
      let spots = Array.isArray(lot.spots) ? [...lot.spots] : [];

      const getIndex = (s) => {
        if (!s || !s.spot_number) return 0;
        const parts = String(s.spot_number).split('-');
        const n = parseInt(parts[parts.length - 1], 10);
        return Number.isNaN(n) ? 0 : n;
      };

      spots.sort((a, b) => getIndex(a) - getIndex(b));

      const capacity = lot.capacity || spots.length || 0;
      const occupied = spots.filter((s) => s.is_occupied).length;
      const available = capacity - occupied;

      return {
        ...lot,
        spots,          
        capacity,
        occupied,
        available
      };
    });

    users.value = await resUsers.json();

    const analytics = await resAnalytics.json();
    occupancySummary.value = analytics.occupancy_summary;
    revenueSummary.value = analytics.revenue_summary;

    lotsSummary.value = analytics.lots_summary || [];

    chartData.value = {
      labels: ['Occupied', 'Available'],
      datasets: [{
        backgroundColor: ['#f87171', '#34d399'],
        hoverBackgroundColor: ['#ef4444', '#10b981'],
        data: [
          analytics.occupancy_summary.occupied,
          analytics.occupancy_summary.available
        ],
        borderWidth: 0
      }]
    };
  } catch (e) {
    console.error('Data load error', e);
  }
};


const occupancyPercent = (lot) => {
  if (!lot.capacity) return 0;
  return Math.round((lot.occupied / lot.capacity) * 100);
};

const getOccupancyColorClass = (lot) => {
  const pct = occupancyPercent(lot);
  if (pct > 85) return 'bg-critical';
  if (pct > 50) return 'bg-warning';
  return 'bg-success';
};


const buildReleasePreview = () => {
  if (!selectedSpot.value || !selectedSpot.value.reservation) return;

  const res = selectedSpot.value.reservation;

  const start = new Date(res.start_time);   
  const now = new Date();

  const ms = now - start;
  const hoursFloat = ms / 3600000;
  const hours = Math.floor(hoursFloat);
  const minutes = Math.round((hoursFloat - hours) * 60);

  const lot = lots.value.find(l => l.id === selectedSpot.value.lot_id);
  const rate = lot ? Number(lot.price_per_hour || 0) : 0;

  const billedHours = Math.max(1, hoursFloat); 
  const approxCost = billedHours * rate;

  releasePreview.value = {
    reservationId: res.id,
    userId: res.user_id,
    userEmail: res.user_email || 'N/A',
    start,
    hours,
    minutes,
    rate,
    approxCost: approxCost.toFixed(2)
  };

  showReleaseConfirm.value = true;
};

// View Reservation Details Logic
const viewReservationDetails = () => {
  if (!selectedSpot.value || !selectedSpot.value.reservation) return;
  const res = selectedSpot.value.reservation;

  // similar logic to release preview for consistent data display
  const start = new Date(res.start_time);
  const now = new Date();
  const ms = now - start;
  const hoursFloat = ms / 3600000;
  const hours = Math.floor(hoursFloat);
  const minutes = Math.round((hoursFloat - hours) * 60);

  const lot = lots.value.find(l => l.id === selectedSpot.value.lot_id);
  const rate = lot ? Number(lot.price_per_hour || 0) : 0;
  const billedHours = Math.max(1, hoursFloat);
  const approxCost = billedHours * rate;

  reservationInfo.value = {
    reservationId: res.id,
    userId: res.user_id,
    userEmail: res.user_email || 'N/A',
    start,
    hours,
    minutes,
    rate,
    approxCost: approxCost.toFixed(2)
  };

  showReservationInfoModal.value = true;
};

const closeReservationInfoModal = () => {
  showReservationInfoModal.value = false;
  reservationInfo.value = null;
};


const handleConfirmRelease = async () => {
  if (releasingSpot.value) return;
  showReleaseConfirm.value = false;
  await releaseSpot();
};


const buildSpotsArray = (lot) => {
  if (!lot.spots || !Array.isArray(lot.spots)) {
    const capacity = lot.capacity || 0;
    const occupied = lot.occupied || 0;
    return Array.from({ length: capacity }, (_, idx) => (idx < occupied ? 'O' : 'A'));
  }

  return lot.spots.map((s) => (s.is_occupied ? 'O' : 'A'));
};



const toggleExpanded = (id) => {
  expandedLotId.value = expandedLotId.value === id ? null : id;
};

// Modals
const openAddModal = () => {
  newLot.value = { name: '', address: '', pin_code: '', capacity: '', price_per_hour: '' };
  showAddModal.value = true;
};
const closeAddModal = () => showAddModal.value = false;

const fetchLotSpots = async (lotId) => {
  if (lotSpots.value[lotId]) return;

  try {
    loadingSpotLotId.value = lotId;
    const res = await apiFetch(`/parking-lot/${lotId}/spots`);
    const data = await res.json();

    if (!res.ok) {
      console.error(data);
      alert(data.message || 'Failed to load spot details.');
      return;
    }

    lotSpots.value = { ...lotSpots.value, [lotId]: data };
  } catch (err) {
    console.error(err);
    alert('Error loading spot details.');
  } finally {
    loadingSpotLotId.value = null;
  }
};

const handleSpotClick = async (lot, idx) => {
  await fetchLotSpots(lot.id);
  const spots = lotSpots.value[lot.id] || [];
  const spot = spots[idx];

  if (!spot) {
    alert('Spot information not available.');
    return;
  }

  selectedSpot.value = spot;
  showSpotModal.value = true;
};

const closeSpotModal = () => {
  showSpotModal.value = false;
  selectedSpot.value = null;
};

const releaseSpot = async () => {
  if (!selectedSpot.value || !selectedSpot.value.is_occupied) return;

  releasingSpot.value = true;
  try {
    const res = await apiFetch(`/parking-spot/${selectedSpot.value.id}/release`, {
      method: 'POST'
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.message || 'Failed to release spot.');
      return;
    }

    alert(`Spot released. Total cost: ₹${data.total_cost ?? 0}.`);

    if (selectedSpot.value.lot_id && lotSpots.value[selectedSpot.value.lot_id]) {
      const clone = { ...lotSpots.value };
      delete clone[selectedSpot.value.lot_id];
      lotSpots.value = clone;
    }

    showReleaseConfirm.value = false;
    closeSpotModal();
    await fetchData();
  } catch (err) {
    console.error(err);
    alert('Error releasing spot.');
  } finally {
    releasingSpot.value = false;
  }
};


const closeEditModal = () => {
  showEditModal.value = false;
  editLotTarget.value = null;
};

const saveLotEdits = async () => {
  if (!editLotTarget.value) return;
  editingLot.value = true;

  try {
    const res = await apiFetch(`/parking-lot/${editLotTarget.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editLotForm.value)
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.message || 'Failed to update parking lot.');
      return;
    }

    showEditModal.value = false;
    editLotTarget.value = null;
    await fetchData();
  } catch (err) {
    console.error(err);
    alert('Error updating parking lot.');
  } finally {
    editingLot.value = false;
  }
};

const createLot = async () => {
  creatingLot.value = true;
  try {
    await apiFetch('/parking-lot', { method: 'POST', body: JSON.stringify(newLot.value) });
    showAddModal.value = false;
    await fetchData();
  } catch (e) {
    alert('Failed to create lot');
  } finally {
    creatingLot.value = false;
  }
};

const openDeleteModal = (lot) => {
  lotToDelete.value = lot;
  showDeleteModal.value = true;
};
const closeDeleteModal = () => {
  showDeleteModal.value = false;
  lotToDelete.value = null;
};
const confirmDelete = async () => {
  if (!lotToDelete.value) return;

  try {
    const res = await apiFetch(`/parking-lot/${lotToDelete.value.id}`, {
      method: 'DELETE'
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.message || 'Failed to delete parking lot.');
      return;
    }

    closeDeleteModal();
    expandedLotId.value = null;
    await fetchData();
    alert('Parking lot deleted.');
  } catch (err) {
    console.error(err);
    alert('Error deleting parking lot.');
  }
};


const handleEditLot = (lot) => {
  editLotTarget.value = lot;
  editLotForm.value = {
    name: lot.name,
    address: lot.address,
    pin_code: lot.pin_code,
    capacity: lot.capacity,
    price_per_hour: lot.price_per_hour
  };
  showEditModal.value = true;
};


const openLotAnalytics = async (lotId) => {
  try {
    const res = await apiFetch(`/parking-lot/${lotId}/analytics`);
    const data = await res.json();
    if (!res.ok) {
      alert(data.message || 'Failed to load lot analytics.');
      return;
    }
    
    lotAnalyticsData.value = data;

    // build chart data from timeseries_30d
    const labels = (data.timeseries_30d || []).map(d => d.date);
    const values = (data.timeseries_30d || []).map(d => d.revenue);
    
    lotChartData.value = {
      labels,
      datasets: [{
        label: 'Revenue',
        data: values,
        fill: true,
        tension: 0.4,
        borderColor: '#60a5fa',
        backgroundColor: 'rgba(59, 130, 246, 0.15)',
        borderWidth: 2,
        pointBackgroundColor: '#60a5fa',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 6
      }]
    };

    showLotAnalyticsModal.value = true;
  } catch (err) {
    console.error(err);
    alert('Error loading lot analytics.');
  }
};

const closeLotAnalytics = () => {
  showLotAnalyticsModal.value = false;
  lotAnalyticsData.value = null;
  lotChartData.value = null;
};

// Function to open modal and fetch data ===
const openUserModal = async (userId) => {
  userDetails.value = null; // Clear previous data
  loadingUser.value = true;
  showUserModal.value = true;

  try {
    const res = await apiFetch(`/users/${userId}`);
    if (res.ok) {
      userDetails.value = await res.json();
    } else {
      alert('Failed to fetch user details');
      showUserModal.value = false;
    }
  } catch (e) {
    console.error(e);
    alert('Error connecting to server');
    showUserModal.value = false;
  } finally {
    loadingUser.value = false;
  }
};

const closeUserModal = () => {
  showUserModal.value = false;
  userDetails.value = null;
};

// Mount & Auto Refresh
onMounted(() => {
  fetchData();
  // Tame interval
  autoRefreshInterval = setInterval(() => {
    fetchData();
  }, 20000);
});

// Clean up interval when component is destroyed
onUnmounted(() => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
});
</script>

<style scoped>
/* --- VARIABLES & BASE --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

.admin-container {
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  background: radial-gradient(circle at top left, #1e293b, #0f172a);
  color: #f1f5f9;
  padding: 2rem 1rem;
  box-sizing: border-box;
}

/* Glassmorphism utility */
.glass-panel {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
}

/* --- HEADER --- */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  margin-bottom: 2.5rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.gradient-text {
  background: linear-gradient(135deg, #60a5fa, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  font-size: 1.8rem;
}

.admin-subtitle {
  color: #94a3b8;
  font-size: 0.95rem;
  margin-top: 0.25rem;
}

/* --- MAIN LAYOUT --- */
.admin-content {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.section-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #e2e8f0;
}

/* --- BUTTONS --- */
.btn-text {
  background: linear-gradient(135deg, #cb6666, #eb2525);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(235, 37, 37, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-text:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(235, 37, 37, 0.6);
}

.btn-primary-glow {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
}

.btn-secondary {
  background: transparent;
  border: 1px solid #475569;
  color: #cbd5e1;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
}
.btn-danger {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  margin-left: 0.5rem;
}

/* --- GRID & CARDS --- */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  /* prevents siblings from stretching height */
  align-items: start; 
}

.lot-card {
  padding: 1.5rem;
  transition: transform 0.3s ease, border-color 0.3s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}
.lot-card.interactive:hover {
  transform: translateY(-5px);
  border-color: rgba(96, 165, 250, 0.5);
}
.lot-card.is-expanded {
  border-color: #60a5fa;
  background: rgba(30, 41, 59, 0.85);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.lot-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}
.lot-badges {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.badge-pin, .badge-price {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.4);
  color: #94a3b8;
}
.badge-price {
  color: #c084fc;
  background: rgba(192, 132, 252, 0.1);
}

.lot-actions {
  display: flex;
  gap: 0.5rem;
}
.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.icon-btn:hover {
  color: white;
  background: #334155;
}
.icon-btn.delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-color: #ef4444;
}

.card-body {
  margin-top: 1rem;
}
.address-text {
  font-size: 0.85rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
  height: 40px; /* fixed height for alignment */
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Progress Bar */
.occupancy-wrapper {
  margin-top: auto;
}
.occupancy-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  margin-bottom: 0.4rem;
}
.progress-track {
  height: 8px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease-in-out, background-color 0.3s;
}
.bg-success { background: linear-gradient(90deg, #10b981, #34d399); box-shadow: 0 0 10px rgba(52, 211, 153, 0.4); }
.bg-warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.bg-critical { background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 10px rgba(248, 113, 113, 0.4); }

/* --- EXPANDED DETAILS --- */
.lot-details {
  margin-top: 1rem;
}
.details-divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.2);
  margin-bottom: 1rem;
}
.details-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.details-header h6 {
  margin: 0;
  font-size: 0.85rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.legend {
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  align-items: center;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}
.available { background: #34d399; box-shadow: 0 0 5px #34d399; }
.occupied { background: #ef4444; }

.spot-grid-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 150px;
  overflow-y: auto;
  padding-right: 4px;
}
/* Scrollbar styling */
.spot-grid-container::-webkit-scrollbar { width: 4px; }
.spot-grid-container::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }

.spot-indicator {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  transition: transform 0.2s;
}
.spot-indicator.is-available {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid #10b981;
}
.spot-indicator.is-occupied {
  background: rgba(239, 68, 68, 0.8);
  border: 1px solid #ef4444;
}

/* --- TABLE STYLES (USERS) --- */
.table-container {
  padding: 0;
  overflow: hidden;
}
.panel-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  flex-wrap: wrap;
  gap: 1rem;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.badge-count {
  background: #334155;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
}
.search-input-wrapper.small {
  position: relative;
  width: 200px;
}
.search-input-wrapper.small .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.8rem;
}
.modern-input.compact {
  padding: 0.5rem 0.75rem 0.5rem 2rem;
  font-size: 0.85rem;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
}
.modern-table th {
  text-align: left;
  padding: 1rem 1.5rem;
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}
.modern-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.05);
  vertical-align: middle;
}
.interactive-row {
  transition: background 0.2s;
}
.interactive-row:hover {
  background: rgba(255, 255, 255, 0.05);
}
.id-col { font-family: monospace; color: #64748b; }
.user-cell { display: flex; align-items: center; gap: 1rem; }
.user-avatar {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 0.9rem;
}
.user-info { display: flex; flex-direction: column; }
.username { font-weight: 600; font-size: 0.95rem; }
.email { font-size: 0.8rem; color: #94a3b8; }
.role-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 600;
}
.role-badge.admin { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.role-badge.user { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; }
.status-dot.active { color: #34d399; font-size: 0.8rem; display: flex; align-items: center; gap: 0.3rem; }
.status-dot.active::before { content: ''; width: 6px; height: 6px; background: currentColor; border-radius: 50%; }

 /* SEARCH  */
.search-hero {
  padding: 2rem;
  text-align: center;
  position: relative;
  z-index: 10;
  margin-bottom: 2.5rem;
}
.search-bar-wrapper {
  display: flex;
  max-width: 600px;
  margin: 1.5rem auto 0;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #475569;
  border-radius: 50px;
  padding: 0.3rem;
}
.custom-select {
  background: transparent;
  border: none;
  color: #cbd5e1;
  padding: 0.5rem 1rem;
  border-right: 1px solid #475569;
  outline: none;
}
.search-input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 0.5rem 1rem;
  color: white;
  outline: none;
}
.search-btn {
  background: #3b82f6;
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.2s;
}
.search-btn:hover { background: #2563eb; }

 /* --- SUMMARY STYLES (ENHANCED) --- */
.summary-wrapper {
  padding-bottom: 2rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1.2fr 1.8fr;
  gap: 1.5rem;
  align-items: stretch;
}

/* Revenue Card Revised */
.revenue-card {
  position: relative;
  overflow: hidden;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: 1px solid rgba(96, 165, 250, 0.2);
}
.stat-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  background: rgba(250, 204, 21, 0.1);
  color: #facc15;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}
.stat-label {
  font-size: 0.9rem;
  color: #94a3b8;
  margin-bottom: 0.5rem;
}
.stat-value {
  font-size: 2.75rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
  letter-spacing: -0.5px;
}
.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  font-weight: 500;
}
.stat-trend.positive { color: #34d399; }
.stat-glow {
  position: absolute;
  top: -50px; right: -50px;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

/* Chart Card Revised */
.chart-card {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
}
.panel-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.panel-header-simple h3 {
  font-size: 1.1rem;
  margin: 0;
  color: #e2e8f0;
}
.header-badge {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  border: 1px solid #334155;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}
.chart-flex-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}
.chart-container-summary {
  height: 300px;
  width: 300px;
  position: relative;
}
.chart-legend-vertical {
  flex: 1;
  margin-left: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 8px;
}
.legend-info { display: flex; flex-direction: column; }
.legend-val { font-weight: 700; font-size: 1.1rem; color: white; }
.legend-lbl { font-size: 0.8rem; color: #94a3b8; }
.legend-dot { width: 10px; height: 10px; border-radius: 2px; }

/* Lots Analytics Grid */
.section-subtitle {
  color: #e2e8f0;
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid #3b82f6;
  padding-left: 1rem;
}
.lots-analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.lot-analytics-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(148, 163, 184, 0.05);
}
.lot-analytics-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  border-color: rgba(96, 165, 250, 0.3);
}

.la-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}
.la-title-group { display: flex; flex-direction: column; }
.la-name { margin: 0; font-size: 1rem; font-weight: 600; color: #f1f5f9; }
.la-id { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; font-family: monospace; }
.la-revenue-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #34d399;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}
.la-divider { height: 1px; background: rgba(255,255,255,0.05); margin-bottom: 1rem; }

.la-stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.la-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.stat-icon { color: #64748b; font-size: 0.9rem; margin-bottom: 0.3rem; }
.stat-num { font-weight: 700; color: #e2e8f0; font-size: 1.1rem; }
.stat-lbl { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; }

.la-progress-mini {
  height: 4px;
  background: #1e293b;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 1.25rem;
}
.la-progress-mini .track { width: 100%; height: 100%; }
.la-progress-mini .fill { background: #3b82f6; height: 100%; border-radius: 2px; }

.btn-analytics-ghost {
  width: 100%;
  padding: 0.6rem;
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}
.btn-analytics-ghost:hover {
  background: #3b82f6;
  color: white;
}
.empty-placeholder { width: 100%; text-align: center; color: #64748b; padding: 2rem; font-style: italic; }

/* Animation Classes */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-up {
  opacity: 0;
  animation: fadeUp 0.6s ease-out forwards;
  animation-delay: var(--delay, 0s);
}

/* --- ANIMATED MODAL ANALYTICS --- */
.analytics-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-box {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  transition: transform 0.2s;
}
.stat-box:hover {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(96, 165, 250, 0.3);
  transform: translateY(-2px);
}
.icon-circle {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.icon-circle.revenue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.icon-circle.bookings { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.icon-circle.month { background: rgba(168, 85, 247, 0.15); color: #a855f7; }
.icon-circle.duration { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.stat-content-mini { display: flex; flex-direction: column; }
.stat-content-mini .label { font-size: 0.75rem; color: #94a3b8; margin-bottom: 2px; }
.stat-content-mini .value { font-size: 1rem; font-weight: 700; color: #e2e8f0; }

.chart-section {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 12px;
  border: 1px solid rgba(51, 65, 85, 0.3);
  padding: 1.5rem;
}
.chart-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.chart-header-row h4 { margin: 0; font-size: 1rem; color: #e2e8f0; font-weight: 600; }
.chart-badge {
  font-size: 0.7rem; background: rgba(59, 130, 246, 0.1); color: #60a5fa; 
  padding: 0.2rem 0.6rem; border-radius: 4px; border: 1px solid rgba(59, 130, 246, 0.2);
}
.chart-modal-inner { height: 260px; position: relative; }

/* Slide Up Animation for Modal Content */
@keyframes slideUpShort {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-slide-up {
  opacity: 0;
  animation: slideUpShort 0.5s ease-out forwards;
  animation-delay: var(--delay, 0s);
}

/* --- MODAL STYLES --- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-content {
  width: 90%;
  max-width: 500px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}
.modal-content.mini { max-width: 400px; padding: 2rem; }
.modal-header {
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.modal-body { padding: 1.5rem; }
.close-btn { background: none; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; }
.form-group { margin-bottom: 1rem; }
.form-row { display: flex; gap: 1rem; }
.form-group.half { flex: 1; }
.form-group label { display: block; font-size: 0.85rem; color: #cbd5e1; margin-bottom: 0.4rem; }
.modern-input {
  width: 100%;
  background: #0f172a;
  border: 1px solid #334155;
  padding: 0.75rem;
  border-radius: 8px;
  color: white;
  outline: none;
  box-sizing: border-box;
}
.modern-input:focus { border-color: #60a5fa; box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2); }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; }
.modal-actions.center { justify-content: center; }
.modal-icon.warning {
  font-size: 3rem;
  color: #facc15;
  text-align: center;
  margin-bottom: 1rem;
}

/* --- ANIMATIONS --- */
/* Page Transitions */
.fade-slide-enter-active, .fade-slide-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }

/* Accordion */
.accordion-enter-active, .accordion-leave-active { transition: all 0.3s ease; max-height: 200px; opacity: 1; }
.accordion-enter-from, .accordion-leave-to { max-height: 0; opacity: 0; padding: 0; margin: 0; }

/* Modal */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .modal-content { animation: modal-scale 0.25s ease-out; }
@keyframes modal-scale { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }

/* Responsive */
@media (max-width: 768px) {
  .admin-header { flex-direction: column; gap: 1rem; align-items: flex-start; }
  .analytics-grid { grid-template-columns: 1fr; }
  .grid-layout { grid-template-columns: 1fr; }
  .search-hero { margin-bottom: 2rem; }
  .lots-analytics-grid { grid-template-columns: 1fr; }
  .chart-flex-wrapper { flex-direction: column; height: auto; }
  .chart-container-summary { margin-bottom: 1.5rem; }
  .chart-legend-vertical { margin-left: 0; width: 100%; flex-direction: row; justify-content: center; }
  .analytics-grid-modal { grid-template-columns: 1fr 1fr; }
}

.text-muted { color: #94a3b8; }
.text-danger { color: #f87171; }
.text-success { color: #4ade80; }


/* Release Modal confirm */
.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
}

.text-accent {
  color: #38bdf8;
  font-weight: 600;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0rem 0.4rem;
  transition: all 0.2s ease;
}
.status-badge.occupied {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}
.status-badge.free {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.status-badge.clickable {
  cursor: pointer;
}
.status-badge.clickable:hover {
  background: rgba(239, 68, 68, 0.25);
  transform: translateY(-1px);
}

/*  STYLES FOR USER MODAL */
.user-avatar-large {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: bold;
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

/* Custom Scrollbar for history list */
.history-list::-webkit-scrollbar {
  width: 4px;
}
.history-list::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

.history-item {
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(15, 23, 42, 0.3);
  border-radius: 8px;
}
</style>