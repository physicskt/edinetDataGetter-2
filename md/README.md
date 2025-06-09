# Technical Documentation | 技術ドキュメント

## 🇯🇵 日本語

このフォルダには、EDINET Data Getterの技術的なドキュメントが含まれています。

### ドキュメント一覧
- [config.md](config.md) - 設定ガイド（環境変数、認証情報の設定方法）
- [processing_flow.md](processing_flow.md) - 処理フローの詳細説明
- 処理結果レポート（実行時に自動生成）

### 自動生成されるファイル
実行すると以下のファイルが自動生成されます：
- `run_summary_YYYY-MM-DD_HHMMSS.md` - 各実行の結果サマリー

---

## 🇺🇸 English

This folder contains technical documentation for EDINET Data Getter.

### Document List
- [config.md](config.md) - Configuration guide (environment variables, authentication setup)
- [processing_flow.md](processing_flow.md) - Detailed processing flow explanation
- Processing result reports (automatically generated during execution)

### Auto-generated Files
The following files are automatically generated during execution:
- `run_summary_YYYY-MM-DD_HHMMSS.md` - Result summary for each execution

---

## 📊 Current Configuration Summary

- **Company Count Limit**: 1
- **Default Start Date**: 2024-03-08
- **Sheet Name**: EDINET_Data
- **JSON Folder**: C:\code\git\Edinet\edinetDataGetter-2\json
- **Log Folder**: C:\code\git\Edinet\edinetDataGetter-2\log
- **MD Folder**: C:\code\git\Edinet\edinetDataGetter-2\md
- **XBRL Folder**: C:\code\git\Edinet\edinetDataGetter-2\xbrl_files

## 💾 Extracted Data Fields
- 配当性向 (Dividend Payout Ratio)
- EPS (Earnings Per Share)
- 株価収益率 (Price-to-Earnings Ratio)
- 営業CF (Operating Cash Flow)
- 営業利益率 (Operating Profit Margin)
- 配当利回り (Dividend Yield)
- 自己資本比率 (Equity Ratio)

---
Last updated: 2025-06-10 07:30:03
