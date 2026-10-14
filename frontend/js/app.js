/**
 * TalentScan AI — Interactive Recruiter Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const jdTextarea = document.getElementById('jd-text');
  const jdTitleInput = document.getElementById('jd-title-display');
  const fileInput = document.getElementById('file-input');
  const dropzone = document.getElementById('dropzone');
  const fileQueue = document.getElementById('file-queue');
  const fileCountBadge = document.getElementById('file-count-badge');
  const btnScreen = document.getElementById('btn-screen');
  const btnSampleDemo = document.getElementById('btn-sample-demo');
  const btnParseJd = document.getElementById('btn-parse-jd');
  const btnExportCsv = document.getElementById('btn-export-csv');
  const anonymizeToggle = document.getElementById('anonymize-toggle');

  // Theme Management
  const btnThemeToggle = document.getElementById('btn-theme-toggle');
  const themeLabel = document.getElementById('theme-label');
  const themeIcon = document.getElementById('theme-icon');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('talentscan_theme', theme);
    if (theme === 'light') {
      if (themeLabel) themeLabel.textContent = 'Dark Mode';
      if (themeIcon) {
        themeIcon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>';
      }
    } else {
      if (themeLabel) themeLabel.textContent = 'Light Mode';
      if (themeIcon) {
        themeIcon.innerHTML = `
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        `;
      }
    }
  }

  // Set default theme to 'light' since user requested white theme
  const savedTheme = localStorage.getItem('talentscan_theme') || 'light';
  applyTheme(savedTheme);

  if (btnThemeToggle) {
    btnThemeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      applyTheme(current === 'light' ? 'dark' : 'light');
    });
  }

  // Sliders
  const sliderSemantic = document.getElementById('slider-semantic');
  const sliderSkills = document.getElementById('slider-skills');
  const sliderExp = document.getElementById('slider-exp');
  const sliderEdu = document.getElementById('slider-edu');
  const valSemantic = document.getElementById('val-semantic');
  const valSkills = document.getElementById('val-skills');
  const valExp = document.getElementById('val-exp');
  const valEdu = document.getElementById('val-edu');
  const btnResetWeights = document.getElementById('btn-reset-weights');

  // Results & Analytics
  const resultsContainer = document.getElementById('results-section');
  const candidateList = document.getElementById('candidate-list');
  const statTotal = document.getElementById('stat-total');
  const statAvg = document.getElementById('stat-avg');
  const statTop = document.getElementById('stat-top');
  const statStrongFit = document.getElementById('stat-strong-fit');
  const skillGapsSummary = document.getElementById('skill-gaps-summary');

  // Search & Filter
  const candidateSearch = document.getElementById('candidate-search');
  const thresholdFilter = document.getElementById('threshold-filter');

  // Modal
  const modalOverlay = document.getElementById('modal-overlay');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const modalCandidateName = document.getElementById('modal-candidate-name');
  const modalRank = document.getElementById('modal-rank');
  const modalFinalScore = document.getElementById('modal-final-score');
  const modalTierBadge = document.getElementById('modal-tier-badge');
  const modalSubScores = document.getElementById('modal-subscores');
  const modalStrengths = document.getElementById('modal-strengths');
  const modalGaps = document.getElementById('modal-gaps');
  const modalSkillsMatched = document.getElementById('modal-skills-matched');
  const modalSkillsMissing = document.getElementById('modal-skills-missing');
  const modalCategories = document.getElementById('modal-categories');

  // State
  let uploadedFiles = [];
  let currentScreeningResult = null;
  let sampleData = null;

  // Fetch preloaded samples from backend
  async function fetchSamples() {
    try {
      const res = await fetch('/api/samples');
      if (res.ok) {
        sampleData = await res.json();
        setupPresetButtons();
      }
    } catch (e) {
      console.warn('Could not load samples from server:', e);
    }
  }

  // Setup Role Preset Chips
  function setupPresetButtons() {
    const chipsContainer = document.getElementById('preset-chips');
    if (!chipsContainer || !sampleData || !sampleData.jds) return;

    chipsContainer.innerHTML = '';
    Object.keys(sampleData.jds).forEach((key, idx) => {
      const jd = sampleData.jds[key];
      const chip = document.createElement('button');
      chip.className = `chip ${idx === 0 ? 'active' : ''}`;
      chip.textContent = jd.title;
      chip.onclick = () => {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        jdTextarea.value = jd.description;
        triggerJdParse();
      };
      chipsContainer.appendChild(chip);
    });

    // Load first preset by default
    const firstKey = Object.keys(sampleData.jds)[0];
    if (firstKey) {
      jdTextarea.value = sampleData.jds[firstKey].description;
      triggerJdParse();
    }
  }

  // Sliders listener
  function updateSliderDisplay() {
    valSemantic.textContent = `${sliderSemantic.value}%`;
    valSkills.textContent = `${sliderSkills.value}%`;
    valExp.textContent = `${sliderExp.value}%`;
    valEdu.textContent = `${sliderEdu.value}%`;
  }

  [sliderSemantic, sliderSkills, sliderExp, sliderEdu].forEach(s => {
    s.addEventListener('input', updateSliderDisplay);
  });

  btnResetWeights.addEventListener('click', () => {
    sliderSemantic.value = 35;
    sliderSkills.value = 40;
    sliderExp.value = 15;
    sliderEdu.value = 10;
    updateSliderDisplay();
  });

  // Drag and Drop Handling
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const files = Array.from(e.dataTransfer.files);
    handleFileSelection(files);
  });

  dropzone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    const files = Array.from(e.target.files);
    handleFileSelection(files);
  });

  function handleFileSelection(files) {
    const validExtensions = ['.pdf', '.docx', '.txt', '.md'];
    files.forEach(f => {
      const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
      if (validExtensions.includes(ext)) {
        if (!uploadedFiles.some(existing => existing.name === f.name)) {
          uploadedFiles.push(f);
        }
      }
    });
    renderFileQueue();
  }

  function renderFileQueue() {
    fileQueue.innerHTML = '';
    fileCountBadge.textContent = `${uploadedFiles.length} file(s) queued`;

    if (uploadedFiles.length === 0) {
      fileQueue.innerHTML = '<div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; padding: 0.5rem;">No files uploaded yet. Drag & drop resumes or click demo button.</div>';
      return;
    }

    uploadedFiles.forEach((file, index) => {
      const item = document.createElement('div');
      item.className = 'file-item';
      const sizeKb = Math.round(file.size / 1024);
      item.innerHTML = `
        <div class="file-info">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <div>
            <div class="file-name" title="${file.name}">${file.name}</div>
            <div class="file-size">${sizeKb} KB</div>
          </div>
        </div>
        <button class="file-remove" title="Remove file" data-index="${index}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      `;

      item.querySelector('.file-remove').onclick = (e) => {
        e.stopPropagation();
        uploadedFiles.splice(index, 1);
        renderFileQueue();
      };

      fileQueue.appendChild(item);
    });
  }

  // Parse JD Extraction Trigger
  async function triggerJdParse() {
    const text = jdTextarea.value.trim();
    if (!text) return;

    try {
      const res = await fetch('/api/parse-jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jd_text: text })
      });
      if (res.ok) {
        const data = await res.json();
        renderExtractedCriteria(data.criteria);
      }
    } catch (e) {
      console.error('Error parsing JD:', e);
    }
  }

  btnParseJd.addEventListener('click', triggerJdParse);

  function renderExtractedCriteria(criteria) {
    if (jdTitleInput) {
      jdTitleInput.textContent = criteria.title;
    }
    const mustContainer = document.getElementById('criteria-must-skills');
    const goodContainer = document.getElementById('criteria-good-skills');
    const expBadge = document.getElementById('criteria-exp-badge');
    const eduBadge = document.getElementById('criteria-edu-badge');

    if (mustContainer) {
      mustContainer.innerHTML = criteria.skills.must_have.length
        ? criteria.skills.must_have.map(s => `<span class="pill pill-must">${s}</span>`).join('')
        : '<span class="pill">General Technical Skills</span>';
    }

    if (goodContainer) {
      goodContainer.innerHTML = criteria.skills.good_to_have.length
        ? criteria.skills.good_to_have.map(s => `<span class="pill pill-good">${s}</span>`).join('')
        : '<span class="pill" style="opacity: 0.6;">None specified</span>';
    }

    if (expBadge) {
      expBadge.textContent = `${criteria.min_experience_years}+ years exp required`;
    }
    if (eduBadge) {
      eduBadge.textContent = criteria.education.required_degree;
    }
  }

  // Get current weights from sliders
  function getWeights() {
    const sem = parseFloat(sliderSemantic.value) / 100;
    const skl = parseFloat(sliderSkills.value) / 100;
    const exp = parseFloat(sliderExp.value) / 100;
    const edu = parseFloat(sliderEdu.value) / 100;
    const sum = sem + skl + exp + edu || 1.0;
    return {
      semantic: sem / sum,
      skills: skl / sum,
      experience: exp / sum,
      education: edu / sum
    };
  }

  // Screening Trigger (Uploaded Files)
  btnScreen.addEventListener('click', async () => {
    const jdText = jdTextarea.value.trim();
    if (!jdText) {
      alert('Please provide a Job Description.');
      return;
    }

    if (uploadedFiles.length === 0) {
      // Fallback: offer to run sample resumes demo
      if (confirm('No resumes uploaded. Would you like to screen the preloaded sample candidate batch?')) {
        runSampleDemo();
      }
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('jd_text', jdText);
    formData.append('weights_json', JSON.stringify(getWeights()));
    formData.append('anonymize', anonymizeToggle.checked);
    formData.append('min_threshold', parseFloat(thresholdFilter.value || '0'));

    uploadedFiles.forEach(file => {
      formData.append('resume_files', file);
    });

    try {
      const res = await fetch('/api/screen', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Screening request failed');
      }

      const data = await res.json();
      currentScreeningResult = data;
      renderScreeningResults(data);
    } catch (err) {
      alert('Error during screening: ' + err.message);
    } finally {
      setLoading(false);
    }
  });

  // Fast Sample Demo Run
  btnSampleDemo.addEventListener('click', runSampleDemo);

  async function runSampleDemo() {
    const jdText = jdTextarea.value.trim();
    if (!jdText) {
      alert('Please provide or select a Job Description preset.');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch('/api/screen-json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jd_text: jdText,
          resumes: sampleData ? sampleData.resumes : null,
          weights: getWeights(),
          anonymize: anonymizeToggle.checked,
          min_threshold: parseFloat(thresholdFilter.value || '0')
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Demo screening failed');
      }

      const data = await res.json();
      currentScreeningResult = data;
      renderScreeningResults(data);
    } catch (err) {
      alert('Error running demo screening: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  function setLoading(isLoading) {
    if (isLoading) {
      btnScreen.disabled = true;
      btnSampleDemo.disabled = true;
      btnScreen.innerHTML = '<span class="spinner"></span> Analyzing Resumes...';
    } else {
      btnScreen.disabled = false;
      btnSampleDemo.disabled = false;
      btnScreen.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Run AI Resume Screening
      `;
    }
  }

  // Render Full Results
  function renderScreeningResults(data) {
    resultsContainer.style.display = 'flex';
    resultsContainer.scrollIntoView({ behavior: 'smooth' });

    // Analytics Cards
    statTotal.textContent = data.total_screened;
    statAvg.textContent = `${data.analytics.average_score}%`;
    statTop.textContent = `${data.analytics.top_score}%`;
    statStrongFit.textContent = data.analytics.tier_distribution['Strong Fit'] || 0;

    // Common Gaps
    if (data.analytics.most_common_skill_gaps && data.analytics.most_common_skill_gaps.length > 0) {
      skillGapsSummary.innerHTML = data.analytics.most_common_skill_gaps
        .map(g => `<span class="pill pill-missing">${g.skill} (${g.missing_in_candidates} missing)</span>`)
        .join(' ');
    } else {
      skillGapsSummary.innerHTML = '<span class="pill pill-match">High overall skills coverage</span>';
    }

    renderCandidateCards(data.candidates);
  }

  function renderCandidateCards(candidates) {
    candidateList.innerHTML = '';

    const searchTerm = (candidateSearch.value || '').toLowerCase().trim();
    const minThreshold = parseFloat(thresholdFilter.value || '0');

    const filtered = candidates.filter(c => {
      const matchScore = c.final_score >= minThreshold;
      const matchSearch = !searchTerm || 
        c.candidate_name.toLowerCase().includes(searchTerm) ||
        (c.sub_scores.skills.matched_must || []).some(s => s.toLowerCase().includes(searchTerm));
      return matchScore && matchSearch;
    });

    if (filtered.length === 0) {
      candidateList.innerHTML = '<div class="glass-panel" style="padding: 2.5rem; text-align: center; color: var(--text-muted);">No candidates match your current search/threshold filter.</div>';
      return;
    }

    filtered.forEach(cand => {
      const card = document.createElement('div');
      card.className = 'candidate-card';

      // Rank Badge Class
      let rankClass = '';
      if (cand.rank === 1) rankClass = 'rank-1';
      else if (cand.rank === 2) rankClass = 'rank-2';
      else if (cand.rank === 3) rankClass = 'rank-3';

      // Score color
      let scoreColor = '#10b981';
      if (cand.final_score < 50) scoreColor = '#ef4444';
      else if (cand.final_score < 70) scoreColor = '#f59e0b';

      const matchedPills = (cand.sub_scores.skills.matched_must || []).slice(0, 4)
        .map(s => `<span class="pill pill-match">✓ ${s}</span>`).join('');
      const missingPills = (cand.sub_scores.skills.missing_must || []).slice(0, 3)
        .map(s => `<span class="pill pill-missing">✗ ${s}</span>`).join('');

      card.innerHTML = `
        <div class="rank-badge ${rankClass}">#${cand.rank}</div>
        
        <div class="cand-info">
          <div class="cand-name">${cand.candidate_name}</div>
          <div class="cand-meta">
            <span>📄 ${cand.filename}</span>
            <span>💼 ${cand.sub_scores.experience.years} yrs</span>
            <span>🎓 ${cand.sub_scores.education.degree}</span>
          </div>
          <div style="margin-top: 0.35rem; font-size: 0.76rem; color: #94a3b8;">
            ⚡ <em>${cand.recommended_action}</em>
          </div>
        </div>

        <div class="cand-skills-col">
          <div class="skills-subhead">Must-Have Skill Alignment:</div>
          <div class="pills-container">
            ${matchedPills}
            ${missingPills}
          </div>
        </div>

        <div class="score-gauge-col">
          <div class="score-num" style="color: ${scoreColor};">${cand.final_score}%</div>
          <span class="tier-pill tier-${cand.tier_badge}">${cand.tier}</span>
        </div>

        <div>
          <button class="btn btn-secondary btn-sm btn-details" style="width: 100%;">
            Deep Dive ➔
          </button>
        </div>
      `;

      card.querySelector('.btn-details').onclick = () => openCandidateModal(cand);
      candidateList.appendChild(card);
    });
  }

  // Filter Listeners
  candidateSearch.addEventListener('input', () => {
    if (currentScreeningResult) {
      renderCandidateCards(currentScreeningResult.candidates);
    }
  });

  thresholdFilter.addEventListener('change', () => {
    if (currentScreeningResult) {
      renderCandidateCards(currentScreeningResult.candidates);
    }
  });

  // Candidate Deep-Dive Modal
  function openCandidateModal(cand) {
    modalCandidateName.textContent = cand.candidate_name;
    modalRank.textContent = `#${cand.rank}`;
    modalFinalScore.textContent = `${cand.final_score}%`;
    modalTierBadge.textContent = cand.tier;
    modalTierBadge.className = `tier-pill tier-${cand.tier_badge}`;

    // Subscores
    const sub = cand.sub_scores;
    modalSubScores.innerHTML = `
      <div class="metric-box">
        <div class="metric-title">Skills Match (${sub.skills.weight_pct}%)</div>
        <div class="metric-val" style="color: #60a5fa;">${sub.skills.score}%</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${(sub.skills.matched_must || []).length} of ${(sub.skills.matched_must || []).length + (sub.skills.missing_must || []).length} Must-Haves</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Semantic Context (${sub.semantic.weight_pct}%)</div>
        <div class="metric-val" style="color: #a78bfa;">${sub.semantic.score}%</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">TF-IDF / N-gram cosine</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Experience (${sub.experience.weight_pct}%)</div>
        <div class="metric-val" style="color: #34d399;">${sub.experience.score}%</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${sub.experience.years} yrs verified</div>
      </div>
      <div class="metric-box">
        <div class="metric-title">Education (${sub.education.weight_pct}%)</div>
        <div class="metric-val" style="color: #f59e0b;">${sub.education.score}%</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${sub.education.degree}</div>
      </div>
    `;

    // Strengths
    modalStrengths.innerHTML = (cand.strengths || []).map(s => `<li style="margin-bottom: 0.4rem;">${s}</li>`).join('');

    // Gaps
    modalGaps.innerHTML = (cand.gap_areas || []).map(g => `<li style="margin-bottom: 0.4rem;">${g}</li>`).join('');

    // Skill Pills
    modalSkillsMatched.innerHTML = (cand.sub_scores.skills.matched_must || []).map(s => `<span class="pill pill-match">✓ ${s}</span>`).join(' ') || 'None';
    modalSkillsMissing.innerHTML = (cand.sub_scores.skills.missing_must || []).map(s => `<span class="pill pill-missing">✗ ${s}</span>`).join(' ') || '<span class="pill pill-match">Zero gaps</span>';

    // Categories
    const cats = cand.candidate_skills_by_category || {};
    let catHtml = '';
    Object.keys(cats).forEach(cat => {
      catHtml += `<div style="margin-bottom: 0.5rem;"><strong style="font-size: 0.8rem; color: var(--text-secondary);">${cat}:</strong> <span style="font-size: 0.8rem; color: var(--text-muted);">${cats[cat].join(', ')}</span></div>`;
    });
    modalCategories.innerHTML = catHtml || '<div style="color: var(--text-muted);">Standard technical taxonomy</div>';

    modalOverlay.classList.add('open');
  }

  btnCloseModal.addEventListener('click', () => {
    modalOverlay.classList.remove('open');
  });

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) modalOverlay.classList.remove('open');
  });

  // Export CSV
  btnExportCsv.addEventListener('click', async () => {
    if (!currentScreeningResult || !currentScreeningResult.candidates) {
      alert('Please run a resume screening first before exporting.');
      return;
    }

    try {
      const res = await fetch('/api/export-csv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidates: currentScreeningResult.candidates })
      });

      if (!res.ok) throw new Error('Export failed');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume_screening_ranking_${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert('Error exporting CSV: ' + err.message);
    }
  });

  // Initial load
  fetchSamples();
  renderFileQueue();
});
