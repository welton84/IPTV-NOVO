import yt_dlp
import json
import os
import time
from yt_dlp.utils import DownloadError

# Defina o navegador que deseja usar para cookies
NAVEGADOR = "chrome"  # ou "firefox", "edge", etc.

def carregar_urls_e_limite(caminho='infos.json'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            data = json.load(f)
            urls = data.get("urls", []) or data.get("streamers", [])
            limite = data.get("limite", 20)
            return urls, limite
    except Exception as e:
        print(f"[ERRO] Falha ao carregar infos.json: {e}")
        return [], 20

def get_ytdlp_opts(cookies='cookies.txt'):
    # Tenta usar cookies do navegador
    try:
        import yt_dlp.cookies
        # Testa se consegue extrair cookies do navegador
        cookies_from_browser = {"cookiesfrombrowser": NAVEGADOR}
        yt_dlp.YoutubeDL(cookies_from_browser)
        print(f"[INFO] Usando cookies diretamente do navegador: {NAVEGADOR}")
        return {
            "quiet": True,
            "skip_download": True,
            "cookiesfrombrowser": NAVEGADOR
        }
    except Exception:
        # Se falhar, tenta o cookies.txt
        if cookies and os.path.exists(cookies):
            print(f"[INFO] Usando cookies do arquivo: {cookies}")
            return {
                "quiet": True,
                "skip_download": True,
                "cookiefile": cookies
            }
        print("[INFO] Rodando sem cookies (apenas vídeos públicos ou que não exigem login).")
        return {
            "quiet": True,
            "skip_download": True
        }

def extrair_todos_formatos(video_url, ytdlp_opts):
    try:
        ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)
        stream_link = ytdlp.extract_info(video_url, download=False)
        title = stream_link.get("title", "Sem título")
        formatos = stream_link.get("formats", [])
        encontrados = []

        for fmt in formatos:
            link = fmt.get("url")
            ext = fmt.get("ext", "")
            height = fmt.get("height", 0)
            protocol = fmt.get("protocol", "")
            vcodec = fmt.get("vcodec", "none")
            acodec = fmt.get("acodec", "none")

            if (
                link
                and (
                    ext in ["mp4", "m3u8"]
                    or protocol == "m3u8_native"
                )
                and vcodec != "none"
                and acodec != "none"
                and isinstance(height, int)
                and height <= 1080
            ):
                encontrados.append((title, ext, height, link))

        return encontrados

    except Exception as e:
        print(f"[ERRO] Falha ao extrair formatos de {video_url}: {e}")
        return []

def gerar_m3u8(urls, ytdlp_opts, limite_por_playlist=20):
    with open("iptv.m3u8", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        for url in urls:
            print(f"[INFO] Processando: {url}")
            try:
                ytdlp_check = yt_dlp.YoutubeDL(ytdlp_opts)
                stream_link = ytdlp_check.extract_info(url, download=False)

                if stream_link.get('_type') == 'playlist':
                    entries = stream_link.get('entries', [])[:limite_por_playlist]
                    for entry in entries:
                        video_id = entry.get('id')
                        if not video_id:
                            continue
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        formatos = extrair_todos_formatos(video_url, ytdlp_opts)
                        for titulo, ext, height, link in formatos:
                            f.write(f'#EXTINF:-1 tvg-name="{titulo} {height}p" group-title="YouTube", {titulo} ({height}p)\n{link}\n\n')
                        time.sleep(2)
                else:
                    formatos = extrair_todos_formatos(url, ytdlp_opts)
                    for titulo, ext, height, link in formatos:
                        f.write(f'#EXTINF:-1 tvg-name="{titulo} {height}p" group-title="YouTube", {titulo} ({height}p)\n{link}\n\n')
                    time.sleep(2)

            except DownloadError as e:
                print(f"[ERRO] yt-dlp falhou para {url}: {e}")
            except Exception as e:
                print(f"[ERRO] Erro inesperado para {url}: {e}")

    print("\n✅ Arquivo iptv.m3u8 gerado com sucesso.")

if __name__ == "__main__":
    urls, limite = carregar_urls_e_limite()
    ytdlp_opts = get_ytdlp_opts()
    if urls:
        gerar_m3u8(urls, ytdlp_opts, limite_por_playlist=limite)
    else:
        print("[AVISO] Nenhuma URL válida encontrada no infos.json.")
