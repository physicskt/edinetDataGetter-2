# Configuration Guide | 設定ガイド

## 🇯🇵 日本語

### 環境変数の設定 (.env)

このアプリケーションは環境変数を使って設定を管理しています。`.env.example`を`.env`にコピーして、必要に応じて変更してください。

**重要**: 設定は `.env` ファイルからのみ読み込まれます。すべての必要な設定値を `.env` ファイルに記述してください。

#### API設定
- `EDINET_API_KEY`: EDINETのAPIサブスクリプションキー（必須）
- `GOOGLE_SPREADSHEET_URL`: GoogleスプレッドシートのURL（必須）
- `GOOGLE_SERVICE_ACCOUNT_FILE`: GoogleサービスアカウントのJSONファイルパス

#### デフォルト設定
- `DEFAULT_COMPANY_COUNT`: 処理する企業数 (デフォルト: 1)
- `DEFAULT_START_DATE`: 書類取得の開始日 (形式: YYYY-MM-DD)
- `SHEET_NAME`: Googleスプレッドシートのシート名 (デフォルト: EDINET_Data)

#### フォルダ設定
- `JSON_FOLDER`: JSON APIレスポンス保存フォルダ (デフォルト: json)
- `LOG_FOLDER`: ログファイル保存フォルダ (デフォルト: log)
- `MD_FOLDER`: マークダウンドキュメント保存フォルダ (デフォルト: md)
- `XBRL_FOLDER`: XBRLファイルダウンロードフォルダ (デフォルト: xbrl_files)

#### ログ設定
- `LOG_FILE`: ログファイル名 (デフォルト: logfile.log)
- `MAX_LOG_LINES`: ログファイルの最大行数（トリミング前） (デフォルト: 10000)
- `DELETE_LOG_LINES`: トリミング時の削除行数 (デフォルト: 2000)

### 必要な認証情報

#### EDINET APIキー
1. [EDINET公式サイト](https://disclosure.edinet-fsa.go.jp/)でアカウント作成
2. APIサブスクリプションキーを取得
3. `.env`ファイルの`EDINET_API_KEY`に設定

#### Google認証設定
1. Google Cloud Consoleでプロジェクト作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成してJSONキーをダウンロード
4. JSONファイルを`_gcp_key.json`として保存
5. Googleスプレッドシートをサービスアカウントと共有

---

## 🇺🇸 English

### Environment Variables (.env)

The application uses environment variables for configuration. Copy `.env.example` to `.env` and modify as needed.

**Important**: Configuration is only read from the `.env` file. All required configuration values must be specified in the `.env` file.

#### API Configuration
- `EDINET_API_KEY`: Your EDINET API subscription key (required)
- `GOOGLE_SPREADSHEET_URL`: URL of your Google Drive folder for spreadsheets (required)
- `GOOGLE_SERVICE_ACCOUNT_FILE`: Path to your Google service account JSON file

#### Default Settings
- `DEFAULT_COMPANY_COUNT`: Number of companies to process (default: 1)
- `DEFAULT_START_DATE`: Default start date for document fetching (format: YYYY-MM-DD)
- `SHEET_NAME`: Name of the Google Sheets sheet (default: EDINET_Data)

#### Folder Configuration
- `JSON_FOLDER`: Folder for storing JSON API responses (default: json)
- `LOG_FOLDER`: Folder for log files (default: log)
- `MD_FOLDER`: Folder for markdown documentation (default: md)
- `XBRL_FOLDER`: Folder for XBRL file downloads (default: xbrl_files)

#### Log Settings
- `LOG_FILE`: Log file name (default: logfile.log)
- `MAX_LOG_LINES`: Maximum lines in log file before trimming (default: 10000)
- `DELETE_LOG_LINES`: Number of lines to delete when trimming (default: 2000)

### Required Authentication

#### EDINET API Key
1. Create account on [EDINET official website](https://disclosure.edinet-fsa.go.jp/)
2. Obtain API subscription key
3. Set in `.env` file as `EDINET_API_KEY`

#### Google Authentication Setup
1. Create project in Google Cloud Console
2. Enable Google Sheets API
3. Create service account and download JSON key
4. Save JSON file as `_gcp_key.json`
5. Share Google Spreadsheet with service account

## 📋 Example .env File

```env
# EDINET API Configuration
EDINET_API_KEY=your_edinet_api_key_here

# Google Configuration
GOOGLE_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/your_sheet_id/edit
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json

# Processing Settings
DEFAULT_COMPANY_COUNT=10
DEFAULT_START_DATE=2024-01-01
SHEET_NAME=EDINET_Data

# Folder Settings
JSON_FOLDER=json
LOG_FOLDER=log
MD_FOLDER=md
XBRL_FOLDER=xbrl_files

# Log Settings
LOG_FILE=logfile.log
MAX_LOG_LINES=10000
DELETE_LOG_LINES=2000
```

## 🚀 Getting Started

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration

3. Install required packages:
   ```bash
   pip install -r _requirement.txt
   ```

4. Run the application:
   ```bash
   python edinet_processer.py
   ```