import cx_Freeze
from cx_Freeze import *

setup(
	name = "G14Control",
	options = {'buid_exe':{'packages':['resources','pystray._win32']}},
	executables=[
		Executable(
			"main.pyw",
			)
		]
	)