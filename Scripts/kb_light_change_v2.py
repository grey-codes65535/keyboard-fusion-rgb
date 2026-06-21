from keyboard_fusion_rgb import KeyboardFusionRGB

# Global Tracking Variables
brightnessVal = 50
currentMode = "Static: White (Default)"
keyboard = KeyboardFusionRGB(vendor_id='0x1044', product_id='0x7A3C', layout='eng_us')

# Helper map to cleanly translate user input selections to technical mode keys
MENU_MAP = {
    '1': 'static', '2': 'breathing', '3': 'flow', '4': 'firework',
    '5': 'ripple', '6': 'rain', '7': 'cycling', '8': 'trigger',
    '9': 'pulse', '10': 'radar', '11': 'star', '12': 'wave',
    '13': 'cross', '14': 'dragonstrike', '15': 'bloom',
    '16': 'spiral', '17': 'merge', '18': 'crash'
}

# Master Configuration Engine
# Defines parameter profiles dynamically so the router knows what to ask the user
MODES_CONFIG = {
    'static':       {'func': keyboard.set_static_mode,       'params': ['color']},
    'breathing':    {'func': keyboard.set_breathing_mode,    'params': ['color', 'speed']},
    'flow':         {'func': keyboard.set_flow_mode,         'params': ['speed', 'direction']},
    'firework':     {'func': keyboard.set_firework_mode,     'params': ['random_color', 'speed']},
    'ripple':       {'func': keyboard.set_ripple_mode,       'params': ['color', 'speed']},
    'rain':         {'func': keyboard.set_rain_mode,         'params': ['random_color', 'speed']},
    'cycling':      {'func': keyboard.set_cycling_mode,      'params': ['speed']},
    'trigger':      {'func': keyboard.set_trigger_mode,      'params': ['random_color', 'speed']},
    'pulse':        {'func': keyboard.set_pulse_mode,        'params': ['random_color', 'speed']},
    'radar':        {'func': keyboard.set_radar_mode,        'params': ['random_color', 'speed', 'direction_radar']},
    'star':         {'func': keyboard.set_star_mode,         'params': ['random_color', 'speed']},
    'wave':         {'func': keyboard.set_wave_mode,         'params': ['random_color', 'speed', 'direction_std']},
    'cross':        {'func': keyboard.set_cross_mode,        'params': ['random_color', 'speed']},
    'dragonstrike': {'func': keyboard.set_dragonstrike_mode, 'params': ['dual_color', 'speed', 'direction_std']},
    'bloom':        {'func': keyboard.set_bloom_mode,        'params': ['dual_color', 'speed']},
    'spiral':       {'func': keyboard.set_spiral_mode,       'params': ['speed', 'direction_radar']},
    'merge':        {'func': keyboard.set_merge_mode,        'params': ['dual_color', 'speed']},
    'crash':        {'func': keyboard.set_crash_mode,        'params': ['dual_color', 'speed', 'direction_crash']}
}

def parse_rgb_input(prompt):
    """Safely converts comma-separated strings to 8-bit RGB lists."""
    try:
        rgb = [int(x.strip()) for x in input(prompt).split(',')]
        return rgb if len(rgb) == 3 and all(0 <= c <= 255 for c in rgb) else [255, 255, 255]
    except ValueError:
        return [255, 255, 255]

def get_parameters(param_list):
    """Collects inputs dynamically based on the mode profile."""
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
    """Executes hardware bindings cleanly using kwargs unpacking."""
    global currentMode, brightnessVal
    config = MODES_CONFIG[mode_key]
    
    # Dynamically build argument schema
    arguments = get_parameters(config['params'])
    arguments['brightness'] = brightnessVal
    
    # Unpack collected options right into target hardware method
    config['func'](**arguments)
    currentMode = mode_key.replace('_', ' ').title()

def adjust_brightness(amount):
    """Global brightness handler clamping valid boundaries."""
    global brightnessVal
    brightnessVal = max(0, min(100, brightnessVal + amount))
    keyboard.set_brightness(brightnessVal)

# Execution Loop
while True:
    blocks = max(0, min(10, brightnessVal // 10))
    gauge = f"[{'▒' * blocks}{' ' * (10 - blocks)}]"

    print(f"\n====================== Main Menu ======================")
    print(f" Mode:  {currentMode:<22} Brightness: {gauge} {brightnessVal}%")
    print(f"=======================================================")
    print(" 1. Static       2. Breathing    3. Flow         4. Firework")
    print(" 5. Ripple       6. Rain         7. Cycling      8. Trigger")
    print(" 9. Pulse       10. Radar       11. Star        12. Wave")
    print("13. Cross       14. Dragonstrike15. Bloom       16. Spiral")
    print("17. Merge       18. Crash")
    print("-------------------------------------------------------")
    print(" [+] Increase Brightness (+10%)  [-] Decrease Brightness (-10%)")
    print(" [q] Quit Application")
    print("=======================================================")

    choice = input("\nSelection: ").strip().lower()

    if choice == 'q':
        print("Safely terminating driver connection...")
        break
    elif choice in ['+', '=']:
        adjust_brightness(10)
    elif choice == '-':
        adjust_brightness(-10)
    elif choice in MENU_MAP:
        apply_lighting_mode(MENU_MAP[choice])
    else:
        print("Invalid Selection. Refreshing interface...")