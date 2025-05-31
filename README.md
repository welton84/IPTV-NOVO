# IPTV Gerador Automático

Este script em Python gera uma lista IPTV (.m3u8) com links diretos de vídeos do YouTube, ideal para usar em VLC ou TV Box.

## Requisitos

- Python 3.10 ou superior
- yt-dlp
- cookies.txt (opcional, para vídeos restritos)

## Uso

1. Coloque suas URLs de canais ou vídeos no `infos.json`
2. Execute o script:

```bash
python gerar_iptv.py
