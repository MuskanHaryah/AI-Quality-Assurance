"""
Dataset Processing Script for QualityMapAI
==========================================
This script:
1. Reads software_requirements_extended.csv (977 rows)
2. Reads requirements_template.csv (50 rows)
3. Maps ALL category codes to ISO/IEC 9126 standard (7 categories)
4. Classifies NFR (generic non-functional) requirements using keywords
5. Cleans text (encoding issues, whitespace, vague requirements)
6. Removes duplicates
7. Merges both datasets
8. Adds sub-categories and keywords
9. Balances and validates
10. Outputs final training-ready CSV

ISO/IEC 9126 Categories:
1. Functionality
2. Security (elevated from sub-characteristic)
3. Reliability
4. Usability
5. Efficiency
6. Maintainability
7. Portability
"""

import csv
import re
import os
from collections import Counter

# ============================================================
# CONFIGURATION
# ============================================================

# Code-to-ISO mapping
CODE_TO_ISO = {
    'F':   'Functionality',
    'FR':  'Functionality',      # Generic "Functional Requirement"
    'PE':  'Efficiency',         # Performance → Efficiency
    'US':  'Usability',
    'SE':  'Security',
    'A':   'Reliability',        # Availability → Reliability
    'FT':  'Reliability',        # Fault Tolerance → Reliability
    'LF':  'Usability',          # Look & Feel → Usability (Attractiveness)
    'O':   'Portability',        # Operational/Environment → Portability
    'SC':  'Efficiency',         # Scalability → Efficiency (Resource Utilization)
    'MN':  'Maintainability',    # Maintenance → Maintainability
    'L':   'Functionality',      # Legal/Compliance → Functionality (Compliance)
    'PO':  'Portability',        # Portability
}

# Sub-category mapping based on original code
CODE_TO_SUBCATEGORY = {
    'F':   'Suitability',
    'FR':  'Suitability',
    'PE':  'Time_Behavior',
    'US':  'Operability',
    'SE':  'Security',
    'A':   'Maturity',
    'FT':  'Fault_Tolerance',
    'LF':  'Attractiveness',
    'O':   'Adaptability',
    'SC':  'Resource_Utilization',
    'MN':  'Changeability',
    'L':   'Compliance',
    'PO':  'Adaptability',
}

# Keywords for classifying NFR (generic Non-Functional Requirements)
NFR_CLASSIFICATION_KEYWORDS = {
    'Security': [
        'secure', 'security', 'encrypt', 'password', 'authentication', 'authorize',
        'authorization', 'access control', 'login', 'credential', 'permission',
        'firewall', 'ssl', 'https', 'token', 'privacy', 'confidential', 'malicious',
        'virus', 'attack', 'vulnerability', 'threat', 'audit', 'log access',
        'role-based', 'rbac', 'injection', 'xss', 'csrf', 'hash', 'bcrypt',
    ],
    'Efficiency': [
        'performance', 'response time', 'speed', 'fast', 'latency', 'throughput',
        'load time', 'processing time', 'concurrent', 'scalab', 'bandwidth',
        'memory', 'cpu', 'resource', 'cache', 'buffer', 'compress', 'optimize',
        'millisecond', 'second', 'minute', 'capacity', 'simultaneous',
    ],
    'Reliability': [
        'availability', 'uptime', 'downtime', 'reliable', 'fault', 'recover',
        'backup', 'restore', 'failover', 'redundan', 'crash', 'robust',
        'error handling', 'exception', 'resilient', 'tolerance', 'stable',
        'data integrity', '99.', '24/7', '24x7', 'always available',
    ],
    'Usability': [
        'easy to use', 'intuitive', 'user-friendly', 'user friendly', 'usab',
        'learn', 'training', 'accessible', 'interface', 'navigation', 'click',
        'understandable', 'readable', 'attractive', 'look and feel', 'appearance',
        'color', 'font', 'layout', 'design', 'ui ', 'ux ', 'screen',
        'display', 'help', 'feedback', 'error message', 'self-explanatory',
        'localization', 'language', 'translation', 'disability', 'ada ',
    ],
    'Maintainability': [
        'maintain', 'maintenance', 'modular', 'extensible', 'configurable',
        'testable', 'test coverage', 'code quality', 'documentation', 'standard',
        'coding', 'pep-8', 'refactor', 'upgrade', 'update', 'version',
        'backward compatible', 'changeable', 'flexible', 'readable code',
        'design pattern', 'architecture', 'clean code', 'coupling', 'cohesion',
    ],
    'Portability': [
        'portable', 'portability', 'cross-platform', 'platform', 'operating system',
        'windows', 'linux', 'macos', 'mac os', 'browser', 'chrome', 'firefox',
        'safari', 'edge', 'mobile', 'tablet', 'android', 'ios', 'deploy',
        'install', 'cloud', 'docker', 'container', 'migration', 'environment',
        'compatible', 'interoperab', 'coexist', 'hardware',
    ],
    'Functionality': [
        'shall', 'must', 'function', 'feature', 'provide', 'allow', 'enable',
        'create', 'delete', 'update', 'search', 'display', 'generate', 'calculate',
        'process', 'store', 'retrieve', 'send', 'receive', 'notify', 'validate',
        'import', 'export', 'report', 'record', 'manage', 'support',
    ],
}

# Sub-category refinement based on keywords
SUBCATEGORY_KEYWORDS = {
    'Functionality': {
        'Suitability': ['provide', 'allow', 'enable', 'create', 'delete', 'update', 'search',
                        'display', 'store', 'manage', 'support', 'record', 'send', 'receive'],
        'Accuracy': ['validate', 'accurate', 'precision', 'correct', 'verify', 'calculate',
                     'exact', 'integrity'],
        'Interoperability': ['interface', 'integrate', 'api', 'exchange', 'communicate',
                             'interoperable', 'connect', 'protocol'],
        'Compliance': ['comply', 'compliance', 'regulation', 'legal', 'law', 'standard',
                       'guideline', 'audit', 'sarbanes', 'pear', 'w3c'],
    },
    'Efficiency': {
        'Time_Behavior': ['response time', 'speed', 'fast', 'latency', 'load time',
                          'processing time', 'second', 'minute', 'millisecond', 'quick'],
        'Resource_Utilization': ['memory', 'cpu', 'bandwidth', 'disk', 'storage', 'resource',
                                'concurrent', 'simultaneous', 'capacity', 'scalab', 'throughput'],
    },
    'Reliability': {
        'Maturity': ['uptime', 'availability', 'available', '99.', 'failure rate',
                     'mean time', 'mtbf', 'reliable'],
        'Fault_Tolerance': ['fault', 'error handling', 'crash', 'graceful', 'robust',
                            'continue', 'resilient', 'tolerance', 'exception'],
        'Recoverability': ['recover', 'backup', 'restore', 'failover', 'redundan',
                           'disaster', 'resume', 'restart'],
    },
    'Usability': {
        'Understandability': ['understand', 'readable', 'clear', 'obvious', 'comprehensible',
                              'self-explanatory', 'intuitive'],
        'Learnability': ['learn', 'training', 'onboard', 'tutorial', 'documentation',
                         'help', 'guide', 'instruction', 'novice'],
        'Operability': ['easy to use', 'click', 'navigation', 'navigate', 'operate',
                        'efficient', 'task', 'workflow', 'keyboard'],
        'Attractiveness': ['attractive', 'appearance', 'look', 'feel', 'color', 'font',
                           'design', 'professional', 'aesthetic', 'visual', 'branding',
                           'logo', 'theme', 'scheme', 'modern', 'clean'],
    },
    'Security': {
        'Security': ['encrypt', 'password', 'authentication', 'authorize', 'access',
                     'secure', 'firewall', 'privacy', 'malicious', 'virus', 'attack',
                     'permission', 'role', 'credential', 'audit'],
    },
    'Maintainability': {
        'Analyzability': ['code quality', 'standard', 'documentation', 'readable code',
                          'complexity', 'pep-8', 'lint', 'inspect'],
        'Changeability': ['modular', 'extensible', 'flexible', 'changeable', 'configurable',
                          'design pattern', 'architecture', 'decouple'],
        'Stability': ['stable', 'backward compatible', 'regression', 'consistent'],
        'Testability': ['testable', 'test coverage', 'unit test', 'test case', 'testing'],
    },
    'Portability': {
        'Adaptability': ['platform', 'operating system', 'windows', 'linux', 'macos',
                         'browser', 'mobile', 'cloud', 'cross-platform', 'environment'],
        'Installability': ['install', 'setup', 'deploy', 'configure', 'package',
                           'distribution', 'upgrade'],
        'Coexistence': ['coexist', 'alongside', 'compatible', 'conflict', 'other software'],
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    """Clean requirement text: fix encoding, whitespace, etc."""
    if not text:
        return ''
    
    # Fix common encoding issues
    text = text.replace('ï¿½', "'")  # UTF-8 replacement character
    text = text.replace('â€™', "'")
    text = text.replace('â€œ', '"')
    text = text.replace('â€\x9d', '"')
    text = text.replace('â€"', '-')
    text = text.replace('â€"', '-')
    text = text.replace('\x92', "'")
    text = text.replace('\x93', '"')
    text = text.replace('\x94', '"')
    text = text.replace('\x96', '-')
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove leading/trailing punctuation artifacts
    text = text.strip('.,;: ')
    
    # Ensure it starts with a capital letter
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    
    return text


def is_valid_requirement(text):
    """Check if a requirement is valid (not too short, not too vague)."""
    if not text:
        return False
    
    # Too short (less than 15 characters)
    if len(text) < 15:
        return False
    
    # Too few words (less than 4)
    words = text.split()
    if len(words) < 4:
        return False
    
    # Too vague patterns
    vague_patterns = [
        r'^the system$',
        r'^the product$',
        r'^the application$',
        r'^n/a$',
        r'^none$',
        r'^todo$',
        r'^tbd$',
        r'^not applicable$',
    ]
    text_lower = text.lower().strip()
    for pattern in vague_patterns:
        if re.match(pattern, text_lower):
            return False
    
    return True


def classify_nfr(text):
    """Classify a generic NFR requirement into ISO category."""
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in NFR_CLASSIFICATION_KEYWORDS.items():
        if category == 'Functionality':
            continue  # Skip Functionality for NFR - it should be non-functional
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        scores[category] = score
    
    # If no clear match, check for Functionality as fallback
    if max(scores.values(), default=0) == 0:
        return 'Functionality', 'Suitability'
    
    best_category = max(scores, key=scores.get)
    
    # If multiple categories tie, use priority
    priority_order = ['Security', 'Efficiency', 'Reliability', 'Usability',
                      'Maintainability', 'Portability', 'Functionality']
    max_score = scores[best_category]
    tied = [cat for cat, s in scores.items() if s == max_score]
    if len(tied) > 1:
        for p in priority_order:
            if p in tied:
                best_category = p
                break
    
    # Determine sub-category
    sub_category = determine_subcategory(text, best_category)
    
    return best_category, sub_category


def determine_subcategory(text, category):
    """Determine the sub-category within a main ISO category."""
    text_lower = text.lower()
    
    if category not in SUBCATEGORY_KEYWORDS:
        return 'General'
    
    scores = {}
    for sub_cat, keywords in SUBCATEGORY_KEYWORDS[category].items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[sub_cat] = score
    
    if max(scores.values(), default=0) == 0:
        # Return first sub-category as default
        return list(SUBCATEGORY_KEYWORDS[category].keys())[0]
    
    return max(scores, key=scores.get)


def extract_keywords(text, max_keywords=5):
    """Extract relevant keywords from requirement text."""
    # Common stopwords
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'must', 'need', 'to', 'of',
        'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'between', 'out', 'off',
        'up', 'down', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'same', 'so', 'than',
        'too', 'very', 'just', 'because', 'but', 'and', 'or', 'if', 'while',
        'that', 'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'we', 'our', 'he', 'she', 'his', 'her', 'my', 'your', 'any', 'also',
        'which', 'who', 'whom', 'what', 'about', 'over', 'under', 'again',
        'further', 'product', 'system', 'application', 'software', 'user',
        'users', 'able', 'within', 'time', 'using', 'used', 'use', 'new',
        'provide', 'provided', 'upon', 'per', 'been', 'without', 'either',
        'following',
    }
    
    words = re.findall(r'[a-zA-Z]+', text.lower())
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    
    # Count frequency
    freq = Counter(filtered)
    keywords = [w for w, _ in freq.most_common(max_keywords)]
    
    return ' '.join(keywords)


def determine_confidence(text, category, original_code):
    """Determine confidence level of classification."""
    if original_code == 'NFR':
        # NFR was auto-classified, lower confidence
        return 'Medium'
    
    text_lower = text.lower()
    
    # Check if the text clearly matches the category
    if category in NFR_CLASSIFICATION_KEYWORDS:
        matches = sum(1 for kw in NFR_CLASSIFICATION_KEYWORDS[category] if kw in text_lower)
        if matches >= 3:
            return 'High'
        elif matches >= 1:
            return 'Medium'
    
    # If original code clearly maps, high confidence
    if original_code in CODE_TO_ISO:
        return 'High'
    
    return 'Medium'


# ============================================================
# MAIN PROCESSING
# ============================================================

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("QualityMapAI - Dataset Processing Script")
    print("=" * 60)
    
    # ----- Step 1: Read software_requirements_extended.csv -----
    print("\n[1/8] Reading software_requirements_extended.csv...")
    csv_path = os.path.join(base_dir, 'software_requirements_extended.csv')
    
    raw_rows = []
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row and len(row) >= 2:
                raw_rows.append((row[0].strip(), row[1].strip()))
    
    print(f"  Read {len(raw_rows)} rows")
    print(f"  Category codes: {dict(Counter(r[0] for r in raw_rows))}")
    
    # ----- Step 2: Read requirements_template.csv -----
    print("\n[2/8] Reading requirements_template.csv...")
    template_path = os.path.join(base_dir, 'ml-training', 'dataset', 'requirements_template.csv')
    
    template_rows = []
    with open(template_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row and len(row) >= 3:
                template_rows.append({
                    'text': row[1].strip(),
                    'category': row[2].strip(),
                    'sub_category': row[3].strip() if len(row) > 3 else '',
                    'source': 'template',
                    'original_code': 'TEMPLATE',
                })
    
    print(f"  Read {len(template_rows)} rows")
    
    # ----- Step 2b: Read additional_requirements.csv (if exists) -----
    additional_path = os.path.join(base_dir, 'ml-training', 'dataset', 'additional_requirements.csv')
    additional_rows = []
    if os.path.exists(additional_path):
        print("\n[2b/8] Reading additional_requirements.csv...")
        with open(additional_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if row and len(row) >= 3:
                    additional_rows.append({
                        'text': clean_text(row[1].strip()),
                        'category': row[2].strip(),
                        'sub_category': row[3].strip() if len(row) > 3 else '',
                        'source': row[6].strip() if len(row) > 6 else 'augmented',
                        'original_code': 'AUGMENTED',
                    })
        print(f"  Read {len(additional_rows)} additional rows")
        cat_counts = Counter(r['category'] for r in additional_rows)
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")
    
    # ----- Step 3: Map codes to ISO categories -----
    print("\n[3/8] Mapping category codes to ISO/IEC 9126...")
    
    mapped_rows = []
    unmapped_count = 0
    nfr_count = 0
    
    for code, text in raw_rows:
        clean = clean_text(text)
        
        if not is_valid_requirement(clean):
            continue
        
        if code == 'NFR':
            # Auto-classify NFR using keywords
            category, sub_category = classify_nfr(clean)
            nfr_count += 1
        elif code in CODE_TO_ISO:
            category = CODE_TO_ISO[code]
            sub_category = CODE_TO_SUBCATEGORY.get(code, 'General')
            # Refine sub-category based on text content
            refined_sub = determine_subcategory(clean, category)
            if refined_sub != list(SUBCATEGORY_KEYWORDS.get(category, {'General': []}).keys())[0]:
                sub_category = refined_sub
        else:
            unmapped_count += 1
            continue
        
        mapped_rows.append({
            'text': clean,
            'category': category,
            'sub_category': sub_category,
            'source': 'extended_csv',
            'original_code': code,
        })
    
    print(f"  Successfully mapped: {len(mapped_rows)}")
    print(f"  NFR auto-classified: {nfr_count}")
    print(f"  Skipped (unmapped/invalid): {unmapped_count + (len(raw_rows) - len(mapped_rows) - unmapped_count)}")
    
    # ----- Step 4: Merge with template + additional -----
    print("\n[4/8] Merging all datasets...")
    
    all_rows = mapped_rows + template_rows + additional_rows
    print(f"  Extended CSV: {len(mapped_rows)}")
    print(f"  Template: {len(template_rows)}")
    print(f"  Additional: {len(additional_rows)}")
    print(f"  Combined total: {len(all_rows)}")
    
    # ----- Step 5: Remove duplicates -----
    print("\n[5/8] Removing duplicates...")
    
    seen = set()
    unique_rows = []
    dup_count = 0
    
    for row in all_rows:
        # Normalize text for comparison
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', row['text'].lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        if normalized not in seen and len(normalized) > 10:
            seen.add(normalized)
            unique_rows.append(row)
        else:
            dup_count += 1
    
    print(f"  Duplicates removed: {dup_count}")
    print(f"  Unique requirements: {len(unique_rows)}")
    
    # ----- Step 6: Clean and validate -----
    print("\n[6/8] Final cleaning and validation...")
    
    final_rows = []
    removed = {'too_short': 0, 'too_vague': 0, 'invalid': 0}
    
    for row in unique_rows:
        text = row['text']
        
        # Skip requirements that are too short
        if len(text) < 20:
            removed['too_short'] += 1
            continue
        
        # Skip very vague ones
        vague_indicators = [
            'the system shall be good',
            'the product shall work',
            'the system shall be nice',
        ]
        if text.lower().strip('.') in vague_indicators:
            removed['too_vague'] += 1
            continue
        
        # Add keywords, confidence
        keywords = extract_keywords(text)
        confidence = determine_confidence(text, row['category'], row['original_code'])
        
        final_rows.append({
            'text': text,
            'category': row['category'],
            'sub_category': row['sub_category'],
            'keywords': keywords,
            'confidence': confidence,
            'source': row['source'],
        })
    
    print(f"  Removed - too short: {removed['too_short']}")
    print(f"  Removed - too vague: {removed['too_vague']}")
    print(f"  Final valid requirements: {len(final_rows)}")
    
    # ----- Step 7: Category distribution -----
    print("\n[7/8] Category distribution analysis...")
    
    cat_counts = Counter(r['category'] for r in final_rows)
    print(f"\n  {'Category':<20} {'Count':>6} {'Percentage':>10}")
    print(f"  {'-'*40}")
    total = len(final_rows)
    for cat in ['Functionality', 'Security', 'Efficiency', 'Usability',
                'Reliability', 'Maintainability', 'Portability']:
        count = cat_counts.get(cat, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = '█' * int(pct / 2)
        print(f"  {cat:<20} {count:>6} {pct:>8.1f}%  {bar}")
    
    # Sub-category distribution
    print(f"\n  Sub-category breakdown:")
    for cat in ['Functionality', 'Security', 'Efficiency', 'Usability',
                'Reliability', 'Maintainability', 'Portability']:
        sub_counts = Counter(
            r['sub_category'] for r in final_rows if r['category'] == cat
        )
        if sub_counts:
            subs = ', '.join(f"{s}:{c}" for s, c in sub_counts.most_common())
            print(f"    {cat}: {subs}")
    
    # ----- Step 8: Write final CSV -----
    print("\n[8/8] Writing final training dataset...")
    
    output_dir = os.path.join(base_dir, 'ml-training', 'dataset')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'requirements_dataset_final.csv')
    
    # Sort by category for consistency
    category_order = ['Functionality', 'Security', 'Efficiency', 'Usability',
                      'Reliability', 'Maintainability', 'Portability']
    final_rows.sort(key=lambda r: (category_order.index(r['category'])
                                    if r['category'] in category_order else 99,
                                    r['sub_category']))
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Requirement_Text', 'ISO_Category', 'ISO_Sub_Category',
            'Keywords', 'Confidence', 'Source'
        ])
        
        for i, row in enumerate(final_rows, 1):
            writer.writerow([
                i,
                row['text'],
                row['category'],
                row['sub_category'],
                row['keywords'],
                row['confidence'],
                row['source'],
            ])
    
    print(f"  Saved to: {output_path}")
    print(f"  Total rows: {len(final_rows)}")
    
    # ----- Summary -----
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"""
  Input files:
    - software_requirements_extended.csv: {len(raw_rows)} rows
    - requirements_template.csv: {len(template_rows)} rows
    - Total input: {len(raw_rows) + len(template_rows)} rows
  
  Processing:
    - Invalid/too short removed: {len(raw_rows) + len(template_rows) - len(all_rows) + removed['too_short'] + removed['too_vague']}
    - Duplicates removed: {dup_count}
    - NFR auto-classified: {nfr_count}
  
  Output:
    - Final dataset: {len(final_rows)} clean, labeled requirements
    - File: ml-training/dataset/requirements_dataset_final.csv
    - Format: ID, Requirement_Text, ISO_Category, ISO_Sub_Category, Keywords, Confidence, Source
  
  Category Summary:""")
    
    for cat in category_order:
        count = cat_counts.get(cat, 0)
        pct = (count / total * 100) if total > 0 else 0
        status = '✓' if count >= 30 else '⚠ LOW'
        print(f"    {cat:<20}: {count:>4} ({pct:.1f}%) {status}")
    
    print(f"\n  TOTAL: {len(final_rows)} requirements ready for ML training")
    print(f"\n  Ready to train! Run: python train_model.py")


if __name__ == '__main__':
    main()
