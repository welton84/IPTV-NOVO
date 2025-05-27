import yt_dlp
import json
import os
from yt_dlp.utils import DownloadError

def carregar_urls(caminho='infos.json'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Aceita tanto "urls" quanto "streamers" para maior flexibilidade
            if "urls" in data:
                return data.get("urls", [])
            elif "streamers" in data:
                return data.get("streamers", [])
            else:
                print("[ERRO] Nenhuma chave 'urls' ou 'streamers' encontrada em infos.json.")
                return []
    except Exception as e:
        print(f"[ERRO] Falha ao carregar infos.json: {e}")
        return []

def extrair_stream(video_url, ytdlp):
    try:
        info = ytdlp.extract_info(video_url, download=False)
        title = info.get("title", "Sem título")
        formats = info.get("formats", [])
        for fmt in formats:
            link = fmt.get("url", "")
            ext = fmt.get("ext", "")
            protocol = fmt.get("protocol", "")
            # Aceita formatos mp4 OU m3u8 (HLS) que tenham vídeo e áudio juntos
            if (
                link
                and "manifest.googlevideo.com" not in link
                and (
                    ext == "mp4"
                    or ext == "m3u8"
                    or protocol == "m3u8_native"
                )
                and fmt.get("vcodec", "none") != "none"
                and fmt.get("acodec", "none") != "none"
                and fmt.get("height", 0) <= 480
            ):
                return title, link
        return None, None
    except Exception as e:
        print(f"[ERRO] Falha ao extrair stream de {video_url}: {e}")
        return None, None

def gerar_m3u8(urls, cookies='cookies.txt', limite_por_playlist=5):
    ytdlp_opts = {
        "quiet": True,
        "skip_download": True,
    }

    if cookies and os.path.exists(cookies):
        ytdlp_opts["cookiefile"] = cookies
        print(f"[INFO] Usando {cookies} para autenticação.")
    else:
        print("[INFO] Rodando sem cookies (acesso público).")

    ytdlp = yt_dlp.YoutubeDL(ytdlp_opts)
    with open("iptv.m3u8", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        for url in urls:
            print(f"[INFO] Processando: {url}")
            try:
                stream_link = ytdlp.extract_info(url, download=False)
                # Se for playlist, processa os vídeos
                if stream_link.get('_type') == 'playlist':
                    entries = stream_link.get('entries', [])[:limite_por_playlist]
                    for entry in entries:
                        video_id = entry.get('id')
                        if not video_id:
                            continue
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        title, link = extrair_stream(video_url, ytdlp)
                        if link:
                            f.write(f'#EXTINF:-1 tvg-name="{title}" group-title="YouTube", {title}\n{link}\n\n')
                            print(f"[OK] Adicionado: {title}")
                        else:
                            print(f"[AVISO] Não foi possível extrair link de {video_url}")
                else:
                    title, link = extrair_stream(url, ytdlp)
                    if link:
                        f.write(f'#EXTINF:-1 tvg-name="{title}" group-title="YouTube", {title}\n{link}\n\n')
                        print(f"[OK] Adicionado: {title}")
                    else:
                        print(f"[AVISO] Não foi possível extrair link de {url}")
            except DownloadError as e:
                print(f"[ERRO] yt-dlp falhou para {url}: {e}")
            except Exception as e:
                print(f"[ERRO] Erro inesperado para {url}: {e}")

if __name__ == "__main__":
    urls = carregar_urls()
    if urls:
        gerar_m3u8(urls)
        print("[FINALIZADO] Arquivo iptv.m3u8 gerado.")
    else:
        print("[AVISO] Nenhuma URL encontrada no infos.json.")