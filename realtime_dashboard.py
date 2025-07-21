from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import sqlite3
from pathlib import Path

# Local imports
from realtime_rag_system import RealTimeCommentMonitor, RAGKnowledgeBase

app = FastAPI(title="Gerçek Zamanlı Yorum Analiz Dashboard")

# Global state
monitor = RealTimeCommentMonitor(check_interval=30)
connected_clients: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Bağlantı kopmuş, listeden çıkar
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Ana dashboard sayfası"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Gerçek Zamanlı Yorum Analiz Dashboard</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .metric {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        .priority-high { color: #ff6b6b; }
        .priority-medium { color: #feca57; }
        .priority-low { color: #48cae4; }
        .live-feed {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            height: 400px;
            overflow-y: auto;
        }
        .log-entry {
            background: rgba(255,255,255,0.1);
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid #4ecdc4;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background: #2ecc71; }
        .status-warning { background: #f39c12; }
        .status-critical { background: #e74c3c; }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        .rag-section {
            margin-top: 30px;
        }
        .rag-query {
            width: 100%;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.1);
            color: white;
            margin-bottom: 15px;
        }
        .rag-results {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            min-height: 200px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Gerçek Zamanlı Yorum Analiz Dashboard</h1>
            <p>RAG Destekli Otomatik İzleme Sistemi</p>
            <div class="controls">
                <button onclick="startMonitoring()">▶️ İzlemeyi Başlat</button>
                <button onclick="stopMonitoring()">⏸️ İzlemeyi Durdur</button>
                <button onclick="refreshData()">🔄 Yenile</button>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="metric-label">Toplam Yorum</div>
                <div class="metric" id="totalComments">-</div>
                <div class="metric-label">Son güncelleme: <span id="lastUpdate">-</span></div>
            </div>
            
            <div class="card">
                <div class="metric-label">Acil Kategoriler</div>
                <div class="metric priority-high" id="urgentCategories">-</div>
                <div class="metric-label">80+ öncelik skoru</div>
            </div>
            
            <div class="card">
                <div class="metric-label">Sistem Durumu</div>
                <div class="metric">
                    <span class="status-indicator status-active" id="systemStatus"></span>
                    <span id="statusText">Aktif</span>
                </div>
                <div class="metric-label">Gerçek zamanlı izleme</div>
            </div>
        </div>

        <div class="live-feed">
            <h3>📡 Canlı İzleme Günlüğü</h3>
            <div id="liveLogs">
                <div class="log-entry">
                    <strong>🚀 Sistem başlatılıyor...</strong><br>
                    <small>Dashboard yüklendi ve WebSocket bağlantısı kuruluyor</small>
                </div>
            </div>
        </div>

        <div class="rag-section">
            <div class="card">
                <h3>🧠 RAG Bilgi Sorgulama</h3>
                <input type="text" class="rag-query" id="ragQuery" 
                       placeholder="Örn: kargo gecikmesi nasıl çözülür?"
                       onkeypress="if(event.key==='Enter') queryRAG()">
                <button onclick="queryRAG()">🔍 Sorgula</button>
                
                <div class="rag-results" id="ragResults">
                    <em>RAG sistemi ile harici kaynaklardan bilgi almak için yukarıya bir soru yazın...</em>
                </div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket bağlantısı
        const ws = new WebSocket("ws://localhost:8000/ws");
        let isMonitoring = false;

        ws.onopen = function(event) {
            addLog("✅ WebSocket bağlantısı kuruldu", "success");
        };

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleRealTimeUpdate(data);
        };

        ws.onclose = function(event) {
            addLog("❌ WebSocket bağlantısı koptu", "error");
            document.getElementById("systemStatus").className = "status-indicator status-critical";
            document.getElementById("statusText").textContent = "Bağlantı Kopuk";
        };

        function handleRealTimeUpdate(data) {
            if (data.type === "new_analysis") {
                document.getElementById("totalComments").textContent = data.total_comments || "-";
                document.getElementById("urgentCategories").textContent = data.urgent_count || "0";
                document.getElementById("lastUpdate").textContent = new Date().toLocaleTimeString();
                
                addLog(`📊 ${data.new_comments || 0} yeni yorum analiz edildi`, "info");
                
                if (data.urgent_count > 0) {
                    addLog(`🚨 ${data.urgent_count} acil kategori tespit edildi!`, "warning");
                }
            } else if (data.type === "system_status") {
                const statusEl = document.getElementById("systemStatus");
                const textEl = document.getElementById("statusText");
                
                if (data.status === "active") {
                    statusEl.className = "status-indicator status-active";
                    textEl.textContent = "Aktif";
                } else if (data.status === "warning") {
                    statusEl.className = "status-indicator status-warning";
                    textEl.textContent = "Uyarı";
                } else {
                    statusEl.className = "status-indicator status-critical";
                    textEl.textContent = "Hata";
                }
            }
        }

        function addLog(message, type = "info") {
            const logsContainer = document.getElementById("liveLogs");
            const logEntry = document.createElement("div");
            logEntry.className = "log-entry";
            
            const timestamp = new Date().toLocaleTimeString();
            logEntry.innerHTML = `
                <strong>${message}</strong><br>
                <small>${timestamp}</small>
            `;
            
            logsContainer.insertBefore(logEntry, logsContainer.firstChild);
            
            // En fazla 20 log tut
            if (logsContainer.children.length > 20) {
                logsContainer.removeChild(logsContainer.lastChild);
            }
        }

        function startMonitoring() {
            ws.send(JSON.stringify({action: "start_monitoring"}));
            isMonitoring = true;
            addLog("🚀 Gerçek zamanlı izleme başlatıldı", "success");
        }

        function stopMonitoring() {
            ws.send(JSON.stringify({action: "stop_monitoring"}));
            isMonitoring = false;
            addLog("⏸️ Gerçek zamanlı izleme durduruldu", "info");
        }

        function refreshData() {
            ws.send(JSON.stringify({action: "refresh_data"}));
            addLog("🔄 Veriler yenileniyor...", "info");
        }

        async function queryRAG() {
            const query = document.getElementById("ragQuery").value;
            if (!query.trim()) return;
            
            const resultsDiv = document.getElementById("ragResults");
            resultsDiv.innerHTML = "<em>🔍 RAG sistemi sorgulanıyor...</em>";
            
            try {
                const response = await fetch("/rag/query", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({query: query})
                });
                
                const data = await response.json();
                
                let html = `<h4>🔍 Sorgu: "${query}"</h4>`;
                
                if (data.results && data.results.length > 0) {
                    html += "<div style='margin-top: 15px;'>";
                    data.results.forEach((result, index) => {
                        html += `
                            <div style='margin-bottom: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;'>
                                <strong>${result.source_name}</strong> 
                                <span style='font-size: 0.9em; opacity: 0.8;'>(${(result.similarity * 100).toFixed(1)}% benzerlik)</span><br>
                                <div style='margin-top: 8px;'>${result.content}</div>
                            </div>
                        `;
                    });
                    html += "</div>";
                } else {
                    html += "<div style='margin-top: 15px; opacity: 0.7;'>İlgili bilgi bulunamadı.</div>";
                }
                
                resultsDiv.innerHTML = html;
                
            } catch (error) {
                resultsDiv.innerHTML = `<div style='color: #ff6b6b;'>❌ Hata: ${error.message}</div>`;
            }
        }

        // Sayfa yüklendiğinde veri al
        window.onload = function() {
            refreshData();
        };
    </script>
</body>
</html>
    """
    return html_content

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint gerçek zamanlı güncellemeler için"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["action"] == "start_monitoring":
                # İzlemeyi başlat (background task)
                asyncio.create_task(run_monitoring())
                await manager.send_personal_message(
                    json.dumps({
                        "type": "system_status",
                        "status": "active",
                        "message": "İzleme başlatıldı"
                    }), websocket)
            
            elif message_data["action"] == "stop_monitoring":
                monitor.stop_monitoring()
                await manager.send_personal_message(
                    json.dumps({
                        "type": "system_status", 
                        "status": "inactive",
                        "message": "İzleme durduruldu"
                    }), websocket)
            
            elif message_data["action"] == "refresh_data":
                # Mevcut verileri gönder
                stats = get_current_stats()
                await manager.send_personal_message(
                    json.dumps({
                        "type": "new_analysis",
                        "total_comments": stats["total_comments"],
                        "urgent_count": stats["urgent_count"],
                        "timestamp": datetime.now().isoformat()
                    }), websocket)
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/rag/query")
async def query_rag(request: dict):
    """RAG sistemi sorgulama endpoint'i"""
    query = request.get("query", "")
    
    if not query:
        return {"error": "Sorgu boş olamaz"}
    
    try:
        # RAG bilgi tabanından ara
        results = monitor.rag_kb.find_relevant_context(query, limit=3)
        
        return {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats")
async def get_stats():
    """Mevcut istatistikleri al"""
    return get_current_stats()

def get_current_stats():
    """Mevcut sistem istatistiklerini hesapla"""
    try:
        # Yorumları yükle
        comments = monitor.load_current_comments()
        
        if not comments:
            return {"total_comments": 0, "urgent_count": 0}
        
        # Hızlı analiz
        analysis_results = monitor.comment_analyzer.analyze_all_comments(comments)
        priority_results = monitor.priority_analyzer.analyze_critical_issues(comments, analysis_results)
        
        # Acil kategori sayısını hesapla
        urgent_count = 0
        if priority_results and 'critical_issues' in priority_results:
            urgent_count = sum(
                1 for cat, data in priority_results['critical_issues'].items() 
                if data['priority_score'] >= 80
            )
        
        return {
            "total_comments": len(comments),
            "urgent_count": urgent_count,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        return {"total_comments": 0, "urgent_count": 0, "error": str(e)}

async def run_monitoring():
    """Background task olarak izleme çalıştır"""
    
    previous_comment_count = 0
    
    while True:
        try:
            # Yeni yorumları kontrol et
            new_comments = monitor.check_for_new_comments()
            
            if new_comments:
                # Analiz yap
                enhanced_analysis = monitor.enhanced_analysis_with_rag(new_comments)
                
                # WebSocket ile istemcilere gönder
                stats = get_current_stats()
                
                await manager.broadcast(json.dumps({
                    "type": "new_analysis",
                    "new_comments": len(new_comments),
                    "total_comments": stats["total_comments"],
                    "urgent_count": stats["urgent_count"],
                    "timestamp": datetime.now().isoformat()
                }))
            
            # 30 saniye bekle
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            await asyncio.sleep(60)  # Hata durumunda biraz daha bekle

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Gerçek Zamanlı Dashboard Başlatılıyor...")
    print("🌐 http://localhost:8000 adresinden erişebilirsiniz")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 