import sys
import os
import traceback
import logging
from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtGui import QColor
from keyboard_fusion_rgb import KeyboardFusionRGB

class RGBDashboardApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Load your finished Qt Designer Blueprint
        uic.loadUi("main.ui", self)
        
        # 2. Establish Config and Logging Paths
        self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "RGBFusionPro")
        os.makedirs(self.config_dir, exist_ok=True)
        self.log_file_path = os.path.join(self.config_dir, "error.log")
        
        logging.basicConfig(
            filename=self.log_file_path,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # 3. Hardware Connection
        self.keyboard = KeyboardFusionRGB(vendor_id='0x1044', product_id='0x7A3C', layout='eng_us')
        self.settings = QtCore.QSettings("RGBFusionPro", "Settings")

        # 4. State tracking variables (Staged local memory)
        self.active_mode = "static"
        self.color_1 = [255, 255, 255]
        self.color_2 = [0, 0, 255]
        self.brightness = 50
        self.speed = 50
        self.direction = "right"
        self.random_active = False
        self.debug_logging_enabled = False

        # NEW: Tracks what is currently deployed to the hardware
        self.committed_state = {
            'active_mode': None,
            'brightness': None,
            'speed': None,
            'direction': None,
            'random_active': None,
            'color_1': None,
            'color_2': None
        }

        self.mode_titles = {
            'static': 'Static Mode', 'breathing': 'Breathing Mode', 'flow': 'Flow Mode',
            'firework': 'Firework Mode', 'ripple': 'Ripple Mode', 'rain': 'Rain Mode',
            'cycling': 'Color Cycling', 'trigger': 'Trigger Mode', 'pulse': 'Pulse Mode',
            'radar': 'Radar Mode', 'star': 'Star Shining', 'wave': 'Wave Mode',
            'cross': 'Cross Mode', 'dragonstrike': 'Dragonstrike', 'bloom': 'Bloom Mode',
            'spiral': 'Spiral Mode', 'merge': 'Merge Mode', 'crash': 'Crash Mode'
        }

        self.setup_ui_connections()
        self.load_settings()

    def setup_ui_connections(self):
        """Wires up UI controls to update states locally, and wires Apply to write to hardware."""
        self.slider_global_brightness.valueChanged.connect(self.handle_brightness_change)
        self.slider_global_speed.valueChanged.connect(self.handle_speed_change)
        self.combo_direction.currentIndexChanged.connect(self.handle_direction_change)
        self.chk_random.stateChanged.connect(self.handle_random_checkbox_toggle)
        self.chk_dbg.stateChanged.connect(self.handle_debug_checkbox_toggle)

        # Color Selection
        self.btn_color_1.clicked.connect(lambda: self.pick_color(1))
        self.btn_color_2.clicked.connect(lambda: self.pick_color(2))

        # Explicit Apply Button wiring
        self.btn_apply.clicked.connect(self.execute_hardware_transmission)

        # Mode Selection Buttons
        mode_buttons = {
            'btn_static': 'static', 'btn_breathing': 'breathing', 'btn_flow': 'flow',
            'btn_firework': 'firework', 'btn_ripple': 'ripple', 'btn_rain': 'rain',
            'btn_cycling': 'cycling', 'btn_trigger': 'trigger', 'btn_pulse': 'pulse',
            'btn_radar': 'radar', 'btn_star': 'star', 'btn_wave': 'wave',
            'btn_cross': 'cross', 'btn_dragonstrike': 'dragonstrike', 'btn_bloom': 'bloom',
            'btn_spiral': 'spiral', 'btn_merge': 'merge', 'btn_crash': 'crash'
        }
        
        for btn_name, mode_key in mode_buttons.items():
            button_widget = getattr(self, btn_name, None)
            if button_widget:
                button_widget.clicked.connect(lambda checked, mk=mode_key: self.select_mode(mk))

    # ==================== PERSISTENCE ENGINE ====================

    def load_settings(self):
        """Reads saved values from disk and forces the UI components to reflect them."""
        self.active_mode = self.settings.value("active_mode", "static")
        self.brightness = int(self.settings.value("brightness", 50))
        self.speed = int(self.settings.value("speed", 50))
        self.direction = self.settings.value("direction", "right")
        self.random_active = self.settings.value("random_active", False, type=bool)
        self.debug_logging_enabled = self.settings.value("debug_logging_enabled", False, type=bool)
        self.color_1 = self.settings.value("color_1", [255, 255, 255])
        self.color_2 = self.settings.value("color_2", [0, 0, 255])

        # --- SYNC VISUALS ---
        self.slider_global_brightness.blockSignals(True)
        self.slider_global_speed.blockSignals(True)
        self.combo_direction.blockSignals(True)
        self.chk_random.blockSignals(True)
        self.chk_dbg.blockSignals(True)

        self.slider_global_brightness.setValue(self.brightness)
        self.slider_global_speed.setValue(self.speed)
        self.chk_random.setChecked(self.random_active)
        self.chk_dbg.setChecked(self.debug_logging_enabled)
        
        self.btn_color_1.setStyleSheet(f"background-color: rgb({self.color_1[0]},{self.color_1[1]},{self.color_1[2]});")
        self.btn_color_2.setStyleSheet(f"background-color: rgb({self.color_2[0]},{self.color_2[1]},{self.color_2[2]});")

        self.slider_global_brightness.blockSignals(False)
        self.slider_global_speed.blockSignals(False)
        self.combo_direction.blockSignals(False)
        self.chk_random.blockSignals(False)
        self.chk_dbg.blockSignals(False)

        # Set the UI constraints
        self.select_mode(self.active_mode)
        
        # When first booting up, force apply to be disabled since hardware hasn't changed
        self.evaluate_apply_button_state()

    def save_settings(self):
        """Dumps all current application parameters into the configuration file."""
        self.settings.setValue("active_mode", self.active_mode)
        self.settings.setValue("brightness", self.brightness)
        self.settings.setValue("speed", self.speed)
        self.settings.setValue("direction", self.direction)
        self.settings.setValue("random_active", self.random_active)
        self.settings.setValue("debug_logging_enabled", self.debug_logging_enabled)
        self.settings.setValue("color_1", self.color_1)
        self.settings.setValue("color_2", self.color_2)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    # ==================== INTERACTION FLOW ENGINE ====================

    def evaluate_apply_button_state(self):
        """NEW: Enables btn_apply if staged values don't match committed values."""
        has_changed = (
            self.active_mode != self.committed_state['active_mode'] or
            self.brightness != self.committed_state['brightness'] or
            self.speed != self.committed_state['speed'] or
            self.direction != self.committed_state['direction'] or
            self.random_active != self.committed_state['random_active'] or
            self.color_1 != self.committed_state['color_1'] or
            self.color_2 != self.committed_state['color_2']
        )
        self.btn_apply.setEnabled(has_changed)

    def handle_debug_checkbox_toggle(self, state):
        self.debug_logging_enabled = self.chk_dbg.isChecked()

    def handle_brightness_change(self, value):
        self.brightness = int(value)
        self.lbl_brightness.setText(f"Brightness: {self.brightness}%")
        self.evaluate_apply_button_state()

    def handle_speed_change(self, value):
        self.speed = int(value)
        self.evaluate_apply_button_state()

    def handle_direction_change(self):
        current_text = self.combo_direction.currentText().strip()
        if not current_text:
            return
        self.direction = current_text
        self.evaluate_apply_button_state()

    def handle_random_checkbox_toggle(self, state):
        self.random_active = self.chk_random.isChecked()
        self.select_mode(self.active_mode)
        self.evaluate_apply_button_state()

    def select_mode(self, mode_key):
        """Prepares UI constraints but does NOT push values to the hardware driver."""
        self.active_mode = mode_key
        self.lbl_mode.setText(f"Active Mode: {self.mode_titles[mode_key]} (Staged)")
        
        has_speed = (mode_key != "static")
        self.slider_global_speed.setEnabled(has_speed)
        
        has_dir = mode_key in ["flow", "radar", "spiral", "wave", "dragonstrike", "crash"]
        self.combo_direction.setEnabled(has_dir)
        
        if has_dir:
            self.combo_direction.blockSignals(True)
            self.combo_direction.clear()
            
            if mode_key in ["radar", "spiral"]:
                items = ["cw", "ccw"]
            elif mode_key == "crash":
                items = ["horizontal", "vertical"]
            else:
                items = ["right", "left", "up", "down"]
            
            self.combo_direction.addItems(items)
            
            if self.direction in items:
                self.combo_direction.setCurrentText(self.direction)
            else:
                self.direction = items[0]
                self.combo_direction.setCurrentText(self.direction)
                
            self.combo_direction.blockSignals(False)

        has_random = mode_key in ["firework", "rain", "trigger", "pulse", "radar", "star", "wave", "dragonstrike", "bloom", "merge", "crash"]
        self.chk_random.setEnabled(has_random)

        has_colors = mode_key in ["static", "breathing", "firework", "ripple", "rain", "trigger", "pulse", "radar", "star", "wave", "dragonstrike", "bloom", "merge", "crash"]
        is_dual = mode_key in ["dragonstrike", "bloom", "merge", "crash"]
        is_random_active = self.chk_random.isChecked() if has_random else False

        if not has_colors or (has_random and is_random_active):
            self.btn_color_1.setEnabled(False)
            self.btn_color_2.setEnabled(False)
        else:
            self.btn_color_1.setEnabled(True)
            self.btn_color_2.setEnabled(is_dual)
            
        self.evaluate_apply_button_state()

    def pick_color(self, color_num):
        default_color = QColor(255, 0, 0) if color_num == 1 else QColor(0, 0, 255)
        color = QtWidgets.QColorDialog.getColor(default_color, self, f"Select Color {color_num}")
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            if color_num == 1:
                self.color_1 = rgb
                self.btn_color_1.setStyleSheet(f"background-color: rgb({rgb[0]},{rgb[1]},{rgb[2]});")
            else:
                self.color_2 = rgb
                self.btn_color_2.setStyleSheet(f"background-color: rgb({rgb[0]},{rgb[1]},{rgb[2]});")
                
            self.evaluate_apply_button_state()

    # ==================== EXPLICIT DRIVER TRANSMISSION ENGINE ====================

    def execute_hardware_transmission(self):
        """Fires exclusively when btn_apply is clicked. Dispatches current values over USB."""
        needs_dir = self.active_mode in ["flow", "radar", "spiral", "wave", "dragonstrike", "crash"]
        if needs_dir and not self.direction:
            return

        self.lbl_mode.setText(f"Active Mode: {self.mode_titles[self.active_mode]}")

        try:
            if self.active_mode == "static":
                self.keyboard.set_static_mode(color_rgb=self.color_1, brightness=self.brightness)
            elif self.active_mode == "breathing":
                self.keyboard.set_breathing_mode(color_rgb=self.color_1, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "flow":
                self.keyboard.set_flow_mode(speed=self.speed, direction=self.direction, brightness=self.brightness)
            elif self.active_mode == "firework":
                self.keyboard.set_firework_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "ripple":
                self.keyboard.set_ripple_mode(color_rgb=self.color_1, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "rain":
                self.keyboard.set_rain_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "cycling":
                self.keyboard.set_cycling_mode(speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "trigger":
                self.keyboard.set_trigger_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "pulse":
                self.keyboard.set_pulse_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "radar":
                self.keyboard.set_radar_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, direction=self.direction, brightness=self.brightness)
            elif self.active_mode == "star":
                self.keyboard.set_star_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "wave":
                self.keyboard.set_wave_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, direction=self.direction, brightness=self.brightness)
            elif self.active_mode == "cross":
                self.keyboard.set_cross_mode(color_rgb=self.color_1, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "dragonstrike":
                self.keyboard.set_dragonstrike_mode(color_rgb_1=self.color_1, color_rgb_2=self.color_2, random=self.random_active, speed=self.speed, direction=self.direction, brightness=self.brightness)
            elif self.active_mode == "bloom":
                self.keyboard.set_bloom_mode(color_rgb_1=self.color_1, color_rgb_2=self.color_2, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "spiral":
                self.keyboard.set_spiral_mode(speed=self.speed, direction=self.direction, brightness=self.brightness)
            elif self.active_mode == "merge":
                self.keyboard.set_merge_mode(color_rgb_1=self.color_1, color_rgb_2=self.color_2, random=self.random_active, speed=self.speed, brightness=self.brightness)
            elif self.active_mode == "crash":
                self.keyboard.set_crash_mode(color_rgb_1=self.color_1, color_rgb_2=self.color_2, random=self.random_active, speed=self.speed, direction=self.direction, brightness=self.brightness)
            
            # SUCCESS: Sync committed dictionary state to match newly deployed staged values
            self.committed_state['active_mode'] = self.active_mode
            self.committed_state['brightness'] = self.brightness
            self.committed_state['speed'] = self.speed
            self.committed_state['direction'] = self.direction
            self.committed_state['random_active'] = self.random_active
            self.committed_state['color_1'] = list(self.color_1) # copy list values
            self.committed_state['color_2'] = list(self.color_2) # copy list values
            
            # Turn off apply button until another modification occurs
            self.evaluate_apply_button_state()

        except Exception as hardware_error:
            print(f"[!] Hardware communication error: {hardware_error}")
            if self.debug_logging_enabled:
                log_message = (
                    f"Mode: {self.active_mode} | Brightness: {self.brightness} | Speed: {self.speed} | "
                    f"Dir: {self.direction} | Rand: {self.random_active} | C1: {self.color_1} | C2: {self.color_2}\n"
                    f"Exception Detail: {traceback.format_exc()}"
                )
                logging.error(log_message)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RGBDashboardApp()
    window.show()
    sys.exit(app.exec())