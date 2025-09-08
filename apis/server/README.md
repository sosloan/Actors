# 🌿 Environmental Metrics Server v2.0

En förbättrad real-time miljöövervakningsserver med datapersistens, historisk data och aviseringar.

## 🚀 Funktioner

### ✨ Nya Funktioner
- **📁 Datapersistens** - Automatisk sparning till JSON-filer
- **📊 Historisk Data** - Lagring av upp till 1000 historiska poster
- **🚨 Tröskelvärdesövervakning** - Automatiska varningar vid avvikelser
- **💾 Graceful Shutdown** - Säker avstängning med datasparning
- **📈 Förändringsspårning** - Spårar förändringar mellan uppdateringar
- **🔍 Förbättrad API** - Nya endpoints för historik och tröskelvärden

### 🎯 Miljömetriker
- **Carbon Footprint** - Kolavtryck i kg CO2
- **Water Savings** - Vattenbesparingar i liter
- **Energy Efficiency** - Energieffektivitet i procent
- **Confidence** - Systemtillförlitlighet i procent
- **Water Pressure** - Vattentryck i PSI

## 🛠️ Installation

```bash
cd apis/server
npm install
```

## 🏃‍♂️ Körning

### Utveckling
```bash
npm run dev
```

### Produktion
```bash
npm start
```

## 📡 API Endpoints

### REST API

#### `GET /metrics`
Hämtar aktuella metriker med tröskelvärden
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "metrics": {
    "carbonFootprint": 150.5,
    "waterSavings": 30.2,
    "energyEfficiency": 85.7,
    "confidence": 92.4,
    "waterdruckPsi": 62.0
  },
  "thresholds": { ... }
}
```

#### `GET /metrics/history?limit=100&offset=0`
Hämtar historisk data med paginering
```json
{
  "data": [
    {
      "timestamp": "2024-01-15T10:30:00.000Z",
      "metrics": { ... },
      "changes": { ... }
    }
  ],
  "total": 1000,
  "limit": 100,
  "offset": 0
}
```

#### `GET /thresholds`
Hämtar alla tröskelvärden
```json
{
  "carbonFootprint": {
    "min": 100,
    "max": 200,
    "unit": "kg CO2"
  }
}
```

#### `GET /healthz`
Utökad hälsokontroll
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "uptime": 3600,
  "memory": { ... },
  "historyRecords": 500
}
```

#### `GET /routes`
API-upptäckt och dokumentation

### WebSocket Events

#### `metrics`
Real-time metriker med förändringar
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "metrics": { ... },
  "changes": { ... },
  "alerts": [ ... ]
}
```

#### `alerts`
Varningar vid tröskelvärdesöverskridningar
```json
[
  {
    "metric": "waterdruckPsi",
    "value": 85.2,
    "threshold": { "min": 30, "max": 80, "unit": "PSI" },
    "severity": "warning",
    "message": "waterdruckPsi is 85.2 PSI (WARNING: outside 30-80 range)",
    "timestamp": "2024-01-15T10:30:00.000Z"
  }
]
```

## 🔧 Konfiguration

### Miljövariabler
```bash
PORT=3030  # Server port (standard: 3030)
```

### Tröskelvärden
Tröskelvärdena kan anpassas i `THRESHOLDS`-objektet:

```javascript
const THRESHOLDS = {
  carbonFootprint: { min: 100, max: 200, unit: 'kg CO2' },
  waterSavings: { min: 20, max: 50, unit: 'liters' },
  energyEfficiency: { min: 70, max: 100, unit: '%' },
  confidence: { min: 80, max: 100, unit: '%' },
  waterdruckPsi: { min: 30, max: 80, unit: 'PSI' }
};
```

### Uppdateringsintervaller
```javascript
const CONFIG = {
  UPDATE_INTERVAL: 3000,    // Metriker uppdateras var 3:e sekund
  SAVE_INTERVAL: 60000,     // Data sparas var minut
  MAX_HISTORY: 1000         // Max antal historiska poster
};
```

## 📁 Datafiler

Servern skapar automatiskt följande filer i `../data/`:

- `metrics.json` - Aktuella metriker
- `metrics_history.json` - Historisk data

## 🧪 Klient-exempel

Se `client-example.js` för ett komplett exempel på hur man ansluter till servern:

```javascript
const EnvironmentalMetricsClient = require('./client-example');

const client = new EnvironmentalMetricsClient('http://localhost:3030');
await client.connect();
```

## 🚨 Aviseringssystem

### Severity-nivåer
- **warning** - Värde utanför tröskelvärdesområdet
- **critical** - Värde långt utanför tröskelvärdesområdet (>20% avvikelse)

### Aviseringslogik
```javascript
const severity = value < threshold.min * 0.8 || value > threshold.max * 1.2 
  ? 'critical' 
  : 'warning';
```

## 🔄 Datapersistens

### Automatisk sparning
- Metriker sparas var minut
- Historisk data sparas var minut
- Data sparas vid graceful shutdown

### Dataformat
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "metrics": { ... },
  "changes": { ... }
}
```

## 🛡️ Säkerhet

### CORS
Servern är konfigurerad för bred CORS-support:
```javascript
const corsOptions = {
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
};
```

### Rate Limiting
För produktion, överväg att lägga till rate limiting:
```javascript
const rateLimit = require('express-rate-limit');
app.use('/metrics', rateLimit({ windowMs: 15000, max: 100 }));
```

## 📊 Prestanda

### Minne
- In-memory lagring för snabb åtkomst
- Automatisk historikrensning (max 1000 poster)
- Effektiv datastruktur för real-time uppdateringar

### Nätverk
- WebSocket för real-time kommunikation
- REST API för on-demand data
- Komprimerad JSON-data

## 🔧 Utveckling

### Debugging
```bash
DEBUG=* npm run dev
```

### Loggar
Servern loggar:
- Anslutningar och frånkopplingar
- Metrikeruppdateringar
- Aviseringar
- Datasparning
- Fel

## 🚀 Deployment

### PM2 (Rekommenderat)
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

## 📈 Monitoring

### Hälsokontroll
```bash
curl http://localhost:3030/healthz
```

### Metriker
```bash
curl http://localhost:3030/metrics
```

### Historik
```bash
curl "http://localhost:3030/metrics/history?limit=10"
```

## 🤝 Bidrag

1. Forka projektet
2. Skapa en feature branch
3. Commita dina ändringar
4. Pusha till branchen
5. Skapa en Pull Request

## 📄 Licens

MIT License - se LICENSE-filen för detaljer.

---

**🌿 Environmental Metrics Server v2.0** - Real-time miljöövervakning med intelligenta aviseringar!
