How to use WinSploit
--------------------

Step 1 (Installing the Requirements):
	- $ apt install python3
	- $ pip install -r requirements.txt

Step 2 (Usage):
	- First execute WinSploit script ($ python3 WinSploit.py)
	- Enter your LOCALHOST(IP) or PUBLIC IP (that's if you want to use it over WAN)
	- Open the rshell.py script with any text editor of your choice, look for LOCALHOST &
	  LOCALPORT variables. Change the value of the LOCALHOST & LOCALPORT to that you have supplied to WinSploit.py and save the file.
	- Convert the rshell.py to exe with PyInstaller and send it to the target PC 

Step 3(How convert rshell to exe):
	- $ python3 -m PyInstaller rshell.py --noconsole --onefile
	- you can add an icon to the file if you want, to add icon use the below command
	- $ python3 -m PyInstaller rshell --noconsole --onefile icon="path to your icon file" 


Step 4 (What to do if you managed to get a reverse connection):
	- if you manage to get the reverse connection(shell)
	- you can type show_help to get the help on how to exploit your target device


Have Fun & Happy Hacking!, As always never stop learning

More cool features to be added in the future


