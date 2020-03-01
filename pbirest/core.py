import requests
import datetime

token = { "bearer": None, "expiration": None }
credentials = { "client_id": None, "username": None, "password": None, "tenant_id": None, "client_secret": None }

HTTP_OK = 200
HTTP_ACCEPTED = 202

def connect(client_id: str, username: str, password: str, tenant_id: str = "common", client_secret: str = None) -> None:
    global token
    global credentials

    if client_secret:
        body = {
            "grant_type": "password",
            "resource": "https://analysis.windows.net/powerbi/api",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password
        }
    else:
        body = {
            "grant_type": "password",
            "resource": "https://analysis.windows.net/powerbi/api",
            "client_id": client_id,
            "username": username,
            "password": password
        }

    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    response = requests.post("https://login.microsoftonline.com/{}/oauth2/token".format(tenant_id), headers = headers, data = body)

    if response.status_code == HTTP_OK:
        set_credentials(client_id, username, password, tenant_id, client_secret)
        set_token(response.json()["access_token"])
        print("SUCCESS: Connected to the Power BI REST API with {}".format(username))
    else:
        set_credentials(None, None, None, None, None)
        set_token(None)
        print("CODE {}: Something went wrong when trying to retrieve the token from the REST API".format(response.status_code))

def verify_token() -> bool:
    global token
    if token["bearer"] == None:
        print("ERROR: Please connect to the Power BI REST API with the connect() function before")
        return False
    else:
        if token["expiration"] < datetime.datetime.now():
            connect(credentials["client_id"], credentials["username"], credentials["password"], credentials["tenant_id"], credentials["client_secret"])
            return True
        else:
            return True

def get_token() -> dict:
    global token
    return token

def set_token(bearer: str) -> None:
    global token
    token["bearer"] = "Bearer {}".format(bearer)
    token["expiration"] = datetime.datetime.now() + datetime.timedelta(hours = 1)

def set_credentials(client_id: str, username: str, password: str, tenant_id: str, client_secret: str) -> None:
    global credentials
    credentials["client_id"] = client_id
    credentials["username"] = username
    credentials["password"] = password
    credentials["tenant_id"] = tenant_id
    credentials["client_secret"] = client_secret

# Workspace
def get_workspaces() -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups", headers = headers)

    if response.status_code == HTTP_OK:
        return response.json()["value"]
    else:
        print("CODE {}: Something went wrong when trying to retrieve the list of workspaces you have access".format(response.status_code))

def get_workspace(workspace_id: str) -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups", headers = headers)

    if response.status_code == HTTP_OK:
        ws = [result for result in response.json()["value"] if result["id"] == workspace_id]
        if(len(ws) > 0): return ws[0]
        else: return None
    else:
        print("CODE {}: Something went wrong when trying to retrieve the workspace {}".format(response.status_code, workspace_id))

def create_workspace(workspace_name: str, new: bool = False) -> dict:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    body = { "name": workspace_name }

    if new:
        response = requests.post("https://api.powerbi.com/v1.0/myorg/groups?workspaceV2=True", headers = headers, data = body)

        if response.status_code == HTTP_OK:
            result = response.json()
            return { "id": result["id"], "isOnDedicatedCapacity": result["isOnDedicatedCapacity"], "name": result["name"] }
        else:
            print("CODE {}: Something went wrong when trying to create a new workspace V2 called {}".format(response.status_code, name))
            return None
    else:
        response = requests.post("https://api.powerbi.com/v1.0/myorg/groups", headers = headers, data = body)

        if response.status_code == HTTP_OK:
            result = response.json()
            return { "id": result["id"], "isReadOnly": result["isReadOnly"], "isOnDedicatedCapacity": result["isOnDedicatedCapacity"], "name": result["name"] }
        else:
            print("CODE {}: Something went wrong when trying to create a new workspace called {}".format(response.status_code, name))
            return None

def delete_workspace(workspace_id: str) -> None:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.delete("https://api.powerbi.com/v1.0/myorg/groups/{}".format(workspace_id), headers = headers)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to delete the workspace {}".format(response.status_code, workspace_id))

def get_users_in_workspace(workspace_id: str) -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups/{}/users".format(workspace_id), headers = headers)

    if response.status_code == HTTP_OK:
        return response.json()["value"]
    else:
        print("CODE {}: Something went wrong when trying to retrieve the list of users in the workspace {}".format(response.status_code, workspace_id))

def add_user_to_workspace(workspace_id: str, email: str, access: str = "Member") -> None:
    global token
    if(not verify_token()): return None
    
    if(access in ["Admin", "Contributor", "Member"]):
        headers = { "Authorization": token["bearer"] }
        body = { "userEmailAddress": email, "groupUserAccessRight": access }
        response = requests.post("https://api.powerbi.com/v1.0/myorg/groups/{}/users".format(workspace_id), headers = headers, data = body)

        if response.status_code != HTTP_OK:
            print("CODE {}: Something went wrong when trying to add {} in the workspace {}".format(response.status_code, email, workspace_id))
    else:
        print("CODE 400: Please, make sure the access parameter is either \"Admin\", \"Contributor\" or \"Member\".")

def delete_user_from_workspace(workspace_id: str, email: str) -> None:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.delete("https://api.powerbi.com/v1.0/myorg/groups/{}/users/{}".format(workspace_id, email), headers = headers)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to delete the user {} from the workspace {}".format(response.status_code, email, workspace_id))

def update_user_in_workspace(workspace_id: str, email: str, access: str = "Member") -> None:
    global token
    if(not verify_token()): return None
    
    if(access in ["Admin", "Contributor", "Member"]):
        headers = { "Authorization": token["bearer"] }
        body = { "userEmailAddress": email, "groupUserAccessRight": access }
        response = requests.put("https://api.powerbi.com/v1.0/myorg/groups/{}/users".format(workspace_id), headers = headers, data = body)

        if response.status_code != HTTP_OK:
            print("CODE {}: Something went wrong when trying to update {} in the workspace {}".format(response.status_code, email, workspace_id))
    else:
        print("CODE 400: Please, make sure the access parameter is either \"Admin\", \"Contributor\" or \"Member\".")

# Report
def get_reports(workspace_id: str) -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups/{}/reports".format(workspace_id), headers = headers)

    if response.status_code == HTTP_OK:
        return response.json()["value"]
    else:
        print("CODE {}: Something went wrong when trying to retrieve the list of reports in the workspace {}".format(response.status_code, workspace_id))

def get_report(workspace_id: str, report_id: str) -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}".format(workspace_id, report_id), headers = headers)

    if response.status_code == HTTP_OK:
        return response.json()["value"]
    else:
        print("CODE {}: Something went wrong when trying to retrieve the report {} in the workspace {}".format(response.status_code, report_id, workspace_id))

def delete_report(workspace_id: str, report_id: str) -> None:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.delete("https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}".format(workspace_id, report_id), headers = headers)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to delete the report {} in the workspace {}".format(response.status_code, report_id, workspace_id))

def export_report(workspace_id: str, report_id: str, out_file: str) -> None:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}/export".format(workspace_id, report_id), headers = headers, )

    with open(out_file, "wb") as file:
        file.write(response.content)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to delete the report {} in the workspace {}".format(response.status_code, report_id, workspace_id))

def import_report(workspace_id: str, report_name: str, in_file: str, name_conflict: str = "CreateOrOverwrite") -> dict:
    global token
    if(not verify_token()): return None

    if(name_conflict in ["CreateOrOverwrite", "GenerateUniqueName", "Ignore", "Overwrite"]):
        headers = { "Authorization": token["bearer"], "Content-Type": "multipart/form-data" }
        file = { "file": open(in_file, "rb") }
        response = requests.post("https://api.powerbi.com/v1.0/myorg/groups/{}/imports?datasetDisplayName={}&nameConflict={}".format(workspace_id, report_name, name_conflict), headers = headers, files = file)

        if response.status_code == HTTP_ACCEPTED:
            return response.json()
        else:
            print("CODE {}: Something went wrong when trying to import the report {} in the workspace {}".format(response.status_code, in_file, workspace_id))
    else:
        print("CODE 400: Please, make sure the name_conflict parameter is either \"CreateOrOverwrite\", \"GenerateUniqueName\", \"Ignore\" or \"Overwrite\".")

def clone_report(workspace_id: str, report_id: str, dest_report_name: str, dest_workspace_id: str = None) -> None:
    global token
    if(not verify_token()): return None
    
    headers = { "Authorization": token["bearer"] }
    if dest_workspace_id: body = { "name": dest_report_name, "targetWorkspaceId": dest_workspace_id }
    else: body = { "name": dest_report_name }

    response = requests.post("https://api.powerbi.com/v1.0/myorg/groups/{}/reports/{}/clone".format(workspace_id, report_id), headers = headers, data = body)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to clone the report {} in the workspace {}".format(response.status_code, report_id, workspace_id))

# Dataset
def get_datasets(workspace_id: str) -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups/{}/datasets".format(workspace_id), headers = headers)

    if response.status_code == HTTP_OK:
        return response.json()["value"]
    else:
        print("CODE {}: Something went wrong when trying to retrieve the list of datasets in the workspace {}".format(response.status_code, workspace_id))

def get_dataset(workspace_id: str, dataset_id: str) -> list:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.get("https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id), headers = headers)

    if response.status_code == HTTP_OK:
        return response.json()["value"]
    else:
        print("CODE {}: Something went wrong when trying to retrieve the dataset {} in the workspace {}".format(response.status_code, dataset_id, workspace_id))

def delete_dataset(workspace_id: str, dataset_id: str) -> None:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    response = requests.delete("https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id), headers = headers)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to delete the dataset {} in the workspace {}".format(response.status_code, dataset_id, workspace_id))

def refresh_dataset(workspace_id: str, dataset_id: str, notify_option: str = "NoNotification") -> None:
    global token
    if(not verify_token()): return None

    headers = { "Authorization": token["bearer"] }
    body = { "notifyOption": notify_option }
    response = requests.post("https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshes".format(workspace_id, dataset_id), headers = headers, data = body)

    if response.status_code != HTTP_OK:
        print("CODE {}: Something went wrong when trying to refresh the dataset {} in the workspace {}".format(response.status_code, dataset_id, workspace_id))
