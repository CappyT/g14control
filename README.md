# G14Control
## A simple tray app to control G14 Power options

#### Background:
If you are a user like me, you hate using a bunch of different apps to control all the power saving options of your laptop (sometimes even hidden in the registry) and prefer a simple, handy, tray app utility. The focus of this application is just that!
It does combine all the option offered from other utilities into one, single, configurable TrayApp.

#### What does it do?
G14Control (you can even rename it) can control the current ASUS Power plan, Fan curve, Processor Boost Mode, Processor TDP and dGPU Activation to your needs with a simple right click on the Windows taskbar. You can configure all the presets (and add new ones too) from the `config.yml` file.

#### Does it work?
Not yet fully. See TODO for information about that.

#### What about Linux?
While is possibile to port this app to Linux, at the moment is engineered to work only on Windows. It will be ported to Linux someday as I see the need for it.

### Downloads:
~~Check the release tab!~~

At the moment PyInstaller creates a corrupted EXE file, so it's not currently possibile to package the app.

### How to build:
Make sure python 3 and pip are installed. Then (as admin, in the source folder) run:

`pip install -r requirements.txt`

`pip install pyinstaller`

you can then run the script with: `python main.pyw`

##### NOTE: At the moment PyInstaller creates a corrupted EXE file, so it's not currently possibile to package the app.

Or build an exe with:
`pyinstaller -F --icon=res/icon.ico --noconsole --uac-admin --hidden-import pystray._win32 main.py`


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

### Special thanks:
- https://github.com/FlyGoat/RyzenAdj
- https://github.com/cronosun/atrofac
- https://github.com/dedo1911