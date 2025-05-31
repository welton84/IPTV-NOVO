import yt_dlp
import json
import os
import time
from yt_dlp.utils import DownloadError

def carregar_config(caminho='infos.json'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            data = json.load(f)
            urls = data.get("urls", []) or data.get("streamers", [])
            limite = data.get("limite", 20)
            cookies = data.get("cookies", "cookies.txt")
            return urls, limite, cookies
    except Exception as e:
        print(f"[ERRO] Falha ao carregar {caminho}: {e}")
        return [], 20, "cookies.txt"

def extrair_todos_formatos(video_url, cookies='cookies.txt'):
    ytdlp_opts = {
        "quiet": True,
        "skip_download": True
    }

    if cookies and os.path.exists(cookies):
        ytdlp_opts["cookiefile"] = cookies
        print(f"[INFO] Usando cookies: {cookies}")
    else:
        print("[INFO] Rodando sem cookies.")

    try:
        ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)
        stream_link = ytdlp.extract_info(video_url, download=False)

        print(f"[DEBUG] stream_link extraído de {video_url}")  # stream_link mantido
        title = stream_link.get("title", "Sem título")
        formatos = stream_link.get("formats", [])
        encontrados = []

        for fmt in formatos:
            url = fmt.get("url")
            ext = fmt.get("ext", "")
            mime = fmt.get("mime_type", "")
            protocol = fmt.get("protocol", "")
            vcodec = fmt.get("vcodec", "none")
            acodec = fmt.get("acodec", "none")
            height = fmt.get("height", 0)

            if (
                url and
                not url.endswith(".json") and
                "timedtext" not in url and
                ".vtt" not in url and
                not (mime and mime.startswith("text/")) and
                vcodec != "none" and
                acodec != "none"
            ):
                encontrados.append((title, ext, height or 0, url))

        return encontrados

    except Exception as e:
        print(f"[ERRO] Falha ao extrair formatos de {video_url}: {e}")
        return []

def gerar_m3u8(urls, cookies='cookies.txt', limite_por_playlist=20):
    if os.path.exists("iptv.m3u8"):
        os.rename("iptv.m3u8", "iptv_OLD.m3u8")
        print("[INFO] Backup criado: iptv_OLD.m3u8")

    falhas = []

    with open("iptv.m3u8", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        for url in urls:
            print(f"[INFO] Processando: {url}")
            try:
                ytdlp_check = yt_dlp.YoutubeDL({
                    "quiet": True,
                    "skip_download": True,
                    "cookiefile": cookies if os.path.exists(cookies) else None
                })

                stream_link = ytdlp_check.extract_info(url, download=False)

                if stream_link.get('_type') == 'playlist':
                    entries = stream_link.get('entries', [])[:limite_por_playlist]
                    for entry in entries:
                        video_id = entry.get('id')
                        if not video_id:
                            continue
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        formatos = extrair_todos_formatos(video_url, cookies)
                        for titulo, ext, height, link in formatos:
                            f.write(f'#EXTINF:-1 tvg-name="{titulo} {height}p {ext}" group-title="YouTube", {titulo} ({height}p)\n{link}\n\n')
                        if not formatos:
                            falhas.append(video_url)
                        time.sleep(1)
                else:
                    formatos = extrair_todos_formatos(url, cookies)
                    for titulo, ext, height, link in formatos:
                        f.write(f'#EXTINF:-1 tvg-name="{titulo} {height}p {ext}" group-title="YouTube", {titulo} ({height}p)\n{link}\n\n')
                    if not formatos:
                        falhas.append(url)
                    time.sleep(1)

            except DownloadError as e:
                print(f"[ERRO] yt-dlp falhou para {url}: {e}")
                falhas.append(url)
            except Exception as e:
                print(f"[ERRO] Erro inesperado para {url}: {e}")
                falhas.append(url)

    if falhas:
        with open("falhas.txt", "w", encoding="utf-8") as fail_log:
            for item in falhas:
                fail_log.write(item + "\n")
        print(f"[AVISO] {len(falhas)} vídeos falharam. Veja falhas.txt")

    print("\n✅ Arquivo iptv.m3u8 gerado com sucesso.")

if __name__ == "__main__":
    urls, limite, cookies = carregar_config()
    if urls:
        gerar_m3u8(urls, cookies=cookies, limite_por_playlist=limite)
    else:
        print("[AVISO] Nenhuma URL válida encontrada no infos.json.")

