import re
from urllib.parse import urlparse, parse_qs


def extract_from_curl(curl_file: str, env_file: str = ".env"):
    with open(curl_file, "r", encoding="utf-8") as f:
        content = f.read()

    # --------------------------------------------------
    # Extrai URL (formato: curl 'https://...')
    # --------------------------------------------------
    url_match = re.search(r"curl\s+'([^']+)'", content)
    if not url_match:
        raise RuntimeError("❌ URL não encontrada no curl")

    url = url_match.group(1)
    query_params = parse_qs(urlparse(url).query)

    # --------------------------------------------------
    # Extrai headers (-H 'key: value')
    # --------------------------------------------------
    headers = {}
    for match in re.findall(r"-H\s+'([^:]+):\s*([^']+)'", content):
        key, value = match
        headers[key.lower()] = value

    # --------------------------------------------------
    # Extrai cookie (-b '...')
    # --------------------------------------------------
    cookie_match = re.search(r"-b\s+'([^']+)'", content)
    cookie = cookie_match.group(1) if cookie_match else ""

    # --------------------------------------------------
    # Monta variáveis de ambiente
    # --------------------------------------------------
    env_vars = {
        "X_REQUEST_ID": headers.get("x-request-id", ""),
        "TRACEPARENT": headers.get("traceparent", ""),
        "X_TRACKING_CODE": headers.get("x-trackingcode", ""),
        "X_UOW": headers.get("x-uow", ""),
        "X_REQUESTID": headers.get("x-requestid", ""),
        "PARAM_H": query_params.get("h", [""])[0],
        "COOKIE": cookie,
    }

    # --------------------------------------------------
    # Escreve .env
    # --------------------------------------------------
    with open(env_file, "w", encoding="utf-8") as env:
        for key, value in env_vars.items():
            safe_value = value.replace('"', '\\"')
            env.write(f'{key}="{safe_value}"\n')

    print(f"✅ Arquivo {env_file} gerado com sucesso.")


if __name__ == "__main__":
    extract_from_curl("../curl.txt", ".env")
