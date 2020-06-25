import pystray
from PIL import Image
import yaml
from winreg import *
import ctypes
import time
import os
import psutil
from multiprocessing import Process


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
    value = QueryValueEx(sub_key, "AppsUseLightTheme")[0]  # index 0 is the value, index 1 is the type of key
    return value  # 1 for light theme, 0 for dark theme


def create_icon():
    if get_windows_theme() == 0:  # We will create the icon based on current windows theme
        return Image.open('res\icon_light.png')
    else:
        return Image.open('res\icon_dark.png')


def power_check():
    global ac
    while True:
        ac = psutil.sensors_battery().power_plugged
        time.sleep(10)


def notify(message):
    try:
        icon_app.remove_notification()  # Let's make sure everything is removed prior to spawn new notifications
    except Exception as e:
        print(str(e))
    icon_app.notify(message)  # Display the provided argument as message
    time.sleep(config['notification_time'])  # The message is displayed for the configured time. This is blocking.
    icon_app.remove_notification()  # Then, we will remove the notification


def get_current():
    global ac
    notify(
        "Current config: DEFAULT\n" +
        "Boost active: " + str(get_boost()) + "\n" +
        "AC: " + str(ac) + "\n" +
        "dGPU: " + str(get_dgpu()) + "\n"
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


def set_boost():
    state = not get_boost()  # Inverting the boolean of the state, so we can set the opposite
    current_pwr = os.popen("powercfg /GETACTIVESCHEME")  # Just to be safe, let's get the current power scheme
    pwr_guid = current_pwr.readlines()[0].rsplit(": ")[1].rsplit(" (")[0].lstrip("\n")  # Parse the GUID
    if state is True:  # Activate boost
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 1"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 1"
        )
        notify("Boost ENABLED")  # Inform the user
    elif state is False:  # Deactivate boost
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 0"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " 54533251-82be-4824-96c1-47b60b740d00 be337238-0d82-4146-a960-4f3749d470c7 0"
        )
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


def set_dgpu():
    state = not get_boost()  # Inverting the boolean of the state, so we can set the opposite
    current_pwr = os.popen("powercfg /GETACTIVESCHEME")  # Just to be safe, let's get the current power scheme
    pwr_guid = current_pwr.readlines()[0].rsplit(": ")[1].rsplit(" (")[0].lstrip("\n")  # Parse the GUID
    if state is True:  # Activate dGPU
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 3"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 3"
        )
        notify("dGPU ENABLED")  # Inform the user
    elif state is False:  # Deactivate dGPU
        os.popen(
            "powercfg /setacvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 0"
        )
        os.popen(
            "powercfg /setdcvalueindex " + pwr_guid + " e276e160-7cb0-43c6-b20b-73f5dce39954 a1662ab2-9d34-4e53-ba8b-2639b9e20857 0"
        )
        notify("dGPU DISABLED")  # Inform the user


def click():
    print("Hello world")
    notify("Hello world")


def quit_app():
    power_process.terminate()  # This will terminate the process without waiting to finish
    icon_app.stop()  # This will destroy the the tray icon gracefully.


def create_menu():  # This will create the menu in the tray app
    menu = pystray.Menu(
        pystray.MenuItem("Current Config", get_current, default=True),  # The default setting will make the action run on left click
        pystray.MenuItem("CPU Boost", pystray.Menu(  # The "Boost" submenu
            pystray.MenuItem("Boost ON", set_boost),
            pystray.MenuItem("Boost OFF", set_boost),
        )),
        pystray.MenuItem("dGPU", pystray.Menu(
            pystray.MenuItem("dGPU ON", set_dgpu),
            pystray.MenuItem("dGPU OFF", set_dgpu),
        )),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Test", click),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)  # This to close the app, we will need it.
    )
    return menu


def load_config():  # Small function to load the config and return it after parsing
    with open('config.yml', 'r') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


if __name__ == "__main__":
    # if not is_admin():
    #     exit(0)
    config = load_config()  # Make the config available to the whole script
    ac = None  # Defining a variable for ac power
    power_process = Process(target=power_check)  # A process in the background will check for AC
    power_process.start()  # Let's start the process
    icon_app = pystray.Icon(config['app_name'])  # Initialize the icon app and set its name
    icon_app.title = config['app_name']  # This is the displayed name when hovering on the icon
    icon_app.icon = create_icon()  # This will set the icon itself (the graphical icon)
    icon_app.menu = create_menu()  # This will create the menu
    icon_app.run()  # This runs the icon. Is single threaded, blocking.
