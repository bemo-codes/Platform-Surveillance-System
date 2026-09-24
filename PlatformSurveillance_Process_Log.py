import psutil
import sys
import os
import time
import schedule
import smtplib

from email.message import EmailMessage

CPUAlertSent = False

def ProcessScan():
    listprocess = []

    for proc in psutil.process_iter():

        try:
            info = proc.as_dict(
                attrs=["pid", "name", "username", "status"]
            )
            info["cpu_percent"] = proc.cpu_percent(None)
            info["memory_percent"] = proc.memory_percent()
            listprocess.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return listprocess

def PlatformSurveillance(FolderName, ReceiverEmail):
    Border = "-"*50

    Ret = False

    Ret = os.path.exists(FolderName)

    if Ret == True:
        Ret = os.path.isdir(FolderName)
        if Ret == False:
            print("Unable to proceed as diretory name is existing but its not a directory.")
            return
    else:
        os.mkdir(FolderName)
        print("Directory for the log file gets created successfully.")

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")         #Will be used for naming logfiles.  #getting the time in string format

    FileName = os.path.join(FolderName, "Marvellous_%s.log" %timestamp)

    fobj = open(FileName, "w")
    print(f"Log file gets successfully created with name {FileName}")

    fobj.write(Border+"\n")
    fobj.write("---- Platform Surveillance System ----\n")
    fobj.write("Log file gets created at: " + timestamp + "\n")
    print(Border + "\n\n")

    fobj.write("------------------ System Report -----------------------\n")

    #CPU information

    CPUUsage = psutil.cpu_percent(interval=1)

    fobj.write(f"Number of active CPU cores: {psutil.cpu_count()}\n")
    fobj.write(f"CPU usage: {CPUUsage:.2f} %\n")
    fobj.write(Border + "\n")

    global CPUAlertSent

    if CPUUsage >= 80 and CPUAlertSent == False:
        SendMail(CPUUsage, ReceiverEmail)

    elif CPUUsage < 80:
        CPUAlertSent = False

    #RAM information
    memory = psutil.virtual_memory()

    fobj.write("RAM usage: %s %% bytes\n" %memory.percent)
    fobj.write("Total RAM available: %s bytes\n" %memory.total)

    fobj.write(Border+"\n")

    #Network usage
    netobj = psutil.net_io_counters()

    fobj.write("Network Usage Report\n")
    fobj.write("Sent: %.2f MB\n" %(netobj.bytes_sent / (1024 * 1024)))
    fobj.write("Received: %.2f MB\n" %(netobj.bytes_recv / (1024 * 1024)))
    fobj.write(Border+"\n")

    #Disk information
    disk = psutil.disk_usage("/")

    fobj.write("Disk Usage Report\n")
    fobj.write(f"Disk total: {disk.total / (1024 * 1024 * 1024):.2f} GB\n")
    fobj.write(f"Disk used: {disk.used / (1024 * 1024 * 1024):.2f} GB\n")
    fobj.write(f"Disk free: {disk.free / (1024 * 1024 * 1024):.2f} GB\n")
    fobj.write(f"Disk usage: {disk.percent:.2f} %\n")
    fobj.write(Border+"\n")

    #Process Log
    Data = ProcessScan()

    for info in Data:
        # fobj.write(f"{info} \n")
        fobj.write(f"PID: {info.get('pid')}\n")
        fobj.write(f"Name: {info.get('name')}\n")
        fobj.write(f"User Name: {info.get('username')}\n")
        fobj.write(f"Status: {info.get('status')}\n")
        fobj.write(f"CPU usage: {info.get('cpu_percent'):.4f}\n")
        fobj.write(f"RAM usage: {info.get('memory_percent'):.4f}\n")

        fobj.write(Border+"\n")

    fobj.write(Border+"\n")
    fobj.write("------------------End of log file ----------------------\n")
    fobj.write(Border+"\n")

    fobj.close()

def SendMail(CPUUsage, ReceiverEmail):

    SenderEmail = os.getenv("SENDER_EMAIL")
    AppPassword = os.getenv("EMAIL_APP_PASSWORD")

    if not SenderEmail or not AppPassword:
        print("Email configuration is missing.")
        return

    msg = EmailMessage()

    msg["Subject"] = "CPU Usage Alert"
    msg["From"] = SenderEmail
    msg["To"] = ReceiverEmail

    msg.set_content(
        f"WARNING!\n\n"
        f"CPU usage has reached {CPUUsage:.2f}%.\n"
        f"Please check the system."
    )

    try:
        print("Connecting to Gmail SMTP server...")

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=10
        ) as server:
            print("Connected to Gmail SMTP server.")
            print("Logging into Gmail...")

            server.login(SenderEmail, AppPassword)
            print("Login successful.")
            print("Sending email...")

            server.send_message(msg)
            print("CPU alert email sent successfully.")

    except Exception as e:

        print("Unable to send CPU alert email.")
        print("Error:", e)

def main():
    Border = "-"*50
    print(Border)
    print("---- Marvellous Platform Surveillence System ----")
    print(Border)

    #handling --h and --u
    if (len(sys.argv) == 2):
        if(sys.argv[1] == "--h" or sys.argv[1] == "--H"):
            print("This automation script is used to perform")
            print("1: It fetches the information of running processes.")
            print("2: It fetches information about primary memory (RAM).")
            print("3: It fetches information about secondary storage (HDD/SSD).")
            print("4: It fetches the information about the microprocessor.")
            print("5: It gets auto scheduled periodically.")
            print("6: It maintains all records into log file.")
            print("7: It sends the log files through mail periodically.")

        elif(sys.argv[1] == "--u" or sys.argv[1] == "--U"):
            print("Use the automation script as: ")
            print(f"python {sys.argv[0]} Time_Interval Folder_Name Receiver_Email")
            print("Time_interval: Time in minutes for periodic execution.")
            print("Folder_Name: Name of folder for the log file creation.")
            
        else:
            print("Unable to proceed as there is no matching argument.")
            print("Please use --h or --u flag for getting more details.")

    #actual project code
    elif(len(sys.argv) == 4):

        # print("CPU usage: ", psutil.cpu_percent())
        print("Scheduler started successfully.")
        print("Press Ctrl + C to abort the automation script.")
        schedule.every(int(sys.argv[1])).minutes.do(
            PlatformSurveillance,
            sys.argv[2],
            sys.argv[3]
            )
        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        print("Invalid number of arguments.")
        print("Unable to proceed as arguments are not matching.")
        print("Please use --h or --u flag for getting more details.")

    Border = "-"*50
    print(Border)
    print("--- Thank you for using automation System ---")
    print(Border)

if __name__ == "__main__":
    main()
