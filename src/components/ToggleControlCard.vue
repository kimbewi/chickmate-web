<!-- src/components/ToggleControlCard.vue -->
<template>
  <div class="control-card">
    <div class="card-header">
      <div class="icon-box" :class="isOn ? 'icon-on' : 'icon-off'">
        <slot name="icon"></slot>
      </div>
      <label class="switch">
        <input type="checkbox" :checked="isOn" @change="$emit('toggle', $event.target.checked)">
        <span class="slider round"></span>
      </label>
    </div>
    <div class="card-text">
      <h3>{{ title }}</h3>
      <span class="status-text">
        {{ isOn ? 'On' : 'Off' }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({ title: String, isOn: Boolean });
defineEmits(['toggle']);
</script>

<style scoped>
.control-card {
  position: relative;
  
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 100%);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
  
  border-radius: 8px; 
  padding: 8px 12px;
  display: flex; 
  flex-direction: row; 
  align-items: center; 
  height: 56px; 
  box-sizing: border-box; 
}

.card-header { display: contents; } 

.icon-box { 
  width: 32px; height: 32px; 
  border-radius: 8px; 
  display: flex; align-items: center; justify-content: center; 
  margin-right: 10px; 
  transition: all 0.3s ease;
}

.icon-box svg { width: 16px; height: 16px; }

.icon-off { 
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.1) 100%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #86868B; 
}

.icon-on { 
  background: linear-gradient(135deg, #FF9500 0%, #FF8A00 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #FFFFFF; 
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.3);
}

.card-text { display: flex; flex-direction: column; justify-content: center; margin-right: auto; }

.card-text h3 { font-size: 13px; font-weight: 600; color: #1C1C1E; margin: 0; }

.status-text { color: #86868B; font-size: 11px; margin: 0; font-weight: 500; }

.switch { position: absolute; right: 12px; width: 36px; height: 20px; margin: 0; }
.switch input { opacity: 0; width: 0; height: 0; }

.slider { 
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; 
  background-color: rgba(120, 120, 128, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 34px; 
  transition: .3s;
}

.slider:before { 
  position: absolute; content: ""; 
  height: 16px; width: 16px; left: 1px; bottom: 1px; 
  background-color: white; 
  box-shadow: 0 2px 6px rgba(0,0,0,0.15), 0 0 1px rgba(0,0,0,0.1);
  transition: .3s; border-radius: 50%; 
}

input:checked + .slider { background-color: #34C759; border-color: transparent; }
input:checked + .slider:before { transform: translateX(16px); }
</style>