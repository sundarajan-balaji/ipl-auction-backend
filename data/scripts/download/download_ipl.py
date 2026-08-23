from pathlib import Path
import hashlib
import requests


SOURCE_URL = "https://cricsheet.org/downloads/ipl_json.zip"

DATA_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = DATA_DIR / "raw" / "cricsheet"

OUTPUT_FILE = RAW_DIR / "ipl_json.zip"
CHECKSUM_FILE = RAW_DIR / "ipl_json.sha256"

CHUNK_SIZE = 1024 * 1024  # 1 MB


def download_file() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading IPL data from Cricsheet...")
    print(f"Source : {SOURCE_URL}")
    print(f"Target : {OUTPUT_FILE}")

    response = requests.get(
        SOURCE_URL,
        stream=True,
        timeout=60
    )

    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(OUTPUT_FILE, "wb") as file:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if not chunk:
                continue

            file.write(chunk)
            downloaded += len(chunk)

            if total_size:
                percentage = downloaded / total_size * 100
                print(
                    f"\rProgress: {percentage:6.2f}%",
                    end=""
                )

    print("\nDownload completed.")

    verify_file()


def verify_file() -> None:
    print("Calculating SHA-256 checksum...")

    sha256 = hashlib.sha256()

    with open(OUTPUT_FILE, "rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            sha256.update(chunk)

    checksum = sha256.hexdigest()

    CHECKSUM_FILE.write_text(
        checksum + "\n",
        encoding="utf-8"
    )

    print(f"SHA-256: {checksum}")
    print(f"Checksum saved to: {CHECKSUM_FILE}")
    print("Download verification completed.")


if __name__ == "__main__":
    download_file()