"""
    HELPER FUNCTIONS TO CALL ON WHEN NEEDED
"""
import re
from decimal import Decimal

# Convert for ratings text -> five is the necessary limit since rating never exceeds this value
words_to_int = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def text2number(text: str) -> int:
    return words_to_int[text.capitalize()]


# Convert price unicode string to GPB / integer based money -> readable
def parse_price(price: str) -> float:
    amount = price.replace("\u00a3", "").replace("£", "")
    amount = amount.replace("u00a3", "").replace(",", "")
    return float(amount)


    
