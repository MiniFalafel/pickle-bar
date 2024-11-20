# WIFI MENU:
#   > Uses "nmcli" service to list, connect, disconnect, etc
#   > 

PROGRAM_NAME = "pickle-bar~tr~:wifi_menu"

# GTK
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


import os, subprocess
import threading, time

class FakePointer:
	def __init__(self, value = None):
		self.value = value
		
	def set_(self, v):
		self.value = v
		
	def dereference(self):
		return self.value

def do_os_comm(command: str):
	os.system(command)

def get_os_comm(command: str, ptr: FakePointer):
	# RETURNS NONE: Updates the value stored in "ptr"
	ptr.set_(subprocess.check_output(command, shell=True, text=True))
	
def get_comm_threaded(command: str):
	# Create fake pointer for get_os_comm to set
	pt = FakePointer(None)
	# Try getting the os command in a separate thread
	t = threading.Thread(target = get_os_comm, args = (command, pt))
	t.start()
	# wait until the thread is done
	t.join()
	
	# Return
	return pt.dereference()


class Network:
	wifi_signals = ["󰤯 ", "󰤟 ", "󰤢 ", "󰤥 ", "󰤨 "]
	
	def __init__(self, name: str, bssid: str, signal: int, is_secure: bool, connected: bool):
		self.name = name
		self.bssid = bssid
		self.signal = signal
		self.is_secure = is_secure
		self.is_connected = connected
		
	def get_strength_char(self):
		float_sig = self.signal / 100 # Get's it as a percentage
		# Get the index based on signal percentage and return
		index = int(len(Network.wifi_signals) * float_sig) - 1
		return Network.wifi_signals[index]


# Wifi tool (handles connections and stuff)
class WifiTool:
	def is_enabled() -> bool:
		return "enabled" == get_comm_threaded("nmcli radio wifi").strip("\n")
	
	networks = []
	enabled = is_enabled()
		
	def is_enabled() -> bool:
		return "enabled" == get_comm_threaded("nmcli radio wifi").strip("\n")
		
	def set_enabled(on: bool = True):
		s = "on" if on else "off"
		do_os_comm(f"nmcli radio wifi {s}")
		
	def toggle(*args):
		WifiTool.enabled = not WifiTool.enabled
		WifiTool.set_enabled(WifiTool.enabled)
		
		
	def get_available_connections():
		# Running commands in separate thread since they take time and we don't want the program to freeze while it waits
		# Create fake pointer for get_os_comm to set
		pt = FakePointer(None)
		# Try getting the os command in a separate thread
		command = "nmcli device wifi"
		t = threading.Thread(target = get_os_comm, args = (command, pt))
		t.start()
		# wait until the thread is done
		t.join()
		
		# Get element indices
		first_line = pt.dereference().split("\n")[0]
		indices = {
			"BSSID"    : first_line.find("BSSID"),
			"SSID"     : first_line.find(" SSID"), # This one has a space so that it's not confused for "BSSID"'
			"MODE"     : first_line.find("MODE"),
			"SIGNAL"   : first_line.find("SIGNAL"),
			"BARS"     : first_line.find("BARS"),
			"SECURITY" : first_line.find("SECURITY"),
		}
		
		# Get Networks
		new_networks = [] # Reset
		filter_out = ["--"] # "--" is a blank field, so we exclude those
		connections = []
		for line in pt.dereference().split("\n")[1:-1]:
			# Note that we're slicing off the first and last lines since only the middle ones contain actual network information
			bssid = line[indices["BSSID"]:indices["SSID"]].strip()
			name  = line[indices["SSID"]:indices["MODE"]].strip()
			sig_s = line[indices["SIGNAL"]:indices["BARS"]].strip()
			secu  = not (line[indices["SECURITY"]:].strip == "--")
			connected = line.startswith("*")
			
			# Try connecting if duplicate was listed as connected
			if connected and not name in connections:
				connections.append(name)
				# Check if network with this name has already been added to the list and remove it.
				if name in filter_out:
					filter_out.remove(name)
					for i, n in enumerate(new_networks):
						if n.name == name:
							new_networks[i] = None
				
			# Now check if a connection with this name has already been established
			connected = name in connections
			
			# FILTER OUT NAME
			# TODO: Maybe see if there's a better way of doing this
			if name in filter_out:
				continue
			
			# Append to filters so we don't get duplicates'
			filter_out.append(name)
			
			signal = 0
			try:
				signal = int(sig_s)
			except ValueError:
				pass
			
			# Create network object and append to stored networks
			new_networks.append(Network(name, bssid, signal, secu, connected))
			
		
		# Reorganize networks so that connected ones are at the start
		organized = []
		for i, net in enumerate(new_networks):
			if net is not None:
				if net.is_connected:
					organized.append(net)
					new_networks[i] = None
		# Add the rest of the networks to organized
		for net in new_networks:
			if not net is None:
				organized.append(net)
		
		# Set WifiTool.networks to new list
		WifiTool.networks = organized
		
		return WifiTool.networks
		
		
	def get_autoconnect(callback_object, net_id: str):
		# Check connection autoconnect property
		result = FakePointer()
		get_os_comm(f"nmcli connection show \"{net_id}\" | grep connection.autoconnect:", result)
		# Strip whitespace and check status
		return result.dereference().strip().endswith("yes")
		
	def set_autoconnect(callback_object, net_id: str, auto_con: bool):
		# set string
		set_str = "yes" if auto_con else "no"
		# Try
		status = FakePointer()
		get_os_comm(f"nmcli con mod \"{net_id}\" connection.autoconnect {set_str}", status)
		
		if "error" in status.dereference().lower():
			print("ERROR: idk bruh couldn't change autoconnect: {}".format(status.dereference()))
		
	def toggle_autoconnect(callback_object, net_id: str):
		# Get state
		auto = WifiTool.get_autoconnect(callback_object, net_id)
		# Change state to opposite
		WifiTool.set_autoconnect(callback_object, net_id, not auto)
		
	
		
	def forget_network(callback_object, net_id: str):
		# First disconnect from network
		WifiTool.try_disconnect(callback_object, net_id)
		
		do_os_comm(f"nmcli connection delete id \"{net_id}\"")
	
	def try_disconnect(callback_object, net_id: str):
		do_os_comm(f"nmcli con down \"{net_id}\"")
	
	def try_connect(callback_object, net_id: str, get_pass) -> bool:
		# First, disconnect from current connection
		WifiTool.try_disconnect(callback_object, net_id)
		
		password = get_pass()
		
		# Try connecting
		status = FakePointer()
		if not password == "":
			get_os_comm(f"nmcli device wifi connect \"{net_id}\" password \"{password}\"", status)
		else:
			get_os_comm(f"nmcli device wifi connect \"{net_id}\"", status)
		
		# Check status
		if not "success" in status.dereference().lower():
			print("FAILED CONNECTION")
			return False
		return True

# Netork List
class NetList:
	callback = None
	last_list = None
	running = False
	queue = []
	
	searching = False
	__update_thread = None
	thread_lock = threading.Lock()
	
	@staticmethod
	def set_callback(func_ptr) -> None:
		NetList.callback = func_ptr
	
	# update loop
	def start():
		if NetList.running:
			print("ERROR: Cannot run more than one instance of NetList at a time!")
			exit(1)
			
		# Start the update loop in a separate thread
		NetList.__update_thread = threading.Thread(target=NetList.__update_loop)
		NetList.__update_thread.start()
		
	def stop():
		# Set running to false
		NetList.running = False
		
		# Wait for the thread to exit
		NetList.__update_thread.join()
			
	def __update_loop():
		# Set running to true and loop
		NetList.running = True
		while NetList.running:
			# If there are no tasks left, wait a little bit
			if len(NetList.queue) == 0:
				time.sleep(0.1)
				continue
			
			# Grab next task in the queue
			func, args = NetList.queue[0]
			
			# DO THE THING
			# Lock the thread
			NetList.thread_lock.acquire()
			
			# Do the task
			func(*args)
			
			# Remove from the queue
			NetList.queue = NetList.queue[1:]
			
			# Unlock
			NetList.thread_lock.release()
			
	
	# API for GTK callback
	@staticmethod
	def update_list(widget = None):
		if not NetList.searching:
			# Add task to the queue
			NetList.queue.append([NetList.__update_list, ()])
		else:
			print("COULDN'T START: Waiting for current thread to complete")
	
	@staticmethod
	def __update_list() -> None:
		# Check that there's not an active search
		if not NetList.searching:
			# Set searching
			NetList.searching = True
			
			# Check if the list is populated
			if NetList.last_list is not None:
				# Remove it from the current window
				NetList.callback("empty", NetList.last_list)
			
			# Add a spinner in its place
			NetList.callback("loading", NetList.last_list)
			
			# Try and get network list
			networks = WifiTool.get_available_connections()
			
			# UPDATE last_list
			NetList.last_list = Gtk.ListBox()
			# Loop through networks and add them to the list
			for net in networks:
				icn = net.get_strength_char()
				if net.is_connected:
					icn += "󰄬"
				l = "{} {}".format(icn, net.name)
				net_b = Gtk.Expander(label=l)
				# Connection page box
				d_box = Gtk.Box(margin = 6, orientation=Gtk.Orientation.VERTICAL)
				# Check if we're connected to this network
				if net.is_connected:
					# Line 1 container
					btn_box = Gtk.Box()
					d_box.pack_start(btn_box, False, False, 0)
					
					l = Gtk.Label(label="Connected")
					btn_box.pack_start(l, False, False, 0)
					# Disconnect button
					disc_icon = " "
					disconn = Gtk.Button(label=disc_icon) #("disconnect")
					disconn.connect("clicked", NetList.__do_update, WifiTool.try_disconnect, net.name)
					disconn.connect("enter-notify-event", lambda widget, a: widget.set_label("disconnect"))
					disconn.connect("leave-notify-event", lambda widget, a: widget.set_label(disc_icon))
					# forget button
					forg_icon = " "
					forget = Gtk.Button(label=forg_icon) #("forget")
					forget.connect("clicked", NetList.__do_update, WifiTool.forget_network, net.name)
					forget.connect("enter-notify-event", lambda widget, a: widget.set_label("forget"))
					forget.connect("leave-notify-event", lambda widget, a: widget.set_label(forg_icon))
					
					# Add buttons
					btn_box.pack_end(forget, False, False, 0)
					btn_box.pack_end(disconn, False, False, 0)
					
					# Auto-connect property:
					autocon = Gtk.CheckButton(label="autoconnect?")
					autocon.set_active(WifiTool.get_autoconnect(None, net.name))
					autocon.connect("toggled", NetList.__do_update, WifiTool.toggle_autoconnect, net.name)
					
					# Add autoconnect toggle
					d_box.pack_start(autocon, False, False, 0)	
				else:
					con_box = Gtk.Box()
					# Password entry
					if net.is_secure:
						e = Gtk.Entry()
						e.connect("activate", NetList.__do_update, WifiTool.try_connect, net.name, e.get_text)
						con_box.pack_start(e, True, True, 0)
					# Conect button
					conn = Gtk.Button(label="connect")
					conn.connect("clicked", NetList.__do_update, WifiTool.try_connect, net.name, e.get_text)
					con_box.pack_end(conn, False, False, 0)
					
					# Add to drawer
					d_box.pack_start(con_box, False, False, 0)
				
				# Add d box to net_b
				net_b.add(d_box)
				# Pack net_b into the net list
				#net_b.show()
				NetList.last_list.add(net_b)
				
			# Update the network list with the callback
			NetList.callback("append", NetList.last_list)
			
			# Unset searching
			NetList.searching = False
	
	def __do_update(callback_object, func, *args):
		print(args)
		# Run callback
		func(callback_object, *args)
		# Update the list again
		NetList.update_list()


WIDTH, HEIGHT = 450, 500

class MyWindow(Gtk.Window):
	def __init__(self, css_path: str):
		super().__init__(title=PROGRAM_NAME)
		
		# Set default size
		self.set_size_request(WIDTH, HEIGHT)
		
		self.icons = {
			"toggle" : "󰤨 ",
			"refresh" : "󰑐 "
		}
		
		# Connect callbacks
		self.connect("key-press-event", self.on_key_press)
		
		if css_path is not None:
			# Gdk screen
			screen = Gdk.Screen.get_default()

			# Set up styling
			provider = Gtk.CssProvider()
			provider.load_from_path(css_path)
			Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		# Contents
		self.contents = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=15)
		self.add(self.contents)

		# Wifi header box
		header_box = Gtk.Box()
		self.contents.pack_start(header_box, False, False, 0)
		
		# HEADER
		# Main label
		header_label = Gtk.Label(label="Wifi Networks:  ")
		header_box.pack_start(header_label, False, False, 0)
		
		# Buttons
		# Wifi enable/disable button
		on_off_btn = Gtk.ToggleButton(label=self.icons["toggle"])
		on_off_btn.set_active(WifiTool.is_enabled())
		on_off_btn.connect("toggled", WifiTool.toggle)
		
		# Refresh list button
		refresh_btn = Gtk.Button(label=self.icons["refresh"])
		refresh_btn.connect("clicked", NetList.update_list)
		
		# pack buttons into header
		header_box.pack_end(on_off_btn, False, False, 0)
		header_box.pack_end(refresh_btn, False, False, 0)
		
		# Setup network scroll box
		self.net_scroll_box = None
		self.reset_scroll_window()
		
		# Load the network list into the scroll box
		NetList.set_callback(self.reload_callback)
		NetList.update_list()
		
	def reset_scroll_window(self):
		self.net_scroll_box = Gtk.ScrolledWindow()
		self.net_scroll_box.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		self.contents.pack_start(self.net_scroll_box, True, True, 0)
		
	def set_list_contents(self, wid: Gtk.Widget):
		# Remove the scroll box
		self.contents.remove(self.net_scroll_box)
		
		# Reset scroll window
		self.reset_scroll_window()
		
		if wid is not None:
			# Add the net_list to the scroll window
			self.net_scroll_box.add(wid)
			
		# Add scroll window to the contents
		self.contents.pack_start(self.net_scroll_box, True, True, 0)
		
		# Show everything
		self.contents.show()
		self.net_scroll_box.show()
		if wid is not None:
			try:
				wid.show_all()
			except AttributeError:
				wid.show()
		
	def reload_callback(self, command: str, net_list: list = None):
		match command:
			case "empty":
				# Empty the network lit
				self.set_list_contents(None)
			case "loading":
				# set contents to loading animation
				box = Gtk.Box(margin = 200)
				spinner = Gtk.Spinner()
				spinner.start()
				box.pack_start(spinner, True, True, 0)
				self.set_list_contents(box)
			case "append":
				# Populate the list with new network list object
				self.set_list_contents(net_list)
				# Resize window to match contents
				self.resize(0, 0)
			case _:
				print("UNRECOGNIZED CALLBACK COMMAND")
		
	def dummy(self, widget):
		print("dummy")
		

	def on_action(self, widget, command):
		os.system(command)
		Gtk.main_quit(widget)
	
	# Key press callback
	def on_key_press(self, widget, event):
		if event.keyval == 65307:
			Gtk.main_quit(widget)

def get_path():
	return str(__file__[:__file__.rfind("/") + 1])


# Start network list manager update loop
NetList.start()

# Start window
win = MyWindow(get_path() + "gtk_style.css")
win.connect("destroy", Gtk.main_quit)
win.connect("focus-out-event", Gtk.main_quit)
win.show_all()
win.set_keep_above(True)
Gtk.main()

# Stop the network list manager
NetList.stop()
