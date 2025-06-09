# EDINET Data Getter

## 🇯🇵 日本語

### 概要
EDINET Data Getterは、日本の金融庁が運営するEDINET（Electronic Disclosure for Investors' NETwork）システムから企業の財務データを自動取得・処理するツールです。上場企業の有価証券報告書やXBRLファイルをダウンロードし、重要な財務指標を抽出してGoogleスプレッドシートに整理します。

### 主な機能
- 📊 EDINET APIからの書類一覧取得
- 📁 XBRLファイルの自動ダウンロード・解凍
- 🔍 財務データの自動抽出（配当性向、EPS、株価収益率など）
- 📋 Googleスプレッドシートへの自動書き込み
- 📄 処理結果のマークダウンレポート生成
- 🗂️ ログファイルによる詳細な処理履歴

### 抽出される財務指標
- 配当性向 (Dividend Payout Ratio)
- EPS (Earnings Per Share)
- 株価収益率 (Price-to-Earnings Ratio)
- 営業キャッシュフロー (Operating Cash Flow)
- 営業利益率 (Operating Profit Margin)
- 配当利回り (Dividend Yield)
- 自己資本比率 (Equity Ratio)

### クイックスタート
1. `.env.example`を`.env`にコピーして設定を行う
2. EDINET APIキーとGoogle認証情報を設定
3. `python edinet_processer.py`を実行
4. 結果は各フォルダで確認：
   - `json/` - API レスポンス
   - `log/` - ログファイル
   - `md/` - 処理結果レポート
   - `xbrl_files/` - ダウンロードされたXBRLファイル

### 詳細情報
- 設定方法: [md/config.md](md/config.md)
- 処理フロー: [md/processing_flow.md](md/processing_flow.md)

---

## 🇺🇸 English

### Overview
EDINET Data Getter is an automated tool for fetching and processing corporate financial data from Japan's EDINET (Electronic Disclosure for Investors' NETwork) system. It downloads securities reports and XBRL files from listed companies, extracts key financial metrics, and organizes them in Google Spreadsheets.

### Key Features
- 📊 Document listing from EDINET API
- 📁 Automatic XBRL file download and extraction
- 🔍 Automated financial data extraction (dividend payout ratio, EPS, P/E ratio, etc.)
- 📋 Automatic Google Spreadsheet writing
- 📄 Markdown report generation for processing results
- 🗂️ Detailed processing history via log files

### Extracted Financial Metrics
- Dividend Payout Ratio (配当性向)
- EPS - Earnings Per Share
- P/E Ratio - Price-to-Earnings Ratio
- Operating Cash Flow (営業CF)
- Operating Profit Margin (営業利益率)
- Dividend Yield (配当利回り)
- Equity Ratio (自己資本比率)

### Quick Start
1. Copy `.env.example` to `.env` and configure settings
2. Set up EDINET API key and Google authentication credentials
3. Run `python edinet_processer.py`
4. Check results in respective folders:
   - `json/` - API responses
   - `log/` - Log files
   - `md/` - Processing result reports
   - `xbrl_files/` - Downloaded XBRL files

### Detailed Information
- Configuration: [md/config.md](md/config.md)
- Processing Flow: [md/processing_flow.md](md/processing_flow.md)

---

## 📁 Repository Structure

```
edinetDataGetter/
├── .env.example                    # Environment variables template
├── edinet_processer.py             # Main processing script
├── module/                         # Core modules
│   ├── config.py                  # Configuration management
│   ├── docs.py                    # Documentation utilities
│   ├── fetch_edinet_documents.py  # EDINET API client
│   ├── logger.py                  # Logging utilities
│   └── xbrl_reader.py             # XBRL file parser
├── md/                            # Documentation
│   ├── README.md                  # Technical documentation index
│   ├── config.md                  # Configuration guide
│   └── processing_flow.md         # Processing flow documentation
├── json/                          # API response storage (created at runtime)
├── log/                           # Log files (created at runtime)
└── xbrl_files/                    # Downloaded XBRL files (created at runtime)
```

## 🛠️ Requirements

- Python 3.7+
- Required packages: see `_requirement.txt`
- EDINET API subscription key
- Google Cloud service account for Sheets API access

## 📜 License

This project is for educational and research purposes.