<template>
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
          </select>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
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
    activeFilter.value = 'ALL'; // Reset filter to default
  }
});

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
  const now = new Date();
  return notifications.value.filter(n => {
    if (activeFilter.value === 'ALL') return true;
    
    const ts = new Date(n.created_at);
    if (isNaN(ts)) return true;

    const diffMs = now - ts;
    if (activeFilter.value === '10M') return diffMs <= 10 * 60000;
    if (activeFilter.value === '30M') return diffMs <= 30 * 60000;
    if (activeFilter.value === '24H') return diffMs <= 24 * 3600000;
    
    return true;
  });
});
</script>

<style scoped>
/* Overlay background */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; 
}

/* Modal Box */
.modal-content {
  background-color: #FFFFFF;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #EAEAEA;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h2 { margin: 0; font-size: 20px; color: #202020; }
.header-actions { display: flex; align-items: center; gap: 12px; }

.filter-select { padding: 6px 12px; border-radius: 6px; border: 1px solid #CCCCCC; font-size: 14px; outline: none; }
.close-btn { background: none; border: none; cursor: pointer; color: #888; display: flex; align-items: center; justify-content: center; }
.close-btn:hover { color: #202020; }

.modal-body { padding: 16px 24px; overflow-y: auto; flex: 1; }
.center-state { text-align: center; color: #888; padding: 40px 0; }
.notification-list { display: flex; flex-direction: column; gap: 16px; }

.notification-card {
  background-color: #FFFFFF;
  border: 1px solid #EAEAEA;
  border-radius: 12px;
  padding: 16px;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.unread-dot {
  position: absolute;
  top: 16px; right: 16px;
  width: 8px; height: 8px;
  background-color: #F44336;
  border-radius: 50%;
}

.card-top { display: flex; gap: 16px; }
.icon-warning { color: #FFC107; display: flex; align-items: flex-start; }
.card-info h4 { margin: 0 0 4px 0; font-size: 15px; color: #202020; }
.card-info .message { margin: 0 0 6px 0; font-size: 14px; color: #444; }
.timestamp { font-size: 12px; color: #888; }

.card-recovery { margin-top: 12px; }
.divider { height: 1px; background-color: #EAEAEA; margin-bottom: 12px; }
.recovery-content { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.recovery-content span { font-size: 14px; color: #4CAF50; font-weight: 500; }
</style>