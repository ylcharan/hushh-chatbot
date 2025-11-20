# venv setup

```
cd backend

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
python setup_openai.py # configure API key
python seed_knowledge.py # seed sample data
python app.py

# Frontend

cd frontend
npm install
npm run dev
```
