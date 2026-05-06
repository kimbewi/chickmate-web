<template>
  <div class="status-card" :class="{ 'error-bg': isError }">
    
    <!-- MAIN CONTENT -->
    <div class="card-content" :style="{ opacity: isError ? 0.25 : 1.0 }">
      
      <!-- TOP GROUP -->
      <div class="top-group">
        <div class="header-row">
          <!-- Tinted Icon Box -->
          <div class="icon-box" :style="{ backgroundColor: iconColor + '26', color: iconColor }">
            <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none">
               <path v-if="title === 'Temperature'" d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path>
               <path v-else-if="title === 'Humidity'" d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
               <path v-else-if="title === 'Ammonia Level'" d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4m0 4h.01"></path>
               <path v-else d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>
            </svg>
          </div>
          
          <!-- Dynamic Status Pill -->
          <div v-if="isNumeric" class="status-pill" :class="currentStatus.isWarning ? 'pill-warning' : 'pill-normal'">
            {{ currentStatus.label }}
          </div>
        </div>

        <h3 class="card-title">{{ title }}</h3>
        
        <div class="data-value">
          {{ isError ? '--' : displayData }}
        </div>
        
        <p v-if="isNumeric" class="target-subtitle">{{ sensorConfig.subtitle }}</p>
      </div>

      <!-- BOTTOM GROUP: AI Recommendation -->
      <div v-if="isNumeric" class="rec-box" :class="currentStatus.isWarning ? 'rec-warning' : 'rec-normal'">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" fill="none" stroke-width="2" class="rec-icon">
          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
        </svg>
        <div class="rec-text-group">
          <span class="rec-title">AI RECOMMENDED ACTION</span>
          <span class="rec-text">{{ currentStatus.recommendation }}</span>
        </div>
      </div>
    </div>

    <!-- ERROR OVERLAY -->
    <div v-if="isError" class="error-overlay">
      <svg class="error-icon" viewBox="0 0 24 24" width="28" height="28" stroke="#D32F2F" fill="none" stroke-width="2">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
      </svg>
      <div class="error-text">
        <h4>ERROR</h4>
        <p>Please check your internet connection and ensure the sensor wiring is secure.</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: String,
  data: [String, Number],
  unit: String,
  iconColor: String,
  selectedWeek: { type: Number, default: 1 }
});

// --- Validation Logic ---
const parsedValue = computed(() => parseFloat(props.data));
const isNumeric = computed(() => props.data !== '--' && !isNaN(parsedValue.value));
const isError = computed(() => !isNumeric.value && props.data !== '--');

// --- Unit Formatting ---
const displayData = computed(() => {
  if (!isNumeric.value) return props.data;
  return (props.unit === '°C' || props.unit === '%') 
    ? `${props.data}${props.unit}` 
    : `${props.data} ${props.unit}`;
});

// --- Dynamic Targets & AI Text Mapping ---
const sensorConfig = computed(() => {
  let targetMin = 0; let targetMax = 0;
  let highLabel = 'TOO HIGH'; let lowLabel = 'TOO LOW';
  let highRec = 'Adjust settings to lower the value.';
  let lowRec = 'Adjust settings to increase the value.';
  let normalRec = 'Maintain current controls settings.';
  let subtitle = '';

  switch (props.title) {
    case 'Temperature':
      highLabel = 'TOO HOT'; lowLabel = 'TOO COLD';
      highRec = 'Turn ON the fans and OFF the heater.'; lowRec = 'Turn ON the heater and OFF the fans.';
      targetMin = 32.0 - (2 * (props.selectedWeek - 1));
      targetMax = 34.0 - (2 * (props.selectedWeek - 1));
      subtitle = `Target for Week ${props.selectedWeek}: ${targetMin}-${targetMax}${props.unit}`;
      break;
      
    case 'Ammonia Level':
      highLabel = 'TOO HIGH'; highRec = 'Turn ON the fans immediately.';
      targetMin = 0.0; targetMax = 6.0;
      subtitle = `Safe Threshold: 0-${targetMax} ${props.unit}`;
      break;

    case 'Humidity':
      highLabel = 'TOO HUMID'; lowLabel = 'TOO DRY';
      highRec = 'Increase ventilation to lower humidity.'; lowRec = 'Reduce ventilation slightly to retain moisture.';
      targetMin = 50.0; targetMax = 70.0;
      subtitle = `Recommended Range: ${targetMin}-${targetMax}${props.unit}`;
      break;

    case 'Light Level':
      const currentHour = new Date().getHours();
      let isRestPeriod = false;
      if (props.selectedWeek === 1 && currentHour === 0) isRestPeriod = true;
      else if (props.selectedWeek >= 2 && currentHour >= 0 && currentHour < 8) isRestPeriod = true;

      if (isRestPeriod) {
        highLabel = 'TOO BRIGHT'; lowLabel = 'NORMAL';
        highRec = 'Ensure the brooder is dark for their resting period.'; lowRec = 'Normal resting light level.';
        targetMin = 0.0; targetMax = 20.0;
        subtitle = `Target for Rest Period: 0-${targetMax} ${props.unit}`;
      } else {
        highLabel = 'TOO BRIGHT'; lowLabel = 'TOO DIM';
        highRec = 'Dim the lights.'; lowRec = 'Check if the light bulb is broken or obscured.';
        targetMin = 30.0; targetMax = 300.0;
        subtitle = `Target for Active Period: ${targetMin}-${targetMax} ${props.unit}`;
      }
      break;
  }
  return { targetMin, targetMax, highLabel, lowLabel, highRec, lowRec, normalRec, subtitle };
});

// --- Evaluator ---
const currentStatus = computed(() => {
  if (!isNumeric.value) return { label: 'NORMAL', recommendation: sensorConfig.value.normalRec, isWarning: false };
  
  const val = parsedValue.value;
  const cfg = sensorConfig.value;

  if (val > cfg.targetMax) return { label: cfg.highLabel, recommendation: cfg.highRec, isWarning: true };
  if (val < cfg.targetMin) return { label: cfg.lowLabel, recommendation: cfg.lowRec, isWarning: true };
  
  return { label: 'NORMAL', recommendation: cfg.normalRec, isWarning: false };
});
</script>

<style scoped>
.status-card {
  background-color: #FFFFFF;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.error-bg {
  background-color: #F2F2F2;
}

.card-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.icon-box {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-pill {
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 900;
}

.pill-normal { background-color: #E8F5E9; color: #2E7D32; }
.pill-warning { background-color: #FFEBEE; color: #D32F2F; }

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #1e1e1e;
  margin: 0 0 4px 0;
}

.data-value {
  font-size: 36px;
  font-weight: 800;
  color: #1e1e1e;
  line-height: 1;
  margin-bottom: 6px;
}

.target-subtitle {
  font-size: 10px;
  font-weight: 500;
  color: #888888;
  margin: 0;
}

.rec-box {
  margin-top: 16px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.rec-normal { background-color: #E8F5E9; border-color: #66BB6A; color: #2E7D32; }
.rec-warning { background-color: #FFEBEE; border-color: #EF5350; color: #D32F2F; }

.rec-text-group {
  display: flex;
  flex-direction: column;
}

.rec-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 3px;
}

.rec-text {
  font-size: 12px;
  font-weight: 500;
  line-height: 1.3;
}

/* --- Error Overlay --- */
.error-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.error-icon {
  position: absolute;
  top: 16px;
  right: 16px;
}

.error-text h4 {
  font-size: 24px;
  font-weight: 900;
  color: #D32F2F;
  margin: 0 0 4px 0;
}

.error-text p {
  font-size: 10px;
  font-weight: 500;
  color: #4a4a4a;
  margin: 0;
}
</style>