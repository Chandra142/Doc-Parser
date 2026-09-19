from pathlib import Path

content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DocuQuest - Document Intelligence & Exam Extraction</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
  </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col">

  <!-- Navigation Bar -->
  <header class="bg-slate-900 text-white shadow-lg sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-lg text-white shadow-md">
          DQ
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white leading-tight">DocuQuest</h1>
          <p class="text-xs text-slate-400">Document Intelligence &amp; Question Extraction</p>
        </div>
      </div>
      <div class="flex items-center space-x-3 text-sm">
        <a href="/docs" target="_blank" class="px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition">
          Interactive Swagger (/docs) &rarr;
        </a>
        <span id="healthBadge" class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
          ● System Live
        </span>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8">

    <!-- Left Column: Controls (Auth, Upload, Actions) -->
    <div class="lg:col-span-4 space-y-6">

      <!-- 1. Authentication -->
      <section class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">1. Authentication</h2>
          <span id="authStatusBadge" class="text-xs px-2 py-0.5 rounded font-medium bg-amber-100 text-amber-800">Not Signed In</span>
        </div>
        <p class="text-xs text-slate-500 mb-4">All document routes enforce strict JWT ownership isolation.</p>
        
        <div class="space-y-3">
          <button id="quickDemoLoginBtn" class="w-full py-2 px-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold transition shadow flex items-center justify-center space-x-1.5">
            <span>⚡ 1-Click Demo Login</span>
          </button>
          
          <div class="relative flex py-1 items-center">
            <div class="flex-grow border-t border-slate-200"></div>
            <span class="flex-shrink mx-2 text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Or Custom Credentials</span>
            <div class="flex-grow border-t border-slate-200"></div>
          </div>

          <div class="grid grid-cols-1 gap-2">
            <input id="authEmail" type="email" placeholder="user@example.com" class="w-full px-3 py-1.5 text-xs rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            <input id="authPassword" type="password" placeholder="Password (min 8 chars)" class="w-full px-3 py-1.5 text-xs rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <button id="registerBtn" class="py-1.5 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-medium transition border border-slate-200">Register</button>
            <button id="loginBtn" class="py-1.5 px-3 bg-slate-800 hover:bg-slate-900 text-white rounded text-xs font-medium transition">Login</button>
          </div>
        </div>
      </section>

      <!-- 2. Document Ingestion -->
      <section class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-2">2. Upload &amp; Ingestion</h2>
        <p class="text-xs text-slate-500 mb-4">Upload any PDF, PNG, JPG exam document (max 20MB).</p>

        <!-- Dropzone / File Picker -->
        <div class="border-2 border-dashed border-slate-300 rounded-lg p-4 text-center hover:border-indigo-400 transition bg-slate-50/50 mb-3">
          <input type="file" id="fileInput" accept=".pdf,.png,.jpg,.jpeg" class="hidden" />
          <label for="fileInput" class="cursor-pointer flex flex-col items-center justify-center space-y-1.5">
            <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span id="fileNameLabel" class="text-xs font-medium text-slate-600">Click to browse or drop file</span>
            <span class="text-[11px] text-slate-400">PDF, PNG, JPG, JPEG</span>
          </label>
        </div>

        <button id="uploadBtn" class="w-full py-2 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold transition shadow flex items-center justify-center space-x-1.5">
          <span>🚀 Process Selected Document</span>
        </button>

        <!-- Quick Pre-packaged Fixture Buttons -->
        <div class="mt-5 pt-4 border-t border-slate-200">
          <h3 class="text-xs font-semibold text-slate-700 mb-2">⚡ Test Built-in Assessment Scenarios:</h3>
          <div class="space-y-1.5 text-xs">
            <button onclick="loadFixture('clean_questions.pdf', 'application/pdf')" class="w-full text-left px-2.5 py-1.5 rounded hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 font-medium transition flex items-center justify-between">
              <span>📄 1. Clean PDF + Answer Key</span>
              <span class="text-[10px] text-slate-400">MCQ</span>
            </button>
            <button onclick="loadFixture('multipage_question.pdf', 'application/pdf')" class="w-full text-left px-2.5 py-1.5 rounded hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 font-medium transition flex items-center justify-between">
              <span>📑 2. Multi-Page Question</span>
              <span class="text-[10px] text-slate-400">Spans P1-P2</span>
            </button>
            <button onclick="loadFixture('question_paper.pdf', 'application/pdf')" class="w-full text-left px-2.5 py-1.5 rounded hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 font-medium transition flex items-center justify-between">
              <span>📝 3. Question Paper (for Linking)</span>
              <span class="text-[10px] text-slate-400">Q1-Q3</span>
            </button>
            <button onclick="loadFixture('answer_key.pdf', 'application/pdf')" class="w-full text-left px-2.5 py-1.5 rounded hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 font-medium transition flex items-center justify-between">
              <span>🔑 4. Separate Answer Key</span>
              <span class="text-[10px] text-slate-400">Solutions</span>
            </button>
            <button onclick="loadFixture('low_quality_question.png', 'image/png')" class="w-full text-left px-2.5 py-1.5 rounded hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 font-medium transition flex items-center justify-between">
              <span>🖼️ 5. Scanned / Low Quality Image</span>
              <span class="text-[10px] text-slate-400">OCR Path</span>
            </button>
            <button onclick="loadFixture('invalid_document.txt', 'text/plain')" class="w-full text-left px-2.5 py-1.5 rounded hover:bg-rose-50 hover:text-rose-700 border border-slate-200 font-medium transition flex items-center justify-between text-rose-600">
              <span>⚠️ 6. Unsupported File Test</span>
              <span class="text-[10px] text-slate-400">Rejection</span>
            </button>
          </div>
        </div>
      </section>

      <!-- 3. Cross-Document Linking -->
      <section class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-2">3. Cross-Doc Answer Matching</h2>
        <p class="text-xs text-slate-500 mb-3">Link a Question Paper with an Answer Key document to automatically associate answers.</p>
        <div class="space-y-2">
          <input id="sourceDocId" type="text" placeholder="Question Paper Document ID" class="w-full px-3 py-1.5 text-xs rounded border border-slate-300 font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <input id="targetDocId" type="text" placeholder="Answer Key Document ID" class="w-full px-3 py-1.5 text-xs rounded border border-slate-300 font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <button id="linkBtn" class="w-full py-1.5 px-3 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-semibold transition shadow">
            🔗 Establish ANSWER_KEY Link
          </button>
        </div>
      </section>

    </div>

    <!-- Right Column: Results, Status & Extracted Questions -->
    <div class="lg:col-span-8 space-y-6">

      <!-- Job Status Monitor -->
      <div id="jobStatusCard" class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 hidden transition-all duration-300">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500">Document Processing Status</h3>
            <p id="activeDocIdText" class="text-xs font-mono text-slate-700 mt-0.5">ID: -</p>
          </div>
          <span id="docStatusBadge" class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
            QUEUED
          </span>
        </div>

        <div class="w-full bg-slate-100 rounded-full h-2.5 mb-2 overflow-hidden">
          <div id="progressBar" class="bg-indigo-600 h-2.5 rounded-full transition-all duration-300" style="width: 10%"></div>
        </div>
        <div class="flex justify-between text-[11px] text-slate-500">
          <span id="progressText">Queueing document...</span>
          <span id="progressPercent">10%</span>
        </div>
      </div>

      <!-- Live Notification / Alerts Banner -->
      <div id="alertBanner" class="hidden p-4 rounded-xl border text-xs font-medium"></div>

      <!-- Questions & Review Items Feed -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
          <div>
            <h2 class="text-base font-bold text-slate-800">Extracted Examination Questions</h2>
            <p class="text-xs text-slate-500">Structured questions, options, page provenance, and answer keys.</p>
          </div>
          <button id="refreshQuestionsBtn" class="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-medium transition border border-slate-200">
            🔄 Refresh
          </button>
        </div>

        <div id="questionsContainer" class="space-y-4">
          <div class="text-center py-12 text-slate-400 text-xs">
            No document loaded yet. Choose a built-in scenario on the left or upload an exam paper to begin.
          </div>
        </div>
      </div>

      <!-- Raw JSON Viewer Accordion -->
      <details class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 text-xs group">
        <summary class="font-semibold text-slate-700 cursor-pointer select-none flex items-center justify-between">
          <span>🔍 View Raw JSON Payload (API Output)</span>
          <span class="text-slate-400 group-open:rotate-180 transition-transform">&darr;</span>
        </summary>
        <pre id="jsonViewer" class="mt-3 p-3 bg-slate-900 text-emerald-400 rounded-lg overflow-x-auto text-[11px] font-mono leading-relaxed">// Output JSON will appear here...</pre>
      </details>

    </div>
  </main>

  <!-- Footer -->
  <footer class="bg-white border-t border-slate-200 text-slate-500 text-xs py-4 text-center mt-auto">
    DocuQuest &copy; 2026 &bull; Asynchronous Examination Intelligence &bull; Built with FastAPI, Celery, PostgreSQL &amp; Tesseract OCR
  </footer>

  <!-- Application Logic -->
  <script>
    let authToken = localStorage.getItem('docuquest_token') || '';
    let currentDocId = localStorage.getItem('docuquest_doc_id') || '';
    let pollingInterval = null;

    const authStatusBadge = document.getElementById('authStatusBadge');
    const authEmail = document.getElementById('authEmail');
    const authPassword = document.getElementById('authPassword');
    const registerBtn = document.getElementById('registerBtn');
    const loginBtn = document.getElementById('loginBtn');
    const quickDemoLoginBtn = document.getElementById('quickDemoLoginBtn');
    const fileInput = document.getElementById('fileInput');
    const fileNameLabel = document.getElementById('fileNameLabel');
    const uploadBtn = document.getElementById('uploadBtn');
    const jobStatusCard = document.getElementById('jobStatusCard');
    const docStatusBadge = document.getElementById('docStatusBadge');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressPercent = document.getElementById('progressPercent');
    const activeDocIdText = document.getElementById('activeDocIdText');
    const questionsContainer = document.getElementById('questionsContainer');
    const alertBanner = document.getElementById('alertBanner');
    const jsonViewer = document.getElementById('jsonViewer');
    const linkBtn = document.getElementById('linkBtn');
    const sourceDocId = document.getElementById('sourceDocId');
    const targetDocId = document.getElementById('targetDocId');
    const refreshQuestionsBtn = document.getElementById('refreshQuestionsBtn');

    function showAlert(msg, isError = false) {
      alertBanner.classList.remove('hidden', 'bg-rose-50', 'text-rose-800', 'border-rose-200', 'bg-emerald-50', 'text-emerald-800', 'border-emerald-200');
      if (isError) {
        alertBanner.classList.add('bg-rose-50', 'text-rose-800', 'border-rose-200');
      } else {
        alertBanner.classList.add('bg-emerald-50', 'text-emerald-800', 'border-emerald-200');
      }
      alertBanner.innerText = msg;
    }

    async function checkAuth() {
      if (!authToken) {
        authStatusBadge.className = 'text-xs px-2 py-0.5 rounded font-medium bg-amber-100 text-amber-800';
        authStatusBadge.innerText = 'Not Signed In';
        return;
      }
      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
          const user = await res.json();
          authStatusBadge.className = 'text-xs px-2 py-0.5 rounded font-medium bg-emerald-100 text-emerald-800';
          authStatusBadge.innerText = `Signed In: ${user.email}`;
        } else {
          authToken = '';
          localStorage.removeItem('docuquest_token');
          authStatusBadge.className = 'text-xs px-2 py-0.5 rounded font-medium bg-amber-100 text-amber-800';
          authStatusBadge.innerText = 'Session Expired';
        }
      } catch (err) {
        console.error(err);
      }
    }

    async function doLogin(email, password) {
      try {
        const res = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
          authToken = data.access_token;
          localStorage.setItem('docuquest_token', authToken);
          showAlert(`Successfully authenticated as ${email}`);
          checkAuth();
        } else {
          showAlert(data.error?.message || 'Login failed', true);
        }
      } catch (err) {
        showAlert('Network error during login', true);
      }
    }

    async function doRegister(email, password) {
      try {
        const res = await fetch('/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('Account registered! Logging in...');
          await doLogin(email, password);
        } else {
          if (res.status === 409) {
            await doLogin(email, password);
          } else {
            showAlert(data.error?.message || 'Registration failed', true);
          }
        }
      } catch (err) {
        showAlert('Network error during registration', true);
      }
    }

    quickDemoLoginBtn.addEventListener('click', async () => {
      await doRegister('demo@docuquest.ai', 'Password123!');
    });

    loginBtn.addEventListener('click', () => {
      const e = authEmail.value.trim();
      const p = authPassword.value;
      if (!e || !p) return showAlert('Please provide email and password', true);
      doLogin(e, p);
    });

    registerBtn.addEventListener('click', () => {
      const e = authEmail.value.trim();
      const p = authPassword.value;
      if (!e || !p) return showAlert('Please provide email and password', true);
      doRegister(e, p);
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        fileNameLabel.innerText = e.target.files[0].name;
      }
    });

    uploadBtn.addEventListener('click', async () => {
      if (!authToken) {
        await doRegister('demo@docuquest.ai', 'Password123!');
      }
      if (!fileInput.files.length) {
        return showAlert('Please select or choose a file first', true);
      }
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
      await executeUpload(formData);
    });

    async function executeUpload(formData) {
      showAlert('Uploading file to DocuQuest pipeline...');
      try {
        const res = await fetch('/api/v1/documents', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` },
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          currentDocId = data.document_id;
          localStorage.setItem('docuquest_doc_id', currentDocId);
          sourceDocId.value = currentDocId;
          showAlert(`Document queued! ID: ${currentDocId}`);
          pollStatus(currentDocId);
        } else {
          showAlert(`Upload failed [${data.error?.code || res.status}]: ${data.error?.message || 'Error'}`, true);
          jsonViewer.innerText = JSON.stringify(data, null, 2);
        }
      } catch (err) {
        showAlert('Network error during upload', true);
      }
    }

    window.loadFixture = async function(filename, mime) {
      if (!authToken) {
        await doRegister('demo@docuquest.ai', 'Password123!');
      }
      showAlert(`Fetching fixture: ${filename}...`);
      try {
        const res = await fetch(`/sample_documents/${filename}`);
        if (!res.ok) throw new Error('Fixture fetch error');
        const blob = await res.blob();
        const file = new File([blob], filename, { type: mime });
        const formData = new FormData();
        formData.append('file', file);
        fileNameLabel.innerText = filename;
        await executeUpload(formData);
      } catch (err) {
        showAlert(`Failed to load fixture ${filename}: ${err.message}`, true);
      }
    };

    function pollStatus(docId) {
      if (pollingInterval) clearInterval(pollingInterval);
      jobStatusCard.classList.remove('hidden');
      activeDocIdText.innerText = `Document ID: ${docId}`;

      const poll = async () => {
        try {
          const res = await fetch(`/api/v1/documents/${docId}/status`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
          });
          if (!res.ok) return;
          const job = await res.json();
          if (!job) return;

          docStatusBadge.innerText = job.status;
          progressBar.style.width = `${job.progress}%`;
          progressPercent.innerText = `${job.progress}%`;
          progressText.innerText = `Job State: ${job.status}`;

          if (job.status === 'COMPLETED') {
            docStatusBadge.className = 'px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800';
            clearInterval(pollingInterval);
            fetchQuestions(docId);
          } else if (job.status === 'FAILED') {
            docStatusBadge.className = 'px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800';
            clearInterval(pollingInterval);
            showAlert(`Processing failed: ${job.error_message}`, true);
          }
        } catch (err) {
          console.error(err);
        }
      };

      poll();
      pollingInterval = setInterval(poll, 1200);
    }

    async function fetchQuestions(docId) {
      try {
        const res = await fetch(`/api/v1/documents/${docId}/questions`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const questions = await res.json();
        jsonViewer.innerText = JSON.stringify(questions, null, 2);

        if (!questions.length) {
          questionsContainer.innerHTML = `
            <div class="p-6 text-center text-slate-500 bg-slate-50 rounded-lg border border-slate-200 text-xs">
              No questions detected in this document. (If this is an Answer Key, use Section 3 to link it to a Question Paper!)
            </div>
          `;
          return;
        }

        renderQuestions(questions);
      } catch (err) {
        console.error(err);
      }
    }

    function renderQuestions(questions) {
      questionsContainer.innerHTML = '';
      questions.forEach((q) => {
        const card = document.createElement('div');
        card.className = 'bg-slate-50 rounded-lg p-4 border border-slate-200 transition hover:shadow-sm space-y-3';

        // Badges header
        const statusColor = q.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' :
                            q.status === 'PARTIAL' ? 'bg-amber-100 text-amber-800 border-amber-300' :
                            'bg-rose-100 text-rose-800 border-rose-300';

        const answerBadge = q.answer?.value ?
          `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">
            ✓ Key: Option ${q.answer.value} (${q.answer.status})
          </span>` :
          `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-200 text-slate-600">
            No Answer Key
          </span>`;

        const pagesText = q.source?.pages ? `Pages: ${q.source.pages.join(', ')}` : 'Page: 1';

        let optionsHtml = '';
        if (q.options && q.options.length) {
          optionsHtml = '<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">' +
            q.options.map(opt => {
              const isMatched = q.answer?.value && q.answer.value.toUpperCase() === opt.key.toUpperCase();
              const optStyle = isMatched ?
                'bg-indigo-50 border-indigo-400 text-indigo-900 font-semibold ring-1 ring-indigo-300' :
                'bg-white border-slate-200 text-slate-700';
              return `
                <div class="p-2 rounded border text-xs flex items-start space-x-2 ${optStyle}">
                  <span class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[11px] font-bold">${opt.key}</span>
                  <span class="leading-tight">${opt.text}</span>
                </div>
              `;
            }).join('') + '</div>';
        }

        let warningsHtml = '';
        if (q.warnings && q.warnings.length) {
          warningsHtml = `<div class="p-2 rounded bg-amber-50 border border-amber-200 text-[11px] text-amber-800 font-medium">
            ⚠️ ${q.warnings.join('; ')}
          </div>`;
        }

        card.innerHTML = `
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/60 pb-2">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded font-bold text-xs bg-slate-800 text-white">
                Q${q.question_number || '?'}
              </span>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-200 text-slate-700">
                ${q.question_type || 'UNKNOWN'}
              </span>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                📄 ${pagesText}
              </span>
            </div>
            <div class="flex items-center space-x-2">
              ${answerBadge}
              <span class="px-2 py-0.5 rounded text-[11px] font-semibold border ${statusColor}">
                ${q.status} (${Math.round(q.confidence * 100)}%)
              </span>
            </div>
          </div>

          <div class="text-xs text-slate-800 font-medium leading-relaxed">
            ${q.question}
          </div>

          ${optionsHtml}
          ${warningsHtml}
        `;
        questionsContainer.appendChild(card);
      });
    }

    refreshQuestionsBtn.addEventListener('click', () => {
      if (currentDocId) fetchQuestions(currentDocId);
    });

    linkBtn.addEventListener('click', async () => {
      const src = sourceDocId.value.trim();
      const tgt = targetDocId.value.trim();
      if (!src || !tgt) return showAlert('Please specify both Question Paper Document ID and Answer Key Document ID', true);
      if (!authToken) return showAlert('Please log in first', true);

      try {
        showAlert('Establishing ANSWER_KEY link and triggering matching...');
        const res = await fetch(`/api/v1/documents/${src}/relationships`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({
            target_document_id: tgt,
            relationship_type: 'ANSWER_KEY'
          })
        });
        const data = await res.json();
        if (res.ok) {
          showAlert('Relationship established! Answers successfully matched.');
          fetchQuestions(src);
        } else {
          showAlert(`Failed to link documents: ${data.error?.message || 'Error'}`, true);
        }
      } catch (err) {
        showAlert('Network error while linking documents', true);
      }
    });

    // Initialize
    checkAuth();
    if (currentDocId) {
      activeDocIdText.innerText = `Document ID: ${currentDocId}`;
      sourceDocId.value = currentDocId;
      fetchQuestions(currentDocId);
    }
  </script>
</body>
</html>
"""

target = Path(__file__).resolve().parents[1] / "app" / "static" / "index.html"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(content.strip(), encoding="utf-8")
print(f"Written HTML UI to {target}")
