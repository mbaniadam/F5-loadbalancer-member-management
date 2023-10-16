import sys
import os
import requests
import csv
import json
import urllib3
import getpass

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
path = os.getcwd()
print(path)

def get_members(pool_name):
    endpoint_url = f"{F5_HOST}/mgmt/tm/ltm/pool/~{PARTITION}~{pool_name}/members/"
    response = session.get(endpoint_url)
    if response.status_code == 200:
        members = response.json()['items']
        return members
    else:
        print(f"Failed to retrieve {pool_name} members!")


def manage_member(member_name, pool_name, action, force_offline):
    # Construct endpoint URL
    endpoint_url = f"{F5_HOST}/mgmt/tm/ltm/pool/~{PARTITION}~{pool_name}/members/~{PARTITION}~{member_name}"
    # Fetch current state of member
    current_response = session.get(endpoint_url)
    if current_response.status_code != 200:
        print(f"Failed to retrieve current state for member {member_name}. Skipping.")
        return
    current_data = current_response.json()
    if current_data.get("session") == "monitor-enabled" and current_data.get("state") == "up":
        current_data.update({"session":"user-enabled","state": "user-up"})
    elif current_data.get("state") == "up":
        current_data.update({"state": "user-up"})
    elif current_data.get("state") == "down":
        current_data.update({"state": "user-down"})
    current_session = current_data.get("session")
    current_state = current_data.get("state")
    # Determine desired state
    desired_data = {}
    # Data based on action
    if action == "enable":
        desired_data  = {
            "session": "user-enabled",
            "state": "user-up"
        }
    elif action == "disable":
        desired_data  = {
            "session": "user-disabled",
        }
        if force_offline == "yes":
            desired_data.update({"state":"user-down"})
    else:
        print(f"Invalid action for member {member_name}. Skipping.")
        return

    # Compare desired and current state
    if current_session == desired_data.get("session") and current_state == desired_data.get("state"):
        print(f"Member {member_name} already in desired state. Skipping.")
        return
    elif current_session == desired_data.get("session") and current_state != desired_data.get("state"):
        if current_state != "user-up" and force_offline == "yes":
            print(f"Member {member_name} state is down. No need to force offline. Skipping.")
            return
        elif current_state == "user-up" and force_offline == "no":
            print(f"Member {member_name} state is up and force offline flag is set to no. Skipping.")
            return
        elif current_state == "user-up" and force_offline == "yes":
            print(f"Member {member_name} state is up. Would you like member forces to be offline?.")
            choice = input("Y/n: ").strip().lower()
            if choice != "y":
                print("Skipping.")
                return 

    # Send the request
    response = session.put(endpoint_url, data=json.dumps(desired_data))
    if response.status_code == 200:
        print(
            f"Action '{action}' applied to member {member_name} in pool {pool_name}.")
    else:
        print(
            f"Failed to manage member {member_name}. Status code: {response.status_code}")


def main():
    try:
        # Read CSV file
        with open('members.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pool_members = get_members(row['pool_name'])
                if pool_members and any(member['name'] == row["member_name"] for member in pool_members):
                    manage_member(
                        row["member_name"], row['pool_name'], row['action'], row['force_offline'])

    except FileNotFoundError:
        print("Error: File 'members.csv' not found!")
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
if __name__ == "__main__":
    # Constants
    HTTPS_HOST = 'https://'
    F5_HOST = input("Enter IP address of F5 Host: ")
    F5_HOST = HTTPS_HOST+F5_HOST
    PARTITION = input("Enter partition name: ")
    USERNAME = input("Enter Username: ")
    PASSWORD = getpass.getpass("Enter Password: ")
    # Disable SSL warnings
    urllib3.disable_warnings()
    # Authenticate with the F5
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.verify = False
    session.headers.update({'Content-Type': 'application/json'})
    print("""
    ==================================================
    Welcome to the F5 Load Balancer Member Management
    ==================================================
    
    This script allows you to manage members of F5 load balancer pools based on input from 'members.csv'.
    
    Instructions:
    1. Ensure the 'members.csv' file is in the same directory as this script.
    2. The CSV should have columns: member_name,pool_name,action,force_offline flag.
    3. Run the script and provide F5 Host details when prompted.
    4. The script will read the CSV and apply the specified actions to the members.
    
    Let's get started!
    """)
    main()
