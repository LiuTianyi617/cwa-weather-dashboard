import requests
import streamlit as st
import pandas as pd
import os

# 從 Streamlit Cloud Secrets (環境變數) 讀取金鑰
API_KEY = os.environ.get("CWA_API_KEY") 
DATASTORE_ID = "F-C0032-001" 

# --- 數據抓取與處理函式 (與之前提供的一致，在此省略細節以保持簡潔) ---

def fetch_and_process_data(selected_location):
    # 檢查 API Key 是否已設定
    if not API_KEY:
        st.error("❌ 錯誤：CWA API 金鑰未設定。請在 Streamlit Cloud Secrets 中設定 CWA_API_KEY。")
        return None, None
    
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATASTORE_ID}?Authorization={API_KEY}&locationName={selected_location}"

    try:
        res = requests.get(url, verify=False)
        data = res.json()

        if res.status_code == 200 and data.get("success") == "true":
            # ... (抓取並處理數據邏輯)
            location = data["records"]["location"][0]
            
            # 處理表格數據
            table_data = []
            for element in location["weatherElement"]:
                name = element["elementName"]
                value = element["time"][0]["parameter"]["parameterName"]
                table_data.append({"天氣要素": name, "預報值": value})
            
            # 處理圖表數據 (MinT/MaxT)
            chart_data = []
            min_temp_element = next((e for e in location["weatherElement"] if e["elementName"] == "MinT"), None)
            max_temp_element = next((e for e in location["weatherElement"] if e["elementName"] == "MaxT"), None)
            
            if min_temp_element and max_temp_element:
                for i in range(len(min_temp_element["time"])):
                    time_point = pd.to_datetime(min_temp_element["time"][i]["startTime"]).strftime("%H:%M")
                    min_temp = int(min_temp_element["time"][i]["parameter"]["parameterName"])
                    max_temp = int(max_temp_element["time"][i]["parameter"]["parameterName"])
                    
                    chart_data.append({"時間": time_point, "最低溫 (MinT)": min_temp, "最高溫 (MaxT)": max_temp})
            
            df_chart = pd.DataFrame(chart_data).set_index("時間")
            df_table = pd.DataFrame(table_data)
            
            return df_table, df_chart

        else:
            st.error(f"API 請求失敗: {data.get('message') if data else res.text}")
            return None, None

    except Exception as e:
        st.error(f"應用程式錯誤: {e}")
        return None, None


def run_streamlit_app():
    st.set_page_config(layout="wide")
    st.title("🌧️ 台灣氣象資料 Dashboard")
    st.markdown("---")

    locations = ["臺北市", "臺中市", "高雄市", "新北市", "桃園市", "臺南市", "基隆市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"]
    selected_location = st.selectbox("選擇城市", locations)

    df_table, df_chart = fetch_and_process_data(selected_location)

    if df_table is not None and df_chart is not None:
        st.subheader(f"📍 {selected_location} 36小時溫度趨勢")
        st.caption("未來 36 小時最低溫與最高溫變化")
        st.line_chart(df_chart)

        st.subheader("📋 詳細天氣要素")
        st.table(df_table)

if __name__ == "__main__":
    run_streamlit_app()