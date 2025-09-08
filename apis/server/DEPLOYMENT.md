# 🚀 Deployment Guide for Environmental Metrics Server

## 📋 Pre-GitHub Upload Checklist

### ✅ Cache Cleaning Completed
- [x] Removed `.DS_Store` files
- [x] Cleaned Python cache files (`__pycache__`, `*.pyc`)
- [x] Created comprehensive `.gitignore` files
- [x] No `node_modules` present (will be installed via `npm install`)

### 📁 File Structure Ready for GitHub
```
apis/server/
├── .gitignore              # Comprehensive ignore rules
├── client-example.js       # Complete client implementation
├── index.js               # Enhanced server with persistence & alerts
├── package.json           # Dependencies and scripts
├── README.md              # Comprehensive documentation
└── DEPLOYMENT.md          # This deployment guide
```

## 🔧 Installation Commands

### For Users Cloning from GitHub:
```bash
# Clone the repository
git clone <your-repo-url>
cd ACTORS/apis/server

# Install dependencies
npm install

# Start the server
npm start

# Or run in development mode
npm run dev

# Test the client
npm run client
```

## 📦 Package.json Scripts Available

```json
{
  "start": "node index.js",           # Production server
  "dev": "nodemon index.js",          # Development with auto-reload
  "client": "node client-example.js", # Run client example
  "clean": "rm -rf node_modules package-lock.json && npm install"
}
```

## 🌐 Server Endpoints

### REST API
- `GET /metrics` - Current metrics with thresholds
- `GET /metrics/history` - Historical data (paginated)
- `GET /thresholds` - All threshold configurations
- `GET /healthz` - Server health status
- `GET /routes` - API discovery

### WebSocket Events
- `metrics` - Real-time metric updates
- `alerts` - Threshold violation alerts

## 🔒 Security Considerations

### CORS Configuration
```javascript
const corsOptions = {
  origin: '*',  // Configure for production
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
};
```

### Environment Variables
```bash
PORT=3030  # Server port (default: 3030)
```

## 📊 Data Persistence

### Automatic File Creation
- `../data/metrics.json` - Current metrics
- `../data/metrics_history.json` - Historical data

### Data Directory Structure
```
apis/
├── data/                  # Auto-created
│   ├── metrics.json      # Current state
│   └── metrics_history.json # Historical records
└── server/               # Server code
```

## 🚨 Monitoring & Alerts

### Threshold Configuration
```javascript
const THRESHOLDS = {
  carbonFootprint: { min: 100, max: 200, unit: 'kg CO2' },
  waterSavings: { min: 20, max: 50, unit: 'liters' },
  energyEfficiency: { min: 70, max: 100, unit: '%' },
  confidence: { min: 80, max: 100, unit: '%' },
  waterdruckPsi: { min: 30, max: 80, unit: 'PSI' }
};
```

### Alert Severity Levels
- **Warning**: Value outside threshold range
- **Critical**: Value significantly outside range (>20% deviation)

## 🔄 Production Deployment

### PM2 (Recommended)
```bash
npm install -g pm2
pm2 start index.js --name "env-metrics"
pm2 startup
pm2 save
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3030
CMD ["npm", "start"]
```

### Environment Setup
```bash
# Production environment variables
export NODE_ENV=production
export PORT=3030
```

## 📈 Performance Optimization

### Memory Management
- In-memory storage for fast access
- Automatic history cleanup (max 1000 records)
- Efficient data structures for real-time updates

### Network Optimization
- WebSocket for real-time communication
- REST API for on-demand data
- Compressed JSON responses

## 🧪 Testing

### Manual Testing
```bash
# Test server health
curl http://localhost:3030/healthz

# Test metrics endpoint
curl http://localhost:3030/metrics

# Test historical data
curl "http://localhost:3030/metrics/history?limit=10"
```

### Client Testing
```bash
# Run the example client
npm run client
```

## 📝 GitHub Upload Notes

### Files Included
- ✅ All source code files
- ✅ Comprehensive documentation
- ✅ Package configuration
- ✅ Deployment guides

### Files Excluded (via .gitignore)
- ❌ `node_modules/` (install via npm)
- ❌ `data/` directory (auto-created at runtime)
- ❌ Cache files and temporary data
- ❌ OS-specific files (`.DS_Store`, etc.)
- ❌ IDE configuration files

### Repository Structure
```
ACTORS/
├── .gitignore              # Root-level ignore rules
├── apis/
│   ├── server/            # Environmental metrics server
│   │   ├── .gitignore     # Server-specific ignore rules
│   │   ├── index.js       # Main server file
│   │   ├── client-example.js # Client implementation
│   │   ├── package.json   # Dependencies
│   │   ├── README.md      # Documentation
│   │   └── DEPLOYMENT.md  # This file
│   └── [other API files]
└── [other project files]
```

## 🎯 Ready for GitHub Upload!

Your environmental metrics server is now:
- ✅ Cache-free and clean
- ✅ Properly documented
- ✅ Production-ready
- ✅ GitHub-optimized
- ✅ Easy to install and run

**Next Steps:**
1. Initialize git repository: `git init`
2. Add files: `git add .`
3. Commit: `git commit -m "Initial commit: Environmental Metrics Server v2.0"`
4. Create GitHub repository
5. Push: `git push origin main`

🌿 **Your environmental monitoring platform is ready to go live!** 🚀
