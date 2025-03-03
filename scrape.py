import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://api3.rsna.org/radreport/v1"

def fetch_templates(specialty, limit=50):
    """Fetch templates for a given specialty."""
    url = f"{BASE_URL}/templates?specialty={specialty}&limit={limit}"
    response = requests.get(url)
    try:
        data = response.json()
        print(f"📄 Templates Response: {json.dumps(data, indent=2)}")  # DEBUG: Print Response
        return data.get("DATA", [])
    except Exception as e:
        print(f"❌ Error parsing template response: {e}")
        return []

def fetch_template_details(template_id):
    """Fetch detailed information for a specific template."""
    url = f"{BASE_URL}/templates/{template_id}/details"
    response = requests.get(url)
    try:
        details = response.json().get("DATA", {})
        print(f"📄 Template Details for ID {template_id}: {json.dumps(details, indent=2)}")  # DEBUG
        return details
    except Exception as e:
        print(f"❌ Error fetching template details: {e}")
        return {}

def scrape_radreport():
    # Fetch all specialties (subspecialties)
    specialties = requests.get(f"{BASE_URL}/subspecialty").json()

    # Ensure data is present
    if not specialties.get("SUCCESS") or "DATA" not in specialties:
        print("❌ Failed to fetch specialties.")
        return

    all_data = {}
    specialty_list = specialties["DATA"]

    # Only process the first three specialties
    for spec in specialty_list[:1]:
        code = spec["code"]
        name = spec["name"]

        print(f"📊 Fetching templates for: {name}")
        templates = fetch_templates(specialty=code, limit=50)

        all_data[name] = []

        for template in templates:
            # DEBUG: Print available keys to verify structure
            print(f"🔍 Template Keys: {template.keys()}")

            # Use "template_id" instead of "id"
            if "template_id" not in template:
                print(f"⚠️ Missing 'template_id' in template: {template}")
                continue

            template_id = template["template_id"]

            # Fetch the detailed template information
            details = fetch_template_details(template_id)
            time.sleep(1)  # Prevent rate limiting

            # Store the relevant details (only useful fields)
            all_data[name].append({
                "template_id": template_id,
                "template_version": template.get("template_version", ""),
                "title": template.get("title", ""),
                "description": details.get("description", ""),
                "author": details.get("author", ""),
                "co_author": details.get("co_author", ""),
                "institution": details.get("organization", ""),
                "language": template.get("lang", ""),
                "procedure_name": details.get("procedure", ""),
                "radlex_terms": details.get("radlex", []),
                "downloads": details.get("downloads", 0),
                "views": template.get("views", 0),
                "date_uploaded": template.get("created", ""),
                "report_content": details.get("template", ""),  # Full template content
                "radElement_CDEs": details.get("radElementCDEs", []),
                "translated_by": details.get("translatedBy", ""),
                "references": details.get("references", ""),
                "previous_versions": details.get("previousVersions", []),
            })

    # Save to JSON file
    with open("testreport.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    print("✅ Data successfully saved to testreport.json")

scrape_radreport()
