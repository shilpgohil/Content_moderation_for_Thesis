import re
import os
from pathlib import Path

# Define paths relative to script
backend_root = Path(__file__).parent
project_root = backend_root.parent

def clean_python_file(filepath):
    """Remove excessive comments while keeping 2-3 essential short comments."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove module-level docstrings (triple quotes at start of file)
    content = re.sub(r'^"""[\s\S]*?"""', '', content, count=1, flags=re.MULTILINE)
    content = re.sub(r"^'''[\s\S]*?'''", '', content, count=1, flags=re.MULTILINE)
    
    # Remove class docstrings
    content = re.sub(r'(class [^:]+:)\s*"""[\s\S]*?"""', r'\1', content)
    content = re.sub(r"(class [^:]+:)\s*'''[\s\S]*?'''", r'\1', content)
    
    # Remove method/function docstrings
    content = re.sub(r'(def [^:]+:)\s*"""[\s\S]*?"""', r'\1', content)
    content = re.sub(r"(def [^:]+:)\s*'''[\s\S]*?'''", r'\1', content)
    
    # Remove step comments (# Step 1:, # Step 2:, etc.)
    content = re.sub(r'\n\s*# Step \d+:.*\n', '\n', content)
    
    # Remove section header comments (# ===== HEADER =====)
    content = re.sub(r'\n\s*#\s*=+\s*.*?\s*=+\s*\n', '\n', content)
    
    # Remove obvious inline comments (right after code)
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.search(r'^\s*#\s*(Initialize|Create|Set|Get|Load|Build|Check|Add|Remove|Update|Calculate|Process|Run|Execute|Perform|Return|Import)', line):
            # Skip standalone comment lines that describe obvious actions
            continue
        else:
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines (more than 2 in a row)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def clean_js_file(filepath):
    """Remove excessive comments from JS/JSX files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove section header comments (// ========== HEADER ==========)
    content = re.sub(r'\n\s*//\s*=+\s*.*?\s*=+\s*\n', '\n', content)
    
    # Remove block comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    
    # Remove obvious inline comments
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.search(r'^\s*//\s*(Color Constants|Helper|Add|Create|Setup|Initialize)', line):
            continue
        else:
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Process all Python files
python_files = [
    backend_root / 'content_moderation' / '__init__.py',
    backend_root / 'content_moderation' / 'config.py',
    backend_root / 'content_moderation' / 'pipeline' / '__init__.py',
    backend_root / 'content_moderation' / 'pipeline' / 'decision_engine.py',
    backend_root / 'content_moderation' / 'pipeline' / 'domain_checker.py',
    backend_root / 'content_moderation' / 'pipeline' / 'fuzzy_matcher.py',
    backend_root / 'content_moderation' / 'pipeline' / 'linguistic_analyzer.py',
    backend_root / 'content_moderation' / 'pipeline' / 'preprocessor.py',
    backend_root / 'content_moderation' / 'pipeline' / 'rule_engine.py',
    backend_root / 'content_moderation' / 'pipeline' / 'semantic_checker.py',
    backend_root / 'content_moderation' / 'pipeline' / 'toxicity_checker.py',
    backend_root / 'main.py',
    backend_root / 'models.py',
    backend_root / 'moderator_api.py',
    backend_root / 'analyzer.py',
    backend_root / 'prompts.py',
    backend_root / 'templates.py',
    backend_root / 'vocabularies.py',
    backend_root / 'shared' / '__init__.py',
    backend_root / 'shared' / 'model_manager.py',
]

# Process all JS/JSX files
frontend_root = project_root / 'frontend'
js_files = [
    frontend_root / 'src' / 'App.jsx',
    frontend_root / 'src' / 'main.jsx',
    frontend_root / 'src' / 'api' / 'analyzer.js',
    frontend_root / 'src' / 'components' / 'AuditTable.jsx',
    frontend_root / 'src' / 'components' / 'BiasGauge.jsx',
    frontend_root / 'src' / 'components' / 'ComponentCards.jsx',
    frontend_root / 'src' / 'components' / 'Dashboard.jsx',
    frontend_root / 'src' / 'components' / 'Hero.jsx',
    frontend_root / 'src' / 'components' / 'LoadingState.jsx',
    frontend_root / 'src' / 'components' / 'ModerationBlockedView.jsx',
    frontend_root / 'src' / 'components' / 'ModerationLoadingState.jsx',
    frontend_root / 'src' / 'components' / 'ScoreGauge.jsx',
    frontend_root / 'src' / 'components' / 'SentenceAnalysis.jsx',
    frontend_root / 'src' / 'components' / 'Synthesis.jsx',
    frontend_root / 'src' / 'components' / 'UploadSection.jsx',
    frontend_root / 'src' / 'components' / 'WeaknessReport.jsx',
    frontend_root / 'vite.config.js',
    frontend_root / 'tailwind.config.js',
    frontend_root / 'postcss.config.js',
]

print("Starting comment cleanup...")
print(f"Processing {len(python_files)} Python files...")

processed_count = 0
for py_file in python_files:
    if py_file.exists():
        if clean_python_file(py_file):
            processed_count += 1
            print(f"✓ Cleaned: {py_file.name}")
        else:
            print(f"- No changes: {py_file.name}")
    else:
        print(f"✗ Not found: {py_file}")

print(f"\nProcessing {len(js_files)} JS/JSX files...")
js_processed = 0
for js_file in js_files:
    if js_file.exists():
        if clean_js_file(js_file):
            js_processed += 1
            print(f"✓ Cleaned: {js_file.name}")
        else:
            print(f"- No changes: {js_file.name}")
    else:
        print(f"✗ Not found: {js_file}")

print(f"\n{'='*50}")
print(f"SUMMARY:")
print(f"Python files cleaned: {processed_count}/{len(python_files)}")
print(f"JS/JSX files cleaned: {js_processed}/{len(js_files)}")
print(f"Total files processed: {processed_count + js_processed}")
print(f"{'='*50}")
