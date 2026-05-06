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
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.title-group { display: flex; align-items: center; gap: 12px; }
.icon-box { padding: 8px; border-radius: 8px; background-color: rgba(249, 168, 37, 0.15); color: #F9A825; display: flex; align-items: center; justify-content: center; }
.title-group h3 { font-size: 16px; font-weight: 700; color: #1e1e1e; margin: 0; }
.value-text { font-size: 16px; font-weight: 700; color: #F9A825; }
.custom-slider { -webkit-appearance: none; width: 100%; height: 6px; background: #E0E0E0; border-radius: 4px; outline: none; }
.custom-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #F9A825; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
</style>