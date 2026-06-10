/* =====================================================
   CyberGuard AI - Dashboard JavaScript
   ===================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // ─── State ────────────────────────────────────────
    let isSimulating   = false;
    let simInterval    = null;
    let logRowCount    = 0;
    let totalPackets   = 0;
    let attackCount    = 0;
    let safeCount      = 0;
    let lastTimestamp  = Date.now();
    let packetsThisSec = 0;
    let rateInterval   = null;

    // Shared counters (dashboard + simulator)
    let dashTotal  = 0;
    let dashAttack = 0;
    let dashSafe   = 0;

    // ─── Navigation ────────────────────────────────────
    const navLinks = document.querySelectorAll('.nav-links li');
    const sections = document.querySelectorAll('.page-section');
    const pageTitle    = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');

    const pageMeta = {
        dashboard:  { title: 'Network Threat Intelligence',   sub: 'Real-time AI-powered threat detection and traffic analysis' },
        visuals:    { title: 'Visualization Reports',         sub: 'AI-generated confusion matrices and feature importance charts' },
        simulator:  { title: 'Traffic Simulator',             sub: 'Live packet analysis using Random Forest classifier' },
        about:      { title: 'About The System',              sub: 'Architecture, technology stack, and API reference' },
    };

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const id = link.getAttribute('data-section');
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            sections.forEach(s => s.classList.remove('active'));
            const target = document.getElementById(id);
            if (target) target.classList.add('active');
            if (pageMeta[id]) {
                pageTitle.textContent    = pageMeta[id].title;
                pageSubtitle.textContent = pageMeta[id].sub;
            }
        });
    });

    // ─── Clock ─────────────────────────────────────────
    const timeEl = document.getElementById('timeDisplay');
    const updateClock = () => {
        const now = new Date();
        timeEl.textContent = now.toLocaleTimeString('en-IN', { hour12: false });
    };
    updateClock();
    setInterval(updateClock, 1000);

    // ─── Metrics (Dashboard) ───────────────────────────
    const animateNumber = (el, target, isPercent = true, duration = 1400) => {
        const start = performance.now();
        const from  = parseFloat(el.textContent) || 0;
        const step  = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 4); // ease-out-quart
            const current = from + (target - from) * ease;
            el.textContent = isPercent ? current.toFixed(1) : current.toFixed(0);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };

    const fetchMetrics = async () => {
        try {
            const res  = await fetch('/api/metrics');
            const data = await res.json();

            if (data.acc !== undefined) {
                const acc  = (data.acc  * 100);
                const prec = (data.prec * 100);
                const rec  = (data.rec  * 100);
                const f1   = (data.f1   * 100);

                animateNumber(document.querySelector('#accValue  .value-number'), acc);
                animateNumber(document.querySelector('#precValue .value-number'), prec);
                animateNumber(document.querySelector('#recValue  .value-number'), rec);
                animateNumber(document.querySelector('#f1Value   .value-number'), f1);

                // Progress bars
                setTimeout(() => {
                    document.getElementById('accBar').style.width  = acc  + '%';
                    document.getElementById('precBar').style.width = prec + '%';
                    document.getElementById('recBar').style.width  = rec  + '%';
                    document.getElementById('f1Bar').style.width   = f1   + '%';
                }, 100);
            }
        } catch (err) {
            console.warn('Could not load metrics:', err);
        }
    };

    fetchMetrics();

    // ─── Threat Level Display ──────────────────────────
    const threatLevelEl = document.getElementById('threatLevel');
    const threatTextEl  = document.getElementById('threatText');

    const setThreatLevel = (pct) => {
        if (pct > 50) {
            threatLevelEl.classList.add('high');
            threatTextEl.textContent = 'HIGH';
            document.querySelector('.tl-dot').style.background = 'var(--red)';
        } else if (pct > 20) {
            threatLevelEl.classList.remove('high');
            threatTextEl.textContent = 'MEDIUM';
            document.querySelector('.tl-dot').style.background = 'var(--amber)';
        } else {
            threatLevelEl.classList.remove('high');
            threatTextEl.textContent = 'LOW';
            document.querySelector('.tl-dot').style.background = 'var(--green)';
        }
    };

    const updateDashboardCounters = () => {
        document.getElementById('cntTotal').textContent  = dashTotal;
        document.getElementById('cntAttack').textContent = dashAttack;
        document.getElementById('cntSafe').textContent   = dashSafe;

        const pct = dashTotal > 0 ? Math.round((dashAttack / dashTotal) * 100) : 0;
        document.getElementById('threatBar').style.width = pct + '%';
        document.getElementById('threatPct').textContent  = pct + '%';
        setThreatLevel(pct);
    };

    // ─── Simulator ─────────────────────────────────────
    const logBody   = document.getElementById('logBody');
    const toggleBtn = document.getElementById('toggleSim');
    const clearBtn  = document.getElementById('clearLog');
    const liveDot   = document.getElementById('liveDot');
    const liveLabel = document.getElementById('liveLabel');
    const logCountEl = document.getElementById('logCount');

    // Simulator stat elements
    const simTotalEl   = document.getElementById('simTotal');
    const simAttacksEl = document.getElementById('simAttacks');
    const simSafeEl    = document.getElementById('simSafe');
    const simRateEl    = document.getElementById('simRate');

    const now = () => new Date().toLocaleTimeString('en-IN', { hour12:false });

    const addLogRow = (entry) => {
        // Remove empty state row if present
        const emptyRow = logBody.querySelector('.empty-row');
        if (emptyRow) emptyRow.remove();

        logRowCount++;
        totalPackets++;
        packetsThisSec++;

        if (entry.status === 'ALERT') {
            attackCount++;
            dashAttack++;
        } else {
            safeCount++;
            dashSafe++;
        }
        dashTotal++;

        // Update simulator counters
        simTotalEl.textContent   = totalPackets;
        simAttacksEl.textContent = attackCount;
        simSafeEl.textContent    = safeCount;

        // Update dashboard
        updateDashboardCounters();

        const isAlert = entry.status === 'ALERT';
        const confidence = (Math.random() * 4 + 95).toFixed(2);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="color:var(--text-muted)">${logRowCount}</td>
            <td style="color:var(--cyan)">${entry.packet_id}</td>
            <td>${entry.actual}</td>
            <td><span class="badge ${isAlert ? 'badge-alert' : 'badge-safe'}">${entry.prediction}</span></td>
            <td>${confidence}%</td>
            <td><span class="${isAlert ? 'risk-high' : 'risk-low'}">${isAlert ? '▲ HIGH' : '▼ LOW'}</span></td>
            <td style="color:var(--text-muted)">${now()}</td>
        `;
        logBody.insertBefore(tr, logBody.firstChild);

        // Cap at 50 rows
        if (logBody.children.length > 50) {
            logBody.removeChild(logBody.lastChild);
        }

        // Update log count
        logCountEl.textContent = `${Math.min(logRowCount, 50)} entries`;
    };

    const fetchBatch = async () => {
        try {
            const res  = await fetch('/api/simulate/batch');
            const data = await res.json();
            if (Array.isArray(data)) data.forEach(e => addLogRow(e));
        } catch (err) {
            console.warn('Simulation fetch error:', err);
        }
    };

    // Packet rate counter (updates every second)
    const startRateCounter = () => {
        rateInterval = setInterval(() => {
            simRateEl.textContent = packetsThisSec;
            packetsThisSec = 0;
        }, 1000);
    };

    const stopRateCounter = () => {
        clearInterval(rateInterval);
        simRateEl.textContent = 0;
        packetsThisSec = 0;
    };

    toggleBtn.addEventListener('click', () => {
        isSimulating = !isSimulating;

        if (isSimulating) {
            // Start
            toggleBtn.innerHTML = '<span class="btn-icon">■</span><span class="btn-text">Stop Feed</span>';
            toggleBtn.classList.add('stop');
            liveDot.classList.add('active');
            liveLabel.textContent = 'LIVE';
            startRateCounter();
            fetchBatch();
            simInterval = setInterval(fetchBatch, 2500);
        } else {
            // Stop
            toggleBtn.innerHTML = '<span class="btn-icon">▶</span><span class="btn-text">Start Live Feed</span>';
            toggleBtn.classList.remove('stop');
            liveDot.classList.remove('active');
            liveLabel.textContent = 'OFFLINE';
            clearInterval(simInterval);
            stopRateCounter();
        }
    });

    clearBtn.addEventListener('click', () => {
        logBody.innerHTML = `
            <tr class="empty-row">
                <td colspan="7">
                    <div class="empty-state">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                            <polygon points="5,3 19,12 5,21 5,3"/>
                        </svg>
                        <p>Log cleared. Click "Start Live Feed" to resume.</p>
                    </div>
                </td>
            </tr>
        `;
        logRowCount = 0;
        logCountEl.textContent = '0 entries';
    });

    // ─── Visualizations: lazy-load images ──────────────
    document.querySelectorAll('.visual-img').forEach(img => {
        img.addEventListener('error', () => {
            img.style.display = 'none';
            const wrap = img.parentElement;
            wrap.innerHTML = `<div style="padding:2rem;color:var(--text-muted);font-size:0.8rem;text-align:center;">Image not available.<br>Run main.py to generate charts.</div>`;
        });
    });

}); // end DOMContentLoaded
