import streamlit as st
import requests
import datetime
from unidecode import unidecode

# --- 날씨 설명 변환 데이터 (API 응답을 한글로) ---
ENG_TO_KOR_WEATHER = {
    "Sunny": "맑음 ☀️",
    "Partly cloudy": "구름 조금 ⛅",
    "Cloudy": "흐림 ☁️",
    "Overcast": "구름 많음 🌥️",
    "Mist": "안개 🌫️",
    "Patchy rain possible": "간헐적 비 가능성 🌦️",
    "Patchy rain nearby": "주변 지역 비 🌦️",
    "Clear": "맑음 ☀️",
    "Light rain": "비 🌧️",
    "Moderate rain": "보통 비 🌧️",
    "Heavy rain": "강한 비 🌧️",
    "Light rain shower": "가벼운 소나기 🌦️",
    "Moderate or heavy rain shower": "보통/강한 소나기 🌧️",
    "Fog": "안개 🌫️",
    "Light snow": "눈 🌨️",
    "Moderate snow": "보통 눈 🌨️",
    "Heavy snow": "강한 눈 🌨️",
    "Blizzard": "눈보라 🌨️",
}


# --- 앱의 기본 구조 설정 ---
st.set_page_config(
    page_title="오늘의 날씨 앱",
    page_icon="🌤️",
)

# 앱 제목 설정
st.title("오늘의 날씨는!!? 🌦️")

# --- 핵심 기능: 날씨 정보 가져오기 ---
def get_weather(city):
    if not city:
        st.warning("도시 이름을 입력해주세요.")
        return None
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        # API가 도시를 찾지 못했을 때 (404 Not Found 오류 등)
        st.error(f"'{city}' 도시의 날씨 정보를 찾을 수 없습니다. 도시 이름을 확인해주세요.")
        return None
    except requests.exceptions.RequestException as e:
        # 그 외 네트워크 오류나 API 서버 문제 발생 시
        st.error(f"날씨 정보를 가져오는 데 실패했습니다: {e}")
        return None

# --- 세션 상태(Session State) 초기화 ---
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'city' not in st.session_state:
    st.session_state.city = ""

# --- 사용자 인터페이스(UI) ---
st.subheader("알고 싶은 도시를 검색해보세요! 🏙️")

city_input = st.text_input(
    "국내외 도시 이름을 한글로 입력하세요 (예: 여수, 전주, 파리)",
    placeholder="여기에 도시 이름 입력..."
)

if st.button("날씨 조회하기 🔍"):
    # unidecode를 사용해 한글 입력을 영문으로 자동 변환 (예: "여수" -> "Yeosu")
    city_to_search = unidecode(city_input)
    
    with st.spinner(f"'{city_input}'의 날씨 정보를 가져오는 중..."):
        weather_info = get_weather(city_to_search)
        
        if weather_info:
            st.session_state.weather_data = weather_info
            # 화면에는 사용자가 입력한 한글 도시 이름을 그대로 보여주기 위해 저장
            st.session_state.city = city_input
        else:
            st.session_state.weather_data = None
            st.session_state.city = ""

# --- 결과 표시 ---
if st.session_state.weather_data:
    data = st.session_state.weather_data
    city_name = st.session_state.city
    
    current_condition = data['current_condition'][0]
    today_forecast = data['weather'][0]

    today_date = datetime.date.today().strftime("%Y년 %m월 %d일")
    st.subheader(f"✅ {today_date} '{city_name}'의 날씨 정보입니다.")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="현재 기온", value=f"{current_condition['temp_C']} °C")
        st.metric(label="체감 온도", value=f"{current_condition['FeelsLikeC']} °C")

    with col2:
        # 영문 날씨 설명을 한글로 변환
        weather_description_eng = current_condition['weatherDesc'][0]['value']
        weather_description_kor = ENG_TO_KOR_WEATHER.get(weather_description_eng, weather_description_eng)
        st.metric(label="현재 날씨", value=weather_description_kor)
        st.metric(label="풍속", value=f"{current_condition['windspeedKmph']} km/h")

    st.divider()

    st.write(f"**오늘의 예상 기온:** 최저 {today_forecast['mintempC']}°C / 최고 {today_forecast['maxtempC']}°C")
    st.info("다른 도시가 궁금하면 위 검색창에 입력 후 다시 조회해보세요.");