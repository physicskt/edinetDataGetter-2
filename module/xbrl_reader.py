import re
import os
from lxml import etree, html
try:
    from .logger import *
except ImportError:
    from logger import *

def extract_values_from_xbrl(xbrl_file:str, target_block_name:str, search_words_list:list[str]):
    """
    XBRL ファイルから指定のブロック内の検索ワードに該当する値を抽出する。

    Args:
        xbrl_file (str): XBRLファイルのパス。
        target_block_name (str): 抽出対象のブロック名。
            - "StatementOfIncomeAndRetainedEarningsTextBlock"  # 損益計算書
            - "BalanceSheetTextBlock"  # 貸借対照表
        search_words_list (List[str]): 抽出したいキーワードのリスト。\n
            例:
            - ["発行株式数", "売上高", "期末剰余金又は期末欠損金"]
            - ["純資産合計", "負債純資産合計"]

    Returns:
        Dict[str, str]: 検索ワードとそれに対応する抽出値の辞書。

    Example:
        extract_values_from_xbrl("sample.xbrl", "BalanceSheetTextBlock", ["純資産合計", "負債純資産合計"])
        -> {"純資産合計": "100億円", "負債純資産合計": "500億円"}
    """
    try:
        # XBRLファイルを解析
        xbrl_file = os.path.abspath(xbrl_file)
        tree = etree.parse(xbrl_file)
        root = tree.getroot()

        # 名前空間を取得
        ns = root.nsmap

        # 指定したテキストブロックを取得
        target_block = root.find(f".//{{*}}{target_block_name}", namespaces=ns)

        if target_block is None or not target_block.text:
            logger.warning(f"❌ {target_block_name} が見つかりませんでした: {xbrl_file}")
            return {}

        # HTMLとして解析
        target_html = html.fromstring(target_block.text)

        # 表のデータを取得
        tables = target_html.findall(".//table")

        if not tables:
            logger.warning(f"❌ 表（<table>）が見つかりませんでした: {target_block_name}")
            return {}

        logger.info(f"✅ {len(tables)} 個の表が見つかりました: {target_block_name}")

        # 結果を格納する辞書
        extracted_values = {word: None for word in search_words_list}

        # すべての表を解析
        for table_idx, table in enumerate(tables):
            try:
                rows = table.findall(".//tr")
                for row_idx, row in enumerate(rows):
                    try:
                        cells = [cell.text_content().strip() for cell in row.findall(".//td")] + \
                                [cell.text_content().strip() for cell in row.findall(".//th")]
                        logger.debug(f"Table {table_idx}, Row {row_idx}: {cells}")  # デバッグ用

                        if not cells:
                            continue

                        # すべてのワードについて処理
                        for word in search_words_list:
                            if extracted_values[word] is not None:
                                continue

                            # 完全一致しない場合はスキップ
                            if word in cells:
                                index = cells.index(word)
                                if index + 1 >= len(cells):
                                    continue
                                extracted_value = re.sub(r"^[^\x00-\x7F]+", "", cells[-1])
                                extracted_value = re.sub(r"[^\d-]", "", extracted_value)
                                if "△" in cells[-1]:
                                    extracted_value = "-" + extracted_value
                                extracted_values[word] = int(extracted_value) if extracted_value else None
                                logger.info(f"✅ 完全一致で抽出: {word} = {extracted_values[word]}")
                                break  # このrowで見つかったので次のrowへ

                            # 部分一致
                            found = False
                            for i, cell in enumerate(cells):
                                if word not in cell or i + 1 >= len(cells):
                                    continue
                                extracted_value = re.sub(r"^[^\x00-\x7F]+", "", cells[-1])
                                extracted_value = re.sub(r"[^\d-]", "", extracted_value)
                                if "△" in cells[-1]:
                                    extracted_value = "-" + extracted_value
                                extracted_values[word] = int(extracted_value) if extracted_value else None
                                logger.info(f"✅ 部分一致で抽出: {word} = {extracted_values[word]}")
                                found = True
                                break
                            if found:
                                break  # このrowで見つかったので次のrowへ

                    except Exception as e:
                        logger.exception(f"行解析中にエラー: Table {table_idx}, Row {row_idx}")
                        continue
            except Exception as e:
                logger.exception(f"表解析中にエラー: Table {table_idx}")
                continue

        logger.info(f"✅ 抽出完了: {target_block_name} -> {extracted_values}")
        return extracted_values
        
    except etree.XMLSyntaxError as e:
        logger.exception(f"XBRL XMLパースエラー: {xbrl_file}")
        return {}
    except Exception as e:
        logger.exception(f"XBRL値抽出中に予期しないエラー: {xbrl_file}, {target_block_name}")
        return {}


if __name__ == "__main__":
    # XBRLファイルのパス
    dir = os.path.dirname(os.path.abspath(__file__))
    xbrl_path = os.path.join(dir, "..", "xbrl_files", "XBRL", "PublicDoc", "jpsps070000-asr-001_G15227-000_2024-12-10_01_2025-03-03.xbrl")
    # 取得したいデータのリスト
    search_words = ["発行株式数", "売上高", "当期純利益又は当期純損失", "期末剰余金又は期末欠損金"]
    # 抽出対象のテキストブロック名
    block_name = "StatementOfIncomeAndRetainedEarningsTextBlock"  # 例: 損益計算書
    # XBRLからデータを取得
    extracted_data = extract_values_from_xbrl(xbrl_path, block_name, search_words)    
    # 結果を表示
    print(f"✅ {block_name} からの抽出結果:")
    print(extracted_data)

    log_long_msg("次👇")
    search_words = ["純資産合計","負債純資産合計"]
    block_name = "BalanceSheetTextBlock"
    extracted_data = extract_values_from_xbrl(xbrl_path, block_name, search_words)    
    print(f"✅ {block_name} からの抽出結果:")
    print(extracted_data)

    log_long_msg("次👇")
    search_words = ["当中間会計期間末株式数","配当金の総額","1株当たり配当額",]
    block_name = "NotesFinancialInformationOfInvestmentTrustManagementCompanyEtcTextBlock"
    extracted_data = extract_values_from_xbrl(xbrl_path, block_name, search_words)    
    print(f"✅ {block_name} からの抽出結果:")
    print(extracted_data)


    