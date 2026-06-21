import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QColor
from keyboard_fusion_rgb import KeyboardFusionRGB

class RGBKeyboardApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Load the visual layout blueprint
        uic.loadUi("main.ui", self)
        
        # 2. Initialize hardware connection
        self.keyboard = KeyboardFusionRGB(vendor_id='0x1044', product_id='0x7A3C', layout='eng_us')
        
        # 3. App State Tracking variables
        self.current_brightness = 50
        self.current_mode_name = "Static: White (Default)"
        
        # 4. Bind UI elements to Python code
        self.wire_ui_controls()

    def wire_ui_controls(self):
        """Connects your Qt Designer buttons and sliders to Python functions."""
        # Brightness Slider
        self.slider_brightness.valueChanged.connect(self.handle_brightness_slider)
        
        # Mode Buttons (We'll wire up the first three as a core test group)
        self.btn_static.clicked.connect(lambda: self.apply_mode("static"))
        self.btn_breathing.clicked.connect(lambda: self.apply_mode("breathing"))
        self.btn_flow.clicked.connect(lambda: self.apply_mode("flow"))

    # ==================== CONTROLLER LOGIC ====================

    def handle_brightness_slider(self, value):
        """Fires instantly whenever a user drags the brightness slider."""
        self.current_brightness = value
        self.keyboard.set_brightness(value)
        
        # Update the UI text label instantly
        self.lbl_brightness.setText(f"Brightness: {value}%")

    def get_color_from_user(self):
        """Opens a visual Linux color wheel picker."""
        color = QtWidgets.QColorDialog.getColor(QColor(255, 255, 255), self, "Select Accent Color")
        if color.isValid():
            return [color.red(), color.green(), color.blue()]
        return [255, 255, 255] # Default fallback

    def apply_mode(self, mode_key):
        """Assembles arguments visually based on the clicked button."""
        rgb = [255, 255, 255]
        
        if mode_key == "static":
            rgb = self.get_color_from_user()
            self.keyboard.set_static_mode(color_rgb=rgb, brightness=self.current_brightness)
            self.current_mode_name = "Static Mode"
            
        elif mode_key == "breathing":
            rgb = self.get_color_from_user()
            # Simple default speed of 50 for the UI click
            self.keyboard.set_breathing_mode(color_rgb=rgb, speed=50, brightness=self.current_brightness)
            self.current_mode_name = "Breathing Mode"
            
        elif mode_key == "flow":
            # Simple default right-flow direction
            self.keyboard.set_flow_mode(speed=50, direction="right", brightness=self.current_brightness)
            self.current_mode_name = "Flow Mode"

        # Update the top status label layout
        self.lbl_mode.setText(f"Active Mode: {self.current_mode_name}")


# Main application boot sequence
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RGBKeyboardApp()
    window.show()
    sys.exit(app.exec())