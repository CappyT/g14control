from cx_Freeze import *


setup(
    name="G14Control",
    version="0.1",
    options={'buid_exe': {'packages': ['resources', 'pystray._win32']}},
    executables=[
        Executable(
            script="G14Control.pyw",
            icon="res\icon.ico",
            base="Win32GUI"
            )
        ]
    )
