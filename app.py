from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import json
import asyncio
import os

# Import our environment
from src.env import InventoryGymEnv
from src.models import Action

app = FastAPI(title="InventoryGym-v1 API")

# Global environment instance
env_instance = InventoryGymEnv()

@app.post("/reset")
async def reset():
    """OpenEnv Standard Reset Endpoint"""
    resp = await env_instance.reset()
    return resp.model_dump()

@app.post("/step")
async def step(action: Action):
    """OpenEnv Standard Step Endpoint"""
    resp = await env_instance.step(action)
    return resp.model_dump()

@app.get("/state")
async def state():
    """OpenEnv Standard State Endpoint"""
    state_data = await env_instance.state()
    return state_data

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Ultra-Premium Interactive Intelligence Dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InventoryGym-v1 | Supply Intelligence Alpha</title>
        
        <!-- UI Libraries -->
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <script src="https://unpkg.com/lucide@latest"></script>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        
        <style>
            :root {
                --primary: #3b82f6;
                --primary-glow: rgba(59, 130, 246, 0.4);
                --accent: #f43f5e;
                --success: #10b981;
                --bg: #020617;
                --card-bg: rgba(15, 23, 42, 0.75);
                --border: rgba(255, 255, 255, 0.08);
            }

            body { 
                font-family: 'Outfit', sans-serif; 
                background: var(--bg); 
                color: #f1f5f9;
                overflow-x: hidden;
                background-image: url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=2000&q=80');
                background-size: cover;
                background-attachment: fixed;
                background-position: center;
            }

            h1, h2, h3, .font-heading { font-family: 'Space Grotesk', sans-serif; }

            /* Glassmorphism with deep blur */
            .glass-panel {
                background: var(--card-bg);
                backdrop-filter: blur(20px);
                border: 1px solid var(--border);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            }

            .cyber-border {
                position: relative;
                overflow: hidden;
            }

            .cyber-border::after {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 1px;
                background: linear-gradient(90deg, transparent, var(--primary), transparent);
                animation: scan 3s linear infinite;
            }

            @keyframes scan {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }

            .stat-card:hover {
                transform: translateY(-4px) scale(1.02);
                border-color: var(--primary-glow);
                background: rgba(15, 23, 42, 0.9);
            }

            .pulse-online {
                width: 8px; height: 8px;
                background: var(--success);
                border-radius: 50%;
                box-shadow: 0 0 10px var(--success);
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 0.5; }
                100% { transform: scale(1); opacity: 1; }
            }

            .custom-scrollbar::-webkit-scrollbar { width: 4px; }
            .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
            .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }

            .node-link {
                stroke-dasharray: 10;
                animation: flow 20s linear infinite;
                transition: stroke 0.5s ease;
            }
            @keyframes flow {
                from { stroke-dashoffset: 200; }
                to { stroke-dashoffset: 0; }
            }

            .btn-glow {
                position: relative;
                overflow: hidden;
            }
            .btn-glow::before {
                content: '';
                position: absolute;
                top: -50%; left: -50%; width: 200%; height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                opacity: 0; transition: opacity 0.3s;
            }
            .btn-glow:hover::before { opacity: 1; }
            .btn-glow:hover { box-shadow: 0 0 20px var(--primary-glow); }

            .shimmer {
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
                background-size: 200% 100%;
                animation: shimmer 2s infinite;
            }
            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            
            #shock-banner {
                position: fixed;
                top: 0; left: 0; width: 100%;
                z-index: 1000;
                display: none;
                background: rgba(244, 63, 94, 0.9);
                color: white;
                text-align: center;
                padding: 10px;
                font-weight: 800;
                letter-spacing: 2px;
                text-transform: uppercase;
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; }
            }
        </style>
    </head>
    <body class="min-h-screen flex flex-col">
        <div id="shock-banner">SYSTEMIC SHOCK DETECTED - LOGISTICS CALIBRATION REQUIRED</div>
        <div class="fixed inset-0 bg-black/40 z-[-1]"></div>
        
        <!-- Top Navigation -->
        <nav class="glass-panel border-b px-8 py-4 flex justify-between items-center sticky top-0 z-50">
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <i data-lucide="activity" class="text-white w-6 h-6"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight">InventoryGym <span class="text-blue-500 font-normal italic">Alpha Elite</span></h1>
                    <div class="flex items-center gap-2">
                        <div class="pulse-online"></div>
                        <span class="text-[10px] uppercase tracking-widest text-blue-400/80 font-bold">Strategic Nexus Active</span>
                    </div>
                </div>
            </div>
            
            <div class="hidden md:flex gap-12">
                <div class="text-center group">
                    <p class="text-[10px] text-slate-500 uppercase font-bold tracking-tighter mb-1 group-hover:text-blue-400 transition-colors">Cumulative Reward</p>
                    <p id="top-reward" class="text-lg font-bold text-emerald-400">+0.000</p>
                </div>
                <div class="h-10 w-[1px] bg-slate-800"></div>
                <div class="text-center group">
                    <p class="text-[10px] text-slate-500 uppercase font-bold tracking-tighter mb-1 group-hover:text-blue-400 transition-colors">Operational Cost</p>
                    <p id="top-cost" class="text-lg font-bold">$0.00</p>
                </div>
                <div class="h-10 w-[1px] bg-slate-800"></div>
                <div class="text-center group">
                    <p class="text-[10px] text-slate-500 uppercase font-bold tracking-tighter mb-1 group-hover:text-blue-400 transition-colors">Service Reliability</p>
                    <p id="top-sl" class="text-lg font-bold text-blue-400">100.0%</p>
                </div>
            </div>

            <div class="flex gap-4">
                <button onclick="resetEnv()" class="p-3 hover:bg-white/10 rounded-xl transition-all text-slate-400 group" title="Reset Simulation">
                    <i data-lucide="rotate-ccw" class="w-5 h-5 group-hover:rotate-[-45deg] transition-transform"></i>
                </button>
                <div class="w-10 h-10 rounded-xl border border-white/10 bg-white/5 flex items-center justify-center overflow-hidden">
                    <img src="https://api.dicebear.com/7.x/bottts-neutral/svg?seed=StrategyAlpha&backgroundColor=3b82f6" alt="AI Agent">
                </div>
            </div>
        </nav>

        <main class="flex-grow p-6 grid grid-cols-12 gap-6 max-w-[1800px] mx-auto w-full">
            
            <!-- Left Panel -->
            <div class="col-span-12 xl:col-span-8 space-y-6">
                
                <!-- Visualization Hub -->
                <div class="glass-panel rounded-3xl p-8 h-[450px] relative overflow-hidden group border border-white/5">
                    <div class="absolute top-8 left-8 z-10">
                        <div class="flex items-center gap-3 mb-1">
                            <span class="p-2 bg-blue-500/10 rounded-lg"><i data-lucide="globe" class="text-blue-400 w-5 h-5"></i></span>
                            <h3 class="text-xl font-bold">Network Topology & Real-time Flow</h3>
                        </div>
                        <p class="text-slate-500 text-xs ml-11">Transshipment vectors & dynamic load status</p>
                    </div>
                    
                    <!-- Dynamic Network Viz -->
                    <div class="absolute inset-0 flex items-center justify-center p-12 mt-12">
                        <svg viewBox="0 0 800 400" id="network-svg" class="w-full h-full drop-shadow-2xl">
                            <defs>
                                <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                                    <feGaussianBlur stdDeviation="4" result="blur" />
                                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                                </filter>
                                <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:rgba(59, 130, 246, 0)" />
                                    <stop offset="50%" style="stop-color:rgba(59, 130, 246, 0.5)" />
                                    <stop offset="100%" style="stop-color:rgba(59, 130, 246, 0.8)" />
                                </linearGradient>
                            </defs>
                            
                            <!-- Central Flux / Supplier -->
                            <g transform="translate(100, 200)" filter="url(#glow)">
                                <circle r="20" fill="rgba(255,255,255,0.05)" stroke="white" stroke-width="1" stroke-dasharray="2 2"></circle>
                                <circle r="6" fill="white" />
                                <text y="35" text-anchor="middle" fill="white" font-size="10" font-family="Space Grotesk" font-weight="bold">SUPPLIER-01</text>
                            </g>
                            
                            <g id="map-links"></g>
                            <g id="map-nodes"></g>
                        </svg>
                    </div>

                    <div class="absolute bottom-6 right-8 flex gap-4">
                        <div class="glass-panel px-4 py-2 rounded-xl border-white/5 flex items-center gap-3">
                            <span class="text-xs text-slate-400 font-bold uppercase tracking-widest">Load Velocity</span>
                            <span class="text-blue-400 font-bold" id="load-velocity">4.2x</span>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6" id="warehouse-grid"></div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="glass-panel rounded-3xl p-6 border-white/5 relative overflow-hidden">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">Aggregate Demand Cycle</h3>
                        <div id="demand-chart" style="height: 250px;"></div>
                    </div>
                    <div class="glass-panel rounded-3xl p-6 border-white/5 relative overflow-hidden">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">Unit Distribution</h3>
                        <div id="inventory-chart" style="height: 250px;"></div>
                    </div>
                </div>
            </div>

            <!-- Right Panel: Strategic Controls -->
            <div class="col-span-12 xl:col-span-4 space-y-6 flex flex-col h-full">
                
                <div class="glass-panel rounded-3xl p-8 cyber-border border-white/10 shadow-blue-900/10">
                    <div class="flex items-center gap-3 mb-8">
                        <span class="p-2 bg-amber-500/10 rounded-lg"><i data-lucide="zap" class="text-amber-400 w-5 h-5"></i></span>
                        <h3 class="text-xl font-bold">Strategic Command</h3>
                    </div>
                    
                    <div class="space-y-6">
                        <div class="grid grid-cols-2 gap-4">
                            <div class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Origin</label>
                                <select id="action-origin" class="w-full bg-slate-900 border border-white/10 rounded-xl p-3 text-sm text-white outline-none">
                                    <option value="-1">Global Supplier</option>
                                </select>
                            </div>
                            <div class="space-y-2">
                                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Destination</label>
                                <select id="action-dest" class="w-full bg-slate-900 border border-white/10 rounded-xl p-3 text-sm text-white outline-none"></select>
                            </div>
                        </div>
                        
                        <div class="space-y-4">
                            <div class="flex justify-between items-end mb-2">
                                <label class="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Inventory Allocation</label>
                                <div class="flex items-baseline gap-1">
                                    <span id="qty-disp" class="text-2xl font-bold text-blue-400">500</span>
                                    <span class="text-[10px] text-slate-600 font-bold">UNITS</span>
                                </div>
                            </div>
                            <input type="range" id="action-qty" min="0" max="2500" step="50" value="500" 
                                class="w-full accent-blue-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
                                oninput="document.getElementById('qty-disp').innerText = this.value">
                        </div>

                        <div class="grid grid-cols-2 gap-4 mt-8">
                            <button onclick="runStep('normal')" class="btn-glow group py-5 bg-white/5 hover:bg-white/10 rounded-2xl font-bold transition-all border border-white/5 flex flex-col items-center gap-1">
                                <span class="text-sm">Standard Order</span>
                                <span class="text-[10px] text-slate-600 font-normal">Base Lead Time</span>
                            </button>
                            <button onclick="runStep('expedited')" class="btn-glow group py-5 bg-gradient-to-br from-blue-600 to-indigo-700 hover:from-blue-500 hover:to-indigo-600 rounded-2xl font-bold transition-all shadow-xl shadow-blue-900/40 flex flex-col items-center gap-1">
                                <span class="text-sm">Rush / Expedite</span>
                                <span class="text-[10px] text-blue-200/60 font-normal">Cycle 1 Delivery</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="glass-panel rounded-3xl p-8 flex-grow flex flex-col min-h-[450px] border-white/5 overflow-hidden">
                    <div class="flex justify-between items-center mb-6">
                        <div class="flex items-center gap-3">
                            <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest">Neural Stream</h3>
                        </div>
                    </div>
                    
                    <div id="terminal" class="flex-grow overflow-y-auto custom-scrollbar space-y-4 pr-2"></div>
                    
                    <div class="mt-8 pt-6 border-t border-white/5 flex justify-between items-center">
                        <div>
                            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Cycle Progression</p>
                            <div class="flex items-center gap-3">
                                <div class="w-32 h-1 bg-slate-800 rounded-full overflow-hidden">
                                    <div id="step-progress" class="h-full bg-blue-500 transition-all duration-500" style="width: 0%"></div>
                                </div>
                                <span class="text-xs font-mono font-bold" id="step-counter">00 / 100</span>
                            </div>
                        </div>
                        <div class="flex -space-x-2">
                            <div class="w-8 h-8 rounded-full border-2 border-slate-900 bg-blue-500 flex items-center justify-center text-[10px] font-bold">AI</div>
                            <div class="w-8 h-8 rounded-full border-2 border-slate-900 bg-slate-800 flex items-center justify-center text-[10px] font-bold">BH</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <footer class="p-8 text-center text-slate-600 text-[10px] uppercase tracking-[0.2em] font-medium border-t border-white/5">
            Neural Inventory Management System &bull; Version 1.2.0-Elite &bull; 2026 Space Intel
        </footer>

        <script>
            let history = { step: [], demand: [], cost: [], sl: [] };
            let lastObservation = null;

            async function resetEnv() {
                const res = await fetch('/reset', { method: 'POST' });
                const data = await res.json();
                history = { step: [], demand: [], cost: [], sl: [] };
                document.getElementById('terminal').innerHTML = '';
                log('System re-initialized. Deep protocols active.', 'info');
                updateUI(data.observation);
            }

            async function runStep(priority) {
                const action = {
                    dest_warehouse: parseInt(document.getElementById('action-dest').value),
                    origin_warehouse: parseInt(document.getElementById('action-origin').value),
                    quantity: parseFloat(document.getElementById('action-qty').value),
                    priority: priority
                };
                
                const res = await fetch('/step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(action)
                });
                const data = await res.json();
                
                if (data.done) log('OBJECTIVE REACHED. Terminating cycle.', 'success');
                else if (data.reward < 0) log(`Efficiency Penalty: ${Math.abs(data.reward)} applied.`, 'warn');
                else log(`Optimal Execution: Reward +${data.reward}`, 'success');
                
                updateUI(data.observation, data.reward);
            }

            function log(msg, type) {
                const terminal = document.getElementById('terminal');
                const div = document.createElement('div');
                div.className = 'flex gap-4 group';
                let icon = 'info', color = 'text-blue-400', bg = 'bg-blue-500/10';
                if (type === 'action') { icon = 'zap'; color = 'text-amber-400'; bg = 'bg-amber-500/10'; }
                if (type === 'success') { icon = 'check-circle'; color = 'text-emerald-400'; bg = 'bg-emerald-500/10'; }
                if (type === 'warn') { icon = 'alert-triangle'; color = 'text-rose-400'; bg = 'bg-rose-500/10'; }
                div.innerHTML = `
                    <div class="flex-shrink-0 w-8 h-8 rounded-lg ${bg} flex items-center justify-center transition-transform group-hover:scale-110">
                        <i data-lucide="${icon}" class="${color} w-4 h-4"></i>
                    </div>
                    <div class="pt-1"><p class="text-xs ${color} font-medium leading-relaxed">${msg}</p></div>
                `;
                terminal.prepend(div);
                lucide.createIcons();
                if (terminal.children.length > 20) terminal.removeChild(terminal.lastChild);
            }

            function updateUI(obs, reward = 0) {
                lastObservation = obs;
                lucide.createIcons();
                
                animateCounter('top-cost', obs.total_cost, '$');
                animateCounter('top-sl', obs.service_level * 100, '', '%');
                animateCounter('top-reward', reward, reward >= 0 ? '+' : '');
                
                document.getElementById('step-counter').innerText = `${obs.current_step.toString().padStart(2, '0')} / 100`;
                document.getElementById('step-progress').style.width = `${obs.current_step}%`;

                // Shock UI
                const banner = document.getElementById('shock-banner');
                if (obs.last_action && obs.last_action.includes('SHOCK')) {
                    banner.style.display = 'block';
                    banner.innerText = obs.last_action;
                } else {
                    banner.style.display = 'none';
                }

                // Update Dropdowns
                const originSel = document.getElementById('action-origin');
                const destSel = document.getElementById('action-dest');
                if (destSel.options.length === 0) {
                    obs.warehouses.forEach(w => {
                        const opt = document.createElement('option');
                        opt.value = w.id; opt.innerText = w.name;
                        destSel.appendChild(opt);
                        
                        const opt2 = document.createElement('option');
                        opt2.value = w.id; opt2.innerText = w.name;
                        originSel.appendChild(opt2);
                    });
                }

                // Warehouse Grid
                const grid = document.getElementById('warehouse-grid');
                grid.innerHTML = obs.warehouses.map(w => {
                    const statusColor = w.utilization > 0.8 ? 'rose' : (w.utilization < 0.2 ? 'amber' : 'blue');
                    return `
                        <div class="glass-panel rounded-2xl p-6 stat-card border-white/5 relative overflow-hidden group">
                            <div class="flex justify-between items-start mb-6">
                                <div><h4 class="font-bold text-sm text-slate-200">${w.name}</h4><span class="text-[10px] text-slate-500 uppercase font-bold">${w.location}</span></div>
                                <div class="px-2 py-1 rounded-md bg-${statusColor}-500/10 text-[9px] font-bold text-${statusColor}-400 border border-${statusColor}-500/20">${(w.utilization * 100).toFixed(0)}%</div>
                            </div>
                            <div class="space-y-4">
                                <div class="flex justify-between items-end"><div class="space-y-1"><p class="text-[9px] text-slate-500 uppercase font-bold">Stock</p><p class="text-xl font-bold">${w.inventory.toFixed(0)}</p></div><p class="text-[9px] text-slate-500 font-bold uppercase">/ ${w.capacity}</p></div>
                                <div class="w-full h-1.5 bg-slate-800/50 rounded-full overflow-hidden"><div class="h-full bg-${statusColor}-500 transition-all duration-700" style="width: ${w.utilization * 100}%"></div></div>
                            </div>
                        </div>
                    `;
                }).join('');

                // Map & Flow
                const mapLinks = document.getElementById('map-links');
                const mapNodes = document.getElementById('map-nodes');
                let linkHtml = '', nodeHtml = '';
                
                obs.warehouses.forEach((w, i) => {
                    const tx = 350 + (i % 2 === 0 ? 0 : 250);
                    const ty = 80 + i * 80;
                    const statusColor = w.utilization > 0.8 ? '#f43f5e' : (w.utilization < 0.2 ? '#f59e0b' : '#3b82f6');
                    
                    linkHtml += `<path d="M 120 200 C 200 200, 250 ${ty}, ${tx} ${ty}" class="node-link" stroke="rgba(59, 130, 246, 0.4)" stroke-width="1.5" fill="none" />`;
                    
                    nodeHtml += `
                        <g transform="translate(${tx}, ${ty})" filter="url(#glow)">
                            <circle r="12" fill="rgba(255,255,255,0.05)" stroke="${statusColor}" stroke-width="1" stroke-dasharray="2 2"></circle>
                            <circle r="5" fill="${statusColor}"></circle>
                            <text x="20" y="4" fill="white" font-size="9" font-family="Space Grotesk" font-weight="bold">${w.name}</text>
                        </g>
                    `;
                });
                mapLinks.innerHTML = linkHtml;
                mapNodes.innerHTML = nodeHtml;

                // Sync Charts
                history.step.push(obs.current_step);
                history.demand.push(obs.forecasted_demand.reduce((acc, f) => acc + f.next_5_steps[0], 0));
                history.cost.push(obs.total_cost);
                history.sl.push(obs.service_level);

                const chartLayout = {
                    margin: { t: 5, b: 30, l: 40, r: 10 },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: '#475569', size: 9, family: 'Space Grotesk' },
                    xaxis: { gridcolor: 'rgba(255,255,255,0.02)', zeroline: false },
                    yaxis: { gridcolor: 'rgba(255,255,255,0.02)', zeroline: false }
                };
                Plotly.react('demand-chart', [{ x: history.step, y: history.demand, type: 'scatter', line: { color: '#3b82f6', width: 2, shape: 'spline' }, fill: 'tozeroy', fillcolor: 'rgba(59, 130, 246, 0.05)' }], chartLayout);
                Plotly.react('inventory-chart', [{ x: obs.warehouses.map(w => w.name), y: obs.warehouses.map(w => w.inventory), type: 'bar', marker: { color: 'rgba(59, 130, 246, 0.6)' } }], chartLayout);
                
                lucide.createIcons();
            }

            function animateCounter(id, target, prefix = '', suffix = '') {
                const el = document.getElementById(id);
                const current = parseFloat(el.innerText.replace(/[^\d.-]/g, '')) || 0;
                gsap.to({ val: current }, {
                    val: target, duration: 1.5, ease: "power2.out",
                    onUpdate: function() { el.innerText = prefix + (id.includes('sl') ? this.targets()[0].val.toFixed(1) : this.targets()[0].val.toFixed(2)) + suffix; }
                });
            }

            window.onload = resetEnv;
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
