<template>
  <div class="dashboard-container">
    <header class="dashboard-header animate-fade-down">
      <div class="header-left">
        <h2 class="title">My<span class="text-highlight"> Dashboard</span></h2>
        <div class="user-pill">
          <span class="status-dot online"></span>
          <span class="email-text">{{ userEmail }}</span>
        </div>
      </div>
      
      <div class="header-right">
        <button class="btn-glass-action" @click="downloadCSV" :disabled="exporting" title="Download History">
          <i class="fas fa-file-csv"></i> <span class="btn-text">Export</span>
        </button>
        <button class="btn-glass-action" @click="sendCsvToEmail" :disabled="exportingMail" title="Email Report">
          <i class="fas fa-envelope"></i> <span class="btn-text">Email</span>
        </button>
      </div>
    </header>

    <div class="content-wrapper">
      
      <transition name="fast-fade" mode="out-in">
        <div v-if="currentTab === 'home'" key="home" class="tab-view">
          
          <div class="split-layout">
            
            <section class="panel-section glass-panel fixed-height">
              <div class="panel-header-row sticky-top">
                <div class="ph-left">
                  <h3><i class="fas fa-bolt text-accent"></i>  Active Bookings</h3>
                </div>
                <div class="ph-right">
                  <div class="mini-search">
                    <i class="fas fa-search"></i>
                    <input placeholder="Search..." v-model="liveSearch" />
                  </div>
                  <div class="control-group">
                    <select v-model="liveSort" class="glass-select mini" title="Sort Order">
                      <option value="newest">Newest</option>
                      <option value="oldest">Oldest</option>
                    </select>
                    <select v-model="liveGroupBy" class="glass-select mini" title="View Mode">
                      <option value="none">List</option>
                      <option value="lot">Group</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="scroll-container">
                <div v-if="sortedActiveBookings.length === 0" class="empty-mini">
                  <div class="empty-icon"><i class="fas fa-car-battery"></i></div>
                  <p>No active sessions.</p>
                </div>

                <div v-else class="live-content">
                  <div v-if="liveGroupBy === 'lot'">
                    <div v-for="(group, lotName) in groupedActiveBookings" :key="lotName" class="live-group mb-3">
                      <div class="group-header">
                        <span class="gh-name">{{ lotName }}</span>
                        <span class="gh-count">{{ group.length }} active</span>
                      </div>
                      <div class="live-list">
                        <div v-for="r in group" :key="r.id" class="live-card glow-border">
                          <div class="live-top">
                            <div class="live-spot-pill">{{ r.spot }}</div>
                            <div class="live-status-badge">ACTIVE</div>
                          </div>
                          <div class="live-meta-grid">
                            <div class="meta-item">
                              <label>Start</label> <span>{{ r.start_time.split(' ')[1] }}</span>
                            </div>
                            <div class="meta-item">
                              <label>Duration</label> <span class="text-highlight">{{ r.duration }}</span>
                            </div>
                            
                            
                          </div>
                          <button class="btn-terminate pulsing" @click="openReleaseModal(r)" :disabled="loadingReleaseMap[r.id]">
                            {{ loadingReleaseMap[r.id] ? '...' : 'End Session' }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else class="live-list">
                    <div v-for="r in sortedActiveBookings" :key="r.id" class="live-card glow-border">
                      <div class="live-top">
                        <div class="live-lot-info">
                          <span class="live-lot-name">{{ r.lot }}</span>
                          <div class="live-spot-pill">{{ r.spot }}</div>
                        </div>
                        <div class="live-status-badge">ACTIVE</div>
                      </div>
                      
                      <div class="live-meta-grid">
                        <div class="meta-item">
                          <label>Start Time</label>
                          <span>{{ r.start_time }}</span>
                        </div>
                        <div class="meta-item">
                          <label>Duration</label>
                          <span class="text-highlight">{{ r.duration }}</span>
                        </div>
                      </div>

                      <button 
                        class="btn-terminate pulsing" 
                        @click="openReleaseModal(r)" 
                        :disabled="loadingReleaseMap[r.id]"
                      >
                        {{ loadingReleaseMap[r.id] ? 'Calculating...' : 'End Session' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section class="panel-section glass-panel fixed-height">
              <div class="panel-header-row sticky-top">
                <h3><i class="fas fa-map-marker-alt text-highlight"></i> Find a Spot</h3>
                <div class="ph-right">
                  <div class="mini-search">
                    <i class="fas fa-search"></i>
                    <input placeholder="Location, Pin..." v-model="lotSearch" />
                  </div>
                </div>
              </div>

              <div class="scroll-container">
                <div v-if="filteredLots.length === 0" class="empty-mini">
                  <p>No locations match your search.</p>
                </div>

                <div v-else class="lots-list">
                  <div v-for="lot in filteredLots" :key="lot.id" class="lot-card-modern">
                    <div class="lc-left">
                      <div class="price-circle">
                        <span class="symbol">₹</span>
                        <span class="amt">{{ formatNumber(lot.price_per_hour) }}</span>
                        <span class="unit">/hr</span>
                      </div>
                    </div>
                    <div class="lc-mid">
                      <h4>{{ lot.name }}</h4>
                      <p class="lc-addr">{{ lot.address }}</p>
                      <p class="lc-pin" v-if="lot.pin_code"><i class="fas fa-thumbtack"></i> {{ lot.pin_code }}</p>
                      
                      <div class="lc-bar-wrap">
                        <div class="lc-bar">
                          <div class="lc-fill" :style="{ width: getAvailabilityWidth(lot) + '%' }" :class="getAvailabilityColor(lot)"></div>
                        </div>
                        <span class="lc-stat">{{ lot.available_spots }} spots left</span>
                      </div>
                    </div>
                    <div class="lc-right">
                      <button 
                        class="btn-book-now" 
                        @click="openReserveModal(lot)"
                        :disabled="loadingReserveMap[lot.id] || lot.available_spots === 0"
                      >
                        Book
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <section class="section-block mt-4">
            <div class="glass-panel auto-height">
              <div class="panel-header-row border-bot">
                <h3><i class="fas fa-history text-muted"></i> History</h3>
                
                <div class="controls-row">
                  <div class="mini-search wide">
                    <i class="fas fa-search"></i>
                    <input type="text" placeholder="Search records..." v-model="historySearch" />
                  </div>
                  <select v-model="historySort" class="glass-select">
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="cost-desc">High Cost</option>
                  </select>
                  <select v-model="historyGroupBy" class="glass-select">
                    <option value="none">List View</option>
                    <option value="lot">Group by Lot</option>
                  </select>
                </div>
              </div>

              <div class="history-content-flow">
                <div v-if="historyBookings.length === 0" class="empty-mini py-5">
                  <p>No completed parking history found.</p>
                </div>

                <div v-else-if="historyGroupBy === 'lot'" class="grouped-history p-3">
                  <div v-for="(group, lotName) in historyGroupedByLot" :key="lotName" class="history-group mb-4">
                    <h5 class="group-title">{{ lotName }} <span class="count-badge">{{ group.length }}</span></h5>
                    <div class="history-grid-cards">
                      <div v-for="r in group" :key="r.id" class="history-mini-card">
                        <div class="hm-top">
                          <span class="hm-spot">{{ r.spot }}</span>
                          <span class="hm-cost">₹{{ formatNumber(r.cost) }}</span>
                        </div>
                        <div class="hm-bot">
                          <span title="Start Time">{{ r.start_time }}</span>
                          <span class="text-muted small">to {{ r.end_time || '?' }}</span>
                          <span class="hm-dur">{{ r.duration }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-else class="history-list-view">
                  <div v-for="r in filteredHistory" :key="r.id" class="history-row">
                    <div class="hr-left">
                      <div class="hr-icon"><i class="fas fa-check"></i></div>
                      <div class="hr-info">
                        <span class="hr-lot">{{ r.lot }} <small class="text-accent">({{ r.spot }})</small></span>
                        <div class="hr-dates">
                          <span>{{ r.start_time }}</span>
                          <i class="fas fa-arrow-right mx-2 text-muted" style="font-size:0.7rem"></i>
                          <span>{{ r.end_time }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="hr-right">
                      <span class="hr-dur">{{ r.duration }}</span>
                      <span class="hr-cost">₹{{ formatNumber(r.cost) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </div>
      </transition>

      <transition name="fast-fade" mode="out-in">
        <div v-if="currentTab === 'summary'" key="summary" class="tab-view">
          
          <div class="summary-header">
            <h3>Overview</h3>
            <button class="btn-refresh-modern" @click="fetchSummary" :disabled="summaryLoading">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': summaryLoading }"></i> 
              <span>Refresh</span>
            </button>
          </div>

          <div v-if="summaryError" class="error-banner">{{ summaryError }}</div>

          <div v-else class="summary-layout">
            <div class="summary-left">
              <div class="hero-stat glass-panel">
                <div class="icon-circle"><i class="fas fa-wallet"></i></div>
                <div class="stat-details">
                  <span class="label">Total Spent Lifetime</span>
                  <span class="value">₹{{ formatNumber(summary.total_spent) }}</span>
                </div>
              </div>

              <div class="chart-box glass-panel">
                <h5>30-Day Spending Trend</h5>
                <div class="chart-wrapper">
                  <canvas ref="timeseriesChart"></canvas>
                </div>
              </div>
            </div>

            <div class="summary-right">
              <div class="list-panel glass-panel">
                <div class="panel-head">
                  <h5>Spending by Lot</h5>
                  <input class="mini-search" placeholder="Search..." v-model="summaryLotSearch" />
                </div>
                
                <div class="scroll-area">
                  <div 
                    v-for="p in filteredPerLot" 
                    :key="p.lot_id" 
                    class="list-item"
                    @click="openAnalyticsModal(p.lot_id)"
                  >
                    <div class="item-info">
                      <span class="name">{{ p.lot_name }} - </span>
                      <span style="margin-left: 1rem;" class="cost"> ₹{{ formatNumber(p.total_spent) }}</span>
                    </div>
                    <button class="btn-icon-small"><i class="fas fa-chart-bar"></i></button>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </transition>

    </div>

    <transition name="toast-slide">
      <div v-if="notification.show" class="toast-notification" :class="notification.type">
        <div class="toast-icon">
          <i v-if="notification.type === 'success'" class="fas fa-check-circle"></i>
          <i v-else class="fas fa-info-circle"></i>
        </div>
        <div class="toast-content">{{ notification.message }}</div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="reserveModalVisible" class="modal-backdrop" @click.self="closeReserveModal">
        <div class="modal-window glass-panel">
          <div class="modal-top">
            <h4>Confirm Reservation</h4>
            <button class="btn-close" @click="closeReserveModal">&times;</button>
          </div>
          <div class="modal-mid">
            <h2 class="lot-title">{{ pendingLot?.name }}</h2>
            <div class="lot-meta-details mb-3">
              <div class="d-flex align-items-center gap-2 text-muted mb-1">
                <i class="fas fa-map-marker-alt"></i> {{ pendingLot?.address }}
              </div>
              <div class="d-flex align-items-center gap-2 text-muted" v-if="pendingLot?.pin_code">
                <i class="fas fa-thumbtack"></i> {{ pendingLot?.pin_code }}
              </div>
            </div>
            
            <div class="qty-selector-large">
              <label>Number of Spots (1-10)</label>
              <div class="stepper">
                <button @click="pendingQty = Math.max(1, pendingQty - 1)">-</button>
                <span class="qty-num">{{ pendingQty }}</span>
                <button @click="pendingQty = Math.min(10, pendingQty + 1)">+</button>
              </div>
            </div>

            <div class="est-cost">
              <span>Approx. 1st Hour Charge</span>
              <span class="val">₹{{ formatNumber(estimatedReserveCost) }}</span>
            </div>
            <p class="modal-note">Hourly charges applies for first hour per spot.</p>
          </div>
          <div class="modal-bot">
            <button class="btn-ghost" @click="closeReserveModal">Cancel</button>
            <button class="btn-action" @click="confirmReserve" :disabled="reserveSubmitting">
              {{ reserveSubmitting ? 'Booking...' : 'Confirm & Pay Later' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="releaseModalVisible" class="modal-backdrop" @click.self="closeReleaseModal">
        <div class="modal-window glass-panel warning">
          <div class="modal-top">
            <h4>End Parking Session?</h4>
            <button class="btn-close" @click="closeReleaseModal">&times;</button>
          </div>
          <div class="modal-mid">
            <p class="mb-3">You are checking out of <strong>{{ pendingRelease?.lot }}</strong></p>
            
            <div class="info-grid-simple">
              <div class="info-cell">
                <label>Spot</label> <b>{{ pendingRelease?.spot }}</b>
              </div>
              <div class="info-cell">
                <label>Start</label> <b>{{ pendingRelease?.start_time }}</b>
              </div>
              <div class="info-cell">
                <label>Duration</label> <b>{{ pendingRelease?.duration }}</b>
              </div>
            </div>

            <div class="est-cost warning">
              <span>Bill Estimate</span>
              <span class="val">₹{{ formatNumber(estimatedReleaseCost) }}</span>
            </div>
            <p class="modal-note">First hour is fully charged. Final amount calculated by server.</p>
          </div>
          <div class="modal-bot">
            <button class="btn-ghost" @click="closeReleaseModal">Cancel</button>
            <button class="btn-danger" @click="confirmRelease" :disabled="releaseSubmitting">
              {{ releaseSubmitting ? 'Ending...' : 'Confirm & Release' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="modal-fade">
      <div v-if="analyticsModalVisible" class="modal-backdrop" @click.self="closeAnalyticsModal">
        <div class="modal-window glass-panel large">
          <div class="modal-top">
            <h4>Lot Analytics</h4>
            <button class="btn-close" @click="closeAnalyticsModal">&times;</button>
          </div>
          
          <div class="modal-mid" v-if="selectedLotAnalyticsLoading">
            <div class="loader-area"><i class="fas fa-spinner fa-spin"></i> Loading data...</div>
          </div>

          <div class="modal-mid" v-else-if="selectedLotAnalytics">
            <div class="ma-header">
              <h2 class="ma-title">{{ selectedLotAnalytics.lot_name }}</h2>
              <span class="ma-total">₹{{ formatNumber(selectedLotAnalytics.total_revenue) }}</span>
            </div>
            
            <div class="ma-grid">
              <div class="ma-card">
                <label>Today's Bookings:</label>
                <b style="margin-left: 5px;">{{ selectedLotAnalytics.todays_bookings }}</b>
              </div>
              <div class="ma-card">
                <label>Month:</label>
                <b style="margin-left: 5px;">{{ selectedLotAnalytics.months_bookings }}</b>
              </div>
              <div class="ma-card">
                <label>Avg Time:</label>
                <b style="margin-left: 5px;">{{ selectedLotAnalytics.avg_duration_minutes }}m</b>
              </div>
            </div>

            <div class="ma-chart-container">
              <h5>Revenue Trend</h5>
              <div class="canvas-wrap">
                <canvas ref="lotTimeseriesChart"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Chart } from 'chart.js/auto';
import { apiFetch } from '../api'; 

const route = useRoute();
const router = useRouter();

const userEmail = localStorage.getItem('user_email') || '';
const lots = ref([]);
const reservations = ref([]);
const currentTab = ref(route.query.tab || 'home');

// Maps
const qtyMap = reactive({});
const loadingReserveMap = reactive({});
const loadingReleaseMap = reactive({});

// Filters
const lotSearch = ref('');
const liveSearch = ref('');
const liveSort = ref('newest');
const liveGroupBy = ref('none');
const historySearch = ref('');
const historySort = ref('newest');
const historyGroupBy = ref('none');

// Modals
const reserveModalVisible = ref(false);
const pendingLot = ref(null);
const pendingQty = ref(1); 
const reserveSubmitting = ref(false);

const releaseModalVisible = ref(false);
const pendingRelease = ref(null);
const releaseSubmitting = ref(false);

const analyticsModalVisible = ref(false);
const selectedLotAnalytics = ref(null);
const selectedLotAnalyticsLoading = ref(false);

const exporting = ref(false);
const exportingMail = ref(false);
let refreshInterval = null;

// Notification
const notification = reactive({ show: false, message: '', type: 'success' });
let notificationTimeout = null;
const showToast = (msg, type = 'success') => {
  notification.message = msg;
  notification.type = type;
  notification.show = true;
  if (notificationTimeout) clearTimeout(notificationTimeout);
  notificationTimeout = setTimeout(() => { notification.show = false; }, 4000);
};

// Summary
const summary = reactive({ total_spent:0, per_lot:[], timeseries_30d:[], lots_list:[] });
const summaryLoading = ref(false);
const summaryError = ref('');
const summaryLotSearch = ref('');

const timeseriesChart = ref(null);
let timeseriesChartInstance = null;
const lotTimeseriesChart = ref(null);
let lotTimeseriesChartInstance = null;

const formatNumber = (v) => (v===null||v===undefined||isNaN(Number(v)))? '0' : Number(v).toLocaleString('en-IN',{maximumFractionDigits:2});
const switchTab = (tab) => {
  currentTab.value = tab;
  router.replace({ query: { ...route.query, tab } });
};

/* --- Data Fetching --- */
const fetchData = async () => {
  try {
    const [lotsRes, myRes] = await Promise.all([
      apiFetch('/available-lots'),
      apiFetch('/my-reservations', { method:'POST', body: JSON.stringify({ email: userEmail }) })
    ]);
    lots.value = lotsRes.ok ? await lotsRes.json() : [];
    reservations.value = myRes.ok ? await myRes.json() : [];
  } catch (err) {
    console.error('Fetch error', err);
  }
};

const fetchSummary = async () => {
  summaryLoading.value = true;
  try {
    const res = await apiFetch('/user-summary', { method: 'POST', body: JSON.stringify({ email: userEmail }) });
    if (!res.ok) throw new Error('Failed to load summary');
    const data = await res.json();
    summary.total_spent = Number(data.total_spent || 0);
    summary.per_lot = data.per_lot || [];
    summary.timeseries_30d = data.timeseries_30d || [];
    await nextTick();
    updateTimeseriesChart();
  } catch (err) {
    summaryError.value = err.message;
  } finally {
    summaryLoading.value = false;
  }
};

const openAnalyticsModal = async (lot_id) => {
  analyticsModalVisible.value = true;
  selectedLotAnalyticsLoading.value = true;
  selectedLotAnalytics.value = null;
  try {
    const res = await apiFetch(`/parking-lot/${lot_id}/analytics`, { method:'POST', body: JSON.stringify({ email: userEmail }) });
    if (!res.ok) return;
    selectedLotAnalytics.value = await res.json();
    await nextTick();
    setTimeout(() => { updateLotTimeseriesChart(); }, 150);
  } finally {
    selectedLotAnalyticsLoading.value = false;
  }
};
const closeAnalyticsModal = () => { analyticsModalVisible.value = false; };

onMounted(async ()=>{
  await fetchData();
  if (currentTab.value === 'summary') await fetchSummary();
  // AUTO REFRESH (30s)
  refreshInterval = setInterval(() => {
    if (currentTab.value === 'home') fetchData();
    else if (currentTab.value === 'summary') fetchSummary();
  }, 30000);
});

watch(()=>route.query.tab, (v)=>{
  const tab = v || 'home';
  currentTab.value = tab;
  if (tab === 'summary') fetchSummary();
}, { immediate:true });

onBeforeUnmount(() => {
  if (refreshInterval) clearInterval(refreshInterval);
  if (timeseriesChartInstance) timeseriesChartInstance.destroy();
  if (lotTimeseriesChartInstance) lotTimeseriesChartInstance.destroy();
});

/* --- Splitting & Filtering --- */
const activeBookings = computed(() => reservations.value.filter(r => r.active));
const historyBookings = computed(() => reservations.value.filter(r => !r.active));

// Live Session Filtering & Sorting
const sortedActiveBookings = computed(() => {
  const q = liveSearch.value.trim().toLowerCase();
  let list = activeBookings.value.filter(r => (r.lot + r.spot).toLowerCase().includes(q));
  
  if (liveSort.value === 'newest') {
    list.sort((a,b) => new Date(b.start_ts) - new Date(a.start_ts));
  } else {
    list.sort((a,b) => new Date(a.start_ts) - new Date(b.start_ts));
  }
  return list;
});

const groupedActiveBookings = computed(() => {
  const groups = {};
  sortedActiveBookings.value.forEach(r => {
    if(!groups[r.lot]) groups[r.lot] = [];
    groups[r.lot].push(r);
  });
  return groups;
});

const filteredHistory = computed(() => {
  const q = historySearch.value.trim().toLowerCase();
  let list = historyBookings.value.filter(r => 
    (r.lot + r.spot + r.start_time).toLowerCase().includes(q)
  );
  
  if (historySort.value === 'newest') {
    list.sort((a,b) => new Date(b.end_ts || b.start_ts) - new Date(a.end_ts || a.start_ts));
  } else if (historySort.value === 'oldest') {
    list.sort((a,b) => new Date(a.end_ts || a.start_ts) - new Date(b.end_ts || b.start_ts));
  } else if (historySort.value === 'cost-desc') {
    list.sort((a,b) => (b.cost || 0) - (a.cost || 0));
  }
  return list;
});

const historyGroupedByLot = computed(() => {
  const groups = {};
  filteredHistory.value.forEach(r => {
    if(!groups[r.lot]) groups[r.lot] = [];
    groups[r.lot].push(r);
  });
  return groups;
});

const filteredLots = computed(() => {
  const q = lotSearch.value.trim().toLowerCase();
  if(!q) return lots.value;
  return lots.value.filter(l => (l.name + l.address + (l.pin_code||'')).toLowerCase().includes(q));
});

const filteredPerLot = computed(() => {
  const q = summaryLotSearch.value.trim().toLowerCase();
  if(!q) return summary.per_lot;
  return summary.per_lot.filter(p => p.lot_name.toLowerCase().includes(q));
});

/* --- Actions --- */
const openReserveModal = (lot) => { 
  pendingLot.value = lot; 
  pendingQty.value = 1; 
  reserveModalVisible.value = true; 
};
const closeReserveModal = () => { reserveModalVisible.value = false; pendingLot.value = null; };

const estimatedReserveCost = computed(() => {
  if (!pendingLot.value) return 0;
  return Number(pendingLot.value.price_per_hour || 0) * Number(pendingQty.value);
});

const confirmReserve = async () => {
  if(!pendingLot.value) return;
  reserveSubmitting.value = true;
  try{
    const res = await apiFetch('/reserve', { method:'POST', body: JSON.stringify({ lot_id: pendingLot.value.id, user_email: userEmail, quantity: Number(pendingQty.value) })});
    const data = await res.json();
    if(res.ok){
      const spots = data.reservations ? data.reservations.map(r => r.spot).join(', ') : 'Allocated';
      showToast(`Reservation Confirmed! Spots: ${spots}`, 'success');
      await fetchData();
      closeReserveModal();
    } else showToast(data.message || 'Failed', 'error');
  } catch(e) { showToast('Error reserving', 'error'); } finally { reserveSubmitting.value = false; }
};

const openReleaseModal = (r) => { pendingRelease.value = r; releaseModalVisible.value = true; };
const closeReleaseModal = () => { releaseModalVisible.value = false; pendingRelease.value = null; };

const estimatedReleaseCost = computed(() => {
  const r = pendingRelease.value; if(!r) return 0;
  const lot = lots.value.find(l => l.name === r.lot) || {}; 
  const price = lot.price_per_hour || 0;
  
  const durStr = r.duration || ""; 
  const hMatch = durStr.match(/(\d+)h/);
  const mMatch = durStr.match(/(\d+)m/);
  let hours = hMatch ? parseInt(hMatch[1]) : 0;
  let mins = mMatch ? parseInt(mMatch[1]) : 0;
  
  let totalHours = hours + (mins/60);
  if(totalHours < 1) totalHours = 1; // Min 1 hour rule
  
  return Math.round(totalHours * price * 100) / 100;
});

const confirmRelease = async () => {
  if(!pendingRelease.value) return;
  releaseSubmitting.value = true;
  try {
    const res = await apiFetch('/release-spot', { method:'POST', body: JSON.stringify({ reservation_id: pendingRelease.value.id }) });
    const data = await res.json();
    if(res.ok) {
      showToast(`Ended. Total Cost: ₹${formatNumber(data.cost)}`, 'success');
      await fetchData();
      closeReleaseModal();
    } else showToast(data.message, 'error');
  } catch(e) { showToast('Error releasing', 'error'); } finally { releaseSubmitting.value = false; }
};

const downloadCSV = async () => {
  if(reservations.value.length === 0) return;
  exporting.value = true;
  try {
    const headers = ['ID','Lot','Spot','Start','End','Duration','Cost','Status'];
    const rows = reservations.value.map(r => [r.id, r.lot, r.spot, r.start_time, r.end_time, r.duration, r.cost, r.active?'Active':'Done']);
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'parking_history.csv';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    showToast('CSV Downloaded', 'success');
  } finally { exporting.value = false; }
};

const sendCsvToEmail = async () => {
  exportingMail.value = true;
  try {
    const res = await apiFetch('/export-csv', { method:'POST', body: JSON.stringify({ email: userEmail }) });
    if(res.ok) showToast('Report sent to email', 'success');
  } finally { exportingMail.value = false; }
};

/* Charts */
function updateTimeseriesChart() {
  if(!timeseriesChart.value) return;
  if(timeseriesChartInstance) timeseriesChartInstance.destroy();
  const ds = summary.timeseries_30d;
  timeseriesChartInstance = new Chart(timeseriesChart.value, {
    type:'line', data:{
      labels: ds.map(d=>d.date),
      datasets:[{ label:'Spend', data:ds.map(d=>d.amount), borderColor:'#38bdf8', backgroundColor:'rgba(56,189,248,0.1)', fill:true, tension:0.4 }]
    },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{grid:{color:'rgba(255,255,255,0.05)'}}} }
  });
}

function updateLotTimeseriesChart() {
  if(!lotTimeseriesChart.value || !selectedLotAnalytics.value) return;
  if(lotTimeseriesChartInstance) lotTimeseriesChartInstance.destroy();
  const ds = selectedLotAnalytics.value.timeseries_30d;
  lotTimeseriesChartInstance = new Chart(lotTimeseriesChart.value, {
    type:'bar', data:{
      labels: ds.map(d=>d.date),
      datasets:[{ label:'Revenue', data:ds.map(d=>d.revenue), backgroundColor:'#818cf8', borderRadius:4 }]
    },
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{grid:{color:'rgba(255,255,255,0.05)'}}} }
  });
}

// Visual Helpers
const getAvailabilityWidth = (lot) => Math.min(100, Math.max(10, lot.available_spots * 5));
const getAvailabilityColor = (lot) => lot.available_spots < 5 ? 'bg-danger' : 'bg-success';

</script>

<style scoped>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

/* - Layout Shell -- */
.dashboard-container {
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: #e2e8f0;
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto 4rem auto;
}

/* ---- Header ---- */
.dashboard-header {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.text-highlight {
  color: #818cf8;
  text-shadow: 0 0 20px rgba(129, 140, 248, 0.4);
}

.user-pill {
  background: rgba(255,255,255,0.08);
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255,255,255,0.1);
}

.status-dot.online {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  box-shadow: 0 0 8px #22c55e;
}

.email-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: #cbd5e1;
}

.header-right {
  display: flex;
  gap: 0.8rem;
}

.btn-glass-action {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #cbd5e1;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: 0.2s;
}

.btn-glass-action:hover {
  background: rgba(255,255,255,0.1);
  color: white;
  transform: translateY(-2px);
}

.btn-text {
  font-size: 0.85rem;
  font-weight: 600;
}

/* - Split Layout - */
.split-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.panel-section {
  display: flex;
  flex-direction: column;
  height: 550px;
  overflow: hidden;
}

.fixed-height { height: 550px; }

.sticky-top {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(15,23,42,0.95);
  backdrop-filter: blur(10px);
}

/* Panel Header */
.panel-header-row {
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ph-left h3 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: #f8fafc;
}

.ph-right {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.mini-search {
  display: flex;
  align-items: center;
  background: rgba(0,0,0,0.3);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.1);
}

.mini-search input {
  background: transparent;
  border: none;
  color: white;
  width: 120px;
  font-size: 0.8rem;
  margin-left: 6px;
  outline: none;
}

.glass-select {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  color: #cbd5e1;
  padding: 4px 8px;
  border-radius: 6px;
  outline: none;
  font-size: 0.8rem;
}

.control-group { display: flex; gap: 4px; }

/* - Scroll Areas - */
.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.scroll-container::-webkit-scrollbar { 
  width: 6px; 
}

.scroll-container::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
}

/* Live Session List */
.live-list { display: flex; flex-direction: column; gap: 1rem; }

.live-group { margin-bottom: 1rem; }

.group-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: #94a3b8;
  font-size: 0.8rem;
  text-transform: uppercase;
  font-weight: 700;
  padding: 0 4px;
}

.live-card {
  background: rgba(30,41,59,0.6);
  border: 1px solid rgba(34,197,94,0.3);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  position: relative;
}

.glow-border { box-shadow: 0 0 10px rgba(34,197,94,0.05); }

.live-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.live-lot-name {
  font-weight: 700;
  font-size: 1.1rem;
  display: block;
  color: white;
}

.live-spot-pill {
  display: inline-block;
  background: rgba(255,255,255,0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-top: 4px;
  color: #e2e8f0;
  font-weight: 700;
}

.live-status-badge {
  background: #22c55e;
  color: #000;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  animation: pulse 2s infinite;
}

.live-meta-grid {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #cbd5e1;
  background: rgba(0,0,0,0.2);
  padding: 8px;
  border-radius: 6px;
}

.meta-item { display: flex; flex-direction: column; }

.meta-item label {
  font-size: 0.65rem;
  color: #94a3b8;
  text-transform: uppercase;
  margin-bottom: 2px;
}

.btn-terminate {
  width: 100%;
  background: rgba(239,68,68,0.15);
  color: #ef4444;
  border: 1px solid rgba(239,68,68,0.3);
  padding: 0.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
  font-size: 0.85rem;
  margin-top: auto;
}

.btn-terminate:hover:not(:disabled) { background: #ef4444; color: white; }

/* Find Spot Cards */
.lots-list { display: flex; flex-direction: column; gap: 0.8rem; }

.lot-card-modern {
  display: flex;
  align-items: center;
  background: rgba(30,41,59,0.5);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 0.8rem;
  gap: 1rem;
  transition: background 0.2s;
}

.lot-card-modern:hover { 
  background: rgba(30,41,59,0.8); 
}

.lc-left { 
  min-width: 60px; 
  text-align: center; 
}

.price-circle .symbol { 
  font-size: 0.8rem; color: #64748b; 
}

.price-circle .amt {
  font-size: 1.4rem;
  font-weight: 700;
  color: #818cf8;
  display: block;
  line-height: 1;
}

.price-circle .unit { 
  font-size: 0.7rem; 
  color: #64748b; 
}

.lc-mid { flex: 1; }

.lc-mid h4 { 
  margin: 0; font-size: 1.1rem; 
  font-weight: 600; color: white; 
}

.lc-addr {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 2px 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}

.lc-pin { 
  font-size: 0.75rem; color: #64748b; 
  margin: 2px 0 6px 0; 
}

.lc-bar-wrap { 
  margin-top: 6px; 
}

.lc-bar {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
  width: 120px;
}

.lc-fill { 
  height: 100%; 
  border-radius: 2px; 
}

.bg-success { background: #22c55e; }
.bg-danger { background: #ef4444; }

.lc-stat {
  font-size: 0.75rem;
  color: #cbd5e1;
  margin-top: 2px;
  display: block;
}

.btn-book-now {
  background: #3b82f6;
  border: none;
  color: white;
  padding: 0.4rem 1.2rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
  font-size: 0.85rem;
}

.btn-book-now:hover:not(:disabled) { background: #2563eb; }

.btn-book-now:disabled { opacity: 0.5; cursor: not-allowed; }

/* - History Section -- */
.glass-panel {
  background: rgba(30,41,59,0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  overflow: hidden;
}

.auto-height { height: auto; min-height: 200px; overflow: visible; }

.history-content-flow { padding: 0; }

.grouped-history { /* Grid style */ }

.history-group .group-title {
  margin-bottom: 0.8rem;
  font-size: 0.9rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.history-grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.history-mini-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  padding: 0.8rem;
  border-radius: 8px;
}

.hm-top { display: flex; justify-content: space-between; margin-bottom: 4px; }

.hm-spot {
  font-weight: 700;
  color: #fff;
  font-size: 0.9rem;
}

.hm-cost { color: #22c55e; font-size: 0.9rem; }

.hm-bot {
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  flex-direction: column;
}

.history-list-view { display: flex; flex-direction: column; }

.history-row {
  display: flex;
  justify-content: space-between;
  padding: 0.8rem 1.2rem;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  align-items: center;
  transition: background 0.2s;
}

.history-row:hover { background: rgba(255,255,255,0.02); }

.hr-left { 
  display: flex; gap: 1rem; 
  align-items: center; 
}

.hr-icon {
  width: 32px;
  height: 32px;
  background: rgba(34,197,94,0.1);
  color: #22c55e;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.8rem;
}

.hr-info { 
  display: flex; 
  flex-direction: column; 
}

.hr-lot {
  font-weight: 600;
  font-size: 0.95rem;
  color: white;
}

.hr-dates {
  font-size: 0.8rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}

.hr-right { 
  text-align: right; 
  display: flex; 
  flex-direction: column; 
}

.hr-dur { 
  font-size: 0.8rem; 
  color: #94a3b8; 
}

.hr-cost {
  font-weight: 700;
  color: #e2e8f0;
  font-size: 1rem;
}

/* -- Summary Header & Refresh -- */
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn-refresh-modern {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #cbd5e1;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: 0.2s;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-refresh-modern:hover:not(:disabled) {
  background: rgba(255,255,255,0.1);
  color: white;
  transform: translateY(-1px);
}

/* ---- Modals ---- */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(5px);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-window {
  width: 90%;
  max-width: 450px;
  background: #0f172a;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.1);
  overflow: hidden;
  animation: modalPop 0.25s ease-out;
}

.modal-window.large { max-width: 700px; }

.modal-top {
  padding: 1rem 1.5rem;
  background: rgba(255,255,255,0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.modal-top h4 { margin: 0; font-size: 1.1rem; font-weight: 600; }

.btn-close { background: none; border: none; color: #64748b; font-size: 1.5rem; cursor: pointer; }

.modal-mid { padding: 1.5rem; }

.modal-bot {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: rgba(0,0,0,0.2);
}

/* -- Quantity Selector in Modal - */
.qty-selector-large { margin: 1.5rem 0; text-align: center; }

.qty-selector-large label {
  display: block;
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stepper {
  display: inline-flex;
  align-items: center;
  background: rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid rgba(255,255,255,0.1);
}

.stepper button {
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.2rem;
  cursor: pointer;
  transition: 0.2s;
}

.stepper button:hover { color: white; background: rgba(255,255,255,0.1); border-radius: 6px; }

.stepper .qty-num {
  width: 50px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
}

.lot-title { font-size: 1.4rem; color: #38bdf8; margin: 0; }

.lot-meta-details { font-size: 0.85rem; margin-top: 4px; }

.est-cost {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px dashed rgba(255,255,255,0.1);
  padding-top: 1rem;
  margin-top: 1rem;
}

.est-cost .val { font-size: 1.4rem; font-weight: 800; color: #38bdf8; }

.est-cost.warning .val { color: #f43f5e; }

.modal-note {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 1rem;
  text-align: center;
}

.info-grid-simple {
  background: rgba(255,255,255,0.03);
  padding: 1rem;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-cell { display: flex; flex-direction: column; }

.info-cell label {
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
}

.info-cell b { font-size: 1rem; color: #e2e8f0; }

/* -- Buttons ---- */
.btn-action {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-danger {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.btn-ghost {
  background: transparent;
  border: 1px solid #475569;
  color: #94a3b8;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
}

.empty-mini {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #64748b;
  font-size: 0.9rem;
  flex-direction: column;
  min-height: 200px;
}

.empty-icon { font-size: 2rem; opacity: 0.3; margin-bottom: 1rem; }

/* ---- Toasts ---- */
.toast-notification {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #1e293b;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
  display: flex;
  gap: 1rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  z-index: 9999;
  max-width: 350px;
}

.toast-notification.success { border-color: #22c55e; color: #fff; }

.toast-notification.error { border-color: #ef4444; }

/* - Animations --- */
.animate-fade-down {
  animation: fadeDown 0.3s ease forwards;
  opacity: 0;
  transform: translateY(-10px);
}

.fast-fade-enter-active, .fast-fade-leave-active { transition: opacity 0.2s ease; }

.fast-fade-enter-from, .fast-fade-leave-to { opacity: 0; }

.toast-slide-enter-active { transition: all 0.3s; }

.toast-slide-enter-from { opacity: 0; transform: translateY(20px) scale(0.9); }

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
  70% { box-shadow: 0 0 0 10px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}

@keyframes modalPop { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

@keyframes fadeDown { to { opacity: 1; transform: translateY(0); } }

/* -- Summary & Analytics -- */
.summary-layout { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; }

.hero-stat {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  gap: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(56,189,248,0.2);
  background: linear-gradient(135deg, rgba(56,189,248,0.1), transparent);
  margin-bottom: 1.5rem;
}

.icon-circle { font-size: 2rem; color: #38bdf8; }

.stat-details .value { font-size: 2.2rem; font-weight: 800; display: block; line-height: 1; }

.chart-box {
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.05);
  height: 350px;
  display: flex;
  flex-direction: column;
}

.chart-wrapper { flex: 1; position: relative; }

.list-panel {
  background: rgba(30,41,59,0.4);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.05);
  height: 530px;
  display: flex;
  flex-direction: column;
}

.panel-head {
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}

.list-item:hover { background: rgba(255,255,255,0.05); }

.ma-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 1.5rem; 
}

.ma-title { 
  margin: 0; 
  font-size: 1.5rem; 
}

.ma-total { 
  font-size: 1.5rem; 
  font-weight: 800; 
  color: #22c55e; }

.ma-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr 1fr; 
  gap: 1rem; 
  margin-bottom: 2rem; 
}

.ma-card { 
  background: rgba(255,255,255,0.03); 
  padding: 1rem; 
  border-radius: 8px; 
  text-align: center; 
}

.ma-chart-container { height: 300px; display: flex; flex-direction: column; position: relative; }

.canvas-wrap { 
  flex: 1; 
  position: relative; 
  width: 100%; 
  min-height: 0; 
}

/* Responsive - */
@media (max-width: 900px) {
  .split-layout { grid-template-columns: 1fr; }
  .panel-section { height: 400px; }
  .summary-layout { grid-template-columns: 1fr; }
}

</style>