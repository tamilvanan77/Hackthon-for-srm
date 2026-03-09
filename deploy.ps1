# Deploy the Student Warning system to the network
Write-Host "🚀 Starting Deployment of Student Warning AI System..." -ForegroundColor Cyan

# 1. Install dependencies
Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# 2. Run database setup (optional if already setup)
Write-Host "🗂️ Setting up database..." -ForegroundColor Yellow
python setup_db.py

# 3. Generate initial dataset if missing
Write-Host "📊 Generating data..." -ForegroundColor Yellow
python generate_data.py

# 4. Run Streamlit on 0.0.0.0 for network access
Write-Host "🌐 Launching Application on the Network..." -ForegroundColor Green
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
