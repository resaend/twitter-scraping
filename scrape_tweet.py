import csv
import time
from datetime import datetime
import re  # replace karakter khusus
from unidecode import unidecode
from tqdm import tqdm  # progress bar
from playwright.sync_api import sync_playwright, TimeoutError
from colorama import Fore, Style, init  # pewarnaan teks
import urllib.parse  # untuk URL encoding

init(autoreset=True)

def scrape_tweet(auth_token: str, search_term: str, max_tweets: int, year: int, is_hashtag: bool) -> list:
    tweets_data = []
    tweets_scraped = 0  # Jumlah tweet yang telah diambil
    seen_tweet_ids = set()  # Set untuk melacak ID tweet yang sudah diambil

    # Membuat URL query tahun pencarian
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    # Jika mencari dengan hashtag
    if is_hashtag:
        search_url = f"https://x.com/search?q=%23{search_term}%20until%3A{end_date}%20since%3A{start_date}&src=typed_query"
    else:
        # Jika mencari dengan keyword, ubah spasi menjadi %20 dan encode karakter lainnya
        search_term_encoded = urllib.parse.quote(search_term)  # Menggunakan urllib untuk encode
        search_url = f"https://x.com/search?q={search_term_encoded}%20until%3A{end_date}%20since%3A{start_date}&src=typed_query"

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            if "search" in response.url:  # Menyaring hanya panggilan API pencarian
                try:
                    # Mengambil data JSON dari respons
                    response_json = response.json()
                    
                    # Mengambil tweet dari respons JSON
                    if 'globalObjects' in response_json:
                        tweets = response_json['globalObjects']['tweets']
                        for tweet_id, tweet_data in tweets.items():
                            # Cek apakah tweet sudah ada berdasarkan tweet_id
                            if tweet_id in seen_tweet_ids:
                                continue  # Lewati tweet yang sudah ada

                            # Tambahkan tweet_id ke set untuk mencegah duplikasi
                            seen_tweet_ids.add(tweet_id)

                            # Mengambil username
                            username = tweet_data['user']['screen_name']
                            sanitized_username = unidecode(username)  # Menormalkan karakter khusus
                            

                            # Hapus karakter selain huruf, angka, dan underscore
                            sanitized_username = re.sub(r'[^a-zA-Z0-9_]', '', sanitized_username)

                            # Membuat URL tweet dengan username dan tweet_id yang benar
                            tweet_url = f"https://x.com/{sanitized_username}/status/{tweet_id}"

                            # Format timestamp
                            timestamp = tweet_data['created_at']
                            timestamp_obj = datetime.strptime(timestamp, '%a %b %d %H:%M:%S +0000 %Y')
                            formatted_timestamp = timestamp_obj.strftime('%d-%m-%Y %H:%M:%S')

                            tweets_data.append({
                                'username': sanitized_username,
                                'timestamp': formatted_timestamp,
                                'tweet_text': tweet_data['full_text'],
                                'tweet_url': tweet_url
                            })
                except Exception as e:
                    print(f"{Fore.RED}[!] Gagal parsing respon: {e}")

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(headless=True)  # Menjalankan dalam mode headless
        except Exception as e:
            print(f"{Fore.RED}[!] Gagal menjalankan browser: {e}")
            return tweets_data
        
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        
        # Menambahkan cookie otentikasi dari Twitter
        try:
            context.add_cookies([{
                'name': 'auth_token',
                'value': auth_token,
                'domain': '.x.com',
                'path': '/',
                'httpOnly': True,
                'secure': True,
                'sameSite': 'None'
            }])
        except Exception as e:
            print(f"{Fore.RED}[!] Gagal menambahkan cookies: {e}")
            browser.close()
            return tweets_data
        
        page = context.new_page()

        # Mengaktifkan intersepsi permintaan latar belakang
        page.on("response", intercept_response)

        try:
            # Buka ke halaman hasil pencarian
            page.goto(search_url)
            page.wait_for_selector("article", timeout=30000)  # Tunggu hingga tweet dimuat, dengan timeout 30 detik
        except TimeoutError:
            print(f"{Fore.RED}[!] Tidak ada tweet untuk '{search_term}' di tahun {year} yang tersedia.")
            browser.close()
            return tweets_data
        except Exception as e:
            print(f"{Fore.RED}[!] Error navigasi ke link tweet: {e}")
            browser.close()
            return tweets_data

        # Scroll untuk memuat tweet lebih banyak (untuk memuat tweet tambahan)
        print(f"{Fore.YELLOW}[+] Proses scraping tweet")
        with tqdm(total=max_tweets, desc="[+] Mengambil tweet		", unit="tweet") as pbar:
            while tweets_scraped < max_tweets:
                try:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)

                    # Mengambil detail tweet
                    tweets = page.query_selector_all("article")
                    for tweet in tweets:
                        if tweets_scraped >= max_tweets:
                            break  # Berhenti jika jumlah tweet yang diambil sudah sesuai

                        # Mengambil display name (sebelumnya salah digunakan untuk username)
                        display_name = tweet.query_selector("div[dir='ltr'] span")
                        
                        # Mengambil username yang benar
                        username = tweet.query_selector("div.css-175oi2r a")
                        if username:
                            username_text = username.get_attribute("href").split("/")[1]  # Ambil username dari URL
                        else:
                            username_text = "[!] Username tidak ditemukan"

                        timestamp = tweet.query_selector("time")
                        tweet_text = tweet.query_selector("div[lang]")

                        # Memeriksa apakah ada elemen yang None
                        if username and timestamp and tweet_text:
                            username_text = unidecode(username_text)
                            tweet_text_content = unidecode(tweet_text.text_content().strip())

                            # Hapus karakter selain huruf, angka, dan underscore
                            username_text = re.sub(r'[^a-zA-Z0-9_]', '', username_text)

                            # Format timestamp (jika timestamp tersedia)
                            if timestamp:
                                timestamp_text = timestamp.get_attribute('datetime')
                                timestamp_obj = datetime.strptime(timestamp_text, '%Y-%m-%dT%H:%M:%S.%fZ')
                                formatted_timestamp = timestamp_obj.strftime('%d-%m-%Y %H:%M:%S')
                            else:
                                formatted_timestamp = 'N/A'

                            # Mendapatkan tweet ID langsung dari atribut data tweet jika tersedia
                            tweet_id = tweet.get_attribute('data-tweet-id')
                            if not tweet_id:  # Jika data-tweet-id hilang, coba menggunakan pendekatan lain
                                tweet_id = tweet.query_selector("a[href*='/status/']").get_attribute("href").split('/')[-1]

                            # Cek apakah tweet sudah ada berdasarkan tweet_id
                            if tweet_id in seen_tweet_ids:
                                continue  # Lewati tweet yang sudah ada

                            # Tambahkan tweet_id ke set untuk mencegah duplikasi
                            seen_tweet_ids.add(tweet_id)

                            tweet_url = f"https://x.com/{username_text.replace(' ', '').replace('₿', 'B').replace('Ō', 'O')}/status/{tweet_id}"

                            tweets_data.append({
                                'username': username_text,
                                'timestamp': formatted_timestamp,
                                'tweet_text': tweet_text_content,
                                'tweet_url': tweet_url
                            })
                            tweets_scraped += 1
                            pbar.update(1)  # Update progress bar

                        else:
                            print(f"{Fore.RED}[!] Data tweet tidak lengkap, melewati tweet ini")
                except Exception as e:
                    print(f"{Fore.RED}[!] Error ketika scraping tweet: {e}")

        browser.close()

    return tweets_data


def write_tweets_to_csv(tweets_data: list, filename: str):
    """Menulis data tweet yang telah diambil ke dalam file CSV"""
    try:
        headers = ['username', 'timestamp', 'tweet_text', 'tweet_url']

        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)

            # Jika file kosong, tulis baris header
            if file.tell() == 0:
                writer.writeheader()

            # Menulis data tweet satu per satu
            for tweet in tweets_data:
                writer.writerow(tweet)
    except Exception as e:
        print(f"{Fore.RED}[!] Gagal menulis data ke CSV: {e}")


if __name__ == "__main__":
    auth_token = ""  # Masukkan token authentikasi twitter disini
    try:
        print(f"----- Pilih jenis pencarian -----")
        print("|     1. Cari dengan hashtag    |")
        print("|     2. Cari dengan keyword    |")
        print("---------------------------------")
        choice = input(f"[+] Masukkan pilihan (1/2)	: ").strip()

        if choice == "1":
            search_term = input(f"[+] Masukkan hashtag (tanpa #)	: ").strip()
            is_hashtag = True
        elif choice == "2":
            search_term = input(f"[+] Masukkan keyword		: ").strip()
            is_hashtag = False
        else:
            print(f"{Fore.RED}[!] Pilihan tidak valid! pilih '1' atau '2'")
            exit(1)

        max_tweets = int(input(f"[+] Masukkan total scrape	: ").strip())
        year = int(input(f"[+] Masukkan tahun tweet	: ").strip())  # Input tahun tweet
        tweets_data = scrape_tweet(auth_token, search_term, max_tweets, year, is_hashtag)

        if not tweets_data:
            print(f"{Fore.RED}[!] Tidak ada tweet yang berhasil diambil.")
        else:
            write_tweets_to_csv(tweets_data, f"{search_term}_tweets_{year}.csv")
            print(f"{Fore.GREEN}[✔] Berhasil mengambil {len(tweets_data)} tweet untuk '{search_term}' dari tahun {year} dan disimpan ke {search_term}_tweets_{year}.csv")

    except Exception as e:
        print(f"{Fore.RED}[!] Terjadi kesalahan: {e}")
