<template>
  <div class="system-controls">
    
    <!-- SYSTEM MODE TOGGLE -->
    <div class="control-group">
      <label class="control-label">System Mode</label>
      <div class="toggle-wrapper">
        <!-- Automatic Button -->
        <button 
          class="toggle-btn" 
          :class="{ active: !isManual }"
          @click="$emit('update:isManual', false)"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"></path><path d="M12 18v4"></path><path d="M4.93 4.93l2.83 2.83"></path><path d="M16.24 16.24l2.83 2.83"></path><path d="M2 12h4"></path><path d="M18 12h4"></path><path d="M4.93 19.07l2.83-2.83"></path><path d="M16.24 7.76l2.83-2.83"></path></svg>
          Automatic
        </button>

        <!-- Manual Button -->
        <button 
          class="toggle-btn" 
          :class="{ active: isManual }"
          @click="$emit('update:isManual', true)"
        >
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-4 0v5"></path><path d="M14 10V4a2 2 0 0 0-4 0v6"></path><path d="M10 10.5V3a2 2 0 0 0-4 0v9"></path><path d="M6 14v-2a2 2 0 0 0-4 0v7a8 8 0 0 0 8 8h2a8 8 0 0 0 8-8v-6a2 2 0 0 0-4 0v2"></path></svg>
          Manual
        </button>
      </div>
    </div>

    <!-- CHICKS' AGE DROPDOWN -->
    <div class="control-group">
      <label class="control-label">Chicks' Age</label>
      <div class="dropdown-wrapper">
        <svg class="calendar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
        
        <!-- bind the select value to the prop, and emit changes to the parent -->
        <select 
          class="week-select" 
          :value="selectedWeek" 
          @change="$emit('update:selectedWeek', parseInt($event.target.value))"
        >
          <option v-for="week in 3" :key="week" :value="week">
            Week {{ week }}
          </option>
        </select>
        
        <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </div>
    </div>

  </div>
</template>

<script setup>
// Define the inputs expect from App.vue
defineProps({
  isManual: Boolean,
  selectedWeek: Number
});

// Define the events that can send back to App.vue to update the data
defineEmits(['update:isManual', 'update:selectedWeek']);
</script>

<style scoped>
.system-controls {
  display: flex;
  gap: 64px; /* Space between the two control groups */
  padding: 16px 32px;
  background-color: #F8F9FA;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-label {
  font-size: 14px;
  font-weight: 800;
  color: #1e1e1e;
}

/* --- TOGGLE BUTTON STYLES --- */
.toggle-wrapper {
  display: flex;
  background-color: #EFEFEF;
  border-radius: 8px;
  padding: 4px;
  width: 260px;
}

.toggle-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background-color: transparent;
  color: #555555;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background-color: #4A85F6; /* The specific blue from your Flutter app */
  color: #FFFFFF;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* --- DROPDOWN STYLES --- */
.dropdown-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 200px;
}

.calendar-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: #555555;
  pointer-events: none; /* Allows clicking "through" the icon onto the select menu */
}

.chevron-icon {
  position: absolute;
  right: 12px;
  width: 16px;
  height: 16px;
  color: #555555;
  pointer-events: none;
}

.week-select {
  width: 100%;
  appearance: none; 
  background-color: #FFFFFF;
  border: 1px solid #EAEAEA;
  border-radius: 8px;
  padding: 10px 12px 10px 36px; 
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  color: #1e1e1e;
  cursor: pointer;
  outline: none;
}

.week-select:focus {
  border-color: #4A85F6;
}
</style>