import requests
import time
import psycopg2
import os

DB_URL = os.environ.get('DATABASE_URL')

def save_to_db(price):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO crypto_prices (coin_name, price_usd) VALUES (%s, %s)",
            ('bitcoin', price)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"Successfully saved to Neon Cloud: ${price}")
    except Exception as e:
        print(f"Database Error: {e}")

def fetch_crypto_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        price = response.json()['bitcoin']['usd']
        print(f"Current Bitcoin Price: ${price}")
        save_to_db(price)
    except Exception as e:
        print(f"Fetch Error: {e}")

if __name__ == "__main__":
    print("Starting the Sentinel Cloud-Native Pipeline...")
    fetch_crypto_price()