<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content">
        
        <div class="modal-header">
          <h2>System History</h2>
          <button class="close-btn" @click="$emit('close')">
            <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>

        <div class="controls-container">
          <div class="controls-row">
            <div class="tabs">
              <button :class="{ active: activeTab === 'sensors' }" @click="activeTab = 'sensors'">Sensors</button>
              <button :class="{ active: activeTab === 'actuators' }" @click="activeTab = 'actuators'">Actuators</button>
            </div>

            <select v-model="activeFilter" class="filter-select">
              <option value="TODAY">Today</option>
              <option value="YESTERDAY">Yesterday</option>
              <option value="10M">Last 10 Minutes</option>
              <option value="30M">Last 30 Minutes</option>
              <option value="24H">Last 24 Hours</option>
              <option value="CUSTOM">Custom...</option> 
            </select>
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
        </div>

        <div class="modal-body">
          <div v-if="isLoading" class="center-state">
            <p>Loading data...</p>
          </div>
          
          <div v-else-if="currentData.length === 0" class="center-state">
            <p>No {{ activeTab }} data found for this time period.</p>
          </div>

          <div v-else class="history-list">
            
            <template v-if="activeTab === 'sensors'">
            <div v-for="item in currentData" :key="item._id" class="history-card">
              
              <div class="card-icon">
                <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
              </div>
                <div class="card-content">
                  <h4>Sensor Reading</h4>
                  <div class="reading-grid">
                    <span>Temp: {{ displaySensor(item.temperature, '°C') }}</span>
                    <span>Humidity: {{ displaySensor(item.humidity, '%') }}</span>
                    <span>Ammonia: {{ displaySensor(item.ammonia, 'ppm') }}</span>
                    <span>Light: {{ displaySensor(item.light, 'lux') }}</span>
                  </div>
                  <span class="timestamp">{{ formatTimestamp(item.timestamp) }}</span>
                </div>
              </div>
            </template>

            <template v-if="activeTab === 'actuators'">
              <div v-for="item in currentData" :key="item._id" class="history-card">
                <div class="card-icon" v-html="getActuatorIcon(item.actuator_id)"></div>
                <div class="card-content">
                  <h4>{{ getActuatorName(item.actuator_id) }}</h4>
                  <p class="status-text">{{ item.status ? 'Status: ' + item.status : 'Value: ' + item.value }}</p>
                  <span class="timestamp">{{ formatTimestamp(item.timestamp) }}</span>
                </div>
              </div>
            </template>

          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({ isOpen: Boolean });
const emit = defineEmits(['close']);

// --- STATE ---
const activeTab = ref('sensors'); 
const activeFilter = ref('TODAY');
const sensorsData = ref([]);
const actuatorsData = ref([]);
const isLoading = ref(false);

// Custom Filter State
const customValue = ref(1);
const customUnit = ref('Hours');

const API_BASE_URL = 'http://100.68.113.75:5000/api'; 

const currentData = computed(() => {
  return activeTab.value === 'sensors' ? sensorsData.value : actuatorsData.value;
});

// --- FETCHING LOGIC ---
const fetchHistory = async () => {
  isLoading.value = true;
  
  const now = new Date();
  let since = null;
  let until = null;

  if (activeFilter.value === '10M') {
    since = new Date(now.getTime() - 10 * 60000);
  } else if (activeFilter.value === '30M') {
    since = new Date(now.getTime() - 30 * 60000);
  } else if (activeFilter.value === '24H') {
    since = new Date(now.getTime() - 24 * 3600000);
  } else if (activeFilter.value === 'TODAY') {
    since = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  } else if (activeFilter.value === 'YESTERDAY') {
    since = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
    until = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  } else if (activeFilter.value === 'CUSTOM') {
    // NEW: Handle Custom Math
    const val = customValue.value || 1; // Fallback to 1 if user clears input
    let multiplier = 60000; // Minutes by default
    if (customUnit.value === 'Hours') multiplier = 3600000;
    if (customUnit.value === 'Days') multiplier = 86400000;
    
    since = new Date(now.getTime() - (val * multiplier));
  }

  let url = `${API_BASE_URL}/${activeTab.value}?limit=100`;
  if (since) url += `&since=${since.toISOString()}`;
  if (until) url += `&until=${until.toISOString()}`;

  try {
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      if (activeTab.value === 'sensors') sensorsData.value = data;
      else actuatorsData.value = data;
    }
  } catch (err) {
    console.error(`Failed to fetch ${activeTab.value} history:`, err);
  } finally {
    isLoading.value = false;
  }
};

const applyCustomFilter = () => {
  fetchHistory();
};

watch(() => props.isOpen, (newVal) => { if (newVal) fetchHistory(); });
watch(activeTab, () => fetchHistory());
watch(activeFilter, (newVal) => {
  if (newVal !== 'CUSTOM') {
    fetchHistory();
  } else {
    fetchHistory(); 
  }
});

// --- FORMATTING HELPERS ---
const formatTimestamp = (isoString) => {
  if (!isoString) return "No timestamp";
  try {
    const d = new Date(isoString);
    return d.toLocaleString('en-US', { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
  } catch (e) {
    return "No timestamp";
  }
};

const displaySensor = (val, unit) => {
  if (val === null || val === undefined) return '--';
  return typeof val === 'number' ? `${val} ${unit}` : val;
};

const getActuatorName = (id) => {
  switch (id) {
    case 'lightBrightness': return 'Light';
    case 'fans': return 'Exhaust/Intake Fan';
    case 'heater': return 'Heater';
    case 'manualOverride': return 'System Mode';
    default: return id || 'Unknown';
  }
};

const getActuatorIcon = (id) => {
  if (id === 'lightBrightness') return '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5M9 18h6M10 22h4"/></svg>';
  if (id === 'heater') return '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>';
  
  // FIXED: Returns the correct propeller/fan icon instead of the dollar sign!
  return '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.827 16.379a6.082 6.082 0 0 1-8.618-7.002l5.412 1.45a6.082 6.082 0 0 1 7.002-8.618l-1.45 5.412a6.082 6.082 0 0 1 8.618 7.002l-5.412-1.45a6.082 6.082 0 0 1-7.002 8.618l1.45-5.412Z"></path><path d="M12 12v.01"></path></svg>'; 
};
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

  width: 90%; max-width: 600px; height: 80vh;
  border-radius: 16px; display: flex; flex-direction: column; 
}

.modal-header {
  padding: 20px 24px; display: flex; justify-content: space-between; align-items: center;
}
.modal-header h2 { margin: 0; font-size: 20px; color: #202020; }
.close-btn { background: none; border: none; cursor: pointer; color: #666; display: flex; align-items: center; }
.close-btn:hover { color: #000; }

/* Control Area */
.controls-container {
  padding: 0 24px 16px 24px; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.3); 
  display: flex; flex-direction: column; gap: 12px;
}

.controls-row {
  display: flex; justify-content: space-between; align-items: center;
}

.tabs { display: flex; gap: 8px; background-color: rgba(255, 255, 255, 0.3); padding: 4px; border-radius: 8px; }
.tabs button {
  padding: 6px 16px; border: none; background: transparent; border-radius: 6px;
  font-size: 14px; font-weight: 600; color: #444; cursor: pointer; transition: all 0.2s;
}
.tabs button.active { background-color: rgba(255, 255, 255, 0.6); color: #202020; }

.filter-select, .custom-input, .custom-select { 
  background: rgba(255, 255, 255, 0.5); 
  border: 1px solid rgba(255, 255, 255, 0.6); 
  padding: 8px 12px; border-radius: 6px; font-size: 14px; outline: none; cursor: pointer; color: #202020;
}

/* Custom Filter Row */
.custom-filter-row {
  display: flex; align-items: center; justify-content: flex-end; gap: 8px;
  background-color: rgba(255, 255, 255, 0.2); 
  padding: 12px; border-radius: 8px; 
  border: 1px dashed rgba(255, 255, 255, 0.5);
}
.custom-label { font-size: 14px; color: #444; font-weight: 600;}
.custom-input { width: 60px; padding: 6px 8px; text-align: center; }
.apply-btn { 
  padding: 6px 16px; background-color: #FFC107; color: #202020; border: none; 
  border-radius: 6px; font-size: 14px; font-weight: 700; cursor: pointer; transition: background-color 0.2s;
}
.apply-btn:hover { background-color: #FFB300; }

/* Lists */
.modal-body { padding: 16px 24px; overflow-y: auto; flex: 1; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; }
.center-state { text-align: center; color: #666; font-weight: 500; padding: 40px 0; }
.history-list { display: flex; flex-direction: column; gap: 12px; }

.history-card {
  background: rgba(255, 255, 255, 0.4); 
  border: 1px solid rgba(255, 255, 255, 0.5); 
  border-radius: 12px;
  padding: 16px; display: flex; gap: 16px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.card-icon { 
  width: 32px; 
  height: 32px; 
  border-radius: 8px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.2) 100%);
  border: 1px solid rgba(255, 255, 255, 0.6);
  color: #FF9500;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04), inset 0 1px 2px rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}

.card-icon :deep(svg), .card-icon svg { 
  width: 16px !important; 
  height: 16px !important; 
}
.card-content { flex: 1; }
.card-content h4 { margin: 0 0 6px 0; font-size: 15px; color: #202020; }

.reading-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 8px; }
.reading-grid span { font-size: 13px; color: #222; font-weight: 500; }

.status-text { margin: 0 0 8px 0; font-size: 14px; color: #222; font-weight: 500;}
.timestamp { font-size: 12px; color: #666; font-weight: 500; }
</style>