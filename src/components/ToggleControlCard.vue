<!-- src/components/ToggleControlCard.vue -->
<template>
  <div class="control-card" :class="{ 'is-on': isOn }">
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
      <h3 :class="{ 'text-white': isOn }">{{ title }}</h3>
      <span :class="isOn ? 'status-text-on' : 'status-text-off'">
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
  background-color: #FFFFFF; border-radius: 8px; padding: 8px 12px;
  display: flex; flex-direction: row; align-items: center; 
  height: 50px; 
  box-sizing: border-box; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.control-card.is-on { background-color: #F9A825; }

.card-header { display: contents; } 
.icon-box { width: 28px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center; border-radius: 6px; margin-right: 8px; }

.icon-box svg { width: 14px; height: 14px; }

.icon-off { background-color: rgba(249, 168, 37, 0.15); color: #F9A825; }

.icon-on { background-color: rgba(255, 255, 255, 0.2); color: #FFFFFF; }

.card-text { display: flex; flex-direction: column; justify-content: center; margin-right: auto; }

.card-text h3 { font-size: 12px; font-weight: 700; color: #1e1e1e; margin: 0; }

.card-text h3.text-white { color: #FFFFFF; }

.status-text-off { color: #888888; font-size: 10px; margin: 0; }

.status-text-on { color: rgba(255, 255, 255, 0.7); font-size: 10px; margin: 0; }

.switch { position: absolute; right: 12px; width: 32px; height: 18px; margin: 0; }

.switch input { opacity: 0; width: 0; height: 0; }

.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; border-radius: 34px; }

.slider:before { position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px; background-color: white; transition: .2s; border-radius: 50%; }

input:checked + .slider { background-color: rgba(255, 255, 255, 0.5); }

input:checked + .slider:before { transform: translateX(14px); }

</style>