
import requests

def create_bitrix_lead(full_name, email=None, phone=None, message=None, agent_bitrix_id=None,  property_name=None, property_url=None,):
    """
    Creates a lead in Bitrix24 CRM.
    """
    # CONFIGURATION
    bitrix24_address = "https://iig.bitrix24.com/"
    user_id = "46"
    webhook = "u9x3l5wnzdgcwblo"
    url = f"{bitrix24_address}/rest/{user_id}/{webhook}/crm.lead.add"

    # Parse name
    name_parts = full_name.split() if full_name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[-1] if len(name_parts) > 1 else ''
    
    if agent_bitrix_id:
        try:
            agent_bitrix_id = int(agent_bitrix_id.strip())
        except:
            agent_bitrix_id = ''
            

    payload = {
        "fields": {
            "TITLE": f"Lead: {full_name} - {property_name or 'No Property'}",
            "NAME": first_name,
            "LAST_NAME": last_name,
            "STATUS_ID": "NEW",
            "OPENED": "Y",
            "ASSIGNED_BY_ID":agent_bitrix_id,
            "CURRENCY_ID": "USD",
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}] if phone else [],
            "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}] if email else [],
            "WEB": [{"VALUE": property_url, "VALUE_TYPE": "WORK"}] if property_url else [],
            "COMMENTS": f"Message: {message or 'N/A'}\nProperty: {property_name or 'N/A'}\nURL: {property_url or 'N/A'}"
        },
        "params": {
            "REGISTER_SONET_EVENT": "Y"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return {
            "success": True,
            "response": response.json()
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def notify_hr_via_chat(full_name, phone, email, job_title, resume_file, cover_letter, job_link=None):
    message = f"""
            📥 New Job Application Received!
            👤 {full_name}
            📧 Email: {email}
            📞 Phone: {phone}
            💼 Position: {job_title}
            """

    # If job_link is provided, add it to the message
    if job_link:
        message += f"\n🔗 Job Details: {job_link}"

    # If cover_letter is provided, include it in the message
    if cover_letter:
        message += f"\n✉️ Cover Letter: {cover_letter}"

    # HR user ID or Chat ID (adjust this part if necessary)
    chat_id = "chat636"  # Replace with actual chat ID for group chat if needed

    webhook_base = "https://iig.bitrix24.com/rest/46/bcurdp71khwmrd52"

    # Step 1: Upload resume file to Bitrix24 Disk if resume_file is provided
    file_id = None
    if resume_file:
        file_upload_url = f"{webhook_base}/disk.folder.uploadfile"
        upload_payload = {
            "id": 1,  # Folder ID (default "root" folder here)
        }

        upload_files = {
            "file": (resume_file.name, resume_file)
        }

        try:
            upload_response = requests.post(file_upload_url, data=upload_payload, files=upload_files)
            upload_response.raise_for_status()
            file_result = upload_response.json()

            file_id = file_result.get("result", {}).get("ID")
            if not file_id:
                print("Failed to get file ID from upload response.")
            else:
                # Attach file to the message
                message += f"\n📎 Resume: {resume_file.name}"

        except requests.RequestException as e:
            print(f"Failed to upload resume to Bitrix24: {e}")

    # Step 2: Send chat message with job details, resume file, and cover letter
    chat_webhook_url = f"{webhook_base}/im.message.add"
    chat_payload = {
        "DIALOG_ID": chat_id,  # The ID of the chat (can be a user ID or chat ID)
        "MESSAGE": message,
        "SYSTEM": "N",  # Regular message
        "URL_PREVIEW": "Y",  # Automatically convert links to rich links
    }

    # Add file attachment if available
    if file_id:
        chat_payload["ATTACH"] = [
            {
                "BLOCKS": [
                    {
                        "FILE": {
                            "ID": file_id  # Attach the uploaded file to the chat
                        }
                    }
                ]
            }
        ]

    try:
        chat_response = requests.post(chat_webhook_url, json=chat_payload)
        chat_response.raise_for_status()
        print("HR has been notified!")
    except requests.RequestException as e:
        print(f"Failed to send HR message: {e}")
        



def create_bitrix_base_lead(full_name, email=None, phone=None, branch=None, contact_way=None):
    """
    Creates a lead in Bitrix24 CRM for a call request form submission.
    """
    # CONFIGURATION
    bitrix24_address = "https://iig.bitrix24.com/"
    user_id = "46"
    webhook = "u9x3l5wnzdgcwblo"
    url = f"{bitrix24_address}/rest/{user_id}/{webhook}/crm.lead.add"

    # Parse name
    name_parts = full_name.split() if full_name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[-1] if len(name_parts) > 1 else ''
    
    # Construct the message for Bitrix
    lead_message = f"Branch: {branch or 'N/A'}\nPreferred Contact Method: {contact_way or 'N/A'}"

    # Prepare the payload for Bitrix
    payload = {
        "fields": {
            "TITLE": f"Lead: {full_name} - {branch or 'No Branch'}",
            "NAME": first_name,
            "LAST_NAME": last_name,
            "STATUS_ID": "NEW",
            "OPENED": "Y",
            "CURRENCY_ID": "USD",
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}] if phone else [],
            "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}] if email else [],
            "COMMENTS": lead_message
        },
        "params": {
            "REGISTER_SONET_EVENT": "Y"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        # Send the request to Bitrix24 API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for bad responses (4xx or 5xx)
        return {
            "success": True,
            "response": response.json()
        }
    except requests.RequestException as e:
        # Handle any errors that occur during the API request
        return {
            "success": False,
            "error": str(e)
        }

