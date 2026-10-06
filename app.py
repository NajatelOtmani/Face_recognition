import numpy as np, cv2, streamlit as st
from src.recognizer import load_gallery, identify, draw

st.title("Face Recognition")
thr = st.slider("Threshold", min_value=0.30, max_value=0.95, value=0.342, step=0.01)
file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

gallery = st.cache_resource(load_gallery)()
if file:
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    res = identify(img, gallery, thr)
    st.image(cv2.cvtColor(draw(img, res), cv2.COLOR_BGR2RGB))
    st.table([{"name": r["name"], "score": round(r["score"], 3)} for r in res])