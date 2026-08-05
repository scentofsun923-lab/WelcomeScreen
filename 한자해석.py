import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime

st.set_page_config(page_title="24시간 전서체 AI 판독기", page_icon="🈩")
st.title("📱 24/7 전서체·초서체 AI 판독기 (Gemini Vision)")

# --- Gemini API 키 설정 (단순 문자열 키) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Streamlit Secrets에 GEMINI_API_KEY를 설정해 주세요.")

st.write("Gemini 시각 지능 모델이 전서체, 초서체, 도장의 한자를 정밀 분석합니다.")

uploaded_file = st.file_uploader("📷 한자/도장 사진 촬영 또는 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="촬영된 이미지", use_container_width=True)

    if st.button("🔍 Gemini AI 정밀 분석"):
        with st.spinner("Gemini가 자형 구조와 부수를 시각적으로 분석 중입니다..."):
            try:
                # Gemini 시각 지능 모델 호출
                model = genai.GenerativeModel('gemini-pro-vision')
                
                prompt = """
                당신은 고문서 및 전서체, 초서체, 인장(도장) 한자 전문가입니다.
                업로드된 이미지를 정밀 분석하여 다음 형식으로 답변해 주세요:
                
                1. **추측 한자 (정자/楷書):** [가장 유력한 한자 1~2개]
                2. **자형 및 부수 구조 분석:** [좌우/위아래 구성 요소 및 전서체 특성 설명]
                3. **글자의 기본 의미:** [한자 뜻 풀이]
                """
                
                response = model.generate_content([prompt, image])
                st.success("✅ **Gemini AI 판독 완료!**")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")

    # 데이터 축적 파트
    st.markdown("---")
    correct_label = st.text_input("📝 최종 정답 한자 입력 (내 데이터셋 저장용)")

    if st.button("💾 데이터베이스에 영구 축적"):
        if correct_label.strip():
            dataset_dir = "./my_accumulated_dataset"
            char_dir = os.path.join(dataset_dir, correct_label.strip())
            os.makedirs(char_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(char_dir, f"{correct_label}_{timestamp}.png")
            image.save(save_path)
            
            st.balloons()
            st.success(f"✅ [{correct_label}] 폴더에 성공적으로 축적되었습니다!")
        else:
            st.error("저장할 한자 이름을 입력해 주세요.")
