import firebase_admin
from firebase_admin import db, credentials
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import time
import csv
import gspread
import os
from concurrent.futures import ThreadPoolExecutor
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# BLOCK 1: CLOUD & DATABASE AUTHORIZATION
# ==========================================
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Fetch from .env instead of hardcoding
fb_key_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
fb_db_url = os.getenv("FIREBASE_DATABASE_URL")

fb_cred = credentials.Certificate(fb_key_path)
firebase_admin.initialize_app(fb_cred, {
    'databaseURL': fb_db_url
})

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
gs_key_path = os.path.join(BASE_DIR, "google_sheets_key.json")
gs_cred = ServiceAccountCredentials.from_json_keyfile_name(gs_key_path, scope)
gs_client = gspread.authorize(gs_cred)
sheet = gs_client.open("ChickMate_Data_Log").sheet1


# ==========================================
# BLOCK 1B: FIREBASE RESILIENT WRITE HELPER
# ==========================================

_firebase_consecutive_failures = 0

def firebase_write(ref_path, data, max_retries=5):
    """
    Write to Firebase with exponential backoff.
    On repeated failures, attempts to reinitialize the Firebase connection.
    """
    global _firebase_consecutive_failures

    for attempt in range(max_retries):
        try:
            db.reference(ref_path).update(data)
            if attempt > 0:
                print(f"  [FAILSAFE-FB] '{ref_path}' RECOVERED after {attempt + 1} attempt(s).")
            _firebase_consecutive_failures = 0
            return True
        except Exception as e:
            wait = min(2 ** attempt, 60)
            _firebase_consecutive_failures += 1
            print(f"  [FAILSAFE-FB] Write to '{ref_path}' FAILED "
                  f"(attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait}s...")
            time.sleep(wait)

            if _firebase_consecutive_failures >= 3:
                print(f"  [FAILSAFE-FB] {_firebase_consecutive_failures} consecutive failures -- probing connection...")
                try:
                    db.reference('/').get()
                    print("  [FAILSAFE-FB] Probe succeeded -- connection may be restored.")
                except Exception as re_e:
                    print(f"  [FAILSAFE-FB] Probe FAILED: {re_e}")

    print(f"  [FAILSAFE-FB] '{ref_path}' PERMANENTLY FAILED after {max_retries} attempts.")
    return False

# ==========================================
# BLOCK 2: SENSOR SMOOTHING & DATA SYNC
# ==========================================
temp_history    = []
ammonia_history = []

_gs_executor = ThreadPoolExecutor(max_workers=2)

def get_smoothed_value(new_val, history_list, window_size=5):
    """
    FIX: Only inject into history if the value is genuinely valid.
    When new_val is None, return the current average WITHOUT appending
    anything -- this prevents stale/fake values from poisoning the window.
    """
    if new_val is None:
        # Do NOT append -- just return current average without corrupting history
        return sum(history_list) / len(history_list) if history_list else 32.0
    history_list.append(new_val)
    if len(history_list) > window_size:
        history_list.pop(0)
    return sum(history_list) / len(history_list)

def sync_to_cloud(row_data):
    _gs_executor.submit(lambda: sheet.append_row(row_data) if sheet else None)

# ==========================================
# BLOCK 3: THE FUZZY LOGIC ENGINE
# ==========================================

def setup_fuzzy_system(week):
    ideal_low  = 32 - (2 * (week - 1))
    ideal_high = 34 - (2 * (week - 1))

    temperature = ctrl.Antecedent(np.arange(15, 46, 1), 'temperature')
    ammonia     = ctrl.Antecedent(np.arange(0, 101, 1), 'ammonia')
    heater      = ctrl.Consequent(np.arange(0, 1.1, 0.1),   'heater')
    fans        = ctrl.Consequent(np.arange(0, 1.1, 0.1),   'fans')

    temperature['cold']  = fuzz.trimf(temperature.universe, [15, 15, ideal_low])
    temperature['ideal'] = fuzz.trimf(temperature.universe, [ideal_low, (ideal_low + ideal_high) / 2, ideal_high])
    temperature['hot']   = fuzz.trimf(temperature.universe, [ideal_high, 45, 45])

    ammonia['safe']   = fuzz.trapmf(ammonia.universe, [0,  0,  4,   6])
    ammonia['stress'] = fuzz.trapmf(ammonia.universe, [6,  7,  9,   10])
    ammonia['high']   = fuzz.trapmf(ammonia.universe, [10, 11, 100, 100])

    heater['off'] = fuzz.trimf(heater.universe, [0, 0, 1])
    heater['on']  = fuzz.trimf(heater.universe, [0, 1, 1])
    fans['off']   = fuzz.trimf(fans.universe,   [0, 0, 1])
    fans['on']    = fuzz.trimf(fans.universe,   [0, 1, 1])

    rules = [
        ctrl.Rule(temperature['cold'],                    heater['on']),
        ctrl.Rule(temperature['hot'],                     fans['on']),
        ctrl.Rule(ammonia['high'] | ammonia['stress'],    fans['on']),
        ctrl.Rule(temperature['ideal'] & ammonia['safe'], (heater['off'], fans['off'])),
    ]
    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

fuzzy_sim       = setup_fuzzy_system(1)
last_week_setup = 1

def compute_fuzzy_logic(temp_val, ammonia_val, week):
    global fuzzy_sim, last_week_setup
    if week != last_week_setup:
        fuzzy_sim       = setup_fuzzy_system(week)
        last_week_setup = week

    fuzzy_sim.input['temperature'] = temp_val
    fuzzy_sim.input['ammonia']     = ammonia_val

    try:
        fuzzy_sim.compute()
        out_h = fuzzy_sim.output.get('heater', 0)
        out_f = fuzzy_sim.output.get('fans',   0)
    except Exception as e:
        print(f"Fuzzy compute error: {e}")
        out_h, out_f = 0, 0
    return bool(out_h > 0.5), bool(out_f > 0.5)

# ==========================================
# BLOCK 4: PHOTOPERIOD HELPER
# ==========================================
def get_ambient_adjustment(current_hour):
    """
    Daytime (05:00-19:00): natural sunlight is present -> reduce brightness by 20.
    Nighttime (19:00-05:00): no sunlight -> boost brightness by 10.
    """
    is_daytime = 5 <= current_hour < 19
    return -10 if is_daytime else +10

def get_target_brightness(week, current_hour):
    adjustment = get_ambient_adjustment(current_hour)

    if week == 1:
        if current_hour == 0:
            return 20  # fixed rest, no adjustment
        base = 60
    elif 2 <= week <= 5:
        if 0 <= current_hour < 8:
            return 20  # fixed rest
        base = 30
    else:
        if 0 <= current_hour < 8:
            return 20  # fixed rest
        base = 25
    return max(5, min(100, base + adjustment))

def get_light_status(week, current_hour):
    """Return the human-readable light status string."""
    if week == 1:
        return "REST (1-Hour Dark Period)" if current_hour == 0 else "ACTIVE (23h Brooding Window)"
    elif 2 <= week <= 5:
        return "REST (8-Hour Dark Period)" if 0 <= current_hour < 8 else "ACTIVE (5-10 lux Conditioning)"
    else:
        return "REST (8-Hour Dark Period)" if 0 <= current_hour < 8 else "ACTIVE (Finishing Phase)"

# ==========================================
# BLOCK 5: AI OBSERVE MODE FLAG
# Set to True  -> AI (CV + bioacoustic) only logs and reports.
#                 It has zero effect on heater, fans, or light.
#                 Fuzzy logic + ammonia emergency run the system.
# Set to False -> AI veto is active (V7.3 full behaviour).
# ==========================================
AI_OBSERVE_ONLY = False

def start_brain():
    csv_file = os.path.join(BASE_DIR, 'brooder_logs.csv')
    last_gs_update                   = 0
    last_t, last_a                   = 32.0, 0.0
    current_h_state, current_f_state = False, False
    last_h_change, last_f_change     = 0, 0
    MIN_RUN_TIME                     = 120
    AMMONIA_EMERGENCY_LEVEL          = 5.0
    interpretation_msg               = ""
    last_pushed_h, last_pushed_f, last_pushed_lb = None, None, None

    _init_hour        = datetime.now().hour
    target_brightness = get_target_brightness(1, _init_hour)
    light_status      = get_light_status(1, _init_hour)
    last_good_brightness = target_brightness

    # ------------------------------------------------------------------
    # SENSOR LOCK DETECTION
    # Tracks whether Firebase is returning genuinely new values each
    # cycle vs. the same frozen number caused by ESP32/WiFi dropout.
    # ------------------------------------------------------------------
    last_recorded_raw_temp  = None
    last_recorded_raw_amm   = None
    last_sensor_update_time = time.time()
    sensor_stale_cycles     = 0
    STALE_CYCLE_LIMIT       = 6   # 6 cycles x 10s = 60s before LOCK warning

    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as f:
            csv.writer(f).writerow(["Timestamp", "Mode", "Week", "Temp_C",
                                    "Ammonia", "CV", "Bio", "Heater", "Fans"])

    mode_banner = "OBSERVE-ONLY (AI logging, not controlling)" if AI_OBSERVE_ONLY else "FULL AI ACTIVE"
    print(f"ChickMate Brain [V7.5] Online -- {mode_banner}")

    while True:
        try:
            # -------------------------------------------------------
            # 6A. FETCH DATA
            # Single root fetch replaces four sequential HTTP calls.
            # -------------------------------------------------------
            snapshot   = db.reference('/').get() or {}
            controls_s = snapshot.get('controls',  {}) or {}
            chick_info = snapshot.get('chickInfo',  {}) or {}
            data       = snapshot.get('sensorData', {}) or {}
            ai_data    = snapshot.get('aiResult',   {}) or {}

            is_manual = controls_s.get('manualOverride', False)
            week      = chick_info.get('ageWeeks', 1) or 1

            cv_status  = str(ai_data.get('cv',          'normal')).lower()
            bio_status = str(ai_data.get('bioacoustic', 'normal')).lower()

            # -------------------------------------------------------
            # 6A-FIX: SAFE SENSOR READ + STALENESS DETECTION
            #
            # Root causes of sensor lock (all fixed here):
            #
            #   CAUSE 1 -- Fallback feeds itself:
            #     Old: raw_temp = data.get('temperature', last_t)
            #     If Firebase returned None, last_t was injected into
            #     the smoothing history. last_t then became the smoothed
            #     average of injected fakes. Next cycle repeated it.
            #     Fix: Accept None as None. Never fall back to last_t.
            #
            #   CAUSE 2 -- Smoothing window trapped stale data:
            #     Old: get_smoothed_value always appended, even on None.
            #     Once all 5 slots filled with last_t clones, a real
            #     reading took 5 full cycles (50s) to flush them out.
            #     Fix: get_smoothed_value skips the append when val=None.
            #
            #   CAUSE 3 -- last_t / last_a drifted from smoothed fakes:
            #     Old: last_t = t  (t was already the corrupted average)
            #     Fix: last_t only updates when raw_temp is a real value.
            #
            #   CAUSE 4 -- No staleness detection:
            #     Firebase stores the last written value permanently.
            #     If the ESP32 stops sending (crash/WiFi drop), Firebase
            #     returns the same old number forever with no indication.
            #     Fix: Stale cycle counter + timed LOCK warning.
            # -------------------------------------------------------
            raw_temp = data.get('temperature')
            raw_amm  = data.get('ammonia')

            # Reject anything that is not a real number
            if not isinstance(raw_temp, (int, float)):
                raw_temp = None
            if not isinstance(raw_amm, (int, float)):
                raw_amm = None

            print(f"DEBUG RAW >> Temp: {raw_temp} | NH3: {raw_amm}")

            # Staleness check: have the values actually changed?
            values_changed = (raw_temp != last_recorded_raw_temp or
                              raw_amm  != last_recorded_raw_amm)

            if raw_temp is not None and raw_amm is not None and values_changed:
                # Genuine fresh data
                sensor_stale_cycles     = 0
                last_sensor_update_time = time.time()
                last_recorded_raw_temp  = raw_temp
                last_recorded_raw_amm   = raw_amm
                print(f"  [SENSOR] OK -- Fresh data received. "
                      f"Temp: {raw_temp}C | NH3: {raw_amm} ppm")
            else:
                sensor_stale_cycles += 1
                stale_secs = time.time() - last_sensor_update_time

                if raw_temp is None or raw_amm is None:
                    # Firebase returned no value at all
                    print(f"  [SENSOR] WARNING -- Sensor returned None "
                          f"(stale cycle {sensor_stale_cycles}). "
                          f"Holding last known: Temp={last_t}C | NH3={last_a} ppm")
                elif not values_changed:
                    # Value present but unchanged -- could be valid or frozen
                    if sensor_stale_cycles >= STALE_CYCLE_LIMIT:
                        print(f"  [SENSOR] LOCK DETECTED -- No new data for "
                              f"{stale_secs:.0f}s ({sensor_stale_cycles} cycles). "
                              f"Value frozen at Temp={raw_temp}C | NH3={raw_amm} ppm. "
                              f"Check ESP32 and WiFi connection.")
                    else:
                        print(f"  [SENSOR] Unchanged "
                              f"({sensor_stale_cycles}/{STALE_CYCLE_LIMIT} cycles) -- "
                              f"Temp={raw_temp}C | NH3={raw_amm} ppm (may still be valid)")

            # Smooth only with valid data -- None safely skips append
            t = get_smoothed_value(raw_temp, temp_history)
            a = get_smoothed_value(raw_amm,  ammonia_history)

            # Only advance last_t / last_a on confirmed real readings
            if raw_temp is not None:
                last_t = raw_temp
            if raw_amm is not None:
                last_a = raw_amm

            raw_light = data.get('lightLevel', 0)

            # -------------------------------------------------------
            # 6B. BACKGROUND INTELLIGENCE
            # -------------------------------------------------------
            now_time          = datetime.now()
            current_hour      = now_time.hour
            is_ammonia_danger = a >= AMMONIA_EMERGENCY_LEVEL

            bg_h, bg_f = compute_fuzzy_logic(t, a, week)
            target_h, target_f = bg_h, bg_f

            ai_conflict = (
                (cv_status == "cold" and bio_status == "hot") or
                (cv_status == "hot"  and bio_status == "cold")
            )

            # --- FAILSAFE STATUS PRINT ---
            print(f"\n{'─'*60}")
            print(f"  [FAILSAFE-CHECK] Ammonia Emergency : "
                  f"{'TRIGGERED (' + str(round(a,1)) + ' ppm >= ' + str(AMMONIA_EMERGENCY_LEVEL) + ')' if is_ammonia_danger else 'Normal (' + str(round(a,1)) + ' ppm)'}")
            print(f"  [FAILSAFE-CHECK] AI Signal Conflict: "
                  f"{'CONFLICT -- CV=' + cv_status.upper() + ' vs Bio=' + bio_status.upper() + ' (Falling back to Fuzzy)' if ai_conflict else 'Normal -- CV=' + cv_status.upper() + ', Bio=' + bio_status.upper()}")

            if AI_OBSERVE_ONLY:
                ai_would_h, ai_would_f = target_h, target_f
                if not ai_conflict:
                    if   cv_status == "cold" or bio_status == "cold": ai_would_h, ai_would_f = True,  False
                    elif cv_status == "hot"  or bio_status == "hot":  ai_would_f, ai_would_h = True,  False

                ai_would_override = (ai_would_h != target_h or ai_would_f != target_f)
                ai_obs_note = (
                    f"AI-OBS: CV={cv_status.upper()}, Bio={bio_status.upper()} | "
                    f"Would override: {'YES -- H=' + str(ai_would_h) + ' F=' + str(ai_would_f) if ai_would_override else 'NO'}"
                )
            else:
                if not ai_conflict:
                    if   cv_status == "cold" or bio_status == "cold": target_h, target_f = True,  False
                    elif cv_status == "hot"  or bio_status == "hot":  target_f, target_h = True,  False
                ai_obs_note = ""

            # -------------------------------------------------------
            # 6C. MODE HANDLING
            # -------------------------------------------------------
            if is_manual:
                mode_str          = "MANUAL"
                light_status      = "USER CONTROLLED"
                current_h_state   = controls_s.get('heater',          False)
                current_f_state   = controls_s.get('fans',            False)
                target_brightness = controls_s.get('lightBrightness', 50)

                if is_ammonia_danger:
                    interpretation_msg = "CRITICAL: High Ammonia! Please turn ON Fans immediately."
                elif (cv_status == "cold" or bio_status == "cold") and not target_h:
                    interpretation_msg = "Sensor temp is ideal, but chicks are HUDDLING. Consider checking for drafts."
                elif (cv_status == "hot" or bio_status == "hot") and not target_f:
                    interpretation_msg = "Sensor temp is ideal, but chicks show HEAT STRESS. Increase ventilation."
                elif current_h_state and (cv_status == "cold" or bio_status == "cold"):
                    interpretation_msg = "Both sensors and chick behavior show they are COLD. Turn on Heater."
                elif current_f_state and (cv_status == "hot"  or bio_status == "hot"):
                    interpretation_msg = "Both sensors and chick behavior show they are HOT. Turn on Fans."
                else:
                    interpretation_msg = f"System Stable. H:{'ON' if target_h else 'OFF'}, F:{'ON' if target_f else 'OFF'}."

            else:
                mode_str = "AUTO"

                # --- IMMUTABLE SAFETY OVERRIDES ---
                if is_ammonia_danger:
                    target_f, target_h = True, False
                    
                if t > 40.0:
                    target_h = False # Force heater off regardless of AI/Fuzzy outputs
                    print(f"  [FAILSAFE-CRITICAL] Temp {t:.1f}C exceeds safe limits! Forcing Heater OFF.")

                # Hysteresis filter
                now_sec = time.time()
                if target_h != current_h_state:
                    h_wait_left = max(0, MIN_RUN_TIME - (now_sec - last_h_change))
                    if (now_sec - last_h_change) > MIN_RUN_TIME:
                        print(f"  [FAILSAFE-HYST] Heater change ALLOWED -> {'ON' if target_h else 'OFF'}")
                        current_h_state, last_h_change = target_h, now_sec
                    else:
                        print(f"  [FAILSAFE-HYST] Heater change BLOCKED (cooldown: {h_wait_left:.0f}s left)")

                if target_f != current_f_state:
                    f_wait_left = max(0, MIN_RUN_TIME - (now_sec - last_f_change))
                    if (now_sec - last_f_change) > MIN_RUN_TIME or (is_ammonia_danger and target_f):
                        reason = "EMERGENCY OVERRIDE" if (is_ammonia_danger and target_f) else "cooldown elapsed"
                        print(f"  [FAILSAFE-HYST] Fans change ALLOWED -> {'ON' if target_f else 'OFF'} ({reason})")
                        current_f_state, last_f_change = target_f, now_sec
                    else:
                        print(f"  [FAILSAFE-HYST] Fans change BLOCKED (cooldown: {f_wait_left:.0f}s left)")

                target_brightness = get_target_brightness(week, current_hour)
                light_status      = get_light_status(week, current_hour)

                if   is_ammonia_danger:                            interpretation_msg = f"EXECUTING: EMERGENCY AMMONIA PURGE ({a:.1f} ppm)"
                elif ai_conflict:                                  interpretation_msg = "EXECUTING: Sensor Baseline (AI Conflict)"
                elif cv_status == "cold" or bio_status == "cold": interpretation_msg = "EXECUTING: AI Veto (Cold Distress)"
                elif cv_status == "hot"  or bio_status == "hot":  interpretation_msg = "EXECUTING: AI Veto (Heat Distress)"
                else:                                              interpretation_msg = "EXECUTING: Standard Fuzzy Control"

            # Check for hardware failure ONLY during Active periods
            if "ACTIVE" in light_status and target_brightness >= 25 and raw_light < 30:
                interpretation_msg = "HARDWARE ALERT: Light bulb might be broken, obscured, or reporting low lux!"
                print(f"  [FAILSAFE-HW]  LIGHT ALERT -- Target: {target_brightness}% but sensor reads only {raw_light} lux!")
                last_pushed_lb = None
            else:
                print(f"  [FAILSAFE-HW]  Light Normal -- Target: {target_brightness}% | Sensor: {raw_light} lux")

            last_good_brightness = target_brightness

# -------------------------------------------------------
            # 6D. FIREBASE WRITE -- only when values changed
            # -------------------------------------------------------
            if not is_manual:
                if (current_h_state   != last_pushed_h or
                    current_f_state   != last_pushed_f or
                    target_brightness != last_pushed_lb):

                    success = firebase_write('controls', {
                        'heater':          current_h_state,
                        'fans':            current_f_state,
                        'lightBrightness': target_brightness,
                    })
                    if success:
                        last_pushed_h  = current_h_state
                        last_pushed_f  = current_f_state
                        last_pushed_lb = target_brightness
            else:
                # Optional: If manual is active, we reset last_pushed to ensure 
                # that as soon as the user turns manual OFF, the script 
                # immediately regains control.
                last_pushed_h  = None
                last_pushed_f  = None
                last_pushed_lb = None

            firebase_write('aiResult', {
                'modeStatus':     "Manual Override" if is_manual else "AI Autonomous",
                'interpretation': interpretation_msg,
                'conflictActive': ai_conflict,
            })
            firebase_write('currentSettings', {
                'modeStatus':  mode_str,
                'lightStatus': light_status,
                'isEmergency': is_ammonia_danger,
            })

            # -------------------------------------------------------
            # 6E. LOGGING
            # -------------------------------------------------------
            timestamp = now_time.strftime("%Y-%m-%d %H:%M:%S")
            print("\n" + "=" * 60)
            print(f"DATETIME  >> {now_time.strftime('%A, %B %d, %Y  %I:%M:%S %p')}")
            print(f"[{timestamp}] MODE: {mode_str} | WEEK: {week} | {interpretation_msg}")
            if AI_OBSERVE_ONLY and ai_obs_note:
                print(f"AI-OBS    >> {ai_obs_note}")
            print(f"SENSORS   >> Temp: {t:.2f}C | NH3: {a:.1f}ppm | Light: {raw_light}")
            print(f"ACTUATORS >> Heater: {'[ON]' if current_h_state else '[OFF]'} | Fans: {'[ON]' if current_f_state else '[OFF]'}")
            print(f"LIGHTING  >> {light_status} | Target: {target_brightness}%")
            print("=" * 60)

            row = [timestamp, mode_str, week, round(t, 2), round(a, 2),
                   cv_status, bio_status, current_h_state, current_f_state]
            with open(csv_file, mode='a', newline='') as f:
                csv.writer(f).writerow(row)
            if time.time() - last_gs_update > 60:
                sync_to_cloud(row)
                last_gs_update = time.time()
            time.sleep(10)

        except Exception as e:
            print(f"Error: {e}")
            firebase_write('controls', {'lightBrightness': last_good_brightness}, max_retries=2)
            time.sleep(5)

if __name__ == "__main__":
    start_brain()