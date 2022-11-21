# XIQ Multicast Detector Script
## XIQ-MulticastDetector.py
### Purpose
This script will use a list of device hostnames you provide and run a specific set of commands to detect Tx/Rx Multicast stats.  This will use API's to send commands to device that are online in XIQ and report back if any devices are offline.

### Requirements
Python 3.6 or higher is recommended for this script.
The needed modules are listed in the requirements.txt file and can be installed from there using <br />
CLI:  pip install -r requirements.txt <br />
See API Getting Started Guide if you need further assistance understanding this process.
https://github.com/ExtremeNetworksSA/API_Getting_Started

### User Input
You'll need to modify the script in a few places to establish the desired settings and to provide a list of hostnames

#### Lines 24 ~ 38 are three XIQ authenitcation options (static, prompt, or token)
1) Lines 26 ~ 28 (uncomment to provide static XIQ credentials in the code)<br />
XIQ_token = ""<br />
XIQ_username = "name@contoso.com"<br />
XIQ_password = "P@$$w0rd"<br />

2) Lines 30 ~ 33 (uncomment to prompt the user to provide XIQ credentials)<br />
print ("Enter your XIQ login credentials ")<br />
XIQ_token = ""<br />
XIQ_username = input("Email: ")<br />
XIQ_password = getpass.getpass("Password: ")<br />

3) Lines 35 ~ 37 (uncomment to provide a token you generated from api.extremecloudiq.com)<br />
XIQ_token = "xxxxVeryLongStringOfCharactersxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"<br />
XIQ_username = ""<br />
XIQ_password = ""<br />

Use only one method above.  Use # character to comment out the unused code.

#### Lines 41 Enter access point hostnames
Multiple hostnames comma separated between ["xxxx","xxxx"], single hostname: ["xxxx"] without commas<br />
- apHostname = ["Site1-Prod-Mst","Site1-Lab-AP1","Site1-Lab-AP2"] <-- multiple devices<br />
- apHostname = ["Site1-Prod-Mst"] <-- single devices<br />

### Remove Rate Limit CLI
Simply go to XIQ and push a complete configuration update and it will wipe the CLI commands added by this script.  Assuming you have not implemented the S-CLI below in XIQ.  You can manually remove the commands via CLI:  
- no interface eth0 rate-limit multicast
- save config

### Supplemental CLI
If you choose to implement the multicast rate limits CLI using this script then you should add these commands to XIQ at either the Network Policy level or Device level via Supplemental CLI (S-CLI).
- interface eth0 rate-limit multicast 500
- interface eth0 rate-limit multicast enable
- save config
