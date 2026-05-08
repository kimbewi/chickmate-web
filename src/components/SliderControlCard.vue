<!-- src/components/SliderControlCard.vue -->
<template>
  <div class="slider-card">
    <div class="header-row">
      <div class="title-group">
        <div class="icon-box"><slot name="icon"></slot></div>
        <h3>{{ title }}</h3>
      </div>
      <span class="value-text">{{ value }}%</span>
    </div>
    <input 
      type="range" class="custom-slider" min="0" max="100" :value="value"
      @input="$emit('update:value', parseInt($event.target.value))"
      @change="$emit('save', parseInt($event.target.value))"
    />
  </div>
</template>

<script setup>
defineProps({ title: String, value: Number });
defineEmits(['update:value', 'save']);
</script>

<style scoped>
.slider-card {
  background-color: #FFFFFF; 
  border-radius: 8px; 
  padding: 8px 12px; 
  display: flex; 
  flex-direction: column; 
  justify-content: center; 
  gap: 4px;
  height: 50px; 
  box-sizing: border-box; 
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin: 0; 
}

.title-group { 
  display: flex; 
  lign-items: center; 
  gap: 8px; 
}

.icon-box { 
  width: 24px; 
  height: 24px; 
  padding: 0; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border-radius: 6px; 
  background-color: rgba(249, 168, 37, 0.15); 
  color: #F9A825; 
}

.icon-box svg { 
  width: 12px; 
  height: 12px; 
}

.title-group h3 { font-size: 12px; font-weight: 700; color: #1e1e1e; margin: 0; }

.value-text { font-size: 12px; font-weight: 700; color: #F9A825; margin: 0; }

.custom-slider { -webkit-appearance: none; width: 100%; height: 4px; background: #E0E0E0; border-radius: 4px; outline: none; margin: 0;}

.custom-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%; background: #F9A825; cursor: pointer; }

</style>