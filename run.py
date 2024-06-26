import yt_dlp
import requests
import os

from dotenv import load_dotenv
load_dotenv()

for name in ['output', 'temp']:
    if name not in os.listdir():
        os.mkdir(name)
        print(f"創建 {name} 資料夾...")

if len(os.listdir('temp')) != 0:
    print("'temp' 資料夾內必須為空。")
    exit()

def line():
    print('------------------------------')

def duplicate(list1: list, list2: list):
    for i in list1:
        for j in list2:
            if i == j:
                return True
    return False

def make_request(limit: int, offset: int):
    response = requests.get(
        url=f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}',
        headers={
            'Authorization': f'Bearer {spotify_access_token}'
        }
    )

    return response

self_input = False

while True:
    spotify_client_id = input('輸入 Spotify Client ID: ') if self_input else os.getenv('spotify_client_id')
    spotify_client_secret = input('輸入 Spotify Client secret: ') if self_input else os.getenv('spotify_client_secret')

    print('驗證及取得 Access Token...')

    response = requests.post(
        url='https://accounts.spotify.com/api/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data={
            'grant_type': 'client_credentials',
            'client_id': spotify_client_id,
            'client_secret': spotify_client_secret
        }
    )

    if response.status_code == 200:
        spotify_access_token = response.json()['access_token']
        print('驗證成功！')
        line()
        break
    else:
        print('驗證失敗，請再試一次。')
        self_input = True

while True:
    playlist_url = input('輸入 Spotify 播放清單網址: ')

    try:
        playlist_id = playlist_url.split('/')[4].split('?')[0]
    except:
        print('無法取得播放清單。')
    else:
        response = make_request(1, 0)

        if response.status_code == 200:
            data = response.json()
            total = data['total']

            print(f'\n已確認播放清單可用 (共 {total} 首)，正在讀取歌曲...')

            playlist = []
            for offset in range(0, data['total'], 100):
                response = make_request(100, offset)

                data = response.json()
                items = [f"{i['track']['artists'][0]['name']} - {i['track']['name']}" for i in data['items']]
                playlist += items

                print(f'已讀取 {len(playlist)} / {total} 首...')

            print(f'\n成功取得下列播放清單歌曲 (共 {len(playlist)} 首)：')
            print(', '.join(playlist))
            line()
            break
        else:
            print('無法取得播放清單。')

saved = list(map(lambda s: s.removesuffix('.wav'), os.listdir('output')))
skip = False

if duplicate(playlist, saved):
    while True:
        skip = input('檢測到重複下載曲目。跳過重複曲目? (y/n) ')
        if skip not in ['y', 'n']:
            print('輸入有誤，請再試一次。')
        else:
            skip = True if skip == 'y' else False
            print(('跳過' if skip else '不跳過') + '重複曲目。')
            break
else:
    print('無重複下載曲目。')

line()
print('開始下載...')

ydl_opts = {
    'format': 'wav/bestaudio/best',
    'outtmpl': 'temp/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav'
    }]
}

index = 1
total = len(playlist)

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for song in playlist:
        print(f'\n({index} / {total}) ', end='')
        if skip and f'{song}.wav' in os.listdir('output'):
            print(f'跳過 {song} ...')
        else:
            print(f'正在下載 {song} ...')
            try:
                ydl.extract_info(f"ytsearch:{song}", download=True)['entries'][0]
                os.rename(f"temp/{os.listdir('temp')[0]}", f'output/{song}.wav')
            except Exception as e:
                print(f'未知錯誤 - ({e})')
        index += 1

line()
print('完成。')