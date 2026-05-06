<template>
  <header class="top-nav">
    <div class="logo-area">
      <!-- Note the ../ to go up a folder -->
      <img src="../assets/appLogo.png" alt="Logo" class="logo-img" />
      <h1 class="brand-name">ChickMate</h1>
    </div>
    
    <div class="header-icons">
      <!-- Wi-Fi Icon -->
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>

      <!-- History Icon -->
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>

      <!-- Notification Bell Icon -->
      <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
    </div>
  </header>
</template>

<style scoped>
.top-nav {
  background-color: #FFFFFF;
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #EAEAEA;
  width: 100%; 
  box-sizing: border-box;
}

.logo-area { display: flex; align-items: center; gap: 12px; }
.logo-img { height: 44px; border-radius: 8px; }
.brand-name { margin: 0; font-size: 28px; font-weight: 900; color: #202020; letter-spacing: -0.5px; }

.header-icons { display: flex; align-items: center; gap: 24px; }
.nav-icon {
  width: 26px;
  height: 26px;
  color: #333333;
  cursor: pointer;
  transition: color 0.2s;
}
.nav-icon:hover { color: #000000; }
</style>