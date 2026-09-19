import requests
import os
import pandas as pd
from dotenv import load_dotenv

print("Extracting Hearthstone cards...")


def extract_hearthstone_cards():

    load_dotenv()

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

    # Fetch all Hearthstone cards
    all_cards = []
    page = 1

    cards_url = "https://us.api.blizzard.com/hearthstone/cards"

    while True:

        response = requests.get(
            cards_url,
            headers=headers,
            params={
                "locale": "en_US",
                "pageSize": 100,
                "page": page
            }
        )

        response.raise_for_status()

        data = response.json()

        cards = data.get("cards", [])

        if not cards:
            break

        all_cards.extend(cards)

        print(
            f"Page {page} fetched — "
            f"{len(all_cards)} cards total"
        )

        if page >= data["pageCount"]:
            break

        page += 1

    hearthstone_df = pd.DataFrame(all_cards)

    # Get folder where this Python file is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    output_path = os.path.join(
        script_dir,
        "..",
        "bronze_hearthstone_data",
        "raw_hearthstone_cards.csv"

    )
    
    hearthstone_df.to_csv(output_path, index=False)

    print(f"Raw HearthstoneData saved to {output_path}")

    return hearthstone_df


