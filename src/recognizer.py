import os
import numpy as np
import cv2
from deepface import DeepFace

MODEL = "ArcFace"
DETECTOR = "yunet"


def _normalize(v):
    v = np.asarray(v, dtype=np.float32)
    return v / np.linalg.norm(v)


def build_gallery(folder="data/gallery", out="gallery.npz"):
    """folder/<person_name>/*.jpg  ->  saves embeddings + labels."""
    names, embs = [], []
    for person in sorted(os.listdir(folder)):
        pdir = os.path.join(folder, person)
        if not os.path.isdir(pdir):
            continue
        for fn in os.listdir(pdir):
            try:
                rep = DeepFace.represent(
                    img_path=os.path.join(pdir, fn),
                    model_name=MODEL,
                    detector_backend=DETECTOR,
                    enforce_detection=True,   # skip photos with no face
                )[0]
                embs.append(_normalize(rep["embedding"]))
                names.append(person)
            except ValueError:
                print(f"No face found in {person}/{fn}, skipped")
    np.savez(out, embs=np.array(embs), names=np.array(names))


def load_gallery(path="gallery.npz"):
    d = np.load(path)
    return d["embs"], d["names"]


def identify(img_bgr, gallery, threshold=0.342):
    """Detect every face, return name (or 'Unknown'), score and box."""
    G, names = gallery
    results = []
    try:
        faces = DeepFace.represent(
            img_path=img_bgr,
            model_name=MODEL,
            detector_backend=DETECTOR,
            enforce_detection=True,
        )
    except ValueError:        # no face in the image
        return results

    for f in faces:
        e = _normalize(f["embedding"])
        sims = G @ e                      # cosine similarity to every gallery face
        best = int(np.argmax(sims))
        score = float(sims[best])
        name = str(names[best]) if score >= threshold else "Unknown"
        a = f["facial_area"]
        results.append({"name": name, "score": score,
                        "box": (a["x"], a["y"], a["w"], a["h"])})
    return results


def draw(img_bgr, results):
    out = img_bgr.copy()
    for r in results:
        x, y, w, h = r["box"]
        color = (0, 200, 0) if r["name"] != "Unknown" else (0, 0, 255)
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
        cv2.putText(out, f'{r["name"]} {r["score"]:.2f}', (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return out