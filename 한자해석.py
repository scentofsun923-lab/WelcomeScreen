import streamlit as st
import os
import json
from datetime import datetime
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account

st.set_page_config(page_title="24시간 한자 판독기", page_icon="🈩")
st.title("📱 24/7 전서체·초서체 판독기")

# --- 1. [최종 대안] 원본 JSON 통째로 읽어오기 ---
if "google_json" in st.secrets:
    # 문자열 기호 수정 없이, 안전하게 보호된 원본 JSON을 그대로 딕셔너리로 변환합니다.
    info = json.loads(st.secrets["google_json"])
    credentials = service_account.Credentials.from_service_account_info(info)
    client = vision.ImageAnnotatorClient(credentials=credentials)
else:
    client = vision.ImageAnnotatorClient()

# --- 2. 스마트폰 전용 화면 구성 ---
st.write("야외나 외부에서 사진을 찍어 올리면 구글 AI가 즉시 판독하고 데이터를 저장합니다.")

uploaded_file = st.file_uploader("📷 한자/도장 사진 촬영 또는 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="촬영된 이미지", use_column_width=True)
    
    # 임시 저장 및 API 전달
    temp_path = "temp_upload.png"
    image.save(temp_path)

    with open(temp_path, "rb") as image_file:
        content = image_file.read()

    vision_image = vision.Image(content=content)
    
    # AI 판독 수행
    with st.spinner("구글 AI가 분석 중입니다..."):
        response = client.document_text_detection(image=vision_image)
        
    predicted_text = ""
    if response.text_annotations:
        predicted_text = response.text_annotations[0].description.strip()
        st.success(f"🔍 **AI 추측 결과:** `{predicted_text}`")
    else:
        st.warning("인식된 글자가 없습니다. 정답을 직접 입력해 주세요.")

    # 사용자 정답 확인 및 축적
    st.markdown("---")
    correct_label = st.text_input("📝 정답 한자 확인/수정", value=predicted_text)

    if st.button("💾 데이터베이스에 영구 축적"):
        if correct_label.strip():
            # 저장 폴더 생성
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
