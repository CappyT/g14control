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

### Disclaimer
Please note that this is an ALPHA version of this software, which is still undergoing testing and development. The software and all content found on GitHub related to it are provided “as is”. We do not give any warranties, whether express or implied, as to the safety, reliability, suitability or usability of the software or any of its content.

We will not be held liable for any loss, whether such loss is direct, indirect, special or consequential, suffered by any party as a result of their use of the software or content. Any use of the software or scripts provided here is done at the user’s own risk and the user will be solely responsible for any damage to any computer system or loss of data that results from such activities.

Should you encounter any bugs, glitches, lack of functionality or other problems with the software, please let us know in GitHub so we can look into addressing it.

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
- https://tools.taubenkorb.at/change-screen-resolution/
