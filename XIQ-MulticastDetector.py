#!/usr/bin/env python3
import getpass  ## required if prompting for XIQ crednetials
import json
import requests
from colored import fg, bg, attr

############################################################################################################
## written by:   Mike Rieben
## e-mail:       mrieben@extremenetworks.com
## date:         November, 2022
## version:      1.0
############################################################################################################
## This script will run against access point(s) using provided hostname(s).  It will determine if there's excessive
## multicast in the environment on WiFi0 & WiFi1 interfaces.  If desired it can implement rate limiting commands.
############################################################################################################
## ACTION ITEMS / PREREQUISITES
## Please read the readme.md file in the package to ensure you've completed the desired settings below
############################################################################################################
## <- The Pound character in front of a row will comment out the code to be skipped from runtime
## - ## two pound represents a note about that code. Not executable code.
## - # one pound represents code that is commented out and typically used for troubleshooting
############################################################################################################

## AUTHENTICATION Options:  Uncomment the section you wish to use whie other sections are commented out
## 1) Static Username and password, must have empty token variable (3 lines below)
XIQ_token = ""
XIQ_username = "mikerieben+50@gmail.com"  # Enter your ExtremeCloudIQ Username "xxxx"
XIQ_password = "44vEM2KIoqoCDWDu2Jyl"  # Enter your ExtremeCLoudIQ password "xxxx"
## 2) Prompt user to enter credentials, must have empty token variable (4 lines below)
# print ("Enter your XIQ login credentials ")
# XIQ_token = ""
# XIQ_username = input("Email: ")
# XIQ_password = getpass.getpass("Password: ")
## 3) TOKEN generation from api.extremecloudiq.com (Swagger):  "token".  Must have empty username and password variables (3 lines below)
XIQ_token = "xxxxxxxxx"
XIQ_username = ""
XIQ_password = ""
## Authentication Options END

## Device Management Options:  Static entry or ask user to input
## Credentials XIQ > Global Settings > Device Management Settings > Check to show password
user = "admin"  ## this is always "admin" for IQEngine/HiveOS
##Choose one method below
passwd = "Aerohive123"  ## definition is stored in between "xxxx"
# passwd = input("Enter the Device Management Password: ") ##prompt for user input option instead of static above
## Device Management Options END

## Device Hostnames
apHostname = ["Site1-Prod-MstBed","AP150W","BADHOSTNAME","Site1-Lab-AP1"] ##multiple hostnames comma separated between ["xxxx","xxxx"], single hostname: ["xxxx"] without commas

##************************* No edits below this line ********************************************************************************
##Global Variables
URL = "https://api.extremecloudiq.com"  ## XIQ's API portal
headers = {"Accept": "application/json", "Content-Type": "application/json"}
payload = json.dumps({"username": XIQ_username, "password": XIQ_password})  ## prepare the payload in json format for XIQ credentials
response = requests.post(URL, headers=headers, data=payload)  ## send the API payload to read the response and gather the token
color0 = fg(255) ##DEFAULT Color: color pallete here: https://pypi.org/project/colored/
color1 = fg(1) ##RED
# color2 = fg(2) + bg(255) ##GREEN with a background
color2 = fg(2) ##GREEN
color3 = fg(11) ##YELLOW
reset = attr('reset')
wifiMC = 0

##Function: Use provided credentials to acquire the access token
def GetaccessToken(XIQ_username, XIQ_password):
    url = URL + "/login"
    payload = json.dumps({"username": XIQ_username, "password": XIQ_password})
    response = requests.post(url, headers=headers, data=payload)
    if response is None:
        log_msg = "ERROR: Not able to login into ExtremeCloudIQ - no response!"
        # logging.error(log_msg)
        raise TypeError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error getting access token - HTTP Status Code: {str(response.status_code)}"
        try:
            data = response.json()
            if "error_message" in data:
                log_msg += f"\n\t{data['error_message']}"
        except:
            log_msg += ""
        # logging.error(f"{log_msg}")
        raise TypeError(log_msg)
    data = response.json()

    if "access_token" in data:
        # print("Logged in and got access token: " + data["access_token"])
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0

    else:
        log_msg = "Unknown Error: Unable to gain access token"
        # logging.warning(log_msg)
        raise TypeError(log_msg)

##Function: Get device ID from provided AP hostname
def GetDeviceID(apHostname):
    if not apHostname:
        print("Must enter valid hostname(s), aborting")
        raise SystemExit
    else:
        page = 1
        pageSize = 10
        # pageCount = 1
        # firstCall = True
        ##API Call:  https://api.extremecloudiq.com/devices?page=1&limit=10&hostnames=Site1-Prod-MstBed&fields=ID&deviceTypes=REAL
        url = URL + "/devices?page=" + str(page) + "&limit=" + str(pageSize) + "&hostnames=" + str(apHostname) + "&fields=ID&deviceTypes=REAL"
        response = requests.get(url, headers=headers, verify = True)
        jsonDump = response.json()
        # print (jsonDump)
        # print (jsonDump['data'])
        if jsonDump['data'] == []: #test if the 'data' field is empty due to not finding a device ID from Hostname
            print(color1 + ("Hostname: " + (color3 + (apHostname)) + (color1 + " - Device not found in XIQ. Check your Hostname spelling.")))
            print(color0)
            deviceID = ""
        else:
            deviceID = jsonDump['data'][0]['id']
            print(color0 + ("Hostname: " + (color3 + (apHostname)) + (color0 + ", Device ID: ") + str(deviceID)))
        return deviceID

def SendCLIwifi0(deviceID):
    url = URL + "/devices/" + str(deviceID) + "/:cli"
    ## f"https://api.extremecloudiq.com/devices/{device_id}/:cli"
    payload = json.dumps([
    "show int wifi0 _counter | inc multicast"
    ])
    print(color0 + ("\nGathering multicast counters for WiFi0 interface..."))
    wifi0response = requests.request("POST", url, headers=headers, data=payload)
    jsonDump = wifi0response.json()
    # print(jsonDump)
    wifi0DeviceOutput = jsonDump['device_cli_outputs']
    # print(wifi0DeviceOutput)
    wifi0b = wifi0DeviceOutput[str(deviceID)][0]['output']
    print(wifi0b)
    multicastVals0 = []
    for z in wifi0b.split():
        if z.isdigit():
            multicastVals0.append(int(z))
    # print("First value is Rx, second is Tx:", multicastVals0)
    return multicastVals0

def SendCLIwifi1(deviceID):
    url = URL + "/devices/" + str(deviceID) + "/:cli"
    ## f"https://api.extremecloudiq.com/devices/{device_id}/:cli"
    payload = json.dumps([
    "show int wifi1 _counter | inc multicast"
    ])
    print(color0 + ("\nGathering multicast counters for WiFi1 interface..."))
    wifi1response = requests.request("POST", url, headers=headers, data=payload)
    jsonDump = wifi1response.json()
    # print(jsonDump)
    wifi1DeviceOutput = jsonDump['device_cli_outputs']
    # print(wifi0DeviceOutput)
    wifi1b = wifi1DeviceOutput[str(deviceID)][0]['output']
    print(wifi1b)
    multicastVals1 = []
    for z in wifi1b.split():
        if z.isdigit():
            multicastVals1.append(int(z))
    # print("First value is Rx, second is Tx:", multicastVals1)
    return multicastVals1

##Send Multicast rate limit commands via CLI
def SendCLIMcRateLimit(deviceID):
    url = URL + "/devices/" + str(deviceID) + "/:cli"
    ## f"https://api.extremecloudiq.com/devices/{device_id}/:cli"
    payload = json.dumps([
    "interface eth0 rate-limit multicast 500","interface eth0 rate-limit multicast enable","save config"
    ])
    print(color0 + ("\nSending CLI commands..."))
    cliResponse = requests.request("POST", url, headers=headers, data=payload)
    # jsonDump = cliResponse.json()
    # print(jsonDump)

##Function: determine if device is connected to XIQ
def CheckDeviceConnectedStatus(deviceID):
    ##API Call: 'https://api.extremecloudiq.com/devices/277751240294441?views=BASIC'
    url = URL + "/devices/" + str(deviceID) + "?views=BASIC"
    response = requests.get(url, headers=headers, verify = True)
    jsonDump = response.json()
    # print (jsonDump)
    deviceConnected = jsonDump['connected'] ##Returns True if connected, Flase if disconnected
    if deviceConnected == False:
        print(color1 + ("Device is offline in XIQ and will be skipped..."))
        print(color0)
    return deviceConnected

##Function: do the math
def DoTheMath(deviceConnected,deviceID):
    if deviceConnected == True:
            global wifiMC ##This is required to change the variable value below since it was originally defined in gloabl variables
            multicastVals0 = SendCLIwifi0(deviceID) ##Function: Send CLI to device ID
            if multicastVals0[0] < 500000:
                print(color2 + ("Great! Rx multicast does not exceed 500,000: " + str(multicastVals0[0]) + " data frames reported"))
            else:
                print(color1 + ("***WARNING*** Rx multicast EXCEEDS 500,000: " + str(multicastVals0[0]) + " data frames reported"))
                wifiMC = 1
                if (multicastVals0[1] * 0.90) >= multicastVals0[0]:
                    print("Rx multicast data frames are more than 10% lower than Tx data frames therefor the source of the storm is likey a device on the LAN.")
                else:
                    print("Rx & Tx quantity are within 10% of each other therefor the source of the storm is likey a device on the WLAN.")
        
            if multicastVals0[1] < 8000000:
                print(color2 + ("Great! Tx multicast does not exceed 8,000,000: " + str(multicastVals0[1]) + " data frames reported"))
            else:
                print(color1 + ("***WARNING*** Tx multicast EXCEEDS 8,000,000: " + str(multicastVals0[1]) + " data frames reported"))
                wifiMC = 1
                if (multicastVals0[1] * 0.90) >= multicastVals0[0]:
                    print("Rx multicast data frames are more than 10% lower than Tx data frames therefor the source of the storm is likey a device on the LAN.")
                else:
                    print("Rx & Tx quantity are within 10% of each other therefor the source of the storm is likey a device on the WLAN.")
        
            multicastVals1 = SendCLIwifi1(deviceID) ##Function: Send CLI to device ID
            if multicastVals1[0] < 500000:
                print(color2 + ("Great! Rx multicast does not exceed 500,000: " + str(multicastVals1[0]) + " data frames reported"))
            else:
                print(color1 + ("***WARNING*** Rx multicast EXCEEDS 500,000: " + str(multicastVals1[0]) + " data frames reported"))
                wifiMC = 1
                if (multicastVals1[1] * 0.90) >= multicastVals1[0]:
                    print("Rx multicast data frames are more than 10% lower than Tx data frames therefor the source of the storm is likey a device on the LAN.")
                else:
                    print("Rx & Tx quantity are within 10% of each other therefor the source of the storm is likey a device on the WLAN.")
        
            if multicastVals1[1] < 8000000:
                print(color2 + ("Great! Tx multicast does not exceed 8,000,000: " + str(multicastVals1[1]) + " data frames reported"))
            else:
                print(color1 + ("***WARNING*** Tx multicast EXCEEDS 8,000,000: " + str(multicastVals1[1]) + " data frames reported"))
                wifiMC = 1
                if (multicastVals1[1] * 0.90) >= multicastVals1[0]:
                    print("Rx multicast data frames are more than 10% lower than Tx data frames therefor the source of the storm is likey a device on the LAN.")
                else:
                    print("Rx & Tx quantity are within 10% of each other therefor the source of the storm is likey a device on the WLAN.")
        
            if wifiMC == 1:
                cliYN = input(color0 + ("\nDo you want to implement the rate limit CLI onto the Eth0 interface? [Y/N]: "))
                if cliYN == "Y" or cliYN == "y":
                    SendCLIMcRateLimit(deviceID)
                    print("CLI Complete!  See Readme.md file for more information on implementing Supplemental CLI to ensure rate limits persist with config updates.")
                else:
                    print(color0 + ("Skipped adding CLI commands."))
            else:
                print(color2 + ("\nMulticast is within tollerance. No further action required.\n"))
                print(color0)

##This is the start of the program
def main():
    print("\n") ##print a blank row then cariage return
    ##Test if a token is provided.  If not, use credentials.
    if not XIQ_token:
        try:
            login = GetaccessToken(XIQ_username, XIQ_password)
        except TypeError as e:
            print(e)
            raise SystemExit
        except:
            log_msg = "Unknown Error: Failed to generate token"
            print(log_msg)
            raise SystemExit  
    else:
        headers["Authorization"] = "Bearer " + XIQ_token

    for count in apHostname: ##This is the loop for each hostname entered in the global variables above
        # print (count) ##print each hostname in the list
        deviceID = GetDeviceID(count) ##Function: Acquire device ID from a provided hostnames
        if deviceID != "":
            deviceConnected = CheckDeviceConnectedStatus(deviceID) ##Function: Determine if device is connected to XIQ
            DoTheMath(deviceConnected,deviceID)


##Python will see this and run whatever function is provided: xxxxxx(), should be the last item in this file
if __name__ == '__main__':
    main() ##Go to main function
    