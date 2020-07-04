# G14Control
## A simple tray app to control G14 Power options

#### Background:
If you are a user like me, you hate using a bunch of different apps to control all the power saving options of your laptop (sometimes even hidden in the registry) and prefer a simple, handy, tray app utility. The focus of this application is just that!
It does combine all the option offered from other utilities into one, single, configurable TrayApp.

#### What does it do?
G14Control (you can even rename it) can control the current ASUS Power plan, Fan curve, Processor Boost Mode, Processor TDP, dGPU Activation and Screen refresh rate to your needs with a simple right click on the Windows taskbar. You can configure all the presets (and add new ones too) from the `config.yml` file.

#### Does it work?
Not yet fully. See TODO for information about that.

#### What about Linux?
While is possible to port this app to Linux, at the moment is engineered to work only on Windows. It will be ported to Linux someday as I see the need for it.

### Installation
Download the latest release zip from GitHub: https://github.com/CappyT/g14control/releases

Extract it to some permanent location such as C:\Program Files\G14Control

Edit the config.yml with text editor as needed (see configuring below)

To make it run on boot, you will need to follow these instructions since it requires administrator privileges: https://www.sevenforums.com/tutorials/11949-elevated-program-shortcut-without-uac-prompt-create.html

### Configuring
All done in config.yaml within the root folder of the program. The program must be restarted for any changes to the config.yaml to take effect.

`app_name:` can be customized, this is what the hover text displays over the icon and the windows notification title

`default_starting_plan` set plan name you want on boot or on restart of the program

`default_ac_plan` This plan name will automatically enable when AC adapter plugged in (set both default_ac_plan and default_dc_plan to `null` to disable this feature)

`default_dc_plan` This plan name will automatically enable when on battery power (set both default_ac_plan and default_dc_plan to `null` to disable this feature)

##### Power Plans:
Under Plans, you can configure as many or few plans as you want. A plan includes:
```
- name:
    This is where you will enter the name you want to be displayed for that plan
  plan:
    Name of the ROG Armory plan you want it set on (`silent` or `windows` or `performance` or `turbo`)
  cpu_curve:
    An array of `temps_in_deg_C:fanspeed_percent` for custom fan curve such as "30c:0%,40c:0%,50c:0%,60c:0%,70c:34%,80c:51%,90c:61%,100c:61%". Otherwise use `null` for default
  gpu_curve:
    An array of `temps_in_deg_C:fanspeed_percent` for custom fan curve such as "30c:0%,40c:0%,50c:0%,60c:0%,70c:34%,80c:51%,90c:61%,100c:61%". Otherwise use `null` for default
  cpu_tdp:
    The tdp you want for the CPU expressed in mW, use `null` for default or numeric (45000 = 45W)
  boost:
    Whether you want the CPU to boost above it's 3.0Ghz base clock speed, `true` or `false`
  dgpu_enabled:
    Whether you want the dedicated NVIDIA GPU enabled (uses more power, need for graphics/games), `true`, `false`
  screen_hz:
    The refresh rate of the screen. Can be 60 (numeric) or 120 (numeric) (for supported models) or null for default
```

The config.yaml has many examples of plans included by default. Modify at will.

### Downloads:
Check the release tab!


### How to build:
Make sure python 3 and pip are installed. Then (as admin, in the source folder) run:

`pip install -r requirements.txt`

`python setup.py build`

Then copy config.yml to the \build\exe.win-amd64-3.8\ directory, then rename & zip that folder for release!


### Contribute:
You are very free to contribute with your code. I kinda suck at coding so any help is appreciated. Just submit a pull request, I will merge it or discuss it as soon as possible.

### TODO:
- Automatic config generation
- ~~Dynamic Menu generation based on configured profiles~~ Implemented
- ~~atrofac commands integration~~ Implemented
- ~~ryzenadj command integration~~ Implemented
- ~~Parallel notification spawning (right now when notification is displayed the whole app locks until the notification disappears)~~ Kinda buggy, but better.
- Different options for AC/DC modes
- Windows power plan switching (is it needed?)
- Logging
- Better binary storage
- Better UI (?)
- Better code comments
- Better ~~engrish~~ english (sorry, is just not my native language)
- .... you tell us!

### Contributors:
- https://github.com/FlyGoat/RyzenAdj
- https://github.com/cronosun/atrofac
- https://github.com/dedo1911
- https://github.com/carverhaines
