import requests
import json
import os
from datetime import datetime
from pathlib import Path

# EDINET API から有価証券報告書一覧を取得
def fetch_edinet_documents(yyyy_mm_dd="2024-03-10", EDINET_API_KEY="", save_json=True):
    from .logger import logger, log_user_error, log_user_warning, log_user_success
    
    url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }
    params = {
        "date": yyyy_mm_dd,
        "type": 2,  # 有価証券報告書
        "Subscription-Key": EDINET_API_KEY
    }
    
    try:
        # リクエスト送信➡レスポンス取得
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 403:
            log_user_error("APIアクセスが禁止されています。認証情報を確認してください")
            return []
        
        response.raise_for_status()  # HTTPエラーが発生した場合は例外を発生させる
        json_data = response.json()
        
        # Save JSON response if requested
        if save_json:
            try:
                json_dir = Path(__file__).parent.parent / 'json'
                json_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"edinet_documents_{yyyy_mm_dd}_{timestamp}.json"
                json_path = json_dir / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                logger.info(f"✅ JSON response saved to: {json_path}")
            except Exception as e:
                log_user_warning(
                    "JSON保存中にエラーが発生しましたが、処理を続けます",
                    f"json_path: {json_path}"
                )
        
        documents = []
        
        # json data を処理して documents に辞書として格納
        for doc in json_data.get("results", []):
            try:
                if doc["docTypeCode"] == "120":  # 有価証券報告書のみ取得
                    documents.append({
                        "EDINETコード": doc["edinetCode"],
                        "fundコード": doc["fundCode"],
                        "企業名": doc["filerName"],
                        "会計期間開始": doc["periodStart"],
                        "会計期間終了": doc["periodEnd"],
                        "書類提出日": doc["submitDateTime"],
                        "書類ID": doc["docID"],
                        "XBRLダウンロードURL": f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc['docID']}?type=1"
                    })
                    # docのキーと値もそのまま追加
                    documents[-1].update(doc)
            except Exception as e:
                log_user_error(
                    f"書類データ処理中にエラーが発生しました: {doc.get('filerName', 'Unknown')}",
                    f"doc keys: {list(doc.keys()) if doc else 'None'}",
                    e
                )
                continue  # エラーが発生した書類はスキップして続行
        
        logger.info(f"✅ {len(documents)}件の有価証券報告書を取得しました")
        return documents
        
    except requests.exceptions.RequestException as e:
        log_user_error(
            f"EDINET API リクエスト中にネットワークエラーが発生しました",
            f"date: {yyyy_mm_dd}, API_URL: {url}",
            e
        )
        return []
    except Exception as e:
        log_user_error(
            f"EDINET書類取得中に予期しないエラーが発生しました",
            f"date: {yyyy_mm_dd}",
            e
        )
        return []


