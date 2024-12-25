import csv
from datetime import datetime
from playwright.sync_api import sync_playwright
from alive_progress import alive_bar  
from colorama import init, Fore  
import time  
import sys

init(autoreset=True)

def format_timestamp(timestamp_text):
    try:
        # Mengonversi timestamp ISO 8601 ke objek datetime
        timestamp_obj = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
        
        # Mengubah format ke 'tanggal-bulan-tahun jam:menit:detik'
        formatted_timestamp = timestamp_obj.strftime("%d-%m-%Y %H:%M:%S")
        return formatted_timestamp
    except Exception as e:
        return "[!] Forwmat waktu salah"

def scrape_tweets_with_auth(tweet_url, auth_token, max_replies=10, output_file="replies.csv"):
    with sync_playwright() as p:
        # Inisialisasi browser dan halaman
        browser = p.chromium.launch(headless=True)  # Set headless=True untuk menjalankan di background
        page = browser.new_page()

        # Menambahkan cookie auth token
        print(Fore.YELLOW + "[+] Menambahkan cookie auth token")
        page.context.add_cookies([{
            'name': 'auth_token',
            'value': auth_token,
            'domain': '.x.com',  
            'path': '/',
            'httpOnly': True,
            'secure': True
        }])

        # Akses halaman tweet
        print(f"[+] Mengakses tweet URL		: {tweet_url}")
        page.goto(tweet_url)
        
        # Variabel untuk menghitung jumlah tweet yang diambil
        replies_scraped = 0
        replies = []
        seen_urls = set()  # Set untuk menyimpan URL yang sudah diambil
        first_tweet_skipped = False  # Untuk melewati tweet pertama

        # Inisialisasi animasi progress bar menggunakan alive_bar
        with alive_bar(max_replies, title="[+] Proses mengambil replies	:", force_tty=True) as bar:
            while replies_scraped < max_replies:
                # Mencari semua tweet pada halaman
                tweets = page.query_selector_all("article")
                
                for tweet in tweets:
                    # Abaikan tweet pertama
                    if not first_tweet_skipped:
                        first_tweet_skipped = True
                        continue
                    
                    if replies_scraped >= max_replies:
                        break  # Berhenti jika jumlah reply yang diambil sudah sesuai

                    # Ambil display name
                    display_name = tweet.query_selector("div[dir='ltr'] span")
                    display_name_text = display_name.inner_text() if display_name else "Display name not found"

                    # Ambil username
                    username = tweet.query_selector("div.css-175oi2r a")
                    username_text = username.get_attribute("href").split("/")[1] if username else "Username not found"

                    # Ambil timestamp
                    timestamp = tweet.query_selector("time")
                    formatted_timestamp = format_timestamp(timestamp.get_attribute("datetime")) if timestamp else "Timestamp not found"

                    # Ambil teks tweet
                    tweet_text = tweet.query_selector("div[lang]")
                    tweet_text_content = tweet_text.inner_text() if tweet_text else "Tweet text not found"
                    
                    # Ambil URL tweet dan tambahkan "https://x.com"
                    tweet_url_element = tweet.query_selector("div.css-175oi2r.r-18u37iz.r-1q142lx a")
                    tweet_url_text = "https://x.com" + tweet_url_element.get_attribute("href") if tweet_url_element else "URL not found"

                    # Filter untuk mengecek apakah URL tweet sudah ada di set atau sama dengan URL utama
                    if tweet_url_text in seen_urls or tweet_url_text == tweet_url:
                        continue  # Abaikan jika duplikat

                    # Tambahkan URL ke dalam set
                    seen_urls.add(tweet_url_text)

                    # Menambahkan data tweet ke dalam daftar replies
                    replies.append({
                        "display_name": display_name_text,
                        "username": username_text,
                        "timestamp": formatted_timestamp,
                        "tweet_text": tweet_text_content,
                        "tweet_url": tweet_url_text
                    })

                    # Meningkatkan jumlah reply yang diambil
                    replies_scraped += 1

                    # Update progress bar
                    bar()

                # Scroll untuk memuat lebih banyak tweet jika belum cukup
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                # Menambahkan animasi loading
                time.sleep(3)  # Tunggu 3 detik untuk memuat lebih banyak tweet
        
        # Menyimpan data ke dalam file CSV
        print(Fore.YELLOW + f"[+] Proses menyimpan data ")
        with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["display_name", "username", "timestamp", "tweet_text", "tweet_url"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Menulis header ke file CSV
            writer.writeheader()

            # Menulis setiap reply ke dalam CSV
            for reply in replies:
                writer.writerow(reply)

        print(Fore.GREEN + f"[✔] Data berhasil disimpan di {output_file}")

        # Tutup browser
        browser.close()

# Input URL tweet
tweet_url = input("[+] Masukkan URL twitt		: ")
auth_token = ""  # Ganti dengan token yang valid

# Ambil input jumlah replies dari pengguna
max_replies = int(input("[+] Masukan jumlah scraping 	: "))

# Jalankan fungsi untuk mengambil replies dan menyimpan ke file CSV
scrape_tweets_with_auth(tweet_url, auth_token, max_replies)
