# F5 Load Balancer Member Management Script
Manage members of F5 load balancer pools using a CSV input.

### Description
This script offers an automated approach to manage the state (enable/disable) of members in F5 load balancer pools. It reads a members.csv file for instructions and applies the desired state to the specified members.

### Features
- Enable or disable members.
- Force members offline.
- Display real-time action feedback.

### Prerequisites
Python 3.x
Required Python packages: requests, csv, json, urllib3, os, sys, getpass


### Usage
**1- Prepare your members.csv with the following columns:**

pool_name: Name of the pool in the F5 load balancer.
member_name: Name of the member in the pool.
action: Desired action (enable/disable).
force_offline: Force the member offline (yes/no).


**2- Run the script:**
``` console
python f5_members.py
```

### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
