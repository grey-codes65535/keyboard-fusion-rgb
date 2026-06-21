from keyboard_fusion_rgb import KeyboardFusionRGB

# Global Tracking Variables
brightnessVal = 50
currentMode = "Static: White (Default)"
keyboard = KeyboardFusionRGB(vendor_id='0x1044', product_id='0x7A3C', layout='eng_us')
keyboard.set_brightness(int(brightnessVal))
# Helper map to cleanly translate user input selections to technical mode keys
MENU_MAP = {
    '1': 'static', '2': 'breathing', '3': 'cycling',
    '4': 'flow', '5': 'wave', '6': 'radar', '7': 'spiral',
    '8': 'firework', '9': 'rain', '10': 'star', '11': 'bloom', '12': 'merge', '13': 'crash',
    '14': 'ripple', '15': 'trigger', '16': 'pulse', '17': 'cross', '18': 'dragonstrike'
}

# Master Configuration Engine
MODES_CONFIG = {
    'static':       {'func': keyboard.set_static_mode,       'params': ['color']},
    'breathing':    {'func': keyboard.set_breathing_mode,    'params': ['color', 'speed']},
    'cycling':      {'func': keyboard.set_cycling_mode,      'params': ['speed']},
    'flow':         {'func': keyboard.set_flow_mode,         'params': ['speed', 'direction']},
    'wave':         {'func': keyboard.set_wave_mode,         'params': ['random_color', 'speed', 'direction_std']},
    'radar':        {'func': keyboard.set_radar_mode,        'params': ['random_color', 'speed', 'direction_radar']},
    'spiral':       {'func': keyboard.set_spiral_mode,       'params': ['speed', 'direction_radar']},
    'firework':     {'func': keyboard.set_firework_mode,     'params': ['random_color', 'speed']},
    'rain':         {'func': keyboard.set_rain_mode,         'params': ['random_color', 'speed']},
    'star':         {'func': keyboard.set_star_mode,         'params': ['random_color', 'speed']},
    'bloom':        {'func': keyboard.set_bloom_mode,        'params': ['dual_color', 'speed']},
    'merge':        {'func': keyboard.set_merge_mode,        'params': ['dual_color', 'speed']},
    'crash':        {'func': keyboard.set_crash_mode,        'params': ['dual_color', 'speed', 'direction_crash']},
    'ripple':       {'func': keyboard.set_ripple_mode,       'params': ['color', 'speed']},
    'trigger':      {'func': keyboard.set_trigger_mode,      'params': ['random_color', 'speed']},
    'pulse':        {'func': keyboard.set_pulse_mode,        'params': ['random_color', 'speed']},
    'cross':        {'func': keyboard.set_cross_mode,        'params': ['random_color', 'speed']},
    'dragonstrike': {'func': keyboard.set_dragonstrike_mode, 'params': ['dual_color', 'speed', 'direction_std']}
}

def parse_rgb_input(prompt):
    try:
        rgb = [int(x.strip()) for x in input(prompt).split(',')]
        return rgb if len(rgb) == 3 and all(0 <= c <= 255 for c in rgb) else [255, 255, 255]
    except ValueError:
        return [255, 255, 255]

def get_parameters(param_list):
    kwargs = {}
    for p in param_list:
        if p == 'color':
            kwargs['color_rgb'] = parse_rgb_input("Enter RGB (e.g., 255,0,0 for Red): ")
        elif p == 'dual_color':
            rand = input("Use random colors? (y/n): ").lower() == 'y'
            kwargs['random'] = rand
            kwargs['color_rgb_1'] = [255, 0, 0] if rand else parse_rgb_input("Enter RGB 1: ")
            kwargs['color_rgb_2'] = [0, 0, 255] if rand else parse_rgb_input("Enter RGB 2: ")
        elif p == 'random_color':
            kwargs['random'] = input("Use random colors? (y/n): ").lower() == 'y'
            kwargs['color_rgb'] = [255, 255, 255] if kwargs['random'] else parse_rgb_input("Enter RGB: ")
        elif p == 'speed':
            try: kwargs['speed'] = int(input("Enter speed (0-100) [Default 50]: ") or 50)
            except ValueError: kwargs['speed'] = 50
        elif p == 'direction_std':
            d = input("Enter direction (right, left, up, down) [Default right]: ").lower()
            kwargs['direction'] = d if d in ["right", "left", "up", "down"] else "right"
        elif p == 'direction_radar':
            d = input("Enter direction (cw, ccw) [Default cw]: ").lower()
            kwargs['direction'] = d if d in ["cw", "ccw"] else "cw"
        elif p == 'direction_crash':
            d = input("Enter direction (horizontal, vertical) [Default horizontal]: ").lower()
            kwargs['direction'] = d if d in ["horizontal", "vertical"] else "horizontal"
    return kwargs

def apply_lighting_mode(mode_key):
    global currentMode, brightnessVal
    config = MODES_CONFIG[mode_key]
    arguments = get_parameters(config['params'])
    arguments['brightness'] = brightnessVal
    config['func'](**arguments)
    currentMode = mode_key.replace('_', ' ').title()

def adjust_brightness(amount):
    global brightnessVal
    brightnessVal = max(0, min(100, brightnessVal + amount))
    keyboard.set_brightness(brightnessVal)

# Execution Loop
while True:
    blocks = max(0, min(10, brightnessVal // 10))
    gauge = f"[{'▒' * blocks}{' ' * (10 - blocks)}]"

    print("\n" + "="*55)
    print(f" DEVICE STATUS")
    print(f"  Active Mode: {currentMode}")
    print(f"  Brightness:  {gauge} {brightnessVal}%")
    print("="*55)
    
    print("\n [ Basic Modes ]")
    print("   1. Static Mode          2. Breathing Mode")
    print("   3. Color Cycling")
    
    print("\n [ Animated Motion Patterns ]")
    print("   4. Flow Mode            5. Wave Mode")
    print("   6. Radar Mode           7. Spiral Mode")
    
    print("\n [ Complex Effects ]")
    print("   8. Firework Mode        9. Rain Mode")
    print("  10. Star Shining        11. Bloom Mode")
    print("  12. Merge Mode          13. Crash Mode")
    
    print("\n [ Reactive / Keypress Modes ]")
    print("  14. Ripple Mode         15. Trigger Mode")
    print("  16. Pulse Mode          17. Cross Mode")
    print("  18. Dragonstrike")
    
    print("\n" + "-"*55)
    print("  [+] Increase Brightness   [-] Decrease Brightness")
    print("  [Q] Quit Application")
    print("-"*55)

    choice = input("\nEnter Option / Command: ").strip().lower()

    if choice == 'q':
        print("\nClosing background hardware driver... Goodbye!")
        break
    elif choice in ['+', '=']:
        adjust_brightness(10)
    elif choice == '-':
        adjust_brightness(-10)
    elif choice in MENU_MAP:
        apply_lighting_mode(MENU_MAP[choice])
    else:
        print("\n[!] Invalid input. Please select a valid number or command.")