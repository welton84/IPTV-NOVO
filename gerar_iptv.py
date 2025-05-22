import yt_dlp
import json

def carregar_streamers(caminho='infos.json'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("streamers", [])
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return []

def obter_link_direto(video_url):
    ytdlp = yt_dlp.YoutubeDL({
        "quiet": True,
        "format": "best[height<=480]/best",
        "get_url": True,
        "cookiefile": "cookies.txt"
    })
    try:
        info = ytdlp.extract_info(video_url, download=False)
        return info.get('url')
    except Exception as e:
        print(f"Erro ao pegar link direto: {e}")
        return None

def processar_canal(canal):
    ytdlp = yt_dlp.YoutubeDL({
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "cookiefile": "cookies.txt"
    })
    url = f"https://www.youtube.com/{canal}" if not canal.startswith("http") else canal
    try:
        info = ytdlp.extract_info(url, download=False)
        links = []
        for entry in info.get("entries", [])[:10]:
            video_id = entry.get("id")
            title = entry.get("title", "Sem título")
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            link_direto = obter_link_direto(video_url)
            if link_direto:
                links.append((title, link_direto))
        return links
    except Exception as e:
        print(f"Erro ao processar canal {canal}: {e}")
        return []

def criar_m3u8(entradas, caminho='iptv.m3u8'):
    if not entradas:
        print("Nenhum vídeo válido encontrado.")
        return
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for titulo, url in entradas:
            f.write(f'#EXTINF:-1 tvg-name="{titulo}" group-title="YouTube", {titulo}\n{url}\n\n')
    print(f"Arquivo {caminho} criado com {len(entradas)} vídeos.")

def main():
    canais = carregar_streamers()
    todos = []
    for canal in canais:
        print(f"Processando: {canal}")
        todos.extend(processar_canal(canal))
    criar_m3u8(todos)

if __name__ == "__main__":
    main()
