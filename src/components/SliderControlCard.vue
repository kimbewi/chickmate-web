<template>
  <div class="slider-card">
    
    <div class="icon-box">
      <slot name="icon"></slot>
    </div>

    <div class="content-col">
      <div class="header-row">
        <h3>{{ title }}</h3>
        <span class="value-text">{{ value }}%</span>
      </div>
      <input 
        type="range" class="custom-slider" min="0" max="100" :value="value"
        @input="$emit('update:value', parseInt($event.target.value))"
        @change="$emit('save', parseInt($event.target.value))"
      />
    </div>

  </div>
</template>

<script setup>
defineProps({ title: String, value: Number });
defineEmits(['update:value', 'save']);
</script>

<style scoped>
.slider-card {
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

.icon-box { 
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
  margin-right: 10px; 
  flex-shrink: 0;
}

.icon-box svg { width: 16px; height: 16px; }

.content-col {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  justify-content: center;
  gap: 6px; 
  min-width: 0; 
}

.header-row { 
  display: flex; justify-content: space-between; align-items: center; margin: 0; 
}

.header-row h3 { font-size: 13px; font-weight: 600; color: #1C1C1E; margin: 0; }

.value-text { font-size: 13px; font-weight: 700; color: #FF9500; margin: 0; }

.custom-slider { 
  -webkit-appearance: none; width: 100%; height: 6px; 
  background: rgba(120, 120, 128, 0.16); 
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px; outline: none; margin: 0;
}

.custom-slider::-webkit-slider-thumb { 
  -webkit-appearance: none; 
  width: 20px; height: 20px; 
  border-radius: 50%; 
  background: #FFFFFF; 
  box-shadow: 0 2px 6px rgba(0,0,0,0.15), 0 0 1px rgba(0,0,0,0.1); 
  cursor: pointer; 
}
</style>