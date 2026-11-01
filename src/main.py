from extract import extract_hearthstone_cards, extract_hearthstone_metadata
from transformation import transform_hearthstone_cards

def main (): 
    extract_hearthstone_cards()
    extract_hearthstone_metadata()
    transform_hearthstone_cards()

if __name__ == "__main__":
    main()
