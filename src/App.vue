<script setup>
import { ref, onMounted } from 'vue';
import { ref as dbRef, onValue, set } from "firebase/database";
import { db } from './firebase.js'; 
import TopHeader from './components/TopHeader.vue';
import SystemControls from './components/SystemControls.vue';
import LeftPanel from './components/LeftPanel.vue';
import RightPanel from './components/RightPanel.vue';

// STATE VARIABLES
const isManual = ref(false);
const selectedWeek = ref(1);

// --- READ FROM FIREBASE ---
onMounted(() => {
  // Listen to controls/manualOverride
  const controlsRef = dbRef(db, 'controls');
  onValue(controlsRef, (snapshot) => {
    if (snapshot.exists()) {
      isManual.value = snapshot.val().manualOverride ?? false;
    }
  });

  // Listen to chickInfo/ageWeeks
  const chickInfoRef = dbRef(db, 'chickInfo');
  onValue(chickInfoRef, (snapshot) => {
    if (snapshot.exists()) {
      selectedWeek.value = snapshot.val().ageWeeks ?? 1;
    }
  });
});

// --- WRITE TO FIREBASE ---
const handleManualChange = (newValue) => {
  isManual.value = newValue; 
  set(dbRef(db, 'controls/manualOverride'), newValue); // Push to Database
};

const handleWeekChange = (newWeek) => {
  selectedWeek.value = newWeek;
  set(dbRef(db, 'chickInfo/ageWeeks'), newWeek);
};

</script>

<template>
  <div class="dashboard-container">
  
    <!-- HEADER -->
    <TopHeader />

    <!-- SYSTEM CONTROLS -->
    <SystemControls 
      :isManual="isManual"
      :selectedWeek="selectedWeek"
      @update:isManual="handleManualChange"
      @update:selectedWeek="handleWeekChange"
    />

    <!-- MAIN LAYOUT -->
    <main class="dashboard-grid">
      <LeftPanel />
      <RightPanel />
    </main>
    
  </div>

</template>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh; 
  overflow: hidden; 
  background-color: #F9FAFB;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
  padding: 8px 24px 16px 24px; 
  flex: 1; 
  min-height: 0; 
  box-sizing: border-box;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr; 
    overflow-y: auto; 
  }
}
</style>