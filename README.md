# Fruit Image Classifier

A real-time Fruit Classification AI model with a modern, dynamic React Dashboard.

## 🚀 How to Run the Application

The application consists of two parts: the **Python Backend** and the **React Frontend**. You need to run both simultaneously in separate terminal windows.

### 1. Start the Backend (FastAPI + AI Models)
Open a new terminal and run:
```bash
cd backend
pip install -r requirements.txt  # (Only needed once)
uvicorn app:app --host 127.0.0.1 --port 8000
```
*Note: The first time you run this, it will download both the Fruit CNN and a "Gatekeeper" validation model (~600MB) to ensure building images or cats aren't mistaken for fruit.*

### 2. Start the Frontend Dashboard (React + Vite)
Open a second terminal and run:
```bash
cd frontend
npm install  # (Only needed once)
npm run dev
```
*The frontend will be running at http://localhost:5173*

---

## 📸 How to Use It
1. Once both servers are running, open your browser and go to **[http://localhost:5173](http://localhost:5173)**.
2. Drag and drop any fruit image (like an apple, banana, or orange) into the upload area.
3. Click the **"Identify Fruit"** button and watch the AI classify it in real-time!

## 🧠 Training Your Own Model (Optional)
If you want to train the model on your own dataset instead of using the pre-trained fallback model:
1. Place your images in `backend/dataset/train/<fruit_name>/...`
2. Run the training script:
```bash
cd backend
python train.py --epochs 10 --batch_size 32
```
This will generate a `fruit_classifier_best.pth` file which the backend will automatically load for real-time inference.
