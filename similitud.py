


from sentence_transformers import SentenceTransformer, util
from torchvision import models, transforms
from PIL import Image
import torch, requests
from io import BytesIO
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta, timezone

text_model = SentenceTransformer('all-MiniLM-L6-v2')
image_model = models.mobilenet_v2(weights="IMAGENET1K_V1").features.eval()


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def get_image_embedding(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        tensor = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor()
        ])(img).unsqueeze(0)
        with torch.no_grad():
            features = image_model(tensor)
        return features.flatten()
    except Exception as e:
        print("❌ Error al procesar imagen:", e)
        raise ValueError("Error en la imagen: " + str(e))

# Mensaje de tiempo transcurrido
def tiempo_transcurrido(diferencia):
    if diferencia.days > 0:
        return f"hace {diferencia.days} días"
    horas = diferencia.seconds // 3600
    if horas > 0:
        return f"hace {horas} horas"
    minutos = (diferencia.seconds % 3600) // 60
    if minutos > 0:
        return f"hace {minutos} minutos"
    return "hace unos segundos"


def verificar_incidente_nuevo(nuevo, anteriores):
    try:
        # Validación de datos de entrada
        for campo in ["description", "image_url", "latitude", "longitude"]:
            if campo not in nuevo or nuevo[campo] is None:
                raise ValueError(f"El campo '{campo}' es requerido y no puede ser null")

        lat1 = float(nuevo["latitude"])
        lon1 = float(nuevo["longitude"])
        desc1 = nuevo["description"]
        url_img = nuevo["image_url"]

        emb_text_nuevo = text_model.encode(desc1, convert_to_tensor=True)
        emb_img_nuevo = get_image_embedding(url_img)

    except Exception as e:
        print("❌ Error en validación inicial:", e)
        raise ValueError("Datos de entrada inválidos: " + str(e))

    for inc in anteriores:
        try:
            lat2 = inc.get("latitude")
            lon2 = inc.get("longitude")

            # Validar que existan antes de convertir
            if lat2 is None or lon2 is None:
                print(f"⚠️ Coordenadas inválidas del incidente anterior: {lat2}, {lon2}")
                continue

            lat2 = float(lat2)
            lon2 = float(lon2)
            dist = haversine(lat1, lon1, lat2, lon2)
            if dist > 6:
                continue
            print(f"📍 Distancia entre coordenadas: {dist:.2f} metros")
            # if dist <= 5:
            #     print(f"❌ Muy cerca: {dist:.2f} metros. Posible duplicado.")
            #     return True, inc, 0.0

            tiempo = inc.get("report_date")
            if not tiempo:
                continue
            tiempo_inc = tiempo.replace(tzinfo=timezone.utc)
            # if (datetime.now(timezone.utc) - tiempo_inc) > timedelta(minutes=30):
            #     continue
            #  if (datetime.now(timezone.utc) - tiempo_inc) > timedelta(days=1):
            #     continue

            if (datetime.now(timezone.utc) - tiempo_inc) > timedelta(hours=24):
                continue

            emb_text_ant = text_model.encode(inc["description"], convert_to_tensor=True)
            sim_text = float(util.pytorch_cos_sim(emb_text_nuevo, emb_text_ant)[0][0])

            emb_img_ant = get_image_embedding(inc["image_url"])
            sim_img = float(util.pytorch_cos_sim(emb_img_nuevo.unsqueeze(0), emb_img_ant.unsqueeze(0))[0][0])

            score = (sim_text + sim_img) / 2
            print(f"🧠 Score IA: {score:.2f} (text: {sim_text:.2f}, image: {sim_img:.2f})")

            # if score > 0.75:
            #     return True, inc, score
            # if sim_text >= 0.75 or sim_img >= 0.75 or score >= 0.75:
            #     return True, inc, score

            if sim_text >= 0.75 or sim_img >= 0.75 or score >= 0.75:
                return True, {
                    "description": inc["description"],
                    "image_url": inc["image_url"],
                    "latitude": inc["latitude"],
                    "longitude": inc["longitude"],
                    "report_date": inc["report_date"],
                    "hace_tiempo": tiempo_transcurrido(datetime.now(timezone.utc) - tiempo_inc)
                }, round(score, 2)

        except Exception as e:
            print("⚠️ Error procesando incidente anterior:", e)
            continue

    return False, None, 0.0


