from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from PIL import Image
import io

app = FastAPI(title="Student Fruit Classifier API")

# Enable CORS for the frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simplified Fruit Database for Students (Just Color & Taste)
FRUIT_FEATURES = {
    "apple": {"color": "Red or Green", "taste": "Sweet and crisp", "color_hex": "#ef4444"},
    "banana": {"color": "Yellow", "taste": "Sweet and creamy", "color_hex": "#facc15"},
    "orange": {"color": "Orange", "taste": "Sweet and citrusy", "color_hex": "#f97316"},
    "strawberry": {"color": "Red", "taste": "Sweet and juicy", "color_hex": "#f43f5e"},
    "lemon": {"color": "Yellow", "taste": "Very sour", "color_hex": "#fef08a"},
    "pineapple": {"color": "Yellow/Brown", "taste": "Sweet and tangy", "color_hex": "#eab308"},
    "watermelon": {"color": "Green (Outside) / Red (Inside)", "taste": "Sweet and watery", "color_hex": "#fb7185"},
    "mango": {"color": "Yellow/Orange", "taste": "Very sweet and tropical", "color_hex": "#fbbf24"},
    "pomegranate": {"color": "Dark Red", "taste": "Sweet and tart", "color_hex": "#be123c"},
    "grape": {"color": "Purple or Green", "taste": "Sweet and juicy", "color_hex": "#9333ea"},
    "pear": {"color": "Green or Yellow", "taste": "Sweet and soft", "color_hex": "#a3e635"},
    "kiwi": {"color": "Brown (Outside) / Green (Inside)", "taste": "Tangy and sweet", "color_hex": "#65a30d"},
    "peach": {"color": "Pinkish Orange", "taste": "Sweet and juicy", "color_hex": "#fca5a5"},
}

def get_fruit_features(fruit_name):
    name_lower = fruit_name.lower()
    for key in FRUIT_FEATURES:
        if key in name_lower:
            return FRUIT_FEATURES[key]
    return {"color": "Unknown", "taste": "Unknown", "color_hex": "#3b82f6"}

print("Initializing Highly Accurate HuggingFace Models...")
try:
    # 1. Load Zero-Shot Classification Gatekeeper Model
    print("Loading Gatekeeper Validation Model...")
    gatekeeper = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
    
    # 2. Load dedicated fruit classifier
    print("Loading Primary Fruit Vision CNN...")
    fruit_classifier = pipeline("image-classification", model="jazzmacedo/fruits-and-vegetables-detector-36")
    
    is_model_loaded = True
    print("Models loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    is_model_loaded = False


@app.get("/")
def read_root():
    return {"status": "ok", "message": "API Running", "model_ready": is_model_loaded}

@app.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    if not is_model_loaded:
        raise HTTPException(status_code=500, detail="Vision AI Model is still loading or failed to load.")
        
    try:
        contents = await file.read()
        try:
            image = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception:
            raise HTTPException(status_code=400, detail="The file uploaded is not a valid image.")
        
        # --- 1. VALIDATION PHASE ---
        # First, we ask the gatekeeper model to determine if the image actually contains a fruit
        valid_categories = ["a close-up photo of a fruit or vegetable", "a photo of something else like a building, car, person, animal, or object"]
        
        validation_results = gatekeeper(image, candidate_labels=valid_categories)
        best_category = validation_results[0]['label']
        
        if "something else" in best_category.lower():
            # Stop right here, tell the frontend it's an invalid image
            return {
                "valid_fruit": False,
                "error_message": "Hmm, that looks like something else (a building, car, animal, etc). I only know about fruits!"
            }
        
        # --- 2. CLASSIFICATION PHASE ---
        # If the gatekeeper passed it, send the image to the dedicated Fruit CNN
        predictions = fruit_classifier(image)
        
        # Best prediction
        top_prediction = predictions[0]
        fruit_name = top_prediction['label'].capitalize()
        confidence = top_prediction['score']
        
        # Standardize names (e.g. remove underscores)
        fruit_name = fruit_name.replace("_", " ")
        
        # Edge case: To prevent "Corn" from occasionally overriding on specific datasets
        if confidence < 0.60:
             return {
                 "valid_fruit": False,
                 "error_message": "I'm not exactly sure what fruit that is. Could you try a clearer picture?"
             }
        
        features = get_fruit_features(fruit_name)

        return {
            "valid_fruit": True,
            "fruit_name": fruit_name,
            "confidence": round(confidence * 100, 2),
            "features": features
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
