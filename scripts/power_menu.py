PROGRAM_NAME = "pickle-bar:power_menu"

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import os, math, ctypes

class MyWindow(Gtk.Window):
	def __init__(self, css_path: str):
		super().__init__(title=PROGRAM_NAME)
		
		# Connect callbacks
		self.connect("key-press-event", self.on_key_press)

		# Gdk screen
		screen = Gdk.Screen.get_default()

		# Set up styling
		provider = Gtk.CssProvider()
		provider.load_from_path(css_path)
		Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		# Options
		options = [
				# {text}, {command}
				("", "hyprlock"),
				("󰐥", "shutdown now"),
				("", "reboot"),
				("󰤄", "systemctl hibernate"),
				#("", "swaymsg exit"),
				#("", "systemctl suspend"),
		]

		# Create actions
		self.grid = Gtk.Grid()
		NUM_ROWS = 2
		NUM_COLS = math.ceil(len(options) / NUM_ROWS)
		row, col = 0, 0

		# Loop through options and create acitons
		for icn, comm in options:
			btn = Gtk.Button(label=icn)
			btn.connect("clicked", lambda wid, c=comm : self.on_action(wid, c))
			self.grid.attach(btn, col, row, 1, 1)
			# increment position
			col += 1
			if col >= NUM_COLS:
				col = 0
				row += 1

		# Add the grid
		self.add(self.grid)

	def on_action(self, widget, command):
		os.system(command)
		Gtk.main_quit(widget)
	
	# Key press callback
	def on_key_press(self, widget, event):
		if event.keyval == 65307:
			Gtk.main_quit(widget)

def get_path():
	return str(__file__[:__file__.rfind("/") + 1])

win = MyWindow(get_path() + "gtk_style_power.css")
win.connect("destroy", Gtk.main_quit)
win.connect("focus-out-event", Gtk.main_quit)
win.show_all()
win.set_keep_above(True)
Gtk.main()

