import re

def extract_drive_id(url: str) -> str:
    """Google DriveのURLからフォルダまたはファイルのIDを抽出"""
    match = re.search(r"(?:drive/folders/|file/d/|id=)([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else ""

if __name__ == "__main__":
    folder_url = "https://drive.google.com/drive/folders/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?usp=drive_link"
    folder_url = "https://drive.google.com/drive/folders/1H0nRbuGQ9alIovIadFufum3ehbeBenLg?usp=drive_link"

    # # Google DriveのフォルダURLを取得
    # with open("_google_drive_folder_url.txt", "r", encoding="utf-8") as file:
    #     google_drive_folder_url = file.read()

    # フォルダIDを取得
    folder_id = extract_drive_id(folder_url)
    print("フォルダID:", folder_id)
