# Credit Risk Analysis API Endpoints

## Entity Evaluation Endpoints (for Client Dashboard)

### 1. Get Client List
```
GET /api/data/clients
```
Returns a list of all available clients/entities for the evaluation dashboard.

**Response:**
```json
{
  "total_clients": 50,
  "clients": [
    {
      "entity_id": "ENT001",
      "client_name": "Apex Motors Ltd.",
      "sector": "Automotive",
      "country": "United States",
      "risk_bucket": "Medium",
      "implied_rating": "BBB+",
      "revenue_usd_m": 1250.5
    }
  ]
}
```

### 2. Evaluate Single Entity
```
POST /api/data/entities/{entity_name}/evaluate
```
Evaluates a specific client when the "Evaluate" button is clicked.

**Example:**
```
POST /api/data/entities/Apex Motors Ltd./evaluate
```

**Response:**
```json
{
  "entity_name": "Apex Motors Ltd.",
  "entity_data": {
    "entity_id": "ENT001",
    "entity_name": "Apex Motors Ltd.",
    "sector": "Automotive",
    "financial_metrics": {
      "revenue_usd_m": 1250.5,
      "debt_to_equity": 0.75,
      "current_ratio": 1.25
    },
    "risk_metrics": {
      "pd_1y_pct": 2.5,
      "risk_bucket": "Medium",
      "implied_rating": "BBB+"
    }
  },
  "ml_analysis": {
    "entity_id": "ENT001",
    "credit_analysis": {
      "response": "Detailed AI analysis...",
      "confidence": 0.85
    },
    "status": "completed"
  },
  "evaluation_timestamp": "2025-09-27T15:30:00"
}
```

### 3. Bulk Evaluation
```
POST /api/data/evaluate-multiple
```
Evaluates multiple entities at once.

**Request Body:**
```json
["Apex Motors Ltd.", "Nimbus Retail Pvt.", "Orion Technologies Inc."]
```

## ML Service Endpoints

### 1. Analyze Entity Credit Risk
```
POST /api/ml/analyze-entity
```
Direct ML service endpoint for entity credit analysis.

**Request Body:**
```json
{
  "entity_data": {
    "entity_id": "ENT001",
    "entity_name": "Apex Motors Ltd.",
    "financial_metrics": {...},
    "risk_metrics": {...}
  },
  "analysis_type": "comprehensive_credit_evaluation"
}
```

## Data Management Endpoints

### 1. Upload CSV
```
POST /api/data/upload-csv
```
Upload a CSV file containing entity data.

### 2. Analyze CSV Structure
```
POST /api/data/analyze-csv
```
Analyze CSV file structure without processing (for debugging).

### 3. Get All Entities
```
GET /api/data/entities
```
Get all entities from uploaded CSV.

### 4. Upload Status
```
GET /api/data/upload-status
```
Check if data has been uploaded and is ready for analysis.

## Usage Flow for Client Evaluation Dashboard

1. **Load Client List**: `GET /api/data/clients`
2. **Display Clients**: Show list with "Evaluate" buttons
3. **Evaluate Client**: `POST /api/data/entities/{client_name}/evaluate`
4. **Show Results**: Display ML analysis results

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing data, invalid format)
- `404`: Entity not found
- `500`: Internal server error

Error responses include detailed messages:
```json
{
  "detail": "Entity 'Unknown Company' not found in uploaded data"
}
```