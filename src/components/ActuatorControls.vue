<!-- src/components/ActuatorControls.vue -->
<template>
  <div class="hardware-section">
    <div class="section-header">
      <h2>Hardware Controls</h2>
    </div>

    <!-- Auto Mode Lock Banner -->
    <div v-if="!isManualMode" class="lock-banner">
      <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
      <span>Controls are locked while in Automatic Mode. Switch to Manual to take over.</span>
    </div>

    <!-- The Control Cards -->
    <div class="control-cards" :class="{ 'locked-opacity': !isManualMode }" :style="{ pointerEvents: isManualMode ? 'auto' : 'none' }">
      <div class="toggle-row">
        <ToggleControlCard title="Fans" :isOn="isFansOn" @toggle="val => updateControl('fans', val)">
          <template #icon><svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></template>
        </ToggleControlCard>

        <ToggleControlCard title="Heater" :isOn="isHeaterOn" @toggle="val => updateControl('heater', val)">
          <template #icon><svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg></template>
        </ToggleControlCard>
      </div>

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
.section-header h2 { font-size: 14px; font-weight: 700; color: #888888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
.lock-banner { background-color: #E8F0FE; border: 1px solid #8AB4F8; color: #1967D2; border-radius: 8px; padding: 12px 16px; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; font-size: 13px; font-weight: 500; line-height: 1.4; }
.control-cards { display: flex; flex-direction: column; gap: 16px; transition: opacity 0.3s ease; }
.locked-opacity { opacity: 0.4; }
.toggle-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
</style>