/**
 * ProjetFinalRaisonnement - Frontend Application
 * IEEE TETC 2026
 */

const API_BASE = 'http://localhost:5000';

class ProjetFinalRaisonnementApp {
    constructor() {
        this.currentProject = null;
        this.isGenerating = false;
        this.init();
    }
    
    init() {
        console.log('🚀 ProjetFinalRaisonnement frontend initialized');
        this.setupEventListeners();
        this.updateDesignCount();
        this.log('✅ Système prêt. Cliquez sur "Run Meta-Reasoning" pour commencer.');
    }
    
    setupEventListeners() {
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.runReasoning();
        });
        
        document.getElementById('designsBtn').addEventListener('click', () => {
            this.showDesigns();
        });
        
        document.getElementById('generateCodeBtn').addEventListener('click', () => {
            this.generateCode();
        });
        
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadProject();
        });
        
        ['latency', 'memory', 'power'].forEach(id => {
            const slider = document.getElementById(id);
            const value = document.getElementById(id + 'Value');
            if (slider && value) {
                slider.addEventListener('input', () => {
                    const suffix = id === 'latency' ? ' ms' : (id === 'memory' ? ' KB' : ' mW');
                    value.textContent = slider.value + suffix;
                });
            }
        });
    }
    
    log(message, type = 'info') {
        const container = document.getElementById('logContainer');
        const time = new Date().toLocaleTimeString('fr-FR', { hour12: false });
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        let icon = '📋';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '❌';
        if (type === 'warning') icon = '⚠️';
        if (type === 'system') icon = '🔧';
        
        entry.innerHTML = `<span class="log-time">[${time}]</span> ${icon} ${message}`;
        container.appendChild(entry);
        container.scrollTop = container.scrollHeight;
        
        while (container.children.length > 100) {
            container.removeChild(container.firstChild);
        }
    }
    
    updateProgress(percent) {
        const fill = document.getElementById('progressFill');
        const percentEl = document.getElementById('progressPercent');
        fill.style.width = percent + '%';
        percentEl.textContent = percent + '%';
    }
    
    resetProgress() {
        this.updateProgress(0);
        document.getElementById('metricsGrid').innerHTML = '';
        document.getElementById('selectedDesign').innerHTML = '';
        document.getElementById('downloadBtn').disabled = true;
        this.currentProject = null;
    }
    
    async updateDesignCount() {
        try {
            const response = await fetch(`${API_BASE}/api/designs/list`);
            if (response.ok) {
                const data = await response.json();
                document.getElementById('designCount').textContent = `${data.count} designs`;
            }
        } catch (e) {
            console.error('Erreur chargement designs:', e);
        }
    }
    
    async runReasoning() {
        if (this.isGenerating) return;
        this.isGenerating = true;
        this.resetProgress();
        
        const btn = document.getElementById('generateBtn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reasoning...';
        
        try {
            const domain = document.getElementById('domain').value;
            
            this.log(`🧠 Début du méta-raisonnement pour: ${domain}`);
            this.updateProgress(10);
            
            const response = await fetch(`${API_BASE}/api/meta/reason`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    domain: domain,
                    environment: 'production',
                    criticality: 'high'
                })
            });
            
            this.updateProgress(50);
            this.log('⏳ Traitement du raisonnement...');
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            this.updateProgress(80);
            
            if (data.status === 'success' && data.decision) {
                const decision = data.decision;
                const design = decision.design || {};
                const confidence = decision.confidence || 0.85;
                
                this.log(`✅ Design sélectionné: ${design.id || 'inconnu'}`, 'success');
                this.log(`📊 Confiance: ${(confidence * 100).toFixed(1)}%`);
                
                // Afficher le design
                this.displaySelectedDesign(design, confidence, decision.justification);
                
                // Afficher les métriques
                if (design.metrics) {
                    this.displayMetrics(design.metrics);
                }
                
                // --- IMPORTANT: Générer le projet via /api/generate/design ---
                this.log('📦 Génération du projet pour téléchargement...');
                
                const genResponse = await fetch(`${API_BASE}/api/generate/design`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        design_id: design.id,
                        domain: domain,
                        mcu: document.getElementById('mcu').value
                    })
                });
                
                if (!genResponse.ok) {
                    throw new Error('Erreur génération du projet');
                }
                
                const genData = await genResponse.json();
                this.currentProject = genData;
                
                this.log(`✅ Projet généré: ${genData.project_id}`, 'success');
                document.getElementById('downloadBtn').disabled = false;
                
                this.updateProgress(100);
                this.log('🎉 Méta-raisonnement terminé avec succès!', 'success');
                
            } else {
                throw new Error(data.error || 'Erreur inconnue dans la réponse');
            }
            
        } catch (error) {
            this.log(`❌ Erreur: ${error.message}`, 'error');
            this.updateProgress(0);
        } finally {
            this.isGenerating = false;
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-rocket"></i> Run Meta-Reasoning';
        }
    }
    
    displaySelectedDesign(design, confidence, justification) {
        const container = document.getElementById('selectedDesign');
        if (!design || Object.keys(design).length === 0) {
            container.innerHTML = `<div style="color: #94a3b8;">Aucun design sélectionné</div>`;
            return;
        }
        
        const metrics = design.metrics || {};
        const algo = design.algorithm || {};
        const hw = design.hardware || {};
        
        container.innerHTML = `
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <span style="font-size: 16px; color: #10b981;">⭐ Design sélectionné</span>
                        <div style="font-size: 20px; font-weight: bold; color: #60a5fa; margin-top: 5px;">
                            ${design.id || 'Inconnu'}
                        </div>
                        <div style="color: #94a3b8; font-size: 14px;">
                            ${design.name || ''} | ${algo.model_type || 'N/A'} | ${algo.quantization_bits || '?'}-bit
                        </div>
                        <div style="color: #64748b; font-size: 12px; margin-top: 3px;">
                            ${hw.mcu_type || 'N/A'} | ${hw.clock_mhz || '?'}MHz
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 28px; font-weight: bold; color: #10b981;">
                            ${(confidence * 100).toFixed(0)}%
                        </div>
                        <div style="color: #94a3b8; font-size: 12px;">Confiance</div>
                    </div>
                </div>
                ${design.source ? `<div style="color: #64748b; font-size: 12px; margin-top: 5px;">📁 Source: ${design.source}</div>` : ''}
                ${design.validation_status ? `<div style="color: #64748b; font-size: 12px;">✅ Validation: ${design.validation_status}</div>` : ''}
                <div style="margin-top: 15px; padding: 15px; background: rgba(15, 23, 42, 0.5); border-radius: 8px; font-size: 13px; color: #cbd5e1; max-height: 150px; overflow-y: auto; white-space: pre-wrap;">
                    ${justification || 'Justification non disponible'}
                </div>
            </div>
        `;
    }
    
    displayMetrics(metrics) {
        const grid = document.getElementById('metricsGrid');
        if (!metrics || Object.keys(metrics).length === 0) {
            grid.innerHTML = `<div style="color: #94a3b8; grid-column: 1/-1; text-align: center;">Aucune métrique disponible</div>`;
            return;
        }
        
        const items = [
            { label: 'Précision', value: metrics.accuracy ? `${(metrics.accuracy * 100).toFixed(1)}%` : 'N/A' },
            { label: 'Latence', value: metrics.latency_ms ? `${metrics.latency_ms}ms` : 'N/A' },
            { label: 'Énergie', value: metrics.energy_mj ? `${metrics.energy_mj}mJ` : 'N/A' },
            { label: 'Mémoire', value: metrics.memory_kb ? `${metrics.memory_kb}KB` : 'N/A' },
            { label: 'Puissance', value: metrics.power_mw ? `${metrics.power_mw}mW` : 'N/A' },
            { label: 'Fiabilité', value: metrics.reliability || 'N/A' }
        ];
        
        grid.innerHTML = items.map(item => `
            <div class="metric-card">
                <div class="metric-value">${item.value}</div>
                <div class="metric-label">${item.label}</div>
            </div>
        `).join('');
    }
    
    async showDesigns() {
        const panel = document.getElementById('designsPanel');
        const list = document.getElementById('designsList');
        
        if (panel.style.display === 'block') {
            panel.style.display = 'none';
            return;
        }
        
        panel.style.display = 'block';
        this.log('📋 Chargement des designs...');
        
        try {
            const response = await fetch(`${API_BASE}/api/designs/list`);
            if (!response.ok) throw new Error('Erreur chargement');
            
            const data = await response.json();
            const designs = data.designs || [];
            
            if (designs.length === 0) {
                list.innerHTML = '<div style="color: #94a3b8; padding: 20px;">Aucun design disponible</div>';
                return;
            }
            
            list.innerHTML = designs.map(d => `
                <div class="design-card ${d.recommended ? 'recommended' : ''}" style="cursor: pointer;" onclick="app.selectDesign('${d.id}')">
                    <div class="design-title">${d.id} ${d.recommended ? '⭐' : ''}</div>
                    <div style="color: #94a3b8; font-size: 14px;">${d.name || d.id}</div>
                    <div style="color: #64748b; font-size: 12px; margin-top: 5px;">${d.description || ''}</div>
                    <div class="design-metrics">
                        <span>🎯 ${d.metrics?.accuracy ? (d.metrics.accuracy * 100).toFixed(1) + '%' : 'N/A'}</span>
                        <span>⏱️ ${d.metrics?.latency_ms || 'N/A'}ms</span>
                        <span>⚡ ${d.metrics?.energy_mj || 'N/A'}mJ</span>
                        <span>💾 ${d.metrics?.memory_kb || 'N/A'}KB</span>
                    </div>
                    ${d.source ? `<div style="color: #64748b; font-size: 11px; margin-top: 5px;">📁 ${d.source}</div>` : ''}
                </div>
            `).join('');
            
            this.log(`📊 ${designs.length} designs chargés`);
            
        } catch (error) {
            this.log(`❌ Erreur: ${error.message}`, 'error');
            list.innerHTML = `<div style="color: #ef4444;">Erreur: ${error.message}</div>`;
        }
    }
    
    async selectDesign(designId) {
        this.log(`🎯 Sélection du design: ${designId}`);
        
        try {
            const response = await fetch(`${API_BASE}/api/generate/design`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ design_id: designId })
            });
            
            if (!response.ok) throw new Error('Erreur génération');
            
            const data = await response.json();
            this.currentProject = data;
            
            this.log(`✅ Projet généré: ${data.project_id}`, 'success');
            document.getElementById('downloadBtn').disabled = false;
            
            if (data.metrics) {
                this.displayMetrics(data.metrics);
            }
            
        } catch (error) {
            this.log(`❌ Erreur: ${error.message}`, 'error');
        }
    }
    
    async generateCode() {
        const domain = document.getElementById('domain').value;
        const mcu = document.getElementById('mcu').value;
        
        this.log(`💻 Génération de code pour ${domain} / ${mcu}...`);
        
        try {
            const response = await fetch(`${API_BASE}/api/generate/strict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    domain: domain,
                    mcu: mcu,
                    latency: parseInt(document.getElementById('latency').value),
                    memory: parseInt(document.getElementById('memory').value),
                    power: parseInt(document.getElementById('power').value)
                })
            });
            
            if (!response.ok) throw new Error('Erreur génération');
            
            const data = await response.json();
            this.currentProject = data;
            
            this.log(`✅ Code généré: ${data.project_id}`, 'success');
            if (data.metrics) {
                this.displayMetrics(data.metrics);
            }
            document.getElementById('downloadBtn').disabled = false;
            
        } catch (error) {
            this.log(`❌ Erreur: ${error.message}`, 'error');
        }
    }
    
    async downloadProject() {
        if (!this.currentProject) {
            this.log('❌ Aucun projet à télécharger', 'error');
            return;
        }
        
        // Récupérer le project_id depuis la réponse de génération
        const projectId = this.currentProject.project_id;
        if (!projectId) {
            this.log('❌ ID de projet invalide', 'error');
            return;
        }
        
        this.log(`📥 Téléchargement du projet: ${projectId}...`);
        
        try {
            const response = await fetch(`${API_BASE}/api/download/${projectId}`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${projectId}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.log(`✅ Projet téléchargé: ${projectId}.zip`, 'success');
            
        } catch (error) {
            this.log(`❌ Erreur: ${error.message}`, 'error');
        }
    }
}

// Initialisation
const app = new ProjetFinalRaisonnementApp();
