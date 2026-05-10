<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
      
      <div class="modal-content">
        
        <div class="modal-header">
          <h2>Notifications</h2>
          <div class="header-actions">
            <select v-model="activeFilter" class="filter-select">
              <option value="ALL">All Time</option>
              <option value="10M">Last 10 Minutes</option>
              <option value="30M">Last 30 Minutes</option>
              <option value="24H">Last 24 Hours</option>
              <option value="CUSTOM">Custom...</option>
            </select>
            <button class="close-btn" @click="$emit('close')">
              <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>

        <div v-if="activeFilter === 'CUSTOM'" class="custom-filter-row">
          <span class="custom-label">Last:</span>
          <input type="number" v-model.number="customValue" min="1" class="custom-input" />
          <select v-model="customUnit" class="custom-select">
            <option value="Minutes">Minutes</option>
            <option value="Hours">Hours</option>
            <option value="Days">Days</option>
          </select>
          <button @click="applyCustomFilter" class="apply-btn">Apply</button>
        </div>

        <div class="modal-body">
          <div v-if="isLoading" class="center-state">
            <p>Loading notifications...</p>
          </div>
          
          <div v-else-if="filteredNotifications.length === 0" class="center-state">
            <p>No notifications found.</p>
          </div>

          <div v-else class="notification-list">
            <div v-for="n in filteredNotifications" :key="n._id" class="notification-card">
              
              <div v-if="!n.is_read" class="unread-dot"></div>

              <div class="card-top">
                <div class="icon-warning">
                  <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4m0 4h.01"></path></svg>
                </div>
                <div class="card-info">
                  <h4>{{ n.sensor || 'Unknown Sensor' }}</h4>
                  <p class="message">{{ n.message || 'No message' }}</p>
                  <span class="timestamp">{{ formatTimestamp(n.created_at) }}</span>
                </div>
              </div>

              <div v-if="n.resolved" class="card-recovery">
                <div class="divider"></div>
                <div class="recovery-content">
                  <svg viewBox="0 0 24 24" width="16" height="16" stroke="#4CAF50" fill="none" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                  <span>Sensor recovered</span>
                </div>
                <span class="timestamp">{{ formatTimestamp(n.resolved_at) }}</span>
              </div>

            </div>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  isOpen: Boolean
});
const emit = defineEmits(['close']);

const notifications = ref([]);
const isLoading = ref(false);
const activeFilter = ref('ALL');

const API_BASE_URL = 'http://100.68.113.75:5000/api';

// State for the input fields
const customValue = ref(1);
const customUnit = ref('Hours');

// State that only updates when "Apply" is clicked
const appliedCustomValue = ref(1);
const appliedCustomUnit = ref('Hours');

const fetchNotifications = async () => {
  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/notifications`);
    if (res.ok) {
      notifications.value = await res.json();
    }
  } catch (err) {
    console.error("Failed to fetch notifications:", err);
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    fetchNotifications();
    activeFilter.value = 'ALL'; 
  }
});

// Triggered when the Apply button is clicked
const applyCustomFilter = () => {
  appliedCustomValue.value = customValue.value;
  appliedCustomUnit.value = customUnit.value;
};

const formatTimestamp = (isoString) => {
  if (!isoString) return "No timestamp";
  try {
    const d = new Date(isoString);
    return d.toLocaleString('en-US', { 
      month: 'long', day: 'numeric', year: 'numeric', 
      hour: 'numeric', minute: '2-digit', hour12: true 
    });
  } catch (e) {
    return "No timestamp";
  }
};

const filteredNotifications = computed(() => {
  if (activeFilter.value === 'ALL') return notifications.value;
  
  const now = new Date();
  
  return notifications.value.filter(n => {
    const ts = new Date(n.created_at);
    if (isNaN(ts)) return true;

    const diffMs = now - ts;
    
    if (activeFilter.value === '10M') return diffMs <= 10 * 60000;
    if (activeFilter.value === '30M') return diffMs <= 30 * 60000;
    if (activeFilter.value === '24H') return diffMs <= 24 * 3600000;
    
    if (activeFilter.value === 'CUSTOM') {
      // Uses the 'applied' values so it only filters after clicking the button
      const val = appliedCustomValue.value || 1; 
      let multiplier = 60000; 
      if (appliedCustomUnit.value === 'Hours') multiplier = 3600000;
      if (appliedCustomUnit.value === 'Days') multiplier = 86400000;
      
      return diffMs <= (val * multiplier);
    }
    
    return true;
  });
});
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex; justify-content: center; align-items: center; z-index: 1000; 
}

.modal-content {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); 

  width: 90%; max-width: 500px; max-height: 80vh;
  border-radius: 16px; display: flex; flex-direction: column; 
}

.modal-header {
  padding: 20px 24px; display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3); 
}
.modal-header h2 { margin: 0; font-size: 20px; color: #202020; }
.header-actions { display: flex; align-items: center; gap: 12px; }

.filter-select, .custom-input, .custom-select { 
  background: rgba(255, 255, 255, 0.5); 
  border: 1px solid rgba(255, 255, 255, 0.6); 
  padding: 6px 12px; border-radius: 6px; font-size: 14px; outline: none; color: #202020;
}
.filter-select { cursor: pointer; }

.close-btn { background: none; border: none; cursor: pointer; color: #666; display: flex; align-items: center; justify-content: center; }
.close-btn:hover { color: #000; }

.custom-filter-row {
  display: flex; align-items: center; justify-content: flex-end; gap: 8px;
  background-color: rgba(255, 255, 255, 0.2); 
  padding: 12px 24px; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}
.custom-label { font-size: 14px; color: #444; font-weight: 600;}
.custom-input { width: 60px; padding: 6px 8px; text-align: center; }
.custom-select { cursor: pointer; }

.apply-btn { 
  padding: 6px 16px; background-color: #FFC107; color: #202020; border: none; 
  border-radius: 6px; font-size: 14px; font-weight: 700; cursor: pointer; transition: background-color 0.2s;
}
.apply-btn:hover { background-color: #FFB300; }

.modal-body { padding: 16px 24px; overflow-y: auto; flex: 1; }
.center-state { text-align: center; color: #666; padding: 40px 0; font-weight: 500; }
.notification-list { display: flex; flex-direction: column; gap: 16px; }

.notification-card {
  background: rgba(255, 255, 255, 0.4); 
  border: 1px solid rgba(255, 255, 255, 0.5); 
  border-radius: 12px;
  padding: 16px; position: relative; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.unread-dot {
  position: absolute; top: 16px; right: 16px;
  width: 8px; height: 8px; background-color: #F44336; border-radius: 50%;
}

.card-top { display: flex; gap: 16px; }
.icon-warning { color: #FFC107; display: flex; align-items: flex-start; }
.card-info h4 { margin: 0 0 4px 0; font-size: 15px; color: #202020; }
.card-info .message { margin: 0 0 6px 0; font-size: 14px; color: #444; }
.timestamp { font-size: 12px; color: #666; font-weight: 500; }

.card-recovery { margin-top: 12px; }
.divider { height: 1px; background-color: rgba(255, 255, 255, 0.4); margin-bottom: 12px; }
.recovery-content { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.recovery-content span { font-size: 14px; color: #2E7D32; font-weight: 600; }
</style>