import requests
import zipfile
import io
import os
import pandas as pd
import gspread
from bs4 import BeautifulSoup
import lxml
import sys
from oauth2client.service_account import ServiceAccountCredentials
try:
    import tkinter as tk
    from tkinter import messagebox
    from tkcalendar import Calendar
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter not available. GUI features will be disabled.")
from datetime import datetime

from module.fetch_edinet_documents import *
from module.xbrl_reader import *
from module.logger import *
from module.config import config
from module.docs import save_run_summary, save_config_documentation


DATE_FOR_SHEET = "YYYY-MM-DD"
# Configuration is now handled by config.py
SPREADSHEET_URL = config['google_drive_folder_url']
SHEET_NAME = config['sheet_name']
EDINET_API_KEY = config['edinet_api_key']

##Google API認証（事前にJSONキーをダウンロードして設定）
SERVICE_ACCOUNT_FILE = str(config['google_service_account_file'])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)


# XBRLファイルをダウンロード & 解凍
def download_and_extract_xbrl(download_url, save_folder=None, fund_code:str = "G12239"):
    from module.logger import logger
    
    if save_folder is None:
        save_folder = str(config['xbrl_folder'])
    os.makedirs(save_folder, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }

    params = {
        "Subscription-Key": EDINET_API_KEY
    }
    
    try:
        response = requests.get(download_url, headers=headers, params=params)
        response.raise_for_status()  # HTTPエラーが発生した場合は例外を発生させる
        
        zip_path = os.path.join(save_folder, "edinet_xbrl.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(save_folder)
            
        logger.info(f"✅ XBRLダウンロード・解凍完了: {fund_code}")

        folder_public_doc = os.path.abspath(os.path.join(save_folder, "XBRL/PublicDoc"))
        # XBRLファイルを検索
        for root, _, files in os.walk(folder_public_doc):
            for file in files:
                if file.endswith(".xbrl") and fund_code and (fund_code in file):
                    target_xbrl = os.path.join(root, file)
                    log_long_msg(f"見つかったXBRLファイル: {target_xbrl}")
                    return target_xbrl
                    
        logger.warning(f"⚠️ {fund_code} に該当するXBRLファイルが見つかりませんでした")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.exception(f"XBRLダウンロード中にネットワークエラーが発生しました: {fund_code}")
        raise
    except zipfile.BadZipFile as e:
        logger.exception(f"ZIPファイルの解凍に失敗しました: {fund_code}")
        raise
    except Exception as e:
        logger.exception(f"XBRLダウンロード・解凍中に予期しないエラーが発生しました: {fund_code}")
        raise


# Googleスプレッドシートにデータを書き込む
def write_to_spreadsheet(data):
    global DATE_FOR_SHEET
    
    try:
        ss = client.open_by_url(SPREADSHEET_URL)
        logger.info("✅ Googleスプレッドシートに接続しました")
    except Exception as e:
        logger.exception("Googleスプレッドシートへの接続に失敗しました")
        raise

    try:
        # 必要な行数と列数を計算
        num_rows = max(len(data) + 2, 100)  # データ行 + ヘッダー + 予備
        num_cols = max(len(data[0]) if data else 10, 10)  # データの列数が基準（最低10列）

        # シートが存在するか確認し、なければ作成
        sheet_name_data = f"{SHEET_NAME}_{DATE_FOR_SHEET}"
        try:
            sheet = ss.worksheet(sheet_name_data)
            logger.info(f"✅ 既存シート '{sheet_name_data}' を使用します")
        except gspread.exceptions.WorksheetNotFound:
            sheet = ss.add_worksheet(title=sheet_name_data, rows=str(num_rows), cols=str(num_cols))
            logger.info(f"✅ シート '{sheet_name_data}' を新規作成しました！（{num_rows}行 × {num_cols}列）")

        # 既存シートの内容をクリア
        try:
            sheet.clear()
            logger.info("✅ シートの内容をクリアしました")
        except Exception as e:
            logger.exception("シートクリア中にエラーが発生しました")
            raise

        headers = [
            "EDINETコード", "fundコード", "会計期間開始", "会計期間終了", "書類提出日",
            "企業名", "書類ID", "配当性向", "EPS", "株価収益率",
            "営業活動によるキャッシュ・フロー",
            "売上高", "営業利益", "当期純利益", "営業利益率", "配当利回り", 
            "純資産合計", "負債純資産合計", "自己資本比率",
            "営業収益合計", "当期純利益又は当期純損失", "営業利益又は営業損失"
        ]
        
        try:
            sheet.append_row(headers)
            logger.info("✅ ヘッダー行を追加しました")
        except Exception as e:
            logger.exception("ヘッダー行追加中にエラーが発生しました")
            raise

        # headersが辞書のキーとして使われている前提
        data_to_insert = []
        for row_idx, row in enumerate(data):
            new_row = []
            for key in headers:
                try:
                    new_row.append(row[key])
                except Exception as e:
                    logger.exception(f"{row.get('企業名', 'Unknown')}: {key}に有効なデータがありません")
                    new_row.append("NA")

            data_to_insert.append(new_row)

        # 一括で行を追加する
        try:
            sheet.append_rows(data_to_insert)
            logger.info(f"✅ {len(data_to_insert)}行のデータを追加しました")
        except Exception as e:
            logger.exception("データ行追加中にエラーが発生しました")
            raise

        # 全ての書式をリセット
        try:
            start_col_letter = "A"
            end_col_letter = col_number_to_letter(len(headers) + 1)
            range_ = f'{start_col_letter}:{end_col_letter}'
            sheet.format(range_, {
                "numberFormat": {
                    "type": "NUMBER",
                    "pattern": "@"
                }
            })
            logger.info(f"✅ 書式設定を適用した範囲: {range_}")
        except Exception as e:
            logger.exception("書式設定中にエラーが発生しました")
            # 書式設定エラーは処理を止めない
            logger.info("書式設定に失敗しましたが、データ書き込みは完了しています")
            
    except Exception as e:
        logger.exception("Googleスプレッドシート書き込み処理中にエラーが発生しました")
        raise


# 列番号をアルファベットに変換する関数
def col_number_to_letter(col_num):
    col_letter = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        col_letter = chr(remainder + 65) + col_letter
    return col_letter


# メイン処理
def main(company_conuts:int=None, start_date=None):
    # Use configuration defaults if not provided
    if company_conuts is None:
        company_conuts = config['default_company_count']
    if start_date is None:
        start_date = config['default_start_date']
        
    # 最大データ取得数
    # company_conuts = 10
    # start_date="2025-03-08"
    skip_company_word_list = config['skip_company_words']

    logger.info("📌 EDINETの書類を取得中...")
    logger.info(f"日付: {start_date}")
    documents = fetch_edinet_documents(start_date, EDINET_API_KEY)
    # logger.info(documents)

    if not documents:
        logger.error("⚠️ 取得できる書類がありません。")
        return

    final_data = []
    
    for doc in documents[: + company_conuts]:
        log_long_msg("# 次の企業")

        # ファンドだったら処理スキップ
        skip_flag = False
        for word in skip_company_word_list:
            if word in doc['企業名']:
                skip_flag = True
                continue
        if skip_flag is True:
            log_long_msg(f"{doc['企業名']} の処理はスキップします")
            continue

        data_dict = {
            "配当性向": "",
            "EPS": "",
            "株価収益率": "",
            "営業CF": "",
            "営業利益率": "",
            "配当利回り": "",
            "自己資本比率": "",
        }
        # logger.info(doc)
        logger.info("xbrl_path ダウンロードURLは:")
        logger.info(doc["XBRLダウンロードURL"])
        logger.info(f"📂 {doc['企業名']} のXBRLをダウンロード中...")
        xbrl_path = None
        try:
            if doc["fundCode"] is not None:
                logger.info("fundです。スキップします。")
                continue
            # ファンドコードが取れなければ EDINETコードをとる
            logger.info("fundコード")
            logger.info(doc["fundコード"])
            logger.info(doc["fundCode"])
            xbrl_path = download_and_extract_xbrl(doc["XBRLダウンロードURL"], str(config['xbrl_folder']), fund_code=doc["fundCode"])
        except Exception as e:
            logger.exception(f"fundCodeでのXBRLダウンロードに失敗しました: {doc['企業名']}")   
            try:
                # ファンドコードが取れなければ EDINETコードをとる
                logger.info("EDINETコード")
                logger.info(doc["EDINETコード"])
                xbrl_path = download_and_extract_xbrl(doc["XBRLダウンロードURL"], str(config['xbrl_folder']), fund_code=doc["EDINETコード"])
            except Exception as e:
                logger.exception(f"EDINETコードでのXBRLダウンロードに失敗しました: {doc['企業名']}")    
                logger.info(f"❌ {doc['企業名']} のXBRLダウンロードに失敗しました。次の企業に進みます。")
                continue


        logger.info("xbrl_path は:")
        logger.info(xbrl_path)
        if not xbrl_path:
            logger.info(f"❌ {doc['企業名']} のXBRLファイルが見つかりませんでした")
            continue

        # XBRL ファイルの解析。fundの場合。
        logger.info(f"📊 {doc['企業名']} のXBRLを解析中...")
        financial_data = {}
        
        # Try fund-specific extraction first
        try:
            financial_data = extract_values_from_xbrl(xbrl_path, "BalanceSheetTextBlock", ["純資産合計", "負債純資産合計"])
            profit_loss = extract_values_from_xbrl(xbrl_path, "StatementOfIncomeAndRetainedEarningsTextBlock", ["営業収益合計", "営業利益又は営業損失", "当期純利益又は当期純損失"])
            if profit_loss:
                financial_data = {**financial_data, **profit_loss}
            logger.info(f"✅ {doc['企業名']} fund形式でのXBRL解析が成功しました")
        except Exception as e:
            logger.exception(f"fund形式でのXBRL解析に失敗しました: {doc['企業名']}")
            logger.info("通常企業形式での解析を試行します。")
        
        # Try regular company extraction if fund extraction failed or didn't get enough data
        if not financial_data or len(financial_data) == 0:
            try:
                financial_data = extract_values_from_xbrl(xbrl_path, "ConsolidatedBalanceSheetTextBlock", ["純資産合計", "負債純資産合計"])
                profit_loss = extract_values_from_xbrl(xbrl_path, "ConsolidatedStatementOfIncomeTextBlock", ["売上高", "営業利益", "当期純利益"])
                if profit_loss:
                    financial_data = {**financial_data, **profit_loss}
                logger.info(f"✅ {doc['企業名']} 通常企業形式でのXBRL解析が成功しました")
            except Exception as e:
                logger.exception(f"通常企業形式でのXBRL解析に失敗しました: {doc['企業名']}")
                logger.info(f"❌ {doc['企業名']} のXBRL解析に失敗しました。次の企業に進みます。")
                continue

        # キャッシュフロー取得 ConsolidatedStatementOfCashFlowsTextBlock
        try:
            cash_flow_data = extract_values_from_xbrl(xbrl_path, "ConsolidatedStatementOfCashFlowsTextBlock", ["営業活動によるキャッシュ・フロー"])
            if cash_flow_data:
                financial_data = {**financial_data, **cash_flow_data}
                logger.info(f"✅ {doc['企業名']} キャッシュフロー取得成功")
        except Exception as e:
            logger.exception(f"キャッシュフロー取得に失敗しました: {doc['企業名']}")
            logger.info("キャッシュフローなしで処理を続けます。")

        # 財務指標の計算
        # fundの場合の営業利益率計算
        try:
            if "当期純利益又は当期純損失" in financial_data and "営業収益合計" in financial_data:
                if financial_data["当期純利益又は当期純損失"] is not None and financial_data["営業収益合計"] is not None:
                    data_dict["営業利益率"] = float(financial_data["当期純利益又は当期純損失"]) / float(financial_data["営業収益合計"]) * 100
                    data_dict["営業利益率"] = round(data_dict["営業利益率"], 2)
                    logger.info(f"✅ {doc['企業名']} fund形式営業利益率計算成功: {data_dict['営業利益率']}%")
        except Exception as e:
            logger.exception(f"fund形式営業利益率計算に失敗しました: {doc['企業名']}")
            
        # 通常企業の場合の営業利益率計算
        try:
            if "営業利益" in financial_data and "売上高" in financial_data:
                if financial_data["営業利益"] is not None and financial_data["売上高"] is not None:
                    data_dict["営業利益率"] = float(financial_data["営業利益"]) / float(financial_data["売上高"]) * 100
                    data_dict["営業利益率"] = round(data_dict["営業利益率"], 2)
                    logger.info(f"✅ {doc['企業名']} 通常企業営業利益率計算成功: {data_dict['営業利益率']}%")
        except Exception as e:
            logger.exception(f"通常企業営業利益率計算に失敗しました: {doc['企業名']}")
            
        # 自己資本比率計算
        try:
            if "純資産合計" in financial_data and "負債純資産合計" in financial_data:
                if financial_data["純資産合計"] is not None and financial_data["負債純資産合計"] is not None:
                    data_dict["自己資本比率"] = float(financial_data["純資産合計"]) / float(financial_data["負債純資産合計"]) * 100
                    data_dict["自己資本比率"] = round(data_dict["自己資本比率"], 2)
                    logger.info(f"✅ {doc['企業名']} 自己資本比率計算成功: {data_dict['自己資本比率']}%")
        except Exception as e:
            logger.exception(f"自己資本比率計算に失敗しました: {doc['企業名']}")

        final_data.append({**doc, **data_dict, **financial_data})
        logger.info(f"✅ {doc['企業名']} の処理が完了しました")

    logger.info("📝 Googleスプレッドシートに書き込み中...")
    try:
        write_to_spreadsheet(final_data)
        logger.info("✅ Googleスプレッドシート書き込み完了！")
        logger.info(SPREADSHEET_URL)
    except Exception as e:
        logger.exception("Googleスプレッドシート書き込み中にエラーが発生しました")
        logger.info("処理は続行されます...")
    
    # Generate documentation
    try:
        summary_path = save_run_summary(documents, final_data, start_date)
        logger.info(f"📄 処理結果のサマリーを保存しました: {summary_path}")
        
        config_doc_path = save_config_documentation()
        logger.info(f"📄 設定ドキュメントを更新しました: {config_doc_path}")
    except Exception as e:
        logger.exception("ドキュメント生成中にエラーが発生しました")
        logger.info("処理は完了しています...")
    
    logger.info(f"🎉 全処理完了！ 処理対象: {len(documents)}社, 成功: {len(final_data)}社")
    return final_data

if TKINTER_AVAILABLE:
    def open_calendar(root, listbox, dates):
        """カレンダーを開いて日付を選択"""
        top = tk.Toplevel(root)
        top.title("日付を選択")
        
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd", width=100)
        cal.pack(pady=20)

        def select_date():
            date = cal.get_date()
            if date and date not in dates:  # 重複防止
                dates.append(date)
                listbox.insert(tk.END, date)
            top.destroy()
        
        tk.Button(top, text="OK", command=select_date).pack(pady=10)

    def delete_selected_date(listbox, dates):
        """リストから選択された日付を削除"""
        try:
            selected_index = listbox.curselection()[0]  # 選択されたインデックス
            selected_date = listbox.get(selected_index)  # 選択された日付
            listbox.delete(selected_index)  # Listboxから削除
            dates.remove(selected_date)  # datesリストから削除
        except IndexError:
            messagebox.showwarning("警告", "削除する日付を選択してください")

    def run_main(dates, company_conuts):
        global DATE_FOR_SHEET
        if not dates:
            messagebox.showerror("エラー", "最低1つの日付を入力してください")
            return
        for date in dates:
            DATE_FOR_SHEET = date
            main(company_conuts, start_date=date)


def run_gui():
    """Run the GUI interface if tkinter is available"""
    if not TKINTER_AVAILABLE:
        print("GUI not available. Use main() function directly.")
        return
        
    dates = []  # 入力された日付を保存
    company_conuts = 200

    # GUIのセットアップ
    root = tk.Tk()
    root.title("Edinetデータを取得する日付を選択してください。")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    add_button = tk.Button(frame, text="カレンダーから日付を選択", command=lambda: open_calendar(root, listbox, dates))
    add_button.pack(side=tk.LEFT, padx=5)

    listbox = tk.Listbox(root, height=5, width=100)
    listbox.pack(pady=10)

    delete_button = tk.Button(root, text="選択した日付を削除", command=lambda: delete_selected_date(listbox, dates))
    delete_button.pack(pady=5)

    run_button = tk.Button(root, text="実行", command=lambda: run_main(dates, company_conuts))
    run_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    # If GUI is available, run the GUI interface
    if TKINTER_AVAILABLE:
        run_gui()
    else:
        # Run command line interface
        print("GUI not available. Running with default settings...")
        result = main()
        print(f"Processing completed. Processed {len(result) if result else 0} companies.")