from pystray import _win32
import pystray
from PIL import Image
import yaml
from winreg import *
import ctypes
import time
import os
import sys
import re
import psutil
import resources
from threading import Thread


def parse_boolean(parse_string):  # Small utility to convert windows HEX format to a boolean.
    try:
        if parse_string == "0x00000000":  # We will consider this as False
            return False
        else:  # We will consider this as True
            return True
    except Exception:
        return None  # Just in case™


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()  # Returns true if the user launched the app as admin
    except Exception:
        return False


def get_windows_theme():
    key = ConnectRegistry(None, HKEY_CURRENT_USER)  # By default, this is the local registry
    sub_key = OpenKey(key, "Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")  # Let's open the subkey
    value = QueryValueEx(sub_key, "SystemUsesLightTheme")[0]  # Taskbar (where icon is displayed) uses the 'System' light theme key. Index 0 is the value, index 1 is the type of key
    return value  # 1 for light theme, 0 for dark theme


def create_icon():
    if get_windows_theme() == 0:  # We will create the icon based on current windows theme
        return Image.open(os.path.join(config['temp_dir'], 'icon_light.png'))
    else:
        return Image.open(os.path.join(config['temp_dir'], 'icon_dark.png'))


def power_check():
    global auto_power_switch, ac, current_plan, default_ac_plan, default_dc_plan
    if auto_power_switch:     # Only run while loop on startup if auto_power_switch is On (True)
        while True:
            if auto_power_switch:   # Check to user hasn't disabled auto_power_switch (i.e. by manually switching plans)
                ac = psutil.sensors_battery().power_plugged     # Get the current AC power status
                if ac and current_plan != default_ac_plan:      # If on AC power, and not on the default_ac_plan, switch to that plan
                    for plan in config['plans']:
                        if plan['name'] == default_ac_plan:
                            break
                    apply_plan(plan)
                if not ac and current_plan != default_dc_plan:      # If on DC power, and not on the default_dc_plan, switch to that plan
                    for plan in config['plans']:
                        if plan['name'] == default_dc_plan:
                            break
                    apply_plan(plan)
                time.sleep(10)
    else:
        return


def activate_powerswitching():
    global auto_power_switch
    auto_power_switch = True
    time.sleep(10)   # Plan change notifies first, so this needs to be on a delay to prevent simultaneous notifications
    notify("Auto power switching has been ENABLED")


def deactivate_powerswitching():
    global auto_power_switch
    auto_power_switch = False
    time.sleep(10)   # Plan change notifies first, so this needs to be on a delay to prevent simultaneous notifications
    notify("Auto power switching has been DISABLED")


def notify(message):
    Thread(target=do_notify, args=(message,), daemon=True).start()


def do_notify(message):
    global icon_app
    icon_app.notify(message)  # Display the provided argument as message
    time.sleep(config['notification_time'])  # The message is displayed for the configured time. This is blocking.
    icon_app.remove_notification()  # Then, we will remove the notification


def get_current():
    global ac, current_plan
    notify(
        "Plan: " + current_plan + "\n" +
        "Boost: " + (["Off", "On"][get_boost()]) + "     dGPU: " + (["Off", "On"][get_dgpu()]) + "\n" +
        "Refresh Rate: " + (["60Hz", "120Hz"][get_screen()]) + "\n" +
        "Power: " + (["Battery", "AC"][bool(ac)]) + "     Auto Switching: " + (["Off", "On"][auto_power_switch]) + "\n"
    )  # Let's print the current values


def get_boost():
    current_pwr = os.popen("powercfg /GETACTIVESCHEME")  # I know, it's ugly, but no other way to do that from py.
    pwr_guid = current_pwr.readlines()[0].rsplit(": ")[1].rsplit(" (")[0].lstrip("\n")  # Parse the GUID
    pwr_settings = os.popen(
        "powercfg /Q " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7"
    )  # Let's get the boost option in the currently active power scheme
    output = pwr_settings.readlines()  # We save the output to parse it afterwards
    ac_boost = parse_boolean(output[-3].rsplit(": ")[1].strip("\n"))  # Parsing AC, assuming the DC is the same setting
    # battery_boost = parse_boolean(output[-2].rsplit(": ")[1].strip("\n"))  # currently unused, we will set both
    return ac_boost


def set_boost(state, notification=True):
    current_pwr = os.popen("powercfg /GETACTIVESCHEME")  # Just to be safe, let's get the current power scheme
    pwr_guid = current_pwr.readlines()[0].rsplit(": ")[1].rsplit(" (")[0].lstrip("\n")  # Parse the GUID
    if state is True:  # Activate boost
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 1"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 1"
        )
        if notification is True:
            notify("Boost ENABLED")  # Inform the user
    elif state is False:  # Deactivate boost
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 0"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 0"
        )
        if notification is True:
            notify("Boost DISABLED")  # Inform the user


def get_dgpu():
    current_pwr = os.popen("powercfg /GETACTIVESCHEME")  # I know, it's ugly, but no other way to do that from py.
    pwr_guid = current_pwr.readlines()[0].rsplit(": ")[1].rsplit(" (")[0].lstrip("\n")  # Parse the GUID
    pwr_settings = os.popen(
        "powercfg /Q " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857"
    )  # Let's get the dGPU status in the current power scheme
    output = pwr_settings.readlines()  # We save the output to parse it afterwards
    dgpu_ac = parse_boolean(output[-3].rsplit(": ")[1].strip("\n"))  # Convert to boolean for "On/Off"
    return dgpu_ac


def set_dgpu(state, notification=True):
    current_pwr = os.popen("powercfg /GETACTIVESCHEME")  # Just to be safe, let's get the current power scheme
    pwr_guid = current_pwr.readlines()[0].rsplit(": ")[1].rsplit(" (")[0].lstrip("\n")  # Parse the GUID
    if state is True:  # Activate dGPU
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 2"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 2"
        )
        if notification is True:
            notify("dGPU ENABLED")  # Inform the user
    elif state is False:  # Deactivate dGPU
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 0"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 0"
        )
        if notification is True:
            notify("dGPU DISABLED")  # Inform the user


def check_screen():  # Checks to see if the G14 has a 120Hz capable screen or not
    checkscreenref = str(os.path.join(config['temp_dir'] + 'ChangeScreenResolution.exe'))
    screen = os.popen(checkscreenref + " /m /d=0")  # /m lists all possible resolutions & refresh rates
    output = screen.readlines()
    for line in output:
        if re.search("@120Hz", line):
            return True
    else:
        return False


def get_screen():  # Gets the current screen resolution
    getscreenref = str(os.path.join(config['temp_dir'] + 'ChangeScreenResolution.exe'))
    screen = os.popen(getscreenref + " /l /d=0")  # /l lists current resolution & refresh rate
    output = screen.readlines()
    for line in output:
        if re.search("@120Hz", line):
            return True
    else:
        return False


def set_screen(refresh, notification=True):
    if check_screen():  # Before trying to change resolution, check that G14 is capable of 120Hz resolution
        if refresh is None:
            set_screen(120)  # If screen refresh rate is null (not set), set to default refresh rate of 120Hz
        checkscreenref = str(os.path.join(config['temp_dir'] + 'ChangeScreenResolution.exe'))
        os.popen(
            checkscreenref + " /d=0 /f=" + str(refresh)
        )
        if notification is True:
            notify("Screen refresh rate set to: " + str(refresh) + "Hz")
    else:
        return


def set_atrofac(asus_plan, cpu_curve=None, gpu_curve=None):
    atrofac = str(os.path.join(config['temp_dir'] + "atrofac-cli.exe"))
    if cpu_curve is not None and gpu_curve is not None:
        os.popen(
            atrofac + " fan --cpu " + cpu_curve + " --gpu " + gpu_curve + " --plan " + asus_plan
        )
    elif cpu_curve is not None and gpu_curve is None:
        os.popen(
            atrofac + " fan --cpu " + cpu_curve + " --plan " + asus_plan
        )
    elif cpu_curve is None and gpu_curve is not None:
        os.popen(
            atrofac + " fan --gpu " + gpu_curve + " --plan " + asus_plan
        )
    else:
        os.popen(
            atrofac + " plan " + asus_plan
        )


def set_ryzenadj(tdp):
    ryzenadj = str(os.path.join(config['temp_dir'] + "ryzenadj.exe"))
    if tdp is None:
        pass
    else:
        os.popen(
            ryzenadj + " -a " + tdp + " -b " + tdp
        )


def apply_plan(plan):
    global current_plan
    current_plan = plan['name']
    set_atrofac(plan['plan'], plan['cpu_curve'], plan['gpu_curve'])
    set_boost(plan['boost'], False)
    set_dgpu(plan['dgpu_enabled'], False)
    set_screen(plan['screen_hz'], False)
    set_ryzenadj(plan['cpu_tdp'])
    notify("Applied plan " + plan['name'])


def quit_app():
    icon_app.stop()  # This will destroy the the tray icon gracefully.


def create_menu():  # This will create the menu in the tray app
    menu = pystray.Menu(
        pystray.MenuItem("Current Config", get_current, default=True),  # The default setting will make the action run on left click
        pystray.MenuItem("CPU Boost", pystray.Menu(  # The "Boost" submenu
            pystray.MenuItem("Boost ON", lambda: set_boost(True)),
            pystray.MenuItem("Boost OFF", lambda: set_boost(False)),
        )),
        pystray.MenuItem("dGPU", pystray.Menu(
            pystray.MenuItem("dGPU ON", lambda: set_dgpu(True)),
            pystray.MenuItem("dGPU OFF", lambda: set_dgpu(False)),
        )),
        pystray.MenuItem("Screen Refresh", pystray.Menu(
            pystray.MenuItem("120Hz", lambda: set_screen(120)),
            pystray.MenuItem("60Hz", lambda: set_screen(60)),
        ), visible=check_screen()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Re-Enable Auto Power Switching", activate_powerswitching),
        pystray.Menu.SEPARATOR,
        # I have no idea of what I am doing, fo real, man.
        *list(map((lambda plan: pystray.MenuItem(plan['name'], (lambda: (apply_plan(plan),deactivate_powerswitching())))), config['plans'])),  # Blame @dedo1911 for this. You can find him on github.
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)  # This to close the app, we will need it.
    )
    return menu


def load_config():  # Small function to load the config and return it after parsing
    if getattr(sys, 'frozen', False):
    #if the script is run frozen
        with open(os.path.join(os.path.dirname(sys.executable), "config.yml"), 'r') as config_file:
            return yaml.load(config_file, Loader=yaml.FullLoader)
    else:
    #if the scirpt is run outside of frozen package
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml"), 'r') as config_file:
            return yaml.load(config_file, Loader=yaml.FullLoader)


if __name__ == "__main__":
    config = load_config()  # Make the config available to the whole script
    if is_admin() or config['debug']:  # If running as admin or in debug mode, launch program
        current_plan = config['default_starting_plan']
        default_ac_plan = config['default_ac_plan']
        default_dc_plan = config['default_dc_plan']
        ac = psutil.sensors_battery().power_plugged  # Set AC/battery status on start
        if default_ac_plan is not None and default_dc_plan is not None:  # Only enable auto_power_switch on boot if default power plans are enabled (not set to null)
            auto_power_switch = True
        else:
            auto_power_switch = False
        Thread(target=power_check, daemon=True).start()  # A process in the background will check for AC, autoswitch plan if enabled and detected
        resources.extract(config['temp_dir'])
        icon_app = pystray.Icon(config['app_name'])  # Initialize the icon app and set its name
        icon_app.title = config['app_name']  # This is the displayed name when hovering on the icon
        icon_app.icon = create_icon()  # This will set the icon itself (the graphical icon)
        icon_app.menu = create_menu()  # This will create the menu
        icon_app.run()  # This runs the icon. Is single threaded, blocking.
    else:  # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
