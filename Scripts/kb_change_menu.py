from keyboard_fusion_rgb import KeyboardFusionRGB
import time
brightnessVal = 100
brtval = 0
keyboard = KeyboardFusionRGB(vendor_id = '0x1044', product_id = '0x7A3C', layout = 'eng_us')

def set_static_red(brtval):
    global brightnessVal
    brightnessVal = int(brtval)
    keyboard.set_static_mode(color_rgb=[0xff, 0x00, 0x00])
    keyboard.set_brightness(int(brtval))

def set_static_white(brtval):
    global brightnessVal
    brightnessVal = int(brtval)
    keyboard.set_static_mode(color_rgb=[0xff, 0xff, 0xff])
    keyboard.set_brightness(int(brtval))

def set_flow(spd,brt):
    # Set Flow mode
    global brightnessVal
    keyboard.set_flow_mode(speed=int(spd), brightness=int(brt))
    brightnessVal = int(brt)

def inc_bright(val1,val2):
    global brightnessVal
    if brightnessVal == 100:
        print("Brightness is 100%")
    else:
        brightnessVal = int(val1) + int(val2)
        keyboard.set_brightness(brightnessVal)

def dec_bright(val1,val2):
    global brightnessVal
    if brightnessVal == 0:
        print("Brightness is 0%")
    else:
        brightnessVal = int(val1) + int(val2)
        keyboard.set_brightness(brightnessVal)

while True:
    print("\n---Main Menu---")
    blocks = max(0, min(10, brightnessVal // 10))
    gauge = f"[{'▒' * blocks}{' ' * (10 - blocks)}]"
    print(f"Brightness level: {gauge} {brightnessVal}%")
    print("1. Set Light to Red")
    print("2. Set Light to White")
    print("3. Set Light to Flow")
    print("4. Increase Brightness")
    print("5. Decrease Brightness")
    print("6. Quit")

    choice = input("Enter Your Choice 1-7: ")

    if choice == '6':
        print("Exiting Program...")
        break

    elif choice == '1':
        brtval = input("Please Input a Brightness 1-100: ")
        set_static_red(brtval)
        
    elif choice == '2':
        brtval = input("Please Input a Brightness 1-100: ")
        set_static_white(int(brtval))
        
    elif choice == '3':
        spd1 = input("Enter a speed between 0-100: ")
        brt1 = input("Enter a brightness 0-100: ")
        set_flow(spd1, brt1)

    elif choice == '4':
        inc_bright(brightnessVal,10)

    elif choice == '5':
        dec_bright(brightnessVal, -10)
