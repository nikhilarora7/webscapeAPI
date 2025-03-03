import os
import json
import requests

# Load the JSON file containing all template information
with open("radreport_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create the output directory "templates" if it doesn't exist
output_dir = "templates"
os.makedirs(output_dir, exist_ok=True)

# API endpoint (corrected URL)
api_url = "https://api3.rsna.org/document/v1/download/html/rad/rad-report"

# Headers to mimic the successful Postman request
headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.28.4",
    "Accept": "*/*",
    "Origin": "https://radreport.org",
    "Referer": "https://radreport.org/"
}

total = 0
failed = 0

# Iterate through each category and then each template
for category, templates in data.items():
    for template in templates:
        total += 1
        # Get the template id and template version
        template_id = template.get("template_id")
        template_version = template.get("template_version")
        if not template_id or not template_version:
            print(f"Skipping a template in {category} due to missing id/version.")
            continue

        # Build the payload using the template version (as required by the API)
        payload = {
            "templates": [template_version],
            "format": "html"
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            # Check if we got a non-empty response
            if response.status_code == 200 and response.text.strip():
                file_name = f"{template_id}.html"
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, "w", encoding="utf-8") as out_file:
                    out_file.write(response.text)
                print(f"Saved template {template_id} to {file_path}")
            else:
                print(f"Template {template_id} (version {template_version}) failed: "
                      f"status {response.status_code}, notfound: {response.headers.get('notfound', 'N/A')}")
                failed += 1
        except Exception as e:
            print(f"Exception processing template {template_id}: {e}")
            failed += 1

print(f"\nFinished processing {total} templates with {failed} failures.")
