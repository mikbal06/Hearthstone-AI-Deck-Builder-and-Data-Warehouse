from email.mime import text

import pandas as pd
import requests
import re
from dotenv import load_dotenv
import os 

load_dotenv()
file_path = '../bronze_hearthstone_data/raw_hearthstone_cards.csv' 
hearthstone_df = pd.read_csv(file_path)

def map_hearthstone_cards(hearthstone_df):

    
    client_id = os.getenv("BLIZZARD_CLIENT_ID")
    client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")
    
    # Get access token
    token_response = requests.post(
            "https://oauth.battle.net/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret)
        )
    
    token_response.raise_for_status()
    
    access_token = token_response.json()["access_token"]
    
    print("Token received.")
    
    headers = {
            "Authorization": f"Bearer {access_token}"
        }

    metadata_response = requests.get(
    "https://us.api.blizzard.com/hearthstone/metadata",
    headers=headers,
    params={"locale": "en_US"}
)
    metadata = metadata_response.json()

    #Using metadata api to map ids to names for easier reading
    class_map = {c["id"]: c["slug"] for c in metadata["classes"]}

    hearthstone_df["className"] = hearthstone_df["classId"].map(class_map)
    set_map = {s["id"]: s["slug"] for s in metadata["sets"]}
    spell_school_map = {s["id"]: s["slug"] for s in metadata["spellSchools"]}
    class_map = {c["id"]: c["slug"] for c in metadata["classes"]}

    hearthstone_df["className"] = hearthstone_df["classId"].map(class_map)
    hearthstone_df["setName"] = hearthstone_df["cardSetId"].map(set_map)
    hearthstone_df["spellSchoolName"] = hearthstone_df["spellSchoolId"].map(spell_school_map)

    minion_type_map = {m["id"]: m["slug"] for m in metadata["minionTypes"]}
    rarity_map = {r["id"]: r["slug"] for r in metadata["rarities"]}
    card_type_map = {t["id"]: t["slug"] for t in metadata["types"]}
    hearthstone_df["minionTypeName"] = hearthstone_df["minionTypeId"].map(minion_type_map)
    hearthstone_df["rarityName"] = hearthstone_df["rarityId"].map(rarity_map)
    hearthstone_df["cardTypeName"] = hearthstone_df["cardTypeId"].map(card_type_map)


    hearthstone_df["multiClassNames"] = hearthstone_df["multiClassIds"].apply(
        lambda ids: [class_map.get(i) for i in ids] if isinstance(ids, list) else [] )

    keyword_map = {k["id"]: k["name"] for k in metadata["keywords"]}
    hearthstone_df["keywordNames"] = hearthstone_df["keywordIds"].apply(
        lambda ids: [keyword_map.get(i) for i in ids] if isinstance(ids, list) else []
    )
    return hearthstone_df 


def clean_hearthstone_cards(hearthstone_df):
    columns = [
    # Card identity
    'id', 'name', 'collectible',
    
    # Class
    'classId', 'className', 'multiClassIds', 'multiClassNames',
    
    # Card type & set
    'cardTypeId', 'cardTypeName', 'cardSetId', 'setName', 'rarityId', 'rarityName',
    
    # Stats
    'manaCost', 'attack', 'health', 'armor',
    
    # Minion details
    'minionTypeId', 'minionTypeName', 'keywordIds', 'keywordNames',
    
    # Spell details
    'spellSchoolId', 'spellSchoolName',
    
    # Card text/image
    'text', 'image'
]
    silver_df = hearthstone_df[columns].copy()
    # Handle null values 
    silver_df['attack'] = silver_df['attack'].fillna(0)
    silver_df['health'] = silver_df['health'].fillna(0) 
    silver_df['armor'] = silver_df['armor'].fillna(0)
    silver_df['manaCost'] = silver_df['manaCost'].fillna(0)
    silver_df["spellSchoolName"] = silver_df["spellSchoolName"].fillna("none")
    silver_df["minionTypeName"] = silver_df["minionTypeName"].fillna("none")
    silver_df["text"] = silver_df["text"].fillna("")
    silver_df['setName'] = silver_df['setName'].fillna('classic')
    silver_df["multiClassNames"] = silver_df["multiClassNames"].apply(lambda x: x if isinstance(x, list) else [])

    def clean_text(text):
        if not isinstance(text, str):
            return ""
        return re.sub(r"<.*?>", "", text).strip()

    silver_df["text"] = silver_df["text"].apply(clean_text)
    return silver_df

mapped_hearthstone_df = map_hearthstone_cards(hearthstone_df) 
cleaned_hearthstone_df = clean_hearthstone_cards(mapped_hearthstone_df)
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(
        script_dir,
        "..",
        "silver_hearthstone_data",
        "silver_hearthstone_cards.csv"
    )
cleaned_hearthstone_df.to_csv(output_path, index=False)
print(f"Cleaned Hearthstone Data saved to {output_path}")
