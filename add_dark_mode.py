import re

with open('app/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add tailwind config
config = """<script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
    }
  </script>"""
content = content.replace('<script src="https://cdn.tailwindcss.com"></script>', config)

# Add toggle button
header_insert = """<div class="flex items-center space-x-3 text-sm">
        <button id="darkModeToggle" class="p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
          ☀️
        </button>"""
content = content.replace('<div class="flex items-center space-x-3 text-sm">', header_insert)

# Add JS logic
js_insert = """<script>
    // Dark mode logic
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
      darkModeToggle.innerText = '☀️';
    } else {
      darkModeToggle.innerText = '🌙';
    }
    
    darkModeToggle.addEventListener('click', () => {
      document.documentElement.classList.toggle('dark');
      if (document.documentElement.classList.contains('dark')) {
        localStorage.setItem('theme', 'dark');
        darkModeToggle.innerText = '☀️';
      } else {
        localStorage.setItem('theme', 'light');
        darkModeToggle.innerText = '🌙';
      }
    });
"""
content = content.replace('<script>\n    let authToken', js_insert + '\n    let authToken')

# Replace common classes for dark mode
replacements = {
    'bg-slate-50': 'bg-slate-50 dark:bg-slate-900',
    'text-slate-800': 'text-slate-800 dark:text-slate-200',
    'bg-white': 'bg-white dark:bg-slate-800',
    'border-slate-200': 'border-slate-200 dark:border-slate-700',
    'border-slate-300': 'border-slate-300 dark:border-slate-600',
    'text-slate-700': 'text-slate-700 dark:text-slate-300',
    'text-slate-600': 'text-slate-600 dark:text-slate-400',
    'text-slate-500': 'text-slate-500 dark:text-slate-400',
    'bg-slate-100': 'bg-slate-100 dark:bg-slate-700',
    'bg-slate-200': 'bg-slate-200 dark:bg-slate-700',
    'hover:bg-slate-200': 'hover:bg-slate-200 dark:hover:bg-slate-600',
    'hover:bg-slate-50': 'hover:bg-slate-50 dark:hover:bg-slate-700',
    'border-slate-100': 'border-slate-100 dark:border-slate-700',
    'border-slate-200/60': 'border-slate-200/60 dark:border-slate-700/60',
    'bg-slate-50/50': 'bg-slate-50/50 dark:bg-slate-800/50',
    'bg-indigo-50': 'bg-indigo-50 dark:bg-indigo-900/30',
    'text-indigo-700': 'text-indigo-700 dark:text-indigo-300',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
