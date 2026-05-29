"""Load a profile of known facts and match it to detected fields. Sensitive data is never matched."""
import json, re, unicodedata

SENSITIVE = ("sin", "nas", "social_insurance", "bank", "account", "card", "cvv", "routing")

# normalized field text -> profile key
SYNONYMS = {
    "full_name": "full_name", "name": "full_name", "nom": "full_name", "nom_complet": "full_name",
    "email": "email", "courriel": "email", "e_mail": "email",
    "address": "address", "adresse": "address",
    "postal_code": "postal_code", "code_postal": "postal_code", "zip": "postal_code",
    "phone": "phone", "telephone": "phone", "tel": "phone",
    "date_of_birth": "date_of_birth", "dob": "date_of_birth", "date_de_naissance": "date_of_birth",
    "employer": "employer", "employeur": "employer",
    "city": "city", "ville": "city",
}

def normalize(text):
    text = text.strip().rstrip(":").strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return text

def load_profile(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

def match_fields(fields, profile):
    values, unmatched = {}, []
    for f in fields:
        key_text = normalize(f.get("label") or f.get("id") or "")
        if any(s in key_text for s in SENSITIVE):
            unmatched.append(f["id"]); continue
        profile_key = SYNONYMS.get(key_text, key_text)
        if profile_key in profile and profile[profile_key]:
            values[f["id"]] = str(profile[profile_key])
        else:
            unmatched.append(f["id"])
    return values, unmatched
