<template>
  <div class="hardware-section">
    
    <div class="section-header">Hardware Controls</div>

    <div v-if="!isManualMode" class="lock-banner">
      <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
      <span>Controls are locked while in Automatic Mode. Switch to Manual to take over.</span>
    </div>

    <div class="control-cards" :class="{ 'locked-opacity': !isManualMode }" :style="{ pointerEvents: isManualMode ? 'auto' : 'none' }">
      
      <ToggleControlCard title="Fans" :isOn="isFansOn" @toggle="val => updateControl('fans', val)">
        <template #icon>
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.827 16.379a6.082 6.082 0 0 1-8.618-7.002l5.412 1.45a6.082 6.082 0 0 1 7.002-8.618l-1.45 5.412a6.082 6.082 0 0 1 8.618 7.002l-5.412-1.45a6.082 6.082 0 0 1-7.002 8.618l1.45-5.412Z"></path>
            <path d="M12 12v.01"></path>
          </svg>
        </template>
      </ToggleControlCard>

      <ToggleControlCard title="Heater" :isOn="isHeaterOn" @toggle="val => updateControl('heater', val)">
        <template #icon><svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg></template>
      </ToggleControlCard>

      <SliderControlCard title="Light Bulb" :value="lightBrightness" @update:value="val => lightBrightness = val" @save="val => updateControl('lightBrightness', val)">
        <template #icon><svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5M9 18h6M10 22h4"/></svg></template>
      </SliderControlCard>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getDatabase, ref as firebaseRef, onValue, set } from "firebase/database";
import ToggleControlCard from './ToggleControlCard.vue';
import SliderControlCard from './SliderControlCard.vue';

const isManualMode = ref(false);
const isFansOn = ref(false);
const isHeaterOn = ref(false);
const lightBrightness = ref(0);

onMounted(() => {
  const db = getDatabase();
  onValue(firebaseRef(db, 'controls'), (snapshot) => {
    if (snapshot.exists()) {
      const data = snapshot.val();
      isManualMode.value = data.manualOverride ?? false;
      isFansOn.value = data.fans ?? false;
      isHeaterOn.value = data.heater ?? false;
      lightBrightness.value = data.lightBrightness ?? 0;
    }
  });
});

const updateControl = (key, value) => {
  const db = getDatabase();
  set(firebaseRef(db, `controls/${key}`), value);
};
</script>

<style scoped>
.hardware-section { display: flex; flex-direction: column; width: 100%; }

.section-header { 
  font-size: 13px; 
  font-weight: 600; 
  color: #86868B; 
  text-transform: uppercase; 
  letter-spacing: 0.8px; 
  margin: 0 0 10px 0; 
}

.lock-banner { background-color: #E8F0FE; border: 1px solid #8AB4F8; color: #1967D2; border-radius: 8px; padding: 12px 16px; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 8px; font-size: 13px; font-weight: 500; line-height: 1.4; }

.control-cards { 
  display: grid; 
  grid-template-columns: 1fr 1fr 1.6fr; 
  gap: 8px; 
  transition: opacity 0.3s ease; 
  width: 100%;
}

.locked-opacity { opacity: 0.4; }
</style>