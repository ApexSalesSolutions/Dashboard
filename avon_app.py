import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import re
import requests
from io import BytesIO
import numpy as np
import tempfile
import calendar
import os
import json

# Προαιρετικό import για το PDF (Safe loading)
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# Προαιρετικό import για autorefresh
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# ==========================================
# 1. CONFIG & UI STYLING
# ==========================================
st.set_page_config(page_title="Avon Strategic AI v800 (Machine Learning Edition)", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }

    /* === Ορατή γραμμή κύλισης (scrollbar) — χρήσιμο ειδικά σε κινητό/λειτουργία
       βοηθού, όπου η προεπιλεγμένη γραμμή του browser είναι πολύ λεπτή/αόρατη === */
    ::-webkit-scrollbar { width: 12px; height: 12px; }
    ::-webkit-scrollbar-track { background: #14141f; }
    ::-webkit-scrollbar-thumb { background: #7360f2; border-radius: 10px; border: 2px solid #14141f; }
    ::-webkit-scrollbar-thumb:hover { background: #9280ff; }
    * { scrollbar-width: thin; scrollbar-color: #7360f2 #14141f; }

    /* === Λευκά γράμματα στα tabs — ξεχωρίζουν καθαρά στο σκούρο φόντο === */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p,
    .stTabs [data-baseweb="tab-list"] button p,
    .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-weight: 600 !important; }
    .stTabs [aria-selected="true"] p { color: #ff69b4 !important; }

    /* === Λευκά τηλέφωνα — τα κλικαρίσιμα tel: links εμφανίζονταν με το
       προεπιλεγμένο μπλε χρώμα link, δύσκολα ορατό στο σκούρο φόντο === */
    a[href^="tel:"] { color: #ffffff !important; text-decoration: none !important; }
    a[href^="tel:"]:hover { color: #ff69b4 !important; text-decoration: underline !important; }

    [data-testid="stMetric"] {
        background: rgba(28, 31, 38, 0.7) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    [data-testid="stMetricValue"] { color: #ff2a85 !important; font-size: 28px !important; font-weight: 800; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 14px !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;}
    .daily-box {
        background: linear-gradient(135deg, rgba(214, 51, 132, 0.15) 0%, rgba(89, 27, 60, 0.3) 100%);
        backdrop-filter: blur(12px); border-radius: 16px; padding: 25px; margin: 15px 0 30px 0; 
        text-align: center; border: 1px solid rgba(214, 51, 132, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .vip-box {
        background: linear-gradient(90deg, rgba(30, 70, 32, 0.8) 0%, rgba(20, 45, 22, 0.9) 100%);
        backdrop-filter: blur(8px); color: #ffffff; padding: 20px;
        border-radius: 12px; border-left: 6px solid #10b981; margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    .confidence-box {
        background: rgba(26, 26, 46, 0.6); backdrop-filter: blur(8px);
        padding: 15px 25px; border-radius: 12px; margin: 10px 0 20px 0;
        text-align: center; border: 1px solid rgba(115, 96, 242, 0.3);
        font-size: 1em; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;
    }
    .watchlist-box {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.15) 0%, rgba(139, 0, 0, 0.3) 100%);
        border: 1px solid rgba(220, 53, 69, 0.4); padding: 20px; border-radius: 12px; margin-bottom: 25px;
        backdrop-filter: blur(8px); box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
    }
    hr { border-color: rgba(255,255,255,0.05); margin: 25px 0; }
    .member-card {
        background: rgba(28,31,48,0.8); border: 1px solid rgba(115,96,242,0.25);
        border-radius: 12px; padding: 14px 18px; margin-bottom: 8px;
    }
    .note-badge {
        background: rgba(255,193,7,0.15); border: 1px solid rgba(255,193,7,0.4);
        border-radius: 8px; padding: 3px 9px; font-size: 11px; color: #ffc107;
        display: inline-block; margin-left: 8px;
    }
    .post-campaign-box {
        background: linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,60,40,0.4) 100%);
        border: 1px solid rgba(16,185,129,0.4); border-radius: 16px; padding: 28px;
        margin: 20px 0; text-align: center;
    }
    .near-target-banner {
        background: linear-gradient(90deg, #ff6b35, #f7c948, #ff6b35);
        background-size: 200% auto; animation: shine 2s linear infinite;
        border-radius: 12px; padding: 16px; text-align: center;
        font-size: 1.1em; font-weight: 800; color: #000; margin-bottom: 18px;
    }
    @keyframes shine { to { background-position: 200% center; } }
    </style>
    """, unsafe_allow_html=True)

if 'sent_ids' not in st.session_state:
    st.session_state.sent_ids = set()

# ==========================================
# 2. ΣΥΝΑΡΤΗΣΕΙΣ
# ==========================================
def remove_accents(text):
    if not isinstance(text, str): return str(text)
    replacements = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ώ': 'Ω',
        'ϊ': 'ι', 'ϋ': 'υ', 'ΐ': 'ι', 'ΰ': 'υ'
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    return text

def smart_clean_name(raw_name):
    if pd.isna(raw_name):
        return ""
    cleaned = remove_accents(str(raw_name))
    # ΚΡΙΣΙΜΟ: πολλά ελληνικά διπλά επώνυμα χρησιμοποιούν παύλα (π.χ. "ΣΤΥΛΙΑΝΟΥ-ΚΑΜΤΣΗ").
    # Η επόμενη regex αφαιρεί οτιδήποτε δεν είναι ελληνικό/λατινικό γράμμα ή κενό — αν δεν
    # μετατρέψουμε πρώτα την παύλα σε κενό, τα δύο επώνυμα "κολλάνε" σε μία λέξη
    # (π.χ. "ΣΤΥΛΙΑΝΟΥΚΑΜΤΣΗ"), κάτι που έσπαγε το matching με το ιστορικό.
    cleaned = cleaned.replace('-', ' ').replace('–', ' ').replace('—', ' ')
    cleaned = re.sub(r'[^Α-ΩA-Z\s]', '', cleaned.upper())
    
    # Καθαρισμός των Tiers από το όνομα για σωστό matching με το Ιστορικό
    for t in ['DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'STANDARD', 'VIP', 'NEW BUSINESS', 'MEMBER', 'STAR', 'PRESIDENT', 'ELITE', 'MANAGER', 'LEADER', 'CONSULTANT']:
        cleaned = re.sub(rf'\b{t}\b', '', cleaned)
        
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    words = cleaned.split()
    words.sort()
    return " ".join(words)

def clean_phone(num):
    if pd.isna(num) or str(num).strip() == "": return None
    digits = "".join(re.findall(r'\d+', str(num)))
    if len(digits) == 10 and digits.startswith('69'): return '30' + digits
    if len(digits) == 12 and digits.startswith('3069'): return digits
    if len(digits) > 10 and digits.startswith('69'): return '30' + digits[:10]
    return None

def get_greet():
    return "Καλημέρα" if datetime.now().hour < 12 else "Καλησπέρα"

def get_tier_rank(name):
    n = str(name).upper()
    if 'BRONZE' in n: return 1
    elif 'SILVER' in n: return 2
    elif 'GOLD' in n: return 3
    elif 'PLATINUM' in n: return 4
    elif 'DIAMOND' in n: return 5
    else: return 6

def get_tier_from_name(name):
    n = str(name).upper()
    if 'DIAMOND' in n: return 'DIAMOND'
    elif 'PLATINUM' in n: return 'PLATINUM'
    elif 'GOLD' in n: return 'GOLD'
    elif 'SILVER' in n: return 'SILVER'
    elif 'BRONZE' in n: return 'BRONZE'
    elif 'NEW BUSINESS' in n or 'NEWBUSINESS' in n: return 'NEW BUSINESS'
    return 'STANDARD'

# Defaults αν δεν υπάρχουν ακόμα ιστορικά δεδομένα (bootstrap values)
_TIER_FALLBACK_DEFAULTS = {
    'DIAMOND': 530.0,
    'PLATINUM': 217.0,
    'GOLD': 90.0,
    'SILVER': 45.0,
    'BRONZE': 35.0,
    'STANDARD': 65.0,
    'NEW BUSINESS': 55.0,
}

# Θα συμπληρωθεί δυναμικά μετά τη φόρτωση ιστορικών δεδομένων
_dynamic_tier_baskets = {}

def get_manual_fallback(name):
    """
    Επιστρέφει εκτιμώμενη αξία μέλους βάσει tier.
    Προτεραιότητα: δυναμικό ιστορικό μ.ο. > hardcoded default.
    """
    tier = get_tier_from_name(name)
    if tier in _dynamic_tier_baskets and _dynamic_tier_baskets[tier] > 0:
        return _dynamic_tier_baskets[tier]
    return _TIER_FALLBACK_DEFAULTS.get(tier, 65.0)

def parse_money(val):
    if pd.isna(val): return 0.0
    v = str(val).replace('€', '').replace(' ', '')
    if '.' in v and ',' in v:
        v = v.replace('.', '').replace(',', '.')
    elif ',' in v:
        v = v.replace(',', '.')
    try:
        return float(v)
    except:
        return 0.0

def get_campaign_end_date(ref_date=None):
    """
    Υπολογίζει ημερομηνία κλεισίματος καμπάνιας:
    Τελευταία μέρα του μήνα — αν πέφτει Κυριακή, πάει στο προηγούμενο Σάββατο.
    """
    if ref_date is None:
        ref_date = date.today()
    _, last_day = calendar.monthrange(ref_date.year, ref_date.month)
    end = date(ref_date.year, ref_date.month, last_day)
    if end.weekday() == 6:  # Κυριακή
        end -= timedelta(days=1)
    return end

def parse_period_index(col_name):
    """Εξάγει sortable index από όνομα στήλης ιστορικότητας (π.χ. 'ΜΙΚΤΕΣ 202501' → 202501)"""
    col_upper = col_name.upper()
    # YYYYMM pattern (π.χ. 202501, 202412)
    match = re.search(r'(202\d)(0[1-9]|1[0-2])', col_name)
    if match:
        return int(match.group(1)) * 100 + int(match.group(2))
    # Q pattern: "Q1 2025" ή "2025 Q1"
    match = re.search(r'Q(\d)\s*(202\d)', col_upper)
    if match:
        return int(match.group(2)) * 100 + int(match.group(1)) * 3
    match = re.search(r'(202\d)\s*Q(\d)', col_upper)
    if match:
        return int(match.group(1)) * 100 + int(match.group(2)) * 3
    return 0

def build_member_predictions(history_detailed, n_hist_cols):
    """
    Per-member πρόβλεψη βασισμένη σε:
    - Exponential weighting (πρόσφατες καμπάνιες βαρύτερες 3×)
    - Trend detection (γραμμική κλίση, dampened)
    - Conversion Frequency (κύρια πιθανότητα: x/n καμπανιών παρήγγειλε)
    - Reliability score (consistency παραγγελιών)
    """
    predictions = {}
    for name, entries in history_detailed.items():
        if not entries:
            continue
        entries_sorted = sorted(entries, key=lambda x: x['period_idx'])
        values = [e['net_value'] for e in entries_sorted]
        n = len(values)

        # === ΒΕΛΤΙΩΣΗ 3: Per-member Conversion Frequency ===
        # Η πιο αξιόπιστη πιθανότητα: "σε Ν καμπάνιες παρήγγειλε n φορές"
        # Bayesian smoothing: +1 prior (Laplace smoothing) για να αποφύγουμε 0% ή 100%
        conversion_freq = (n + 0.5) / (n_hist_cols + 1.0)
        conversion_freq = min(0.95, max(0.05, conversion_freq))

        # Exponential weights: 1.0 (παλαιότερο) → 3.0 (πρόσφατο)
        weights = [1.0 + 2.0 * (i / max(1, n - 1)) for i in range(n)]
        weighted_avg = sum(v * w for v, w in zip(values, weights)) / sum(weights)

        # Trend: κλίση γραμμικής παλινδρόμησης (dampened)
        trend_factor = 0.0
        if n >= 3:
            x = np.arange(n, dtype=float)
            coeffs = np.polyfit(x, values, 1)
            slope = coeffs[0]
            trend_factor = slope / max(1.0, weighted_avg) * 0.4  # dampened
            trend_factor = max(-0.25, min(0.25, trend_factor))  # cap ±25%

        # Reliability: πόσες περιόδους παρήγγειλε vs πόσες υπάρχουν
        reliability = n / max(1, n_hist_cols)
        reliability = min(1.0, reliability)

        predicted = weighted_avg * (1.0 + trend_factor)

        predictions[name] = {
            'weighted_avg': weighted_avg,
            'trend_factor': trend_factor,
            'reliability': reliability,
            'conversion_freq': conversion_freq,  # ΝΕΟΣ ΔΕΙΚΤΗΣ
            'predicted': max(0, predicted),
            'n_periods': n,
            'std': float(np.std(values)) if n > 1 else weighted_avg * 0.3
        }

    return predictions

class PurePythonLogisticRegression:
    def __init__(self, lr=0.1, epochs=100):
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = 0.0
        self.feature_maxes = None
        
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        
        for _ in range(self.epochs):
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = 1.0 / (1.0 + np.exp(-np.clip(linear_model, -250, 250)))
            
            dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1 / n_samples) * np.sum(y_predicted - y)
            
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
            
    def predict_proba(self, X):
        linear_model = np.dot(X, self.weights) + self.bias
        p = 1.0 / (1.0 + np.exp(-np.clip(linear_model, -250, 250)))
        return np.array([[1.0-prob, prob] for prob in p])

def train_propensity_model(history_detailed, hist_cols_count):
    """Εκπαιδεύει custom Logistic Regression για πιθανότητα παραγγελίας"""
    X = []
    y = []
    for name, entries in history_detailed.items():
        if len(entries) >= 2:
            ent = sorted(entries, key=lambda e: e['period_idx'])
            target_val = ent[-1]['net_value']
            past_vals = [e['net_value'] for e in ent[:-1]]
            
            reliability = len(past_vals) / max(1, hist_cols_count - 1)
            avg_basket = sum(past_vals) / len(past_vals) if past_vals else 0
            tier_rank = get_tier_rank(name)
            
            X.append([reliability, avg_basket, tier_rank])
            y.append(1.0 if target_val > 10 else 0.0)
            
    if len(X) > 10:
        model = PurePythonLogisticRegression()
        X_arr = np.array(X)
        model.feature_maxes = np.array([X_arr[:, i].max() if X_arr[:, i].max() > 0 else 1.0 for i in range(X_arr.shape[1])])
        
        # Normalize features
        for i in range(X_arr.shape[1]):
            X_arr[:, i] = X_arr[:, i] / model.feature_maxes[i]
            
        original_predict = model.predict_proba
        def normalized_predict(X_infer):
            X_inf_arr = np.array(X_infer, dtype=float)
            for i in range(X_inf_arr.shape[1]):
                X_inf_arr[:, i] = X_inf_arr[:, i] / model.feature_maxes[i]
            return original_predict(X_inf_arr)
            
        model.predict_proba = normalized_predict
        model.fit(X_arr, np.array(y))
        return model
    return None

# ΣΥΝΑΡΤΗΣΗ ΕΞΑΓΩΓΗΣ PDF
# === Κοινή, ανθεκτική φόρτωση Unicode γραμματοσειράς για ελληνικά σε PDF ===
# Ψάχνει σε πολλαπλά πιθανά paths (τοπικό αρχείο + κοινά system fonts του Linux
# που συνήθως υπάρχουν ήδη εγκατεστημένα) αντί να βασίζεται μόνο σε ένα
# χειροκίνητο arial.ttf που ο χρήστης πρέπει να προσθέσει ο ίδιος.
_GREEK_FONT_CANDIDATES_REGULAR = [
    'arial.ttf',
    'DejaVuSans.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
    '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    'C:/Windows/Fonts/arial.ttf',
]
_GREEK_FONT_CANDIDATES_BOLD = [
    'arialbd.ttf',
    'DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf',
    'C:/Windows/Fonts/arialbd.ttf',
]

def setup_greek_font(pdf):
    """
    Προσπαθεί να φορτώσει Unicode γραμματοσειρά με υποστήριξη ελληνικών.
    Επιστρέφει (font_loaded: bool, family_name: str, bold_available: bool).
    Αν αποτύχουν όλα τα candidates, πέφτει σε helvetica (τα ελληνικά θα
    εμφανιστούν ως '?' — ενημερώνει με warning στο Streamlit UI).
    """
    import os
    regular_path = next((p for p in _GREEK_FONT_CANDIDATES_REGULAR if os.path.exists(p)), None)
    if not regular_path:
        return False, 'helvetica', False

    try:
        pdf.add_font('Greek', '', regular_path, uni=True)
        bold_path = next((p for p in _GREEK_FONT_CANDIDATES_BOLD if os.path.exists(p)), None)
        bold_available = False
        if bold_path:
            try:
                pdf.add_font('Greek', 'B', bold_path, uni=True)
                bold_available = True
            except Exception:
                pass
        pdf.set_font('Greek', '', 11)
        return True, 'Greek', bold_available
    except Exception:
        return False, 'helvetica', False


def create_pdf_bytes(df_export, phone_column):
    if FPDF is None: return None
    
    pdf = FPDF()
    pdf.add_page()
    
    font_loaded, font_family, _ = setup_greek_font(pdf)
    if not font_loaded:
        pdf.set_font('helvetica', '', 11)

    def safe_txt(s):
        """Αποφυγή crash όταν δεν βρέθηκε Unicode font — μετατρέπει ελληνικά σε
        λατινικούς χαρακτήρες αντί να αφήνει το FPDF να σκάσει σε core font."""
        if font_loaded:
            return s
        return s.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font_size(16)
    pdf.cell(0, 10, txt=safe_txt("ΑΤΟΜΑ ΧΩΡΙΣ ΠΑΡΑΓΓΕΛΙΑ"), ln=True, align='C')
    pdf.set_font_size(11)
    pdf.ln(8)
    
    for _, row in df_export.iterrows():
        name = str(row['Ονοματεπώνυμο'])
        phone = str(row[phone_column]) if phone_column in row and pd.notna(row[phone_column]) else "-"
        text = safe_txt(f"{name} | Τηλ: {phone}")
        pdf.cell(0, 7, txt=text, ln=True)
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()

def create_campaign_report_pdf(report_data):
    """
    Δημιουργεί ΒΑΘΙΑ αναλυτικό PDF report καμπάνιας — όχι απλή σύνοψη τελικών
    νούμερων, αλλά πλήρη εικόνα της πορείας της καμπάνιας από την αρχή:
    ημερήσια εξέλιξη πωλήσεων/μελών, εξέλιξη πρόβλεψης, adjustments, tier
    ανάλυση, retention, additions, top performers. Κάθε section είναι
    προαιρετικό — αν λείπει κάποιο κλειδί, παραλείπεται σιωπηλά.
    """
    if FPDF is None: return None

    pdf = FPDF()
    pdf.add_page()

    font_loaded, font_family, bold_available = setup_greek_font(pdf)
    bold_name = font_family if bold_available else ('Greek' if font_loaded else 'helvetica')
    # Αν δεν φορτώθηκε Unicode γραμματοσειρά, δεν μπορούμε να τυπώσουμε ελληνικά
    # σωστά με FPDF core fonts — προειδοποιούμε μέσα στο ίδιο το PDF αντί για '??'.
    greek_warning_needed = not font_loaded

    def txt(s):
        s = str(s)
        if not font_loaded:
            # Δεν βρέθηκε Unicode font — μεταγραφή σε λατινικούς χαρακτήρες
            # αντί για άσχημα '?' (καλύτερη αναγνωσιμότητα ως έσχατη λύση).
            # ΣΗΜΑΝΤΙΚΟ: η dict-μορφή του str.maketrans() χρειάζεται εδώ (όχι η
            # μορφή με δύο strings), γιατί κάποια γράμματα χαρτογραφούνται σε
            # ΠΟΛΛΑΠΛΟΥΣ χαρακτήρες (Θ→TH, Ψ→PS) — με δύο strings ίσου μήκους
            # αυτό είναι αδύνατο και προκαλεί ValueError/λάθος αντιστοίχιση.
            greek_to_latin = str.maketrans({
                'Α':'A','Β':'B','Γ':'G','Δ':'D','Ε':'E','Ζ':'Z','Η':'H','Θ':'TH',
                'Ι':'I','Κ':'K','Λ':'L','Μ':'M','Ν':'N','Ξ':'X','Ο':'O','Π':'P',
                'Ρ':'R','Σ':'S','Τ':'T','Υ':'Y','Φ':'F','Χ':'X','Ψ':'PS','Ω':'O',
                'α':'a','β':'b','γ':'g','δ':'d','ε':'e','ζ':'z','η':'h','θ':'th',
                'ι':'i','κ':'k','λ':'l','μ':'m','ν':'n','ξ':'x','ο':'o','π':'p',
                'ρ':'r','σ':'s','ς':'s','τ':'t','υ':'y','φ':'f','χ':'x','ψ':'ps','ω':'o',
            })
            s = s.translate(greek_to_latin)
            s = s.encode('latin-1', 'replace').decode('latin-1')
        return s

    def h1(s):
        pdf.set_font(bold_name, 'B', 18)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, txt(s), ln=True, align='C')
        pdf.set_font(font_family, '', 11)
        pdf.set_text_color(0, 0, 0)

    def h2(s):
        pdf.ln(3)
        pdf.set_font(bold_name, 'B', 13)
        pdf.set_fill_color(230, 230, 250)
        pdf.cell(0, 9, txt(s), ln=True, fill=True)
        pdf.set_font(font_family, '', 10)

    def h3(s):
        pdf.ln(2)
        pdf.set_font(bold_name, 'B', 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, txt(s), ln=True)
        pdf.set_font(font_family, '', 10)
        pdf.set_text_color(0, 0, 0)

    def kv_row(label, value, color=None):
        pdf.set_font(bold_name, 'B', 11)
        pdf.cell(90, 7, txt(label), border=0)
        pdf.set_font(font_family, '', 11)
        if color:
            pdf.set_text_color(*color)
        pdf.cell(0, 7, txt(value), ln=True)
        pdf.set_text_color(0, 0, 0)

    def line():
        pdf.ln(1)
        pdf.set_draw_color(220, 220, 220)
        y = pdf.get_y()
        pdf.line(10, y, 200, y)
        pdf.ln(3)

    def check_page_break(needed=15):
        if pdf.get_y() > 270 - needed:
            pdf.add_page()

    # === COVER / EXECUTIVE SUMMARY (Σελίδα 1) ===
    h1(f"Αναφορά Καμπάνιας — {report_data.get('campaign', '')}")
    pdf.set_font(font_family, '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, txt(f"Δημιουργήθηκε: {report_data.get('generated_at', '')}  |  Κατάσταση: {report_data.get('status_label', '')}"), ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    if greek_warning_needed:
        pdf.set_font(font_family, '', 9)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 6, txt("Σημείωση: δεν βρέθηκε Unicode γραμματοσειρά στον server — τα ελληνικά εμφανίζονται μεταγεγραμμένα."), ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
    line()

    h2("Σύνοψη Πωλήσεων")
    kv_row("Τελικές/Τρέχουσες Πωλήσεις:", f"{report_data.get('total_sales', 0):,.0f} EUR")
    if report_data.get('target') is not None:
        kv_row("Στόχος:", f"{report_data['target']:,.0f} EUR")
        pct = report_data.get('achievement_pct')
        if pct is not None:
            col = (0, 140, 0) if pct >= 100 else ((200, 140, 0) if pct >= 85 else (200, 0, 0))
            kv_row("Επίτευξη Στόχου:", f"{pct:.1f}%", color=col)
    if report_data.get('forecast') is not None:
        kv_row("AI Forecast (Ensemble, εν εξελίξει):", f"{report_data['forecast']:,.0f} EUR")
    dp, dl, cd = report_data.get('days_passed'), report_data.get('days_left'), report_data.get('campaign_duration_est')
    if dp is not None:
        kv_row("Διάρκεια Καμπάνιας:", f"{dp} μέρες πέρασαν" + (f" | {dl} απομένουν" if dl else "") + (f" | σύνολο {cd} μέρες" if cd else ""))

    h2("Μέλη")
    kv_row("Ενεργά Μέλη:", f"{report_data.get('actives', 0)}")
    if report_data.get('goal_actives'):
        kv_row("Στόχος Actives:", f"{report_data['goal_actives']}")
    kv_row("Μέλη Χωρίς Παραγγελία:", f"{report_data.get('no_order_count', 0)}")
    kv_row("VIP που Δεν Παρήγγειλαν:", f"{report_data.get('vip_missing', 0)}")

    if report_data.get('removals_count') is not None:
        h2("Διαγραφές")
        kv_row("Τρέχουσες Διαγραφές:", f"{report_data['removals_count']}")
        if report_data.get('goal_removals'):
            kv_row("Στόχος Διαγραφών:", f"{report_data['goal_removals']}")

    h2("Σύγκριση με Ιστορικό")
    if report_data.get('mom_delta') is not None:
        kv_row("vs Ίδια Μέρα Ιστορικά:", f"{report_data['mom_delta']:+.1f}%")
    if report_data.get('best_camp_total') is not None:
        kv_row("Καλύτερη Καμπάνια Ποτέ:", f"{report_data['best_camp_total']:,.0f} EUR")
    if report_data.get('yoy_delta') is not None:
        kv_row("Year-over-Year:", f"{report_data['yoy_delta']:+.1f}%")

    # === ΗΜΕΡΗΣΙΑ ΕΞΕΛΙΞΗ — η "εικόνα από την αρχή" της καμπάνιας ===
    if report_data.get('daily_timeline'):
        pdf.add_page()
        h2("Ημερήσια Εξέλιξη Καμπάνιας (από την αρχή)")
        pdf.set_font(font_family, '', 8)
        pdf.multi_cell(0, 5, txt("Δείχνει τι συνέβη κάθε μέρα από την έναρξη της καμπάνιας μέχρι σήμερα/το κλείσιμο: ημερήσιες πωλήσεις, σωρευτικό σύνολο, ενεργά μέλη ανά μέρα, και σύγκριση με το ιστορικό μέσο όρο ίδιας ημέρας."))
        pdf.ln(2)
        pdf.set_font(bold_name, 'B', 9)
        headers = ["Ημ/νία", "Πωλ. Ημέρας", "Σωρευτικό", "Μέλη Ημέρας", "Σύνολο Μελών", "Ιστορικό (ίδια μέρα)"]
        widths = [22, 30, 32, 28, 32, 40]
        for wd, hd in zip(widths, headers):
            pdf.cell(wd, 7, txt(hd), border=1, align='C')
        pdf.ln()
        pdf.set_font(font_family, '', 8)
        for row in report_data['daily_timeline']:
            check_page_break(8)
            if pdf.get_y() < 15:  # μόλις άλλαξε σελίδα — ξανατύπωσε header
                pdf.set_font(bold_name, 'B', 9)
                for wd, hd in zip(widths, headers):
                    pdf.cell(wd, 7, txt(hd), border=1, align='C')
                pdf.ln()
                pdf.set_font(font_family, '', 8)
            pdf.cell(widths[0], 6, txt(row['date']), border=1, align='C')
            pdf.cell(widths[1], 6, txt(f"{row['daily_sales']:,.0f}"), border=1, align='R')
            pdf.cell(widths[2], 6, txt(f"{row['cum_sales']:,.0f}"), border=1, align='R')
            pdf.cell(widths[3], 6, txt(str(row['daily_actives'])), border=1, align='C')
            pdf.cell(widths[4], 6, txt(str(row['cum_actives'])), border=1, align='C')
            hs = row.get('hist_same_day', 0)
            pdf.cell(widths[5], 6, txt(f"{hs:,.0f}" if hs else "—"), border=1, align='R')
            pdf.ln()

    # === ΕΞΕΛΙΞΗ ΠΡΟΒΛΕΨΗΣ ===
    if report_data.get('forecast_timeline') and len(report_data['forecast_timeline']) >= 2:
        check_page_break(60)
        h2("Εξέλιξη AI Πρόβλεψης")
        pdf.set_font(font_family, '', 8)
        pdf.multi_cell(0, 5, txt("Πώς άλλαξε η πρόβλεψη ημέρα με ημέρα καθώς προχωρούσε η καμπάνια — δείχνει πόσο σταθεροποιείται η εκτίμηση με τον χρόνο."))
        pdf.ln(2)
        pdf.set_font(bold_name, 'B', 9)
        pdf.cell(50, 7, txt("Ημερομηνία"), border=1, align='C')
        pdf.cell(0, 7, txt("AI Forecast (EUR)"), border=1, align='C', ln=True)
        pdf.set_font(font_family, '', 8)
        for row in report_data['forecast_timeline']:
            check_page_break(8)
            pdf.cell(50, 6, txt(row['date']), border=1, align='C')
            pdf.cell(0, 6, txt(f"{row['forecast']:,.0f}"), border=1, align='R', ln=True)

    # === ADJUSTMENTS ===
    if report_data.get('adjustments'):
        check_page_break(60)
        adj = report_data['adjustments']
        h2("Adjustments (Αρνητικά Ποσά)")
        kv_row("Σύνολο Adjustments:", f"{adj['count']}")
        kv_row("Συνολικό Ποσό:", f"{adj['total']:,.2f} EUR", color=(200, 0, 0))
        if adj.get('rows'):
            pdf.ln(2)
            pdf.set_font(bold_name, 'B', 9)
            pdf.cell(120, 7, txt("Όνομα"), border=1)
            pdf.cell(0, 7, txt("Ποσό (EUR)"), border=1, align='C', ln=True)
            pdf.set_font(font_family, '', 8)
            for r in adj['rows']:
                check_page_break(8)
                pdf.cell(120, 6, txt(r['name']), border=1)
                pdf.cell(0, 6, txt(f"{r['amount']:,.2f}"), border=1, align='R', ln=True)

    # === TIER BREAKDOWN ===
    if report_data.get('tier_breakdown'):
        check_page_break(60)
        h2("Ανάλυση ανά Tier")
        pdf.set_font(bold_name, 'B', 10)
        pdf.cell(50, 7, txt("Tier"), border=1)
        pdf.cell(45, 7, txt("Τρέχον Καλάθι"), border=1)
        pdf.cell(45, 7, txt("Ιστορικό Καλάθι"), border=1)
        pdf.cell(0, 7, txt("Μέλη"), border=1, ln=True)
        pdf.set_font(font_family, '', 10)
        for row in report_data['tier_breakdown']:
            check_page_break(8)
            pdf.cell(50, 7, txt(row['tier']), border=1)
            pdf.cell(45, 7, txt(f"{row['curr']:,.0f} EUR"), border=1)
            pdf.cell(45, 7, txt(f"{row['hist']:,.0f} EUR"), border=1)
            pdf.cell(0, 7, txt(str(row['count'])), border=1, ln=True)

    # === RETENTION / HEALTH ===
    if report_data.get('team_health') is not None:
        check_page_break(30)
        h2("Υγεία Ομάδας")
        kv_row("Team Health Score:", f"{report_data['team_health']}/100")
        if report_data.get('retention_pct') is not None:
            kv_row("Μ.Ο. Retention:", f"{report_data['retention_pct']:.0f}%")

    # === ADDITIONS / WIN-BACKS ===
    if report_data.get('winbacks_count') is not None:
        check_page_break(30)
        h2("Additions (Επανατοποθετήσεις)")
        kv_row("Σύνολο:", f"{report_data['winbacks_count']}")
        kv_row("Αξία που Ξανακερδήθηκε:", f"{report_data.get('winbacks_value', 0):,.0f} EUR")

    # === TOP PERFORMERS ===
    if report_data.get('top_performers'):
        check_page_break(80)
        h2("Top 10 Contributors")
        pdf.set_font(bold_name, 'B', 10)
        pdf.cell(15, 7, txt("#"), border=1)
        pdf.cell(105, 7, txt("Όνομα"), border=1)
        pdf.cell(0, 7, txt("Ποσό"), border=1, ln=True)
        pdf.set_font(font_family, '', 10)
        for i, p in enumerate(report_data['top_performers'], 1):
            check_page_break(8)
            pdf.cell(15, 7, txt(str(i)), border=1)
            pdf.cell(105, 7, txt(p['name']), border=1)
            pdf.cell(0, 7, txt(f"{p['value']:,.0f} EUR"), border=1, ln=True)

    # === FORECAST ACCURACY / CALIBRATION ===
    if report_data.get('calibration_factor') is not None:
        check_page_break(30)
        h2("Ακρίβεια Πρόβλεψης (Calibration)")
        cf = report_data['calibration_factor']
        bias = (cf - 1) * 100
        kv_row("Calibration Factor:", f"{cf:.3f} ({'υπερεκτίμηση' if bias>0 else 'υποεκτίμηση'} {abs(bias):.1f}%)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()

# ==========================================
# 3. DATA ENGINE
# ==========================================
SHEET_ID = "1hirqSVwtjB2_UdZVWh53lMDnogWSgjGHtQb--4Zzv_4"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

def clean_duplicate_columns(df):
    """
    Καθαρίζει στήλες που προκαλούν 'cannot assemble with duplicate keys' σε
    μελλοντικό pd.concat: (1) πολλαπλές εντελώς κενές/ανώνυμες στήλες (π.χ.
    'Unnamed: 6', ή κυριολεκτικά None ως όνομα στήλης — συνηθισμένο σε Google
    Sheets exports με άδειες trailing στήλες), και (2) οποιαδήποτε ΕΝΑΠΟΜΕΙΝΑΝΤΑ
    διπλότυπα ονόματα στηλών (ασφάλεια, μετονομάζει σε .1, .2 κλπ αντί να σκάει).
    """
    df = df.copy()
    df.columns = [re.sub(r'\s+', ' ', str(c)).strip() if pd.notna(c) else c for c in df.columns]

    cols_to_drop = []
    for i, c in enumerate(df.columns):
        is_unnamed = pd.isna(c) or str(c).strip() == '' or str(c).lower().startswith('unnamed')
        if is_unnamed and df.iloc[:, i].isna().all():
            cols_to_drop.append(df.columns[i])
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    if df.columns.duplicated().any():
        seen = {}
        new_cols = []
        for c in df.columns:
            if c in seen:
                seen[c] += 1
                new_cols.append(f"{c}.{seen[c]}")
            else:
                seen[c] = 0
                new_cols.append(c)
        df.columns = new_cols

    return df

# === CACHED DATA FETCH ===
# ΚΡΙΣΙΜΟ ΓΙΑ ΤΑΧΥΤΗΤΑ: το Streamlit ξανατρέχει ΟΛΟΚΛΗΡΟ το script σε ΚΑΘΕ
# αλληλεπίδραση (κλικ, πληκτρολόγηση σημείωσης, toggle κλπ) — χωρίς caching,
# αυτό σήμαινε ότι το ΟΛΟΚΛΗΡΟ Google Sheet ξαναφορτωνόταν από το δίκτυο σε
# ΚΑΘΕ μονή αλλαγή, κάνοντας ακόμα και μια απλή σημείωση αργή. Με το
# @st.cache_data, το αποτέλεσμα "παγώνει" για 5 λεπτά — μέσα σε αυτό το
# διάστημα, όσες αλλαγές κι αν κάνεις, δεν ξαναφορτώνεται το Sheet από το
# μηδέν, μόνο οι υπολογισμοί που πραγματικά χρειάζονται τρέχουν ξανά.
@st.cache_data(ttl=300, show_spinner="📥 Φόρτωση δεδομένων από Google Sheets...")
def fetch_sheet_data(url):
    response = requests.get(url)
    xls = pd.ExcelFile(BytesIO(response.content))
    df_sales = pd.read_excel(xls, sheet_name=0)
    df_todo = pd.read_excel(xls, sheet_name=1)
    df_removals = pd.read_excel(xls, sheet_name=2)
    df_members = pd.read_excel(xls, sheet_name=3)
    return df_sales, df_todo, df_removals, df_members

try:
    df_sales_all, df_todo_raw, df_removals_raw, df_members_raw = fetch_sheet_data(EXCEL_URL)

    df_sales_all = clean_duplicate_columns(df_sales_all)
    df_todo_raw = clean_duplicate_columns(df_todo_raw)
    df_removals_raw = clean_duplicate_columns(df_removals_raw)
    df_members_raw = clean_duplicate_columns(df_members_raw)

    # =========================================================
    # ΑΠ' ΕΥΘΕΙΑΣ UPLOAD RAW AVON EXPORTS — παρακάμπτει εντελώς το
    # χειροκίνητο: αλλαγή δεκαδικού, επιλογή στηλών, copy-paste στο
    # Google Sheet. Ανεβάζεις τα ίδια αρχεία που κατεβάζεις από το
    # report της Avon, και το app κάνει μόνο του το parsing.
    # =========================================================
    # Πρόωρος έλεγχος λειτουργίας βοηθού — χρειάζεται εδώ, ΠΡΙΝ οριστεί το
    # πλήρες is_assistant_mode (που εξαρτάται από το selected_camp το οποίο
    # δεν έχει οριστεί ακόμα σε αυτό το σημείο), ειδικά για να κρύβει τα
    # στοιχεία upload από τη βοηθό — δεν τα χρειάζεται, μόνο μπερδεύουν.
    _is_assistant_early = st.query_params.get("view", "") == "assistant"

    if not _is_assistant_early:
        st.sidebar.markdown("### 📤 Γρήγορη Ενημέρωση (προαιρετικό)")
        st.sidebar.caption("Ανέβασε τα raw αρχεία από το Avon report — χωρίς μετατροπή δεκαδικού ή αντιγραφή στο Google Sheet.")

    def read_avon_export_file(uploaded_file):
        """
        Διαβάζει raw αρχείο export από την Avon (.xls παλιού τύπου ή .xlsx),
        δοκιμάζοντας πολλαπλές μεθόδους ανάγνωσης — κάποια web reports
        αποθηκεύονται ως HTML πίνακας με επέκταση .xls.
        """
        raw_bytes = uploaded_file.getvalue()
        for engine in ('xlrd', 'openpyxl', 'calamine'):
            try:
                return pd.read_excel(BytesIO(raw_bytes), engine=engine)
            except Exception:
                continue
        try:
            tables = pd.read_html(BytesIO(raw_bytes))
            if tables:
                return tables[0]
        except Exception:
            pass
        return None

    def map_all_orders_to_schema(df_raw, manual_camp_code=None):
        """
        Μετατρέπει το raw ALL_ORDERS export της Avon στη μορφή που περιμένει
        η υπόλοιπη εφαρμογή (ίδιες στήλες με το Φύλλο1 του Google Sheet).
        Το raw αρχείο έχει ΕΝΤΕΛΩΣ διαφορετικά ονόματα στηλών, γι' αυτό η
        αντιστοίχιση γίνεται ρητά εδώ, αντί να βασιζόμαστε στη γενική
        ασαφή αναζήτηση (fuzzy matching) που χρησιμοποιείται αλλού.
        """
        df_raw = df_raw.copy()
        df_raw.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df_raw.columns]

        def find_col(*keywords):
            # Σημαντικό: ελέγχουμε ΛΕΞΗ-ΚΛΕΙΔΙ ΠΡΩΤΑ (με τη σειρά προτεραιότητας),
            # όχι στήλη-στήλη — αλλιώς μια λιγότερο επιθυμητή στήλη που τυχαίνει
            # να έρχεται νωρίτερα στο αρχείο (π.χ. "Πρωϊνό Τηλέφωνο") κερδίζει
            # έναντι της σωστής (π.χ. "Κινητό Τηλέφωνο") μόνο επειδή προηγείται.
            for kw in keywords:
                for c in df_raw.columns:
                    if kw in remove_accents(str(c)).upper():
                        return c
            return None

        col_camp   = find_col('ΚΑΜΠ')            # "Καμπ."
        col_name   = find_col('ΣΤΟΙΧΕΙΑ ΜΕΛΟΥΣ', 'ΟΝΟΜΑ', 'NAME')
        col_amount = find_col('ΠΛΗΡΩΤΕΟ', 'ΠΟΣΟ', 'AMOUNT')
        col_status = find_col('ΚΑΤΑΣΤΑΣΗ', 'STATUS')
        col_phone  = find_col('ΚΙΝΗΤΟ', 'ΤΗΛ', 'PHONE')
        col_date   = find_col('ΗΜΕΡΟΜΗΝΙΑ ΠΑΡΑΓΓΕΛΙΑΣ', 'ΗΜΕΡΟΜ', 'DATE')

        missing = [n for n, c in [('Όνομα', col_name), ('Ποσό', col_amount), ('Κατάσταση', col_status)] if c is None]
        if missing:
            return None, f"Δεν βρέθηκαν οι στήλες: {', '.join(missing)}. Έλεγξε τη μορφή του αρχείου."

        out = pd.DataFrame()
        out['Ονοματεπώνυμο'] = df_raw[col_name]
        out['Ποσό'] = df_raw[col_amount]
        out['Κατάσταση'] = df_raw[col_status]
        out['Τηλέφωνο'] = df_raw[col_phone] if col_phone else None
        if col_date:
            out['Ημερομηνία'] = pd.to_datetime(df_raw[col_date], format='%d/%m/%Y', errors='coerce')
        # Fallback αν κάποιες ημερομηνίες δεν διαβάστηκαν με το ελληνικό format
        if col_date and out['Ημερομηνία'].isna().all():
            out['Ημερομηνία'] = pd.to_datetime(df_raw[col_date], errors='coerce')

        # === Μετατροπή "Καμπ." (π.χ. 7) σε YYYYMM (π.χ. 202607) ===
        if manual_camp_code:
            out['Καμπάνια'] = int(manual_camp_code)
        elif col_camp and col_date:
            camp_num = pd.to_numeric(df_raw[col_camp], errors='coerce').dropna()
            camp_num = int(camp_num.mode().iloc[0]) if not camp_num.empty else None
            valid_dates = out['Ημερομηνία'].dropna()
            camp_year = int(valid_dates.dt.year.mode().iloc[0]) if not valid_dates.empty else date.today().year
            if camp_num:
                out['Καμπάνια'] = camp_year * 100 + camp_num
            else:
                out['Καμπάνια'] = int(f"{date.today().year}{date.today().month:02d}")
        else:
            out['Καμπάνια'] = int(f"{date.today().year}{date.today().month:02d}")

        return out, None

    if _is_assistant_early:
        up_all_orders = None
        up_not_placed = None
    else:
        up_all_orders = st.sidebar.file_uploader("📦 ALL_ORDERS (→ Φύλλο1)", type=['xls', 'xlsx'], key="up_all_orders")
        up_not_placed = st.sidebar.file_uploader("📋 NOT_PLACED_AN_ORDER (→ Φύλλο2)", type=['xls', 'xlsx'], key="up_not_placed")

    # === ΜΟΝΙΜΗ ΑΠΟΘΗΚΕΥΣΗ ΑΝΕΒΑΣΜΕΝΩΝ ΔΕΔΟΜΕΝΩΝ ===
    # ΚΡΙΣΙΜΟ: το st.file_uploader είναι ΠΡΟΣΩΡΙΝΟ — υπάρχει μόνο όσο είναι
    # ανοιχτό το συγκεκριμένο browser tab. Χωρίς αυτό το cache, αν ανανεώσεις τη
    # σελίδα (ή αν η βοηθός σου ανοίξει το link) θα εξαφανιζόταν το upload και
    # θα επέστρεφε στα (παλιά) δεδομένα του Google Sheet. Το cache αποθηκεύεται
    # τοπικά και εφαρμόζεται ΑΥΤΟΜΑΤΑ σε κάθε άνοιγμα, μέχρι να ανεβάσεις κάτι
    # πιο πρόσφατο ή να το καθαρίσεις χειροκίνητα.
    UPLOADED_ORDERS_CACHE = "uploaded_all_orders_cache.csv"

    def load_cached_upload():
        if os.path.exists(UPLOADED_ORDERS_CACHE):
            try:
                df = pd.read_csv(UPLOADED_ORDERS_CACHE)
                if 'Ημερομηνία' in df.columns:
                    df['Ημερομηνία'] = pd.to_datetime(df['Ημερομηνία'], errors='coerce')
                return df
            except Exception:
                return None
        return None

    def save_cached_upload(df):
        try:
            df.to_csv(UPLOADED_ORDERS_CACHE, index=False)
        except Exception:
            pass

    def merge_cached_or_uploaded(df_base, df_new_mapped, camp_code):
        """Αφαιρεί τις παλιές γραμμές της ίδιας καμπάνιας και προσθέτει τις νέες."""
        camp_col_existing = next((c for c in df_base.columns if 'ΚΑΜΠΑΝΙΑ' in remove_accents(str(c)).upper()), None)
        if camp_col_existing:
            df_base = df_base[df_base[camp_col_existing] != camp_code]
            df_new_mapped = df_new_mapped.rename(columns={'Καμπάνια': camp_col_existing})
        df_base = clean_duplicate_columns(df_base)
        df_new_mapped = clean_duplicate_columns(df_new_mapped)
        result = pd.concat([df_base, df_new_mapped], ignore_index=True)
        return clean_duplicate_columns(result)

    # Αυτόματη εφαρμογή προηγούμενου (cached) upload — ΠΡΙΝ ελέγξουμε αν
    # ανέβηκε κάτι νέο τώρα. Έτσι η τελευταία γνωστή ενημέρωση εμφανίζεται
    # πάντα, ακόμα κι αν κανείς δεν ανεβάσει τίποτα αυτή τη φορά.
    _cached_df = load_cached_upload()
    if _cached_df is not None and not _cached_df.empty and up_all_orders is None:
        try:
            _cached_camp = int(_cached_df['Καμπάνια'].iloc[0])
            df_sales_all = merge_cached_or_uploaded(df_sales_all, _cached_df, _cached_camp)
            if not _is_assistant_early:
                st.sidebar.caption(f"💾 Χρησιμοποιείται αποθηκευμένο ALL_ORDERS (καμπάνια {_cached_camp}). Ανέβασε νέο για ενημέρωση.")
        except Exception:
            pass

    if up_all_orders is not None:
        df_raw_orders = read_avon_export_file(up_all_orders)
        if df_raw_orders is not None and not df_raw_orders.empty:
            df_mapped, err = map_all_orders_to_schema(df_raw_orders)
            if err:
                st.sidebar.error(f"⚠️ {err}")
            else:
                derived_camp = int(df_mapped['Καμπάνια'].iloc[0])
                confirmed_camp = st.sidebar.number_input(
                    "Επιβεβαίωση κωδικού καμπάνιας (YYYYMM)",
                    value=derived_camp, step=1, key="confirm_camp_code",
                    help="Αυτόματα παράχθηκε από το 'Καμπ.' του αρχείου + το έτος των ημερομηνιών παραγγελίας. Διόρθωσε αν χρειάζεται."
                )
                if confirmed_camp != derived_camp:
                    df_mapped['Καμπάνια'] = confirmed_camp

                df_sales_all = merge_cached_or_uploaded(df_sales_all, df_mapped.copy(), confirmed_camp)
                save_cached_upload(df_mapped)  # ΜΟΝΙΜΗ αποθήκευση — θα εφαρμόζεται αυτόματα από εδώ και πέρα
                st.sidebar.success(f"✅ ALL_ORDERS: {len(df_mapped)} γραμμές φορτώθηκαν για την καμπάνια {confirmed_camp}")
        else:
            st.sidebar.error("⚠️ Δεν κατέστη δυνατή η ανάγνωση του ALL_ORDERS — έλεγξε τη μορφή αρχείου.")

    if not _is_assistant_early and os.path.exists(UPLOADED_ORDERS_CACHE):
        if st.sidebar.button("🗑️ Καθαρισμός αποθηκευμένου upload", key="clear_upload_cache",
                              help="Επιστροφή στα δεδομένα του Google Sheet, αγνοώντας το τελευταίο ανεβασμένο αρχείο."):
            try:
                os.remove(UPLOADED_ORDERS_CACHE)
            except Exception:
                pass
            st.rerun()


    if up_not_placed is not None:
        df_uploaded_notplaced = read_avon_export_file(up_not_placed)
        if df_uploaded_notplaced is not None and not df_uploaded_notplaced.empty:
            df_uploaded_notplaced.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df_uploaded_notplaced.columns]
            camp_col_np = next((c for c in df_uploaded_notplaced.columns
                                 if 'ΚΑΜΠΑΝΙΑ' in remove_accents(str(c)).upper() or 'CAMPAIGN' in remove_accents(str(c)).upper()), None)
            if camp_col_np:
                # Αυτόματο φιλτράρισμα στην πιο πρόσφατη (τρέχουσα) καμπάνια —
                # αντικαθιστά το χειροκίνητο φίλτρο που έκανες μέχρι τώρα στο Excel.
                latest_camp = sorted(df_uploaded_notplaced[camp_col_np].dropna().unique(), reverse=True)[0]
                df_uploaded_notplaced = df_uploaded_notplaced[df_uploaded_notplaced[camp_col_np] == latest_camp].copy()
                st.sidebar.caption(f"ℹ️ Αυτόματο φίλτρο καμπάνιας: {latest_camp}")
            df_todo_raw = df_uploaded_notplaced
            st.sidebar.success(f"✅ NOT_PLACED: {len(df_uploaded_notplaced)} γραμμές ενημερώθηκαν")
        else:
            st.sidebar.error("⚠️ Δεν κατέστη δυνατή η ανάγνωση του NOT_PLACED — δοκίμασε `pip install xlrd` στον server, ή έλεγξε τη μορφή αρχείου.")

    st.sidebar.markdown("---")

    # Έξυπνη εύρεση στήλης Ονόματος (ΚΑΙ τηλεφώνου — χρειάζεται παντού για κλήσεις)
    for df in [df_sales_all, df_todo_raw, df_removals_raw, df_members_raw]:
        df.columns = [re.sub(r'\s+', ' ', str(c)).strip() for c in df.columns]
        
        name_col = next((c for c in df.columns if 'ΟΝΟΜΑ' in remove_accents(str(c)).upper() or 'NAME' in remove_accents(str(c)).upper()), None)
        if name_col:
            df['NameClean'] = df[name_col].apply(smart_clean_name)
            if 'Ονοματεπώνυμο' not in df.columns:
                df['Ονοματεπώνυμο'] = df[name_col]
        else:
            df['NameClean'] = "ΑΓΝΩΣΤΟ"
            df['Ονοματεπώνυμο'] = "ΑΓΝΩΣΤΟ"

        # ΚΡΙΣΙΜΟ: κοινή στήλη τηλεφώνου σε ΟΛΑ τα sheets, ανεξάρτητα από το πώς
        # λέγεται στο καθένα (π.χ. 'Τηλέφωνο', 'Κινητό Τηλέφωνο') — χωρίς αυτό,
        # το render_list() (Smart Rank/Εκκρεμείς/Διαγραφές) δεν είχε αξιόπιστο
        # τρόπο να βρει τηλέφωνο σε λίστες που προέρχονται από διαφορετικά φύλλα.
        phone_col_here = next((c for c in df.columns if 'ΤΗΛ' in remove_accents(str(c)).upper() or 'PHONE' in remove_accents(str(c)).upper()), None)
        df['TelClean'] = df[phone_col_here] if phone_col_here else None

    # ΑΣΦΑΛΗΣ ΥΠΟΛΟΓΙΣΜΟΣ ΠΟΣΟΥ
    amount_col = next((c for c in df_sales_all.columns if 'ΠΟΣΟ' in remove_accents(str(c)).upper() or 'AMOUNT' in remove_accents(str(c)).upper()), 'Ποσό')
    df_sales_all['Ποσό_Net'] = df_sales_all[amount_col].apply(parse_money) / 1.24

    # ΕΝΤΟΠΙΣΜΟΣ ΣΤΗΛΗΣ ΗΜΕΡΟΜΗΝΙΑΣ (για same-day σύγκριση)
    date_col = next((c for c in df_sales_all.columns if any(k in remove_accents(str(c)).upper() for k in ['ΗΜΕΡΟΜ', 'DATE', 'ΗΜΝΙΑ'])), None)
    if date_col:
        df_sales_all['_OrderDate'] = pd.to_datetime(df_sales_all[date_col], errors='coerce')

    # =========================================================
    # CROSS-CAMPAIGN INTELLIGENCE (ΝΕΟ)
    # Ανάλυση ΟΛΩΝ των ιστορικών καμπανιών για εξαγωγή:
    # - Ιστορικό conversion rate (% μελών που παραγγέλνουν)
    # - Ιστορικός μέσος όρος καλαθιού
    # - Ιστορικά σύνολα πωλήσεων per campaign
    # =========================================================
    camp_col = next((c for c in df_sales_all.columns if 'ΚΑΜΠΑΝΙΑ' in remove_accents(str(c)).upper()), 'Καμπάνια')
    status_col_global = next((c for c in df_sales_all.columns if 'ΚΑΤΑΣΤΑΣΗ' in remove_accents(str(c)).upper() or 'STATUS' in remove_accents(str(c)).upper()), 'Κατάσταση')

    # --- SIDEBAR ---
    available_camps = sorted(df_sales_all[camp_col].unique(), reverse=True)
    if _is_assistant_early:
        # Καμία διαχείριση στη βοηθό — αυτόματα η πιο πρόσφατη (τρέχουσα) καμπάνια
        selected_camp = available_camps[0]
    else:
        st.sidebar.header("🚀 Διαχείριση")
        selected_camp = st.sidebar.selectbox("Ενεργή Καμπάνια", available_camps)
        if st.sidebar.button("🔄 Ανανέωση Δεδομένων Τώρα", key="force_refresh",
                              help="Παρακάμπτει το cache 5 λεπτών — χρήσιμο αν μόλις ενημέρωσες το Google Sheet και θες να το δεις αμέσως."):
            fetch_sheet_data.clear()
            st.rerun()

    # === ΛΕΙΤΟΥΡΓΙΑ ΒΟΗΘΟΥ (ορίζεται νωρίς ώστε να κρύβει ΚΑΙ τα στοιχεία του
    # sidebar — στόχους, ποσά, calibration — όχι μόνο το κυρίως περιεχόμενο) ===
    # ΚΡΙΣΙΜΟ: αν το link ήρθε με ?view=assistant, η λειτουργία ΚΛΕΙΔΩΝΕΙ — δεν
    # εμφανίζεται καθόλου διαδραστικό toggle, ώστε η βοηθός να ΜΗΝ μπορεί να το
    # απενεργοποιήσει η ίδια και να δει στόχους/ποσά. Το toggle (για να το αλλάζεις
    # ΕΣΥ χειροκίνητα, π.χ. για δοκιμή) εμφανίζεται ΜΟΝΟ όταν ανοίγεις το app
    # χωρίς αυτή την παράμετρο στο URL.
    _qp_view = st.query_params.get("view", "")
    if _qp_view == "assistant":
        is_assistant_mode = True
        st.sidebar.info("🙋 Λειτουργία Βοηθού")
    else:
        is_assistant_mode = st.sidebar.toggle(
            "🙋 Λειτουργία Βοηθού (χωρίς ποσά/στόχους)",
            value=False,
            help="Κρύβει στόχους, ποσά, calibration και analytics — μόνο ονόματα/τηλέφωνα/λίστες κλήσεων. Πρόσθεσε '?view=assistant' στο τέλος του link για μόνιμη, κλειδωμένη ενεργοποίηση σε όποιον ανοίξει αυτό το link."
        )

    # =========================================================
    # PERSISTENT CAMPAIGN GOALS (αποθηκεύονται σε JSON)
    # Οι στόχοι αποθηκεύονται ανά καμπάνια — δεν χάνονται στο refresh
    # =========================================================
    GOALS_FILE = "campaign_goals.json"

    def load_goals():
        if os.path.exists(GOALS_FILE):
            try:
                with open(GOALS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_goals(goals):
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump(goals, f, ensure_ascii=False, indent=2)

    all_goals = load_goals()
    camp_key_str = str(selected_camp)
    saved = all_goals.get(camp_key_str, {})

    # === ΟΝΟΜΑ ΒΟΗΘΟΥ (για προσωπικό χαιρετισμό στη Λειτουργία Βοηθού) ===
    # Αποθηκεύεται μόνιμα, ρυθμίζεται ΜΟΝΟ από σένα (κρυμμένο σε λειτουργία
    # βοηθού) — η βοηθός απλά βλέπει το αποτέλεσμα, δεν μπορεί να το αλλάξει.
    assistant_name = all_goals.get("_assistant_name", "")
    owner_message = all_goals.get("_owner_message", "")
    if not is_assistant_mode:
        st.sidebar.markdown("---")
        new_assistant_name = st.sidebar.text_input(
            "🙋 Όνομα Βοηθού", value=assistant_name,
            placeholder="π.χ. Georgia",
            help="Θα εμφανίζεται ως προσωπικός χαιρετισμός στην κορυφή της Λειτουργίας Βοηθού."
        )
        if new_assistant_name != assistant_name:
            all_goals["_assistant_name"] = new_assistant_name
            save_goals(all_goals)
            assistant_name = new_assistant_name

        # === ΜΗΝΥΜΑ ΠΡΟΣ ΤΗ ΒΟΗΘΟ ===
        # Το μόνο σημείο στη Λειτουργία Βοηθού όπου ΕΣΥ αποφασίζεις τι θα δει —
        # π.χ. "Κάλεσε πρώτα τη Μαρία σήμερα" ή "Ξεκίνα από τις Διαγραφές".
        # Εμφανίζεται σαν ειδοποίηση στην κορυφή της δικής της προβολής.
        new_owner_message = st.sidebar.text_area(
            "💬 Μήνυμα προς τη Βοηθό", value=owner_message,
            placeholder="π.χ. Ξεκίνα σήμερα από τις Διαγραφές — έχουν προτεραιότητα.",
            help="Θα εμφανίζεται σαν ειδοποίηση στην κορυφή της προβολής της βοηθού. Άδειασέ το για να μην εμφανίζεται τίποτα."
        )
        if new_owner_message != owner_message:
            all_goals["_owner_message"] = new_owner_message
            save_goals(all_goals)
            owner_message = new_owner_message
    else:
        # === Λειτουργία Βοηθού: το sidebar δείχνει ΜΟΝΟ μηνύματα — από σένα
        # (owner_message) ή από το σύστημα (π.χ. τα Smart Alerts αργότερα) —
        # καμία διαχείριση/ρύθμιση δεν εμφανίζεται εδώ.
        if owner_message.strip():
            st.sidebar.markdown(
                f"<div style='padding:12px 14px;border-radius:10px;"
                f"background:rgba(255,105,180,0.12);border:1px solid rgba(255,105,180,0.35);margin-bottom:10px;'>"
                f"<span style='font-size:12px;color:#ff69b4;font-weight:700;'>💬 ΜΗΝΥΜΑ</span><br>"
                f"<span style='font-size:13px;color:#fff;'>{owner_message}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

    # === ΔΥΝΑΜΙΚΟΣ ΧΑΙΡΕΤΙΣΜΟΣ ΩΡΑΣ ===
    def get_time_greeting():
        h = datetime.now().hour
        return "Καλημέρα" if h < 17 else "Καλησπέρα"

    # === ΜΟΝΙΜΗ ΑΠΟΘΗΚΕΥΣΗ "✓ Ok" ===
    # Πριν, το st.session_state.sent_ids ζούσε ΜΟΝΟ στη μνήμη της συνεδρίας —
    # έσβηνε αν κλείσει το tab, ξαναφορτωθεί η σελίδα, ή "κοιμηθεί" το app (κοινό
    # στο δωρεάν Streamlit Cloud μετά από αδράνεια). Αν η βοηθός καλούσε 10 άτομα
    # και μετά ξανάνοιγε το link, τα έβλεπε όλα σαν να μην τα είχε καλέσει ποτέ.
    # Τώρα αποθηκεύεται στο ίδιο JSON, ανά ΗΜΕΡΑ + καμπάνια — έτσι "σήμερα
    # τσεκαρισμένο" παραμένει τσεκαρισμένο όλη μέρα, αλλά αύριο η λίστα
    # ξεκινάει καθαρή (λογικό, αφού μπορεί να τους ξανακαλέσει σε νέα καμπάνια).
    _contacted_key = f"_contacted_{camp_key_str}_{date.today().isoformat()}"

    def load_contacted_today():
        goals = load_goals()
        return set(goals.get(_contacted_key, []))

    def save_contacted_today(ids_set):
        goals = load_goals()
        goals[_contacted_key] = list(ids_set)
        save_goals(goals)

    def mark_contacted(row_key):
        """Τσεκάρει ΚΑΙ αποθηκεύει μόνιμα — χρησιμοποιείται παντού αντί για
        απευθείας st.session_state.sent_ids.add(), ώστε να μην ξεχνιέται ποτέ
        ξανά κάποιο σημείο αποθήκευσης."""
        st.session_state.sent_ids.add(row_key)
        save_contacted_today(st.session_state.sent_ids)

    # Φόρτωση μία φορά ανά session (merge με ό,τι ήδη τσεκαρίστηκε σήμερα)
    if '_contacted_loaded_for' not in st.session_state or st.session_state._contacted_loaded_for != _contacted_key:
        st.session_state.sent_ids = st.session_state.sent_ids | load_contacted_today()
        st.session_state._contacted_loaded_for = _contacted_key

    if is_assistant_mode:
        # Λειτουργία Βοηθού: μη εμφάνιση στόχων — χρήση αποθηκευμένων τιμών σιωπηλά
        goal_sales = float(saved.get("sales", 32226.0))
        goal_actives = int(saved.get("actives", 0))
        goal_removals = int(saved.get("removals", 0))
    else:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Στόχοι Καμπάνιας")
        st.sidebar.caption("Συμπλήρωσε μία φορά — αποθηκεύονται αυτόματα ανά καμπάνια.")

        goal_sales   = st.sidebar.number_input("💰 Στόχος Πωλήσεων (€)",  min_value=0.0, step=100.0,
                                                value=float(saved.get("sales",   32226.0)))
        goal_actives = st.sidebar.number_input("👥 Στόχος Actives (μέλη)", min_value=0,   step=1,
                                                value=int(saved.get("actives", 0)))
        goal_removals= st.sidebar.number_input("🗑️ Στόχος Διαγραφών",      min_value=0,   step=1,
                                                value=int(saved.get("removals", 0)))

        # Αποθήκευση αν άλλαξε κάτι
        new_saved = {"sales": goal_sales, "actives": goal_actives, "removals": goal_removals}
        if new_saved != saved:
            all_goals[camp_key_str] = new_saved
            save_goals(all_goals)

    # === Feature 3: Forecast Accuracy Tracker — αποθήκευση ημερήσιας πρόβλεψης ===
    def save_daily_forecast(camp_key, forecast_val):
        today_str = date.today().isoformat()
        goals = load_goals()
        tracker = goals.get("_forecast_history", {})
        camp_track = tracker.get(str(camp_key), {})
        camp_track[today_str] = round(forecast_val, 2)
        tracker[str(camp_key)] = camp_track
        goals["_forecast_history"] = tracker
        save_goals(goals)

    def get_forecast_history(camp_key):
        goals = load_goals()
        return goals.get("_forecast_history", {}).get(str(camp_key), {})

    # === Feature 8: Notes ανά μέλος ===
    def load_notes():
        goals = load_goals()
        return goals.get("_member_notes", {})

    def save_note(name_clean, text):
        goals = load_goals()
        notes = goals.get("_member_notes", {})
        if text.strip():
            notes[name_clean] = text.strip()
        elif name_clean in notes:
            del notes[name_clean]
        goals["_member_notes"] = notes
        save_goals(goals)

    member_notes = load_notes()

    # === Feature 5: Prediction Calibration — φόρτωση correction factor ===
    def load_calibration():
        goals = load_goals()
        return goals.get("_calibration_factor", 1.0)

    def save_calibration(factor):
        goals = load_goals()
        goals["_calibration_factor"] = round(factor, 4)
        save_goals(goals)

    calibration_factor = load_calibration()

    if calibration_factor != 1.0 and not is_assistant_mode:
        bias_pct = (calibration_factor - 1) * 100
        st.sidebar.caption(
            f"🎯 Calibration ενεργό: ×{calibration_factor:.3f} "
            f"({'μειώνει' if bias_pct < 0 else 'αυξάνει'} τις προβλέψεις κατά {abs(bias_pct):.0f}%)"
        )
        if st.sidebar.button("🔄 Επαναφορά Calibration (πλήρης καθαρισμός)", key="reset_calib",
                              help="Καθαρίζει ΚΑΙ το calibration factor ΚΑΙ τα παλιά snapshots πρόβλεψης που το ξαναδηλητηριάζουν αυτόματα σε κάθε refresh (π.χ. μετά από διόρθωση bug στο μοντέλο πρόβλεψης)."):
            save_calibration(1.0)
            # ΚΡΙΣΙΜΟ: καθαρίζουμε ΚΑΙ τα αποθηκευμένα daily-forecast snapshots
            # παλαιότερων (ήδη κλειστών) καμπανιών — αυτά είναι η πηγή του
            # "δηλητηριασμένου" calibration. Χωρίς αυτό, η αυτόματη επανεκμάθηση
            # παρακάτω στον κώδικα θα ξαναϋπολογίσει το ΙΔΙΟ λάθος factor στο
            # επόμενο render, ακυρώνοντας αμέσως το reset.
            _goals_clear = load_goals()
            _fh = _goals_clear.get("_forecast_history", {})
            for _ck in list(_fh.keys()):
                if str(_ck) != str(selected_camp):
                    del _fh[_ck]
            _goals_clear["_forecast_history"] = _fh
            save_goals(_goals_clear)
            st.sidebar.success("Καθαρίστηκαν το calibration factor και τα παλιά snapshots.")
            st.rerun()

    target_val = goal_sales

    st.sidebar.markdown("---")

    # === Αυτόματο κλείσιμο καμπάνιας — ΠΑΝΤΑ βασισμένο στον μήνα της ΕΠΙΛΕΓΜΕΝΗΣ
    # καμπάνιας (όχι στον σημερινό μήνα). Έτσι λειτουργεί σωστά είτε κοιτάς την
    # τρέχουσα καμπάνια είτε μια παλαιότερη, χωρίς να χρειάζεται να το πειράξεις
    # χειροκίνητα κάθε φορά.
    try:
        camp_str = str(int(selected_camp))
        camp_year, camp_month = int(camp_str[:4]), int(camp_str[4:6])
        auto_end = get_campaign_end_date(ref_date=date(camp_year, camp_month, 1))
    except Exception:
        auto_end = get_campaign_end_date()  # fallback αν το selected_camp δεν είναι YYYYMM

    end_date = auto_end
    st.sidebar.caption(f"📅 Λήξη Καμπάνιας: **{end_date.strftime('%d/%m/%Y')}** (αυτόματο — τελευταία μέρα μήνα, Σάββατο αν πέφτει Κυριακή)")
    if not is_assistant_mode:
        with st.sidebar.expander("✏️ Χειροκίνητη διόρθωση ημερομηνίας (σπάνια χρήσιμο)", expanded=False):
            end_date = st.date_input("Λήξη Καμπάνιας", value=auto_end, key="manual_end_override")

    campaign_start = date(end_date.year, end_date.month, 1)
    campaign_duration_est = max(1, (end_date - campaign_start).days + 1)
    days_passed = max(1, (date.today() - campaign_start).days + 1)
    days_left = max(0, (end_date - date.today()).days)

    # === Ακριβής λήξη στις 15:00 της τελευταίας ημέρας ===
    CAMPAIGN_CUTOFF_HOUR = 15
    campaign_end_dt = datetime.combine(end_date, datetime.min.time()).replace(hour=CAMPAIGN_CUTOFF_HOUR)
    now_dt = datetime.now()
    seconds_left_total = max(0, (campaign_end_dt - now_dt).total_seconds())
    hours_left_precise  = seconds_left_total / 3600.0
    days_left_precise   = seconds_left_total / (24 * 3600.0)  # fractional, για ακριβές pacing
    is_final_day = (date.today() == end_date)
    is_closed    = now_dt >= campaign_end_dt

    total_members_count = len(df_members_raw['NameClean'].unique())
    
    df_members_raw['Tier'] = df_members_raw['Ονοματεπώνυμο'].apply(get_tier_from_name)

    campaign_stats = {}
    tier_conversions = {t: {'total': 0, 'billed': 0} for t in ['DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'STANDARD', 'NEW BUSINESS']}
    for camp_name in df_sales_all[camp_col].unique():
        # ΚΡΙΣΙΜΟ: το campaign_stats πρέπει να περιέχει ΜΟΝΟ ολοκληρωμένες
        # ιστορικές καμπάνιες. Χωρίς αυτό το φίλτρο, η ΤΡΕΧΟΥΣΑ (ημιτελής)
        # καμπάνια έμπαινε μέσα με το ΜΕΡΙΚΟ της σύνολο μέχρι σήμερα (π.χ. 13.420€
        # ενώ βρισκόμαστε ακόμα στα μισά του μήνα) — τραβώντας τεχνητά προς τα
        # κάτω τον ιστορικό μέσο όρο, το ελάχιστο, και κάθε forecast/σύγκριση
        # που βασίζεται σε αυτά (Historical Trend, Pacing floor, Goal Recommendation,
        # Team Health, Year-over-Year, best-campaign-ever κ.ά.).
        if str(camp_name) == str(selected_camp):
            continue
        df_camp = df_sales_all[df_sales_all[camp_col] == camp_name].copy()
        df_camp['_StatusTmp'] = df_camp[status_col_global].apply(remove_accents).str.upper()
        df_camp = df_camp[~df_camp['_StatusTmp'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
        billed_mask_camp = df_camp['_StatusTmp'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
        billed_names_camp = set(df_camp[billed_mask_camp & (df_camp['Ποσό_Net'] > 0.01)]['NameClean'])
        total_net_camp = df_camp[billed_mask_camp]['Ποσό_Net'].sum()

        if len(billed_names_camp) > 0:
            campaign_stats[camp_name] = {
                'total_net': total_net_camp,
                'unique_members': len(billed_names_camp),
                'avg_basket': total_net_camp / len(billed_names_camp),
                'conversion_rate': len(billed_names_camp) / max(1, total_members_count),
                'billed_names': billed_names_camp
            }
            
        for _, m in df_members_raw.iterrows():
            if pd.notna(m.get('Tier')):
                tier_conversions[m['Tier']]['total'] += 1
                if m['NameClean'] in billed_names_camp:
                    tier_conversions[m['Tier']]['billed'] += 1

    # Ιστορικά στατιστικά ομάδας (μέσοι όροι από ΟΛΕΣ τις καμπάνιες)
    tier_conversion_rates = {}
    for t, data in tier_conversions.items():
        tier_conversion_rates[t] = data['billed'] / max(1, data['total']) if data['total'] > 0 else 0.50

    # =========================================================
    # ΔΥΝΑΜΙΚΟΣ ΥΠΟΛΟΓΙΣΜΟΣ TIER BASKETS από ιστορικά (βελτίωση #7)
    # Για κάθε tier: EWMA μ.ο. καλαθιού από όλες τις ιστορικές καμπάνιες
    # Αντικαθιστά τα hardcoded 530/217/90/45/35/65 με πραγματικά δεδομένα
    # =========================================================
    tier_basket_history = {t: [] for t in _TIER_FALLBACK_DEFAULTS}

    for camp_name in sorted(campaign_stats.keys()):  # χρονολογική σειρά
        df_camp_t = df_sales_all[df_sales_all[camp_col] == camp_name].copy()
        df_camp_t['_StatusTmp'] = df_camp_t[status_col_global].apply(remove_accents).str.upper()
        df_camp_t = df_camp_t[~df_camp_t['_StatusTmp'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
        bm_t = df_camp_t['_StatusTmp'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
        df_billed_t = df_camp_t[bm_t & (df_camp_t['Ποσό_Net'] > 0.01)].copy()

        if df_billed_t.empty:
            continue

        # Προσθήκη tier ανά παραγγελία
        name_to_tier = dict(zip(df_members_raw['NameClean'], df_members_raw['Tier']))
        df_billed_t['_Tier'] = df_billed_t['NameClean'].map(name_to_tier).fillna('STANDARD')

        # ΚΡΙΣΙΜΟ: πρώτα SUM ανά μέλος (ένα μέλος = πολλές γραμμές),
        # μετά μέσος όρος των συνόλων ανά tier → πραγματικό "καλάθι" μέλους
        member_totals = df_billed_t.groupby(['NameClean', '_Tier'])['Ποσό_Net'].sum().reset_index()
        tier_groups = member_totals.groupby('_Tier')['Ποσό_Net'].mean()
        for tier_name, avg_val in tier_groups.items():
            if tier_name in tier_basket_history and avg_val > 5:
                tier_basket_history[tier_name].append(avg_val)

    # EWMA: πιο πρόσφατες καμπάνιες βαρύτερες (3×)
    for tier_name, values in tier_basket_history.items():
        if len(values) >= 2:
            w = np.array([1.0 + 2.0 * (i / max(1, len(values) - 1)) for i in range(len(values))])
            _dynamic_tier_baskets[tier_name] = float(np.average(values, weights=w))
        elif len(values) == 1:
            _dynamic_tier_baskets[tier_name] = values[0]
        # Αν δεν υπάρχουν δεδομένα, το get_manual_fallback() χρησιμοποιεί τα defaults


    hist_conversion_rates = [s['conversion_rate'] for s in campaign_stats.values()]
    hist_avg_baskets = [s['avg_basket'] for s in campaign_stats.values()]
    hist_totals = [s['total_net'] for s in campaign_stats.values()]

    # Ορισμός hist_camp_sorted εδώ — χρησιμοποιείται παντού παρακάτω
    hist_camp_sorted = sorted(campaign_stats.keys())

    # =========================================================
    # ΔΥΝΑΜΙΚΟΣ LAST-DAY RUSH FACTOR
    # Υπολογίζει από τα πραγματικά ιστορικά δεδομένα πόσο % των
    # τελικών πωλήσεων/actives ήρθε την ΤΕΛΕΥΤΑΙΑ ημέρα κάθε καμπάνιας.
    # Λειτουργεί μόνο αν υπάρχει στήλη ημερομηνίας.
    # =========================================================
    last_day_sales_ratios = []
    last_day_actives_ratios = []

    if date_col and '_OrderDate' in df_sales_all.columns:
        for ck in hist_camp_sorted:
            df_ck_full = df_sales_all[df_sales_all[camp_col] == ck].copy()
            df_ck_full['_st2'] = df_ck_full[status_col_global].apply(remove_accents).str.upper()
            df_ck_full = df_ck_full[~df_ck_full['_st2'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
            bm_full = df_ck_full['_st2'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
            df_ck_b = df_ck_full[bm_full & (df_ck_full['Ποσό_Net'] > 0.01)].copy()
            df_ck_b['_OrderDate'] = pd.to_datetime(df_sales_all.loc[df_ck_b.index, '_OrderDate'], errors='coerce')
            df_ck_b = df_ck_b.dropna(subset=['_OrderDate'])

            if df_ck_b.empty:
                continue

            last_day_of_camp = df_ck_b['_OrderDate'].dt.day.max()
            total_camp_net = df_ck_b['Ποσό_Net'].sum()
            total_camp_members = df_ck_b['NameClean'].nunique()

            last_day_net = df_ck_b[df_ck_b['_OrderDate'].dt.day == last_day_of_camp]['Ποσό_Net'].sum()
            last_day_members = df_ck_b[df_ck_b['_OrderDate'].dt.day == last_day_of_camp]['NameClean'].nunique()

            if total_camp_net > 0:
                last_day_sales_ratios.append(last_day_net / total_camp_net)
            if total_camp_members > 0:
                last_day_actives_ratios.append(last_day_members / total_camp_members)

    if last_day_sales_ratios:
        # EWMA: πιο πρόσφατες καμπάνιες βαρύτερες
        w = np.array([1.0 + 2.0 * (i / max(1, len(last_day_sales_ratios) - 1)) for i in range(len(last_day_sales_ratios))])
        avg_last_day_sales_pct = float(np.average(last_day_sales_ratios, weights=w))
        avg_last_day_actives_pct = float(np.average(last_day_actives_ratios, weights=w[:len(last_day_actives_ratios)]))
        has_last_day_data = True
    else:
        # Fallback: γνωστή επιχειρηματική γνώση — η τελευταία μέρα είναι πολύ δυνατή
        avg_last_day_sales_pct = 0.22    # ~22% των πωλήσεων την τελευταία μέρα (default εκτίμηση)
        avg_last_day_actives_pct = 0.18  # ~18% των actives
        has_last_day_data = False

    # Feature 9: Καλύτερη καμπάνια ποτέ
    if campaign_stats:
        best_camp_key   = max(campaign_stats, key=lambda k: campaign_stats[k]['total_net'])
        best_camp_total = campaign_stats[best_camp_key]['total_net']
    else:
        best_camp_key, best_camp_total = None, 0

    # Feature 6: Tier Upgrade/Downgrade detection
    # Συγκρίνει ιστορικό μέσο καλάθι με τρέχον tier fallback
    tier_upgrade_notes = {}
    for _, row in df_members_raw.iterrows():
        n   = row['NameClean']
        hist = sheet4_history.get(n, 0) if 'sheet4_history' in dir() else 0
        tier_expected = _dynamic_tier_baskets.get(row.get('Tier','STANDARD'),
                        _TIER_FALLBACK_DEFAULTS.get(row.get('Tier','STANDARD'), 65))
        if hist > 0 and tier_expected > 0:
            ratio = hist / tier_expected
            if ratio > 1.5:
                tier_upgrade_notes[n] = f"📈 Απόδοση >{ratio:.0%} tier avg — πιθανή αναβάθμιση"
            elif ratio < 0.5:
                tier_upgrade_notes[n] = f"📉 Απόδοση <{ratio:.0%} tier avg — πιθανή υποβάθμιση"

    # === ΒΕΛΤΙΩΣΗ 1: Trend-Adjusted Historical Anchor (EWMA + Linear Trend) ===
    # Αντί απλού μέσου, δίνουμε 3× βάρος στις 2 πιο πρόσφατες καμπάνιες
    historical_conversion_rate = float(np.mean(hist_conversion_rates)) if hist_conversion_rates else 0.50
    historical_avg_basket = float(np.mean(hist_avg_baskets)) if hist_avg_baskets else 65.0
    
    if len(hist_totals) >= 3:
        # EWMA: βάρη 1,1,2,2,3 για τις πιο πρόσφατες
        ewma_weights = np.array([1.0 + 2.0*(i/max(1,len(hist_totals)-1)) for i in range(len(hist_totals))])
        historical_avg_total = float(np.average(hist_totals, weights=ewma_weights))
        
        # Linear trend on totals: αν πέφτουν ή ανεβαίνουν
        x_trend = np.arange(len(hist_totals), dtype=float)
        coeffs_trend = np.polyfit(x_trend, hist_totals, 1)
        trend_slope = coeffs_trend[0]  # €/καμπάνια
        # Εκτίμηση επόμενης καμπάνιας βάσει τάσης
        trend_projected_total = historical_avg_total + trend_slope * 0.5  # 50% dampening
        # Blend EWMA + Trend (60/40)
        historical_avg_total = historical_avg_total * 0.60 + max(0, trend_projected_total) * 0.40
        
        # Trend-adjusted CR
        if len(hist_conversion_rates) >= 3:
            x_cr = np.arange(len(hist_conversion_rates), dtype=float)
            cr_coeffs = np.polyfit(x_cr, hist_conversion_rates, 1)
            trend_cr_slope = cr_coeffs[0]
            historical_conversion_rate = float(np.average(hist_conversion_rates, weights=ewma_weights))
            historical_conversion_rate = max(0.20, min(0.90, historical_conversion_rate + trend_cr_slope * 0.5))
    else:
        historical_avg_total = float(np.mean(hist_totals)) if hist_totals else 0.0

    historical_std_total = float(np.std(hist_totals)) if len(hist_totals) > 1 else max(1.0, historical_avg_total * 0.20)
    historical_cv = historical_std_total / max(1.0, historical_avg_total) if historical_avg_total > 0 else 0.25
    
    # MAPE από ιστορικά: μέτρο τυπικής απόκλισης σε % (για confidence intervals)
    historical_mape = historical_cv  # proxy: CV ≈ MAPE για σταθερό μοντέλο

    # =========================================================
    # ΒΕΛΤΙΩΜΕΝΗ ΙΣΤΟΡΙΚΟΤΗΤΑ ΑΠΟ ΤΟ ΦΥΛΛΟ 1 (ΟΛΕΣ ΟΙ ΚΑΜΠΑΝΙΕΣ)
    # Χτίζει το ιστορικό χρησιμοποιώντας τα πραγματικά τιμολογημένα ποσά
    # =========================================================
    sheet4_history = {}          
    history_detailed = {}        
    all_historical_nets = []
    
    # Βρίσκουμε τις ιστορικές καμπάνιες (όλες όσες είναι ΠΡΙΝ από την selected_camp)
    historical_camps = sorted([c for c in available_camps if str(c) < str(selected_camp)])
    
    # Ετοιμάζουμε ένα γρήγορο λεξικό από το df_sales_all για να μην κάνουμε αργά queries στο loop
    df_hist_all = df_sales_all[df_sales_all[camp_col].isin(historical_camps)].copy()
    if not df_hist_all.empty:
        df_hist_all['_StatusTmp'] = df_hist_all[status_col_global].apply(lambda x: remove_accents(str(x)).upper())
        df_hist_all = df_hist_all[~df_hist_all['_StatusTmp'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
        df_hist_all = df_hist_all[df_hist_all['Ποσό_Net'] > 0.01]
        
        hist_grouped = df_hist_all.groupby(['NameClean', camp_col])['Ποσό_Net'].sum().reset_index()
    else:
        hist_grouped = pd.DataFrame(columns=['NameClean', camp_col, 'Ποσό_Net'])
        
    # === ΙΣΤΟΡΙΚΟΤΗΤΑ ΑΠΟΚΛΕΙΣΤΙΚΑ ΑΠΟ ΤΟ ΦΥΛΛΟ1 ===
    # ΚΡΙΣΙΜΗ ΑΛΛΑΓΗ: το ιστορικό ΔΕΝ χτίζεται πλέον κάνοντας loop πάνω στα ονόματα
    # του Φύλλο4 (μέλη) και ψάχνοντας ταίριασμα στο Φύλλο1. Αντίθετα, κάνουμε loop
    # ΑΠΕΥΘΕΙΑΣ πάνω σε ό,τι όνομα υπάρχει ήδη στο Φύλλο1 (hist_grouped) — δηλαδή
    # οτιδήποτε έχει πραγματική καταγεγραμμένη παραγγελία στο ιστορικό, ανεξάρτητα
    # από το αν/πώς εμφανίζεται στο Φύλλο4. Το Φύλλο4 αγνοείται εντελώς εδώ.
    # Αυτό λύνει οριστικά προβλήματα σαν το "ΑΓΑΠΗ ΧΑΤΖΗΔΗΜΗΤΡΙΑΔΟΥ" (διαφορετική
    # γραφή ονόματος ανάμεσα στα δύο φύλλα), αφού η τρέχουσα καμπάνια (names_with_any_order)
    # προέρχεται ΚΙ ΑΥΤΗ από το Φύλλο1 — άρα τα ονόματα πλέον ταιριάζουν πάντα μεταξύ τους.
    all_hist_names = hist_grouped['NameClean'].unique().tolist() if not hist_grouped.empty else []
    fuzzy_name_matches = {}  # διατηρείται κενό/αχρησιμοποίητο· υπάρχει μόνο για συμβατότητα με το Data Health Check

    for name in all_hist_names:
        entries = []
        member_hist = hist_grouped[hist_grouped['NameClean'] == name]

        for pidx, camp in enumerate(historical_camps):
            camp_data = member_hist[member_hist[camp_col] == camp]
            if not camp_data.empty:
                net_val = camp_data['Ποσό_Net'].iloc[0]
                entries.append({'period_idx': pidx, 'net_value': net_val})

        if entries:
            history_detailed[name] = entries
            avg_net = sum(e['net_value'] for e in entries) / len(entries)
            sheet4_history[name] = avg_net
            all_historical_nets.append(avg_net)

    if all_historical_nets:
        valid_nets = [n for n in all_historical_nets if n > 15]
        global_avg_basket = sum(valid_nets) / len(valid_nets) if valid_nets else 65.0
    else:
        global_avg_basket = 65.0

    num_hist_camps = len(historical_camps) if historical_camps else 1
    
    # Χτίσιμο per-member predictions (weighted avg + trend + reliability)
    member_predictions = build_member_predictions(history_detailed, num_hist_camps)
    
    # ML Training
    xgb_model = train_propensity_model(history_detailed, num_hist_camps)

    if not is_assistant_mode:
        if st.sidebar.button("🔄 Reset Tik (Ok)"):
            st.session_state.sent_ids = set()
            save_contacted_today(set())  # καθαρισμός ΚΑΙ της μόνιμης αποθήκευσης
            st.rerun()

    # ==========================================
    # --- PROCESSING ---
    # ==========================================
    df_curr = df_sales_all[df_sales_all[camp_col] == selected_camp].copy()
    status_col = next((c for c in df_curr.columns if 'ΚΑΤΑΣΤΑΣΗ' in remove_accents(str(c)).upper() or 'STATUS' in remove_accents(str(c)).upper()), 'Κατάσταση')
    df_curr['Status_Clean'] = df_curr[status_col].apply(remove_accents).str.upper()
    
    # Αφαιρούμε Ακυρωμένες/Απορριφθείσες
    mask_invalid = df_curr['Status_Clean'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)
    df_curr = df_curr[~mask_invalid]

    positive_orders_mask = df_curr['Ποσό_Net'] > 0.01

    # === ADJUSTMENTS: γραμμές με ΑΡΝΗΤΙΚΟ ποσό (διορθώσεις/επιστροφές) ===
    # Αυτές δεν προσμετρώνται πουθενά αλλού (ούτε billed ούτε pending), αλλά
    # πρέπει να είναι ορατές — δείχνουν ποιο μέλος και τι ποσό αφορά κάθε adjustment.
    negative_orders_mask = df_curr['Ποσό_Net'] < -0.01
    df_adjustments = df_curr[negative_orders_mask].copy()
    if not df_adjustments.empty:
        df_adjustments = df_adjustments.sort_values('Ποσό_Net')  # πιο αρνητικά πρώτα

    # === ΚΕΝΗ ΚΑΤΑΣΤΑΣΗ: παραγγελίες χωρίς καμία τιμή στη στήλη Κατάσταση ===
    # Κατά πάσα πιθανότητα έχουν «κολλήσει» σε πιστωτικό έλεγχο και δεν έχουν
    # προχωρήσει ούτε σε "Παρελήφθη" ούτε σε τιμολόγηση — δεν εμφανίζονται
    # πουθενά αλλού στην εφαρμογή, γι' αυτό χρειάζονται δικό τους tab.
    empty_status_mask = (
        df_curr[status_col].isna() |
        (df_curr[status_col].astype(str).str.strip().isin(['', 'nan', 'None', 'NaT']))
    )
    df_empty_status = df_curr[empty_status_mask].copy()

    # 1. ΛΙΣΤΑ "ΠΡΟΣ ΤΙΜΟΛΟΓΗΣΗ" (Η παραγγελία παρελήφθη)
    pending_system_mask = df_curr['Status_Clean'].str.contains('ΠΑΡΕΛΗΦΘΗ', na=False)
    df_pros_timologisi = df_curr[pending_system_mask].copy()

    # 2. ΕΝΤΟΠΙΣΜΟΣ ΤΙΜΟΛΟΓΗΜΕΝΩΝ (Τιμολογήθηκε ή Παραδόδηκε/Παραδόθηκε)
    billed_status_mask = df_curr['Status_Clean'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
    real_billed_names = set(df_curr[billed_status_mask & positive_orders_mask]['NameClean'])

    # Ενεργά Άτομα (Μοναδικές Παραγγελίες)
    unique_orders_count = len(real_billed_names)

    # 3. HEADCOUNT & ΣΥΝΟΛΑ
    pros_timologisi_names = set(df_pros_timologisi['NameClean'])
    names_with_any_order = pros_timologisi_names.union(real_billed_names)

    ekkremis_col = next((c for c in df_todo_raw.columns if 'ΕΚΚΡΕΜ' in remove_accents(str(c)).upper()), 'Εκκρεμής')
    if ekkremis_col in df_todo_raw.columns:
        df_sheet2_list = df_todo_raw[df_todo_raw[ekkremis_col].astype(str).str.upper() == 'Y'].copy()
    else:
        df_sheet2_list = df_todo_raw.copy()

    df_call_list_ekkremeis = df_sheet2_list[~df_sheet2_list['NameClean'].isin(names_with_any_order)].copy()

    # Ενημερωμένο Grouping με διόρθωση σφάλματος (float to str)
    df_member_summary = df_curr.groupby('NameClean').agg({
        'Ονοματεπώνυμο': 'first',
        'Ποσό_Net': 'sum',
        'Τηλέφωνο': lambda x: next((i for i in x if pd.notna(i)), None),
        status_col: lambda x: '✅ Τιμολογήθηκε / Στον Οδηγό' if any(s in " ".join([str(v) for v in x]).upper() for s in ['ΤΙΜΟΛΟΓ', 'ΠΑΡΑΔΟΔ', 'ΠΑΡΑΔΟΘ']) else '⏳ Η παραγγελία παρελήφθη'
    }).reset_index()
    df_member_summary.rename(columns={status_col: 'Κατάσταση'}, inplace=True)

    # ---------------------------------------------------------
    # PDF EXPORT LOGIC: Βρίσκουμε άτομα χωρίς καμία παραγγελία
    # ---------------------------------------------------------

        
    df_no_order = df_members_raw[~df_members_raw['NameClean'].isin(names_with_any_order)].copy()
    df_no_order['TierRank'] = df_no_order['Ονοματεπώνυμο'].apply(get_tier_rank)
    df_no_order = df_no_order.sort_values(by=['TierRank', 'Ονοματεπώνυμο'])
    
    phone_col_main = next((c for c in df_members_raw.columns if 'ΤΗΛ' in remove_accents(str(c)).upper() or 'PHONE' in remove_accents(str(c)).upper()), 'Τηλέφωνο')

    # Auto-refresh toggle (Feature 7)
    st.sidebar.markdown("---")
    if HAS_AUTOREFRESH:
        if is_assistant_mode:
            # Λειτουργία Βοηθού: auto-refresh ΠΑΝΤΑ ενεργό, αυτόματα — έτσι η
            # λίστα ενημερώνεται μόνη της όσο δουλεύει, χωρίς να χρειάζεται να
            # θυμάται να κάνει refresh χειροκίνητα (και χωρίς επιλογή να το κλείσει).
            st.sidebar.caption("🔄 Auto Refresh: ενεργό (κάθε 5 λεπτά)")
            st_autorefresh(interval=5 * 60 * 1000, key="autorefresh")
        else:
            auto_refresh = st.sidebar.toggle("🔄 Auto Refresh (15')", value=False)
            if auto_refresh:
                st_autorefresh(interval=15 * 60 * 1000, key="autorefresh")
    else:
        st.sidebar.caption("💡 `pip install streamlit-autorefresh` για auto-refresh")

    if not is_assistant_mode:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Εξαγωγή Λίστας")
        if FPDF is None:
            st.sidebar.warning("⚠️ Για εξαγωγή PDF εγκαταστήστε το fpdf2: `pip install fpdf2`")
        else:
            pdf_bytes = create_pdf_bytes(df_no_order, phone_col_main)
            if pdf_bytes:
                st.sidebar.download_button(
                    label="📥 Κατέβασμα PDF (Χωρίς Παραγγελία)",
                    data=pdf_bytes,
                    file_name=f"No_Orders_List_{selected_camp}.pdf",
                    mime="application/pdf"
                )

    # Feature 8: Excel export με όλα τα sheets
    def build_excel_export():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not df_billed_only.empty:
                df_billed_only[['Ονοματεπώνυμο','Ποσό_Net','Κατάσταση']]\
                    .sort_values('Ποσό_Net', ascending=False)\
                    .to_excel(writer, sheet_name='Τιμολογημένες', index=False)
            if not df_pros_timologisi.empty:
                df_pros_timologisi[['Ονοματεπώνυμο','Ποσό_Net','Τηλέφωνο']]\
                    .to_excel(writer, sheet_name='Προς Τιμολόγηση', index=False)
            if not df_call_list_ekkremeis.empty:
                df_call_list_ekkremeis[['Ονοματεπώνυμο','Τηλέφωνο']]\
                    .to_excel(writer, sheet_name='Εκκρεμείς', index=False)
            if not df_rem_clean.empty:
                df_rem_clean[['Ονοματεπώνυμο','Τηλέφωνο']]\
                    .to_excel(writer, sheet_name='Διαγραφές', index=False)
            # Φύλλο προβλέψεων ανά μέλος
            pred_rows = []
            for n, p in member_predictions.items():
                orig = name_to_original.get(n, n)
                pred_rows.append({
                    'Όνομα': orig,
                    'Πιθανότητα %': round(p['ml_prob']*100, 1),
                    'Εκτίμηση €': round(p['predicted'], 0),
                    'Εύρος P25 €': round(p.get('p25', p['predicted']*0.7), 0),
                    'Εύρος P75 €': round(p.get('p75', p['predicted']*1.3), 0),
                    'Αξιοπιστία %': round(p['reliability']*100, 1),
                })
            if pred_rows:
                pd.DataFrame(pred_rows).sort_values('Εκτίμηση €', ascending=False)\
                    .to_excel(writer, sheet_name='Προβλέψεις', index=False)
        return output.getvalue()

    if not is_assistant_mode:
        try:
            xl_bytes = build_excel_export()
            st.sidebar.download_button(
                label="📊 Κατέβασμα Excel (Πλήρης Αναφορά)",
                data=xl_bytes,
                file_name=f"Avon_Report_{selected_camp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception:
            pass

    # =========================================================
    # 4. DATA-DRIVEN FORECAST (v600)
    # =========================================================
    total_billed_net = df_curr[billed_status_mask]['Ποσό_Net'].sum()
    total_sales_net = df_curr['Ποσό_Net'].sum()
    remaining_to_target = max(0.0, target_val - total_billed_net)
    
    df_billed_only = df_member_summary[df_member_summary['NameClean'].isin(real_billed_names)].copy()

    # === GOAL RECOMMENDATION ENGINE ===
    # Προτείνει ρεαλιστικό στόχο βάσει ιστορικού trend, αντί να ξεκινάς από μηδέν
    if hist_totals and len(hist_totals) >= 2 and not is_assistant_mode:
        ewma_w_goal = np.array([1.0 + 2.0 * (i / max(1, len(hist_totals) - 1)) for i in range(len(hist_totals))])
        weighted_hist_avg = float(np.average(hist_totals, weights=ewma_w_goal))
        if len(hist_totals) >= 3:
            recent_growth = (hist_totals[-1] - hist_totals[-3]) / max(1, hist_totals[-3]) / 2  # μέση ανά καμπάνια
        else:
            recent_growth = (hist_totals[-1] - hist_totals[0]) / max(1, hist_totals[0]) / max(1, len(hist_totals) - 1)
        recent_growth = max(-0.15, min(0.15, recent_growth))  # sanity clamp ±15%
        recommended_goal = weighted_hist_avg * (1 + recent_growth)

        st.sidebar.caption(
            f"💡 **Προτεινόμενος στόχος:** {recommended_goal:,.0f}€ "
            f"(βάσει EWMA ιστορικού {weighted_hist_avg:,.0f}€ {'+' if recent_growth>=0 else ''}{recent_growth:.0%} τάση)"
        )
        if abs(goal_sales - recommended_goal) > recommended_goal * 0.15:
            st.sidebar.caption(f"⚠️ Ο τρέχων στόχος σου ({goal_sales:,.0f}€) διαφέρει σημαντικά από την πρόταση.")

    # --- Sidebar: Tier Baskets vs Ιστορικό (εδώ γιατί χρειάζεται df_billed_only) ---
    name_to_tier_curr = dict(zip(df_members_raw['NameClean'], df_members_raw['Tier']))
    df_billed_only['_Tier'] = df_billed_only['NameClean'].map(name_to_tier_curr).fillna('STANDARD')
    curr_tier_baskets = (
        df_billed_only[df_billed_only['Ποσό_Net'] > 0]
        .groupby('_Tier')['Ποσό_Net'].mean()
        .to_dict()
    )
    tier_icons = {'DIAMOND': '💎', 'PLATINUM': '🥈', 'GOLD': '🥇', 'SILVER': '🪙', 'BRONZE': '🥉'}
    tier_order = ['DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE']

    st.sidebar.markdown("---")
    if not is_assistant_mode:
        st.sidebar.subheader("🎯 Καλάθι ανά Tier: Τρέχον vs Ιστορικό")
        for t in tier_order:
            hist_val = _dynamic_tier_baskets.get(t)
            curr_val = curr_tier_baskets.get(t)
            icon = tier_icons[t]
            if hist_val and curr_val:
                delta_pct = (curr_val - hist_val) / hist_val * 100
                arrow = "↑" if delta_pct > 0 else "↓"
                color = "#28a745" if delta_pct > 0 else "#dc3545"
                st.sidebar.markdown(
                    f"{icon} **{t}**<br>"
                    f"<span style='font-size:12px'>Τρέχον: <b>{curr_val:,.0f}€</b> &nbsp;|&nbsp; Ιστορικό: {hist_val:,.0f}€ &nbsp;"
                    f"<span style='color:{color}'>{arrow}{abs(delta_pct):.0f}%</span></span>",
                    unsafe_allow_html=True
                )
            elif hist_val:
                st.sidebar.markdown(
                    f"{icon} **{t}**<br>"
                    f"<span style='font-size:12px'>Ιστορικό: {hist_val:,.0f}€ &nbsp;"
                    f"<span style='color:#888'>— χωρίς τρέχουσες παραγγελίες</span></span>",
                    unsafe_allow_html=True
                )
        st.sidebar.caption("Μ.Ο. καλαθιού ανά μέλος. Τρέχον = τιμολογημένες αυτής της καμπάνιας.")
    
    def get_smart_value(name_clean, name_original):
        """Επιστρέφει εκτίμηση αξίας μέλους: prediction > history > tier fallback"""
        pred = member_predictions.get(name_clean)
        if pred and pred['predicted'] > 0:
            return pred['predicted']
        hist_val = float(sheet4_history.get(name_clean, 0.0))
        if hist_val > 0:
            return hist_val
        return float(get_manual_fallback(name_original))

    # Αξία Προς Τιμολόγηση
    val_pros_timologisi = 0.0
    for _, r in df_pros_timologisi.iterrows():
        val = r['Ποσό_Net'] if r['Ποσό_Net'] > 0 else get_smart_value(r['NameClean'], r['Ονοματεπώνυμο'])
        val_pros_timologisi += float(val)

    # --- ΜΕΛΗ ΠΟΥ ΔΕΝ ΕΧΟΥΝ ΠΑΡΑΓΓΕΙΛΕΙ ΑΚΟΜΑ ---
    names_not_ordered = [n for n in df_members_raw['NameClean'].unique() if n not in names_with_any_order]

    # Pre-compute arrays για vectorized Monte Carlo
    n_remaining = len(names_not_ordered)
    member_probs = np.zeros(n_remaining)
    member_pred_vals = np.zeros(n_remaining)
    member_pred_stds = np.zeros(n_remaining)

    # Mapping name → original name (για fallbacks)
    name_to_original = dict(zip(df_members_raw['NameClean'], df_members_raw['Ονοματεπώνυμο']))

    # === ΒΕΛΤΙΩΣΗ 4: Calibrated fallback βάσει global avg basket από ΠΡΑΓΜΑΤΙΚΑ δεδομένα ===
    calibrated_fallback_basket = global_avg_basket if global_avg_basket > 20 else 65.0
    calibrated_fallback_prob = min(0.40, historical_conversion_rate * 0.60)  # Νέα μέλη έχουν χαμηλότερη CR

    for idx, name in enumerate(names_not_ordered):
        pred = member_predictions.get(name)
        tier = get_tier_from_name(name_to_original.get(name, name))
        tier_cr = tier_conversion_rates.get(tier, historical_conversion_rate)
        
        if pred:
            # === ΒΕΛΤΙΩΣΗ 3: Conversion Frequency ως κύρια πιθανότητα ===
            conv_freq = pred.get('conversion_freq', pred['reliability'])
            
            if xgb_model is not None:
                features = np.array([[pred['reliability'], pred['weighted_avg'], get_tier_rank(name)]])
                ml_prob = xgb_model.predict_proba(features)[0][1]
                # Blend: 50% Conversion Frequency + 30% ML + 20% Tier CR
                # Conv Frequency είναι ο πιο άμεσος και αξιόπιστος δείκτης
                base_prob = conv_freq * 0.50 + ml_prob * 0.30 + tier_cr * 0.20
            else:
                # Χωρίς ML: 70% Conv Frequency + 30% Tier CR
                base_prob = conv_freq * 0.70 + tier_cr * 0.30
            
            pred['ml_prob'] = min(0.95, base_prob)
            member_probs[idx] = pred['ml_prob']
            member_pred_vals[idx] = pred['predicted']
            member_pred_stds[idx] = pred['std'] if pred['std'] > 0 else pred['predicted'] * 0.3
        else:
            # Βελτιωμένο fallback για νέα μέλη: βάσει ιστορικού avg basket
            fallback_val = get_manual_fallback(name_to_original.get(name, name))
            # Χρήση calibrated basket αν η tier fallback δεν είναι πολύ διαφορετική
            if abs(fallback_val - calibrated_fallback_basket) / max(1, calibrated_fallback_basket) > 0.5:
                fallback_val = calibrated_fallback_basket
            fallback_prob = calibrated_fallback_prob
            # Feature 4: Decay για μέλη που απουσίαζαν σε πολλές καμπάνιες
            absent_camps = sum(1 for ck in hist_camp_sorted
                               if name not in set(df_sales_all[df_sales_all[camp_col]==ck]['NameClean']))
            if absent_camps >= 2:
                decay = 0.70 ** (absent_camps - 1)
                fallback_prob = fallback_prob * decay
                fallback_val  = fallback_val  * max(0.40, decay)
            member_probs[idx] = fallback_prob
            member_predictions[name] = {
                'ml_prob': fallback_prob,
                'predicted': fallback_val,
                'reliability': 0.0,
                'conversion_freq': 0.0,
                'weighted_avg': fallback_val,
                'trend_factor': 0.0,
                'std': fallback_val * 0.35,
                'p25': fallback_val * 0.70,
                'p75': fallback_val * 1.30,
            }
            member_pred_vals[idx] = fallback_val
            member_pred_stds[idx] = fallback_val * 0.35

    # === TIME DECAY (μόνο για τα εναπομείναντα μέλη) ===
    # ΔΙΟΡΘΩΣΗ: total_days χρησιμοποιούσε days_left (ακέραιος, =0 πάντα την τελευταία μέρα)
    # αντί για τις πραγματικές ώρες που απομένουν ως τις 15:00. Αυτό έκανε το
    # time_passed_ratio=1.0 τεχνητά νωρίς μέσα στην τελευταία μέρα.
    total_days = days_passed + (days_left_precise if 'days_left_precise' in dir() else days_left)
    time_passed_ratio = days_passed / max(1.0, total_days)

    # === ΔΙΟΡΘΩΣΗ ΚΡΙΣΙΜΟΥ BUG: αντεστραμμένη λογική confidence_buffer ===
    # Η ΠΑΛΙΑ λογική: "αν το μέλος έχει υψηλό ιστορικό p, μην το αποδυναμώσεις πολύ"
    # (confidence_buffer = p², actual_decay ανεβαίνει όσο πιο υψηλό το p).
    # Αυτό είναι ΛΑΘΟΣ: ένα μέλος με ιστορικά 88% πιθανότητα συμμετοχής που ΑΚΟΜΑ
    # δεν έχει παραγγείλει την τελευταία μέρα είναι αδύναμο σήμα (κάτι άλλαξε φέτος),
    # όχι ισχυρό. Σωστή λογική: όσο πλησιάζει το τέλος, ΟΛΑ τα μέλη που καθυστερούν
    # αποδυναμώνονται σημαντικά, ανεξάρτητα από το πόσο υψηλό ήταν το ιστορικό τους p —
    # ειδικά τα υψηλής πιθανότητας μέλη, γιατί η απουσία τους είναι πιο "περίεργη".
    for idx, name in enumerate(names_not_ordered):
        p = member_probs[idx]
        if time_passed_ratio > 0.5:
            # Βασικό decay που εντείνεται όσο περνάει ο χρόνος (μέχρι ×0.35 στο τέλος)
            decay_factor = 1.0 - ((time_passed_ratio - 0.5) / 0.5) * 0.65
            decay_factor = max(0.25, decay_factor)
            member_probs[idx] = p * decay_factor
        if name in member_predictions:
            member_predictions[name]['ml_prob'] = member_probs[idx]

    # === Same-Day Historical Comparison ===
    # Συγκρίνει την τρέχουσα πρόοδο με την ΙΔΙΑ ΗΜΕΡΑ της αντίστοιχης ιστορικής καμπάνιας
    # (Μετακινήθηκε ΠΡΙΝ το Pacing Model γιατί το pacing χρειάζεται το hist_same_day_net)
    prev_camp_key = hist_camp_sorted[-1] if hist_camp_sorted else None

    def get_same_day_stats(target_camp_key, day_of_month):
        """
        Επιστρέφει τις τιμολογημένες πωλήσεις & ενεργά μέλη έως την ίδια ημέρα
        μιας ιστορικής καμπάνιας.
        - Αν υπάρχει στήλη ημερομηνίας: φιλτράρει βάσει ημέρας μήνα.
        - Αν δεν υπάρχει: επιστρέφει weighted avg από ΟΛΑ τα ιστορικά × αναλογία ημέρας.
        """
        df_camp_h = df_sales_all[df_sales_all[camp_col] == target_camp_key].copy()
        df_camp_h['_StatusTmp'] = df_camp_h[status_col_global].apply(remove_accents).str.upper()
        df_camp_h = df_camp_h[~df_camp_h['_StatusTmp'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
        bm = df_camp_h['_StatusTmp'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)

        if date_col and '_OrderDate' in df_sales_all.columns:
            df_camp_h['_OrderDate'] = pd.to_datetime(df_sales_all.loc[df_camp_h.index, '_OrderDate'], errors='coerce')
            df_camp_h_day = df_camp_h[df_camp_h['_OrderDate'].dt.day <= day_of_month]
            bm_day = df_camp_h_day['_StatusTmp'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
            same_day_net = df_camp_h_day[bm_day]['Ποσό_Net'].sum()
            same_day_members = len(df_camp_h_day[bm_day & (df_camp_h_day['Ποσό_Net'] > 0.01)]['NameClean'].unique())
        else:
            stats = campaign_stats.get(target_camp_key, {})
            ratio = days_passed / max(1, campaign_duration_est)
            same_day_net = stats.get('total_net', 0) * ratio
            same_day_members = round(stats.get('unique_members', 0) * ratio)

        return same_day_net, same_day_members

    today_day = date.today().day
    same_day_nets = []
    same_day_members_list = []

    for ck in hist_camp_sorted:
        sd_net, sd_mem = get_same_day_stats(ck, today_day)
        if sd_net > 0:
            same_day_nets.append(sd_net)
            same_day_members_list.append(sd_mem)

    if same_day_nets:
        ewma_w = np.array([1.0 + 2.0 * (i / max(1, len(same_day_nets) - 1)) for i in range(len(same_day_nets))])
        hist_same_day_net = float(np.average(same_day_nets, weights=ewma_w))
        hist_same_day_members = round(float(np.average(same_day_members_list, weights=ewma_w)))
        mom_sales_delta = ((total_billed_net - hist_same_day_net) / max(1, hist_same_day_net) * 100)
        mom_members_delta = unique_orders_count - hist_same_day_members
        prev_camp_label = f"ίδια μέρα ({today_day}η) ιστορικά"
    else:
        prev_stats = campaign_stats.get(prev_camp_key, {})
        prev_total = prev_stats.get('total_net', 0)
        prev_members = prev_stats.get('unique_members', 0)
        ratio = days_passed / max(1, campaign_duration_est)
        mom_sales_delta = ((total_billed_net - prev_total * ratio) / max(1, prev_total * ratio) * 100) if prev_total > 0 else 0
        mom_members_delta = unique_orders_count - round(prev_members * ratio)
        hist_same_day_net = prev_total * ratio
        prev_camp_label = f"{prev_camp_key} (≈{today_day}η)"

    # === ΒΕΛΤΙΩΣΗ 2: PACING MODEL (διορθωμένο) ===
    # "Αν τώρα έχουμε Χ€ πωλήσεις και ιστορικά στο ίδιο σημείο είχαμε Υ% του τελικού, τι αναμένεται;"
    # ΔΙΟΡΘΩΣΗ: η παλιά εκδοχή διαιρούσε με το ratio ΑΤΟΜΩΝ (πόσα % των ατόμων έχουν παραγγείλει),
    # κάτι λάθος γιατί οι πρώτες παραγγελίες δεν είναι τυχαίο δείγμα — συνήθως παραγγέλνουν πρώτα
    # τα πιο ενεργά μέλη. Αυτό προκαλούσε τεράστια υπερεκτίμηση (×3-4).
    # Η σωστή προσέγγιση: σύγκριση με το ΠΟΣΟΣΤΟ ΠΩΛΗΣΕΩΝ (όχι ατόμων) που είχε ιστορικά
    # έρθει μέχρι την ίδια ημέρα της καμπάνιας.
    expected_final_orders = max(1.0, total_members_count * historical_conversion_rate)
    current_orders_count = len(names_with_any_order)
    pacing_ratio = current_orders_count / expected_final_orders  # μόνο για το βάρος εμπιστοσύνης

    pacing_forecast = 0.0
    pacing_weight = 0.0

    # Sales-based pacing: ποσοστό πωλήσεων που ιστορικά έχει έρθει ΕΩΣ σήμερα (day_of_month)
    # ΣΗΜΑΝΤΙΚΟ: υπολογίζουμε το ratio (same_day/final) ΑΝΑ ΚΑΜΠΑΝΙΑ πρώτα, και μετά κάνουμε
    # EWMA πάνω στα ratios — ΟΧΙ EWMA σε δύο ξεχωριστά σύνολα (same_day_avg / final_avg),
    # γιατί αυτό μπορεί να βγάλει εξωπραγματικά μικρό/μεγάλο ποσοστό λόγω ασυμφωνίας στάθμισης.
    per_camp_ratios = []
    for ck in hist_camp_sorted:
        ck_final = campaign_stats.get(ck, {}).get('total_net', 0)
        ck_same_day, _ = get_same_day_stats(ck, today_day)
        if ck_final > 100 and ck_same_day > 0:
            r = ck_same_day / ck_final
            if 0.05 <= r <= 1.0:  # sanity: αγνόησε εξωφρενικά outliers
                per_camp_ratios.append(r)

    sales_time_pct = None
    pacing_reliable = False
    if len(per_camp_ratios) >= 2:
        w = np.array([1.0 + 2.0 * (i / max(1, len(per_camp_ratios) - 1)) for i in range(len(per_camp_ratios))])
        sales_time_pct = float(np.average(per_camp_ratios, weights=w))
        # Αξιοπιστία: αν τα ratios έχουν μεγάλη διασπορά μεταξύ τους, δεν εμπιστευόμαστε πολύ
        ratio_std = float(np.std(per_camp_ratios))
        pacing_reliable = ratio_std < 0.15  # σταθερό μοτίβο ανάμεσα στις καμπάνιες
    elif len(per_camp_ratios) == 1:
        sales_time_pct = per_camp_ratios[0]
        pacing_reliable = False  # μόνο 1 δείγμα — χαμηλή εμπιστοσύνη
    elif time_passed_ratio > 0:
        sales_time_pct = min(0.95, time_passed_ratio ** 0.85)
        pacing_reliable = False  # fallback χωρίς πραγματικά δεδομένα — χαμηλή εμπιστοσύνη

    # Επιπλέον sanity clamp: ποτέ κάτω από 20% (αποφυγή ακραίας διαίρεσης) ούτε πάνω από 97%
    if sales_time_pct is not None:
        sales_time_pct = max(0.20, min(0.97, sales_time_pct))

    if sales_time_pct and sales_time_pct > 0.15 and total_billed_net > 500:
        # Last-day boost εφαρμόζεται ΜΟΝΟ στο κομμάτι που λείπει, όχι σε όλο το σύνολο
        if is_final_day:
            hours_in_day = 24.0
            hour_progress = min(1.0, max(0.0, 1.0 - (hours_left_precise / hours_in_day)))
            remaining_boost = 1.0 + avg_last_day_sales_pct * (1.0 - hour_progress * 0.5)
        else:
            remaining_boost = 1.0 + avg_last_day_sales_pct * 0.3  # μικρή προσμονή, όχι όλο το rush νωρίς

        # Σωστός τύπος: total_billed_net / sales_time_pct = εκτιμώμενο τελικό
        # βάσει του πραγματικού ποσοστού πωλήσεων (όχι ατόμων) που έχει έρθει ως τώρα
        raw_pacing = total_billed_net / min(0.97, sales_time_pct)
        remaining_portion = max(0, raw_pacing - total_billed_net)
        pacing_forecast = total_billed_net + remaining_portion * remaining_boost

        # Sanity cap: το pacing δεν μπορεί ποτέ να ξεπεράσει το ρεαλιστικό μέγιστο δυναμικό.
        # Διπλό όριο: (α) τρέχον + pending + όλα τα μέλη στο μέγιστο ιστορικό τους καλάθι,
        # (β) ποτέ πάνω από 1.6× το ιστορικό μέγιστο σύνολο καμπάνιας (hard ceiling λογικής)
        max_plausible_bottom_up = total_billed_net + val_pros_timologisi + float(np.sum(member_pred_vals + 2 * member_pred_stds))
        hist_max_total = max(hist_totals) if hist_totals else (total_billed_net * 1.6)
        max_plausible_ceiling = hist_max_total * 1.6
        max_plausible = min(max_plausible_bottom_up, max_plausible_ceiling)
        pacing_forecast = min(pacing_forecast, max_plausible)

        # === ΣΤΑΘΕΡΟΤΗΤΑ ΚΑΘ' ΟΛΗ ΤΗ ΔΙΑΡΚΕΙΑ ΤΗΣ ΚΑΜΠΑΝΙΑΣ ===
        # Νωρίς στον μήνα, οι τρέχουσες πωλήσεις είναι φυσιολογικά χαμηλές — η
        # extrapolation του Pacing Model πάνω σε ελάχιστα δεδομένα είναι θορυβώδης.
        # ΔΙΟΡΘΩΣΗ: η προηγούμενη εκδοχή "απελευθέρωνε" πλήρως το pacing μετά το
        # 30% του μήνα ΑΣΧΕΤΑ αν τα δεδομένα ήταν αξιόπιστα ή όχι (bug) — αν
        # pacing_reliable=False στα μισά της καμπάνιας, το pacing παρέμενε εντελώς
        # ασταθές/μακριά από το ιστορικό. Τώρα ο χρόνος και η αξιοπιστία συνδυάζονται
        # ΠΡΟΣΘΕΤΙΚΑ: ακόμα και στα μισά της καμπάνιας, αν τα δεδομένα δεν είναι
        # αξιόπιστα, το pacing παραμένει σημαντικά αγκυρωμένο στο ιστορικό.
        if historical_avg_total > 0:
            time_component = max(0.0, 1.0 - time_passed_ratio / 0.50)   # μηδενίζεται στο 50% του μήνα
            reliability_component = 0.0 if pacing_reliable else 0.45     # σταθερή «ποινή» αναξιοπιστίας
            stability_blend = min(0.85, time_component + reliability_component)
            if stability_blend > 0:
                pacing_forecast = pacing_forecast * (1 - stability_blend) + historical_avg_total * stability_blend

        # Σιγουριά pacing: αυξάνεται όσο πιο μέσα στην καμπάνια είμαστε,
        # αλλά μειωμένη δραστικά αν το ratio δεν είναι αξιόπιστο (λίγα/ασταθή δεδομένα)
        base_weight = min(0.35, sales_time_pct * 0.45)
        pacing_weight = base_weight if pacing_reliable else base_weight * 0.35

    # --- BASELINE FORECAST ---
    expected_remaining = float(np.sum(member_probs * member_pred_vals))
    baseline_forecast = total_billed_net + val_pros_timologisi * 0.92 + expected_remaining

    # --- MONTE CARLO SIMULATION ---
    if not is_closed and n_remaining > 0:
        n_sims = 5000

        # === ΔΙΟΡΘΩΣΗ: η τελευταία μέρα φέρνει ΠΕΡΙΣΣΟΤΕΡΑ ΑΤΟΜΑ που παραγγέλνουν,
        # ΟΧΙ μεγαλύτερο καλάθι ανά άτομο. Το παλιό push_factor πολλαπλασίαζε το ΠΟΣΟ
        # (adjusted_vals = member_pred_vals × push_factor) κατά έως +39%, πράγμα λάθος —
        # φούσκωνε τεχνητά κάθε μεμονωμένη παραγγελία. Η σωστή προσέγγιση είναι να
        # αυξήσουμε την ΠΙΘΑΝΟΤΗΤΑ παραγγελίας (member_probs), όχι το ποσό.
        prob_boost = 0.0
        if is_final_day:
            hours_in_day = 24.0
            hour_progress = min(1.0, max(0.0, 1.0 - (hours_left_precise / hours_in_day)))
            # Στην αρχή της τελευταίας μέρας μεγαλύτερη αναμενόμενη ώθηση πιθανότητας
            prob_boost = avg_last_day_actives_pct * (1.0 - hour_progress * 0.4)
        elif days_left <= 1:
            prob_boost = avg_last_day_actives_pct * 0.5
        elif days_left <= 4:
            prob_boost = 0.04
        elif days_left <= 8:
            prob_boost = 0.02

        # Αυξάνουμε την πιθανότητα παραγγελίας (καπαρισμένη στο 1.0), ΟΧΙ το ποσό ανά παραγγελία
        boosted_probs = np.minimum(1.0, member_probs * (1.0 + prob_boost))
        adjusted_vals = member_pred_vals  # το ποσό ανά παραγγελία ΔΕΝ αλλάζει

        order_decisions = np.random.random((n_sims, n_remaining)) < boosted_probs
        order_amounts = np.maximum(0, np.random.normal(
            adjusted_vals, member_pred_stds, (n_sims, n_remaining)
        ))
        sim_remaining = (order_decisions * order_amounts).sum(axis=1)
        pending_factors = np.random.uniform(0.88, 0.98, n_sims)
        mc_results = total_billed_net + val_pros_timologisi * pending_factors + sim_remaining

        # === BAYESIAN 3-WAY BLEND ===
        data_trust = min(0.75, time_passed_ratio * 1.1)
        hist_trust = max(0.15, (1.0 - data_trust) * 0.6)
        pacing_w   = min(pacing_weight, 1.0 - data_trust - hist_trust)
        total_w = data_trust + hist_trust + pacing_w
        data_trust /= total_w
        hist_trust /= total_w
        pacing_w   /= total_w

        if historical_avg_total > 0:
            hist_sim = np.random.normal(historical_avg_total, historical_std_total, n_sims)
        else:
            hist_sim = mc_results

        if pacing_forecast > 0 and pacing_weight > 0:
            pacing_std = pacing_forecast * historical_cv
            pacing_sim = np.random.normal(pacing_forecast, pacing_std, n_sims)
            results = mc_results * data_trust + hist_sim * hist_trust + pacing_sim * pacing_w
        else:
            results = mc_results * data_trust + hist_sim * hist_trust

        # === ENSEMBLE: κρατάμε τα 3 μοντέλα ξεχωριστά ===
        ens_mc_p50      = float(np.percentile(mc_results, 50))
        ens_mc_p25      = float(np.percentile(mc_results, 25))
        ens_mc_p75      = float(np.percentile(mc_results, 75))

        ens_hist_p50    = float(np.percentile(hist_sim, 50))
        ens_hist_p25    = float(np.percentile(hist_sim, 25))
        ens_hist_p75    = float(np.percentile(hist_sim, 75))

        ens_pacing_p50  = float(pacing_forecast) if pacing_forecast > 0 else ens_mc_p50
        ens_pacing_std  = ens_pacing_p50 * historical_cv
        ens_pacing_p25  = max(total_billed_net, ens_pacing_p50 - ens_pacing_std)
        ens_pacing_p75  = ens_pacing_p50 + ens_pacing_std

        # === ΙΣΧΥΡΟ ΕΜΠΕΙΡΙΚΟ ΚΑΤΩΦΛΙ — εφαρμόζεται ΑΠΕΥΘΕΙΑΣ σε κάθε μοντέλο ===
        # Αν η καμπάνια δεν έχει ΠΟΤΕ κλείσει κάτω από ένα όριο ιστορικά, ΚΑΝΕΝΑ
        # μεμονωμένο μοντέλο (Ιστορικό Trend, Pacing) δεν πρέπει να δείχνει
        # χαμηλότερο νούμερο — όχι μόνο το τελικό Ensemble. Το κατώφλι είναι στο
        # 95% του ιστορικού ελαχίστου (σχεδόν hard floor, μικρό περιθώριο μόνο
        # για πραγματικά ασυνήθιστες καταστάσεις).
        if hist_totals and len(hist_totals) >= 2:
            _hist_min_floor = min(hist_totals) * 0.95
            if ens_hist_p50 < _hist_min_floor:
                _shift = _hist_min_floor - ens_hist_p50
                ens_hist_p50 += _shift
                ens_hist_p25 += _shift
                ens_hist_p75 += _shift
            if ens_pacing_p50 < _hist_min_floor:
                _shift = _hist_min_floor - ens_pacing_p50
                ens_pacing_p50 += _shift
                ens_pacing_p25 += _shift
                ens_pacing_p75 += _shift

        # Βάρη (για εμφάνιση)
        ens_weights = {'MC': round(data_trust * 100), 'Hist': round(hist_trust * 100),
                       'Pacing': round(pacing_w * 100)}

        # Συμφωνία μοντέλων — πόσο διαφέρουν μεταξύ τους
        ens_values  = [ens_mc_p50, ens_hist_p50, ens_pacing_p50]
        ens_spread  = (max(ens_values) - min(ens_values)) / max(1, np.mean(ens_values)) * 100
        if ens_spread < 5:
            ens_agreement = ("🟢", "Υψηλή συμφωνία", f"Διαφορά {ens_spread:.1f}% — εμπιστευτείτε την πρόβλεψη")
        elif ens_spread < 15:
            ens_agreement = ("🟡", "Μέτρια συμφωνία", f"Διαφορά {ens_spread:.1f}% — εύλογη αβεβαιότητα")
        else:
            ens_agreement = ("🔴", "Χαμηλή συμφωνία", f"Διαφορά {ens_spread:.1f}% — τα μοντέλα διαφωνούν")

        # === MAPE-calibrated confidence intervals ===
        mape_factor = 1.0 + historical_mape
        raw_p15 = float(np.percentile(results, 15))
        raw_p85 = float(np.percentile(results, 85))
        raw_p98 = float(np.percentile(results, 98))

        # === ΔΙΟΡΘΩΣΗ: το κεντρικό estimate είναι ΠΑΝΤΑ ο διαφανής σταθμισμένος
        # συνδυασμός των 3 point estimates (ens_mc_p50/ens_hist_p50/ens_pacing_p50),
        # ΟΧΙ percentile(weighted_sum_array, 50). Αυτά τα δύο ΔΕΝ είναι μαθηματικά
        # ισοδύναμα όταν οι κατανομές έχουν διαφορετική ασυμμετρία (το Monte Carlo
        # array είναι δεξιά-ασύμμετρο λόγω των per-member Bernoulli αποφάσεων),
        # πράγμα που προκαλούσε συστηματική, αδιαφανή υποεκτίμηση του Ensemble
        # σε σχέση με ό,τι θα περίμενε κανείς κοιτώντας τα 3 εμφανιζόμενα νούμερα.
        weighted_point_estimate = data_trust * ens_mc_p50 + hist_trust * ens_hist_p50 + pacing_w * ens_pacing_p50
        raw_p50 = weighted_point_estimate

        half_width = (raw_p85 - raw_p15) / 2.0 * mape_factor
        pred_pessimistic  = max(total_billed_net, raw_p50 - half_width)
        pred_realistic    = raw_p50
        pred_optimistic   = raw_p50 + half_width
        pred_max_potential = raw_p98 * mape_factor

        final_forecast = pred_realistic

    elif not is_closed:
        # Δεν υπάρχουν μη-παραγγείλαντα μέλη — forecast = τρέχοντα + pending
        final_forecast = total_billed_net + val_pros_timologisi * 0.92
        pred_pessimistic = final_forecast * 0.95
        pred_realistic = final_forecast
        pred_optimistic = final_forecast * 1.05
        pred_max_potential = final_forecast * 1.10
        # Ensemble fallback
        ens_mc_p50 = ens_hist_p50 = ens_pacing_p50 = final_forecast
        ens_mc_p25 = ens_hist_p25 = ens_pacing_p25 = final_forecast * 0.95
        ens_mc_p75 = ens_hist_p75 = ens_pacing_p75 = final_forecast * 1.05
        ens_weights = {'MC': 34, 'Hist': 33, 'Pacing': 33}
        ens_agreement = ("🟡", "Χωρίς εκκρεμείς", "Όλα τα μέλη έχουν παραγγείλει")
        data_trust = 0.0
        hist_trust = 0.0
        pacing_w = 0.0
        sales_time_pct = None
        pacing_reliable = False
    else:
        # Η καμπάνια όντως έκλεισε (πέρασε η ώρα 15:00 της τελευταίας ημέρας) — τελικό αποτέλεσμα
        final_forecast = total_billed_net + val_pros_timologisi * 0.95
        pred_pessimistic = pred_realistic = pred_optimistic = pred_max_potential = final_forecast
        ens_mc_p50 = ens_hist_p50 = ens_pacing_p50 = final_forecast
        ens_mc_p25 = ens_hist_p25 = ens_pacing_p25 = final_forecast
        ens_mc_p75 = ens_hist_p75 = ens_pacing_p75 = final_forecast
        ens_weights = {'MC': 34, 'Hist': 33, 'Pacing': 33}
        ens_agreement = ("⚫", "Καμπάνια έκλεισε", "Τελικό αποτέλεσμα")
        # Ορισμός για το diagnostic panel — δεν τρέχει το Bayesian blend όταν η καμπάνια έκλεισε
        data_trust = 0.0
        hist_trust = 0.0
        pacing_w = 0.0
        sales_time_pct = None
        pacing_reliable = False

    # daily_required: όσο η καμπάνια είναι ανοιχτή, χρησιμοποιεί fractional days (precise)
    daily_required = remaining_to_target / max(days_left_precise, 1/24) if not is_closed else remaining_to_target

    # Feature 3: αποθήκευση ημερήσιας πρόβλεψης
    # Feature 5: Εφαρμογή calibration factor από προηγούμενες καμπάνιες
    if calibration_factor != 1.0 and not is_closed:
        final_forecast = final_forecast * calibration_factor
        pred_pessimistic = pred_pessimistic * calibration_factor
        pred_optimistic  = pred_optimistic  * calibration_factor

    # === ΕΜΠΕΙΡΙΚΟ ΚΑΤΩΦΛΙ ΑΣΦΑΛΕΙΑΣ ===
    # Η πρόβλεψη δεν πρέπει ποτέ να πέφτει κάτω από ό,τι έχει ήδη συμβεί ιστορικά —
    # αν η καμπάνια ΠΟΤΕ δεν έχει κλείσει κάτω από ένα όριο, ούτε η πρόβλεψη πρέπει
    # να δείχνει τόσο χαμηλό νούμερο. Ίδιο αυστηρό όριο (95%) με αυτό που εφαρμόζεται
    # ήδη στα Ιστορικό Trend / Pacing bars, για συνέπεια σε όλο το Ensemble.
    if not is_closed and hist_totals and len(hist_totals) >= 2:
        historical_min_total = min(hist_totals)
        floor_value = historical_min_total * 0.95
        if final_forecast < floor_value:
            final_forecast = floor_value
            pred_pessimistic = max(pred_pessimistic, floor_value * 0.92)
            pred_optimistic = max(pred_optimistic, floor_value * 1.08)

    save_daily_forecast(selected_camp, final_forecast)
    forecast_history = get_forecast_history(selected_camp)

    # Feature 5: Υπολόγισε calibration από ιστορικές καμπάνιες αν υπάρχει forecast history
    hist_calibrations = []
    for ck in hist_camp_sorted:
        fh = get_forecast_history(ck)
        actual = campaign_stats.get(ck, {}).get('total_net', 0)
        if fh and actual > 0:
            # Τελευταία πρόβλεψη D-1 vs τελικό αποτέλεσμα
            last_date = sorted(fh.keys())[-1]
            last_pred = fh[last_date]
            if last_pred > 0:
                hist_calibrations.append(actual / last_pred)
    if len(hist_calibrations) >= 2:
        new_calib = float(np.mean(hist_calibrations[-3:]))  # avg τελευταίων 3
        # Sanity clamp: ποτέ πάνω από ±25% διόρθωση. Χωρίς αυτό, ένα και μόνο
        # παλιό (buggy) forecast snapshot μπορεί να «δηλητηριάσει» μόνιμα όλες
        # τις μελλοντικές προβλέψεις με ακραία διόρθωση.
        new_calib = max(0.75, min(1.25, new_calib))
        if abs(new_calib - calibration_factor) > 0.02:      # αλλάζει μόνο αν διαφέρει >2%
            save_calibration(new_calib)

    # Εκτίμηση αναγκαίων ατόμων (blend ιστορικού basket + τρέχοντος)
    if unique_orders_count > 5:
        current_trend_avg = total_billed_net / unique_orders_count
        final_avg_basket_estimator = (historical_avg_basket * 0.5) + (current_trend_avg * 0.5)
    elif historical_avg_basket > 0:
        final_avg_basket_estimator = historical_avg_basket
    else:
        final_avg_basket_estimator = global_avg_basket
    orders_needed = round(remaining_to_target / final_avg_basket_estimator) if final_avg_basket_estimator > 0 else 0

    # --- CONFIDENCE SCORE ---
    conf_data_pct = min(1.0, days_passed / max(1, campaign_duration_est))
    conf_members_pct = len(names_with_any_order) / max(1, total_members_count)
    n_hist_campaigns = len(campaign_stats)

    if conf_data_pct > 0.5 and conf_members_pct > 0.30 and n_hist_campaigns >= 2:
        confidence_emoji = "🟢"
        confidence_text = "Υψηλή"
        confidence_detail = f"{days_passed}η μέρα, {conf_members_pct:.0%} μέλη ενεργά, {n_hist_campaigns} ιστ. καμπάνιες"
    elif conf_data_pct > 0.20 or conf_members_pct > 0.15:
        confidence_emoji = "🟡"
        confidence_text = "Μέτρια"
        confidence_detail = f"{days_passed}η μέρα, {conf_members_pct:.0%} μέλη ενεργά, {n_hist_campaigns} ιστ. καμπάνιες"
    else:
        confidence_emoji = "🔴"
        confidence_text = "Χαμηλή"
        confidence_detail = f"Λίγα δεδομένα ({days_passed}η μέρα, {conf_members_pct:.0%} μέλη)"

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 Smart Alerts")
    alerts = []
    
    # Alert 1: VIP missing
    missing_vip_count = len(df_members_raw[
        (~df_members_raw['NameClean'].isin(names_with_any_order)) &
        (df_members_raw['Tier'].isin(['DIAMOND', 'PLATINUM', 'GOLD']))
    ])
    if missing_vip_count > 0:
        if is_assistant_mode:
            alerts.append(("🚨", f"**{missing_vip_count} VIP** δεν έχουν παραγγείλει", "error"))
        else:
            missing_vip_value = sum(
                get_manual_fallback(n) for n in
                df_members_raw[~df_members_raw['NameClean'].isin(names_with_any_order) &
                               df_members_raw['Tier'].isin(['DIAMOND', 'PLATINUM', 'GOLD'])]['Ονοματεπώνυμο']
            )
            alerts.append(("🚨", f"**{missing_vip_count} VIP** δεν έχουν παραγγείλει — χάνεις ~{missing_vip_value:,.0f}€", "error"))
    
    # Alert 2: Pace vs prev campaign (same-day comparison) — δεν αφορά ποσά/στόχο, ασφαλές
    if mom_sales_delta < -10:
        alerts.append(("📉", f"Ρυθμός **{abs(mom_sales_delta):.0f}% χαμηλότερος** από {prev_camp_label}", "warning"))
    elif mom_sales_delta > 10:
        alerts.append(("📈", f"Ρυθμός **{mom_sales_delta:.0f}% υψηλότερος** από {prev_camp_label}", "success"))
    
    # Alert 3: Daily burn rate — αφορά αποκλειστικά τον στόχο, κρύβεται εντελώς
    if not is_closed and not is_assistant_mode:
        feasibility = daily_required / max(1, total_billed_net / max(1, days_passed))
        if feasibility > 2.0:
            alerts.append(("🔥", f"Χρειάζεσαι **{daily_required:,.0f}€/μέρα** — {feasibility:.1f}× τον τρέχοντα ρυθμό!", "error"))
        elif feasibility > 1.2:
            alerts.append(("⚡", f"Χρειάζεσαι **{daily_required:,.0f}€/μέρα** — αυξημένος ρυθμός", "warning"))
    
    # Alert 4: Forecast vs target — αφορά αποκλειστικά τον στόχο, κρύβεται εντελώς
    if not is_assistant_mode:
        if final_forecast < target_val * 0.90:
            gap = target_val - final_forecast
            alerts.append(("⚠️", f"Πρόβλεψη **{gap:,.0f}€ κάτω** από τον στόχο", "warning"))
        elif final_forecast >= target_val:
            alerts.append(("✅", f"Στόχος **ασφαλισμένος** — πρόβλεψη +{final_forecast - target_val:,.0f}€", "success"))

    # Alert 5: Actives στόχος — αφορά τον στόχο, κρύβεται εντελώς
    if goal_actives > 0 and not is_assistant_mode:
        gap_act = goal_actives - unique_orders_count
        if gap_act > 0:
            pct_act = unique_orders_count / goal_actives * 100
            level_act = "error" if pct_act < 50 else "warning"
            alerts.append(("👥", f"Actives: **{unique_orders_count}/{goal_actives}** — χρειάζονται {gap_act} ακόμα", level_act))
        else:
            alerts.append(("✅", f"Στόχος Actives **επιτεύχθηκε** ({unique_orders_count}/{goal_actives})", "success"))

    # Alert 6: Feature 6 — "Σιωπηλά VIP" (απόντα σε πολλαπλές καμπάνιες) — δεν αφορά ποσά, ασφαλές
    silent_vips = []
    for _, row in df_members_raw[df_members_raw['Tier'].isin(['DIAMOND','PLATINUM'])].iterrows():
        n = row['NameClean']
        if n in names_with_any_order:
            continue
        absent_count = sum(1 for ck in hist_camp_sorted
                           if n not in set(df_sales_all[df_sales_all[camp_col]==ck]['NameClean']))
        if absent_count >= 2:
            silent_vips.append((row['Ονοματεπώνυμο'], absent_count, row.get('TelClean')))
    if silent_vips:
        silent_vips.sort(key=lambda x: -x[1])
        names_str = ", ".join(f"{n} ({c} καμπ.)" for n,c,_ in silent_vips[:3])
        alerts.append(("🔇", f"**Σιωπηλά VIP:** {names_str} — πιθανή οριστική απώλεια", "error"))
    
    # Alert 5: High value churners — δεν αναφέρει ποσά ρητά, ασφαλές
    churners = [name for name in names_not_ordered
                if member_predictions.get(name, {}).get('predicted', 0) > 150
                and member_predictions.get(name, {}).get('ml_prob', 1) < 0.25]
    if churners:
        alerts.append(("💔", f"**{len(churners)} πελάτες** υψηλής αξίας σε κίνδυνο χαμηλής πιθανότητας", "warning"))
    
    if not alerts:
        st.sidebar.success("✅ Όλα καλά! Δεν υπάρχουν alerts.")
    for emoji, msg, level in alerts:
        if level == "error":
            st.sidebar.error(f"{emoji} {msg}")
        elif level == "warning":
            st.sidebar.warning(f"{emoji} {msg}")
        else:
            st.sidebar.success(f"{emoji} {msg}")

    # Feature 10: Ανίχνευση "Κοντά στον Στόχο"
    near_target_threshold = min(500.0, target_val * 0.03) if target_val > 0 else 500.0
    is_near_target  = 0 < remaining_to_target <= near_target_threshold
    is_target_hit   = remaining_to_target <= 0 and target_val > 0

    # ==========================================
    # 5. UI RENDER
    # ==========================================

    st.title(f"🛡️ Strategic AI Command Center - {selected_camp}")

    if is_assistant_mode:
        _greet_name = f" {assistant_name}" if assistant_name else ""
        st.markdown(
            f"<div style='padding:14px 20px;border-radius:12px;"
            f"background:linear-gradient(135deg, rgba(255,105,180,0.15) 0%, rgba(115,96,242,0.15) 100%);"
            f"border:1px solid rgba(255,105,180,0.3);margin-bottom:16px;'>"
            f"<span style='font-size:20px;font-weight:700;color:#ffffff;'>👋 {get_time_greeting()}{_greet_name}!</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # ==========================================
    # DATA HEALTH CHECK — εντοπίζει προβλήματα ποιότητας δεδομένων
    # ΠΡΙΝ επηρεάσουν την πρόβλεψη, αντί να τα ανακαλύπτεις μέσα από debug panels
    # ==========================================
    health_issues = []
    health_ok = []

    if date_col and '_OrderDate' in df_sales_all.columns:
        health_ok.append("Στήλη ημερομηνίας εντοπίστηκε — same-day σύγκριση και last-day rush factor λειτουργούν με ακρίβεια.")
    else:
        health_issues.append(("⚠️", "Δεν βρέθηκε στήλη ημερομηνίας στο Φύλλο 1 — το pacing model και το last-day rush factor χρησιμοποιούν εκτιμήσεις αντί για πραγματικά δεδομένα."))

    unknown_status_count = len(df_curr[~(billed_status_mask | pending_system_mask)])
    if unknown_status_count > 0:
        health_issues.append(("⚠️", f"{unknown_status_count} γραμμές στην τρέχουσα καμπάνια έχουν status εκτός των αναγνωρισμένων κατηγοριών (Τιμολογημένη/Προς Τιμολόγηση) — δεν προσμετρώνται πουθενά."))
    else:
        health_ok.append("Όλες οι γραμμές της τρέχουσας καμπάνιας έχουν αναγνωρισμένο status.")

    unknown_tier_count = len(df_members_raw[df_members_raw['Tier'] == 'STANDARD'])
    if unknown_tier_count > len(df_members_raw) * 0.3:
        health_issues.append(("ℹ️", f"{unknown_tier_count} μέλη ({unknown_tier_count/max(1,len(df_members_raw)):.0%}) δεν έχουν αναγνωρισμένο tier στο όνομά τους — υπολογίζονται με default εκτιμήσεις."))

    no_history_but_ordered = sum(1 for n in real_billed_names if not history_detailed.get(n))
    if no_history_but_ordered > len(real_billed_names) * 0.4 and len(real_billed_names) > 20:
        health_issues.append(("ℹ️", f"{no_history_but_ordered} από τα ενεργά μέλη δεν έχουν καθόλου ιστορικό μέσα στο διαθέσιμο παράθυρο ({len(historical_camps)} καμπάνιες) — οι προβλέψεις τους βασίζονται σε tier fallback."))

    if len(historical_camps) < 3:
        health_issues.append(("⚠️", f"Μόνο {len(historical_camps)} ιστορικές καμπάνιες διαθέσιμες — οι περισσότερες λειτουργίες σύγκρισης (Additions, Cohort, Ensemble) χρειάζονται τουλάχιστον 3 για αξιόπιστα αποτελέσματα."))
    else:
        health_ok.append(f"{len(historical_camps)} ιστορικές καμπάνιες διαθέσιμες — αρκετό δείγμα για αξιόπιστες συγκρίσεις.")

    # === Εντοπισμός "κολλημένων" ονομάτων (συγχώνευση δύο λέξεων χωρίς κενό) ===
    # Συνήθως προκύπτει από merged cells ή διπλή γραμμή κειμένου στο Excel που
    # διαβάστηκε ως ένα ενιαίο string χωρίς διαχωριστικό — π.χ. "ΣΤΥΛΙΑΝΟΥΚΑΜΤΣ".
    # Τυπικά ελληνικά επώνυμα/ονόματα σπάνια ξεπερνούν τα ~13-14 χαρακτήρες·
    # ένα ενιαίο token πάνω από αυτό το όριο είναι ύποπτο για συγχώνευση.
    SUSPICIOUS_TOKEN_LEN = 14
    suspicious_names = []
    for _, mrow in df_members_raw.iterrows():
        raw_nm = str(mrow.get('Ονοματεπώνυμο', ''))
        clean_nm = remove_accents(raw_nm).upper()
        clean_nm = re.sub(r'[^Α-ΩA-Z\s]', '', clean_nm)
        for tok in clean_nm.split():
            if len(tok) > SUSPICIOUS_TOKEN_LEN:
                suspicious_names.append(raw_nm)
                break
    if suspicious_names:
        sample = ", ".join(suspicious_names[:5])
        more = f" (+{len(suspicious_names)-5} ακόμα)" if len(suspicious_names) > 5 else ""
        health_issues.append(("🔤", f"{len(suspicious_names)} ονόματα φαίνονται «κολλημένα» χωρίς κενό (πιθανό merged-cell πρόβλημα στο Excel): {sample}{more}. Αυτά τα μέλη πιθανόν δεν ταυτοποιούνται σωστά με το ιστορικό ή τις αναφορές της εταιρείας."))

    if fuzzy_name_matches:
        fm_lines = [f"«{name_to_original.get(a, a)}» (Φύλλο4) ≈ «{b}» (Φύλλο1)" for a, b in list(fuzzy_name_matches.items())[:8]]
        more_fm = f" (+{len(fuzzy_name_matches)-8} ακόμα)" if len(fuzzy_name_matches) > 8 else ""
        health_issues.append((
            "🔗",
            f"{len(fuzzy_name_matches)} μέλη ταυτοποιήθηκαν με ελαφρώς διαφορετική γραφή ονόματος "
            f"ανάμεσα σε Φύλλο1 και Φύλλο4 (fuzzy matching): {'; '.join(fm_lines)}{more_fm}. "
            f"Έλεγξε ότι πρόκειται όντως για το ίδιο άτομο — αν όχι, διόρθωσε τη γραφή στο πρωτότυπο αρχείο."
        ))

    if health_issues:
        with st.expander(f"🩺 Data Health Check — {len(health_issues)} σημεία προσοχής", expanded=False):
            for icon, msg in health_issues:
                st.markdown(f"{icon} {msg}")
            if health_ok:
                st.markdown("---")
                for msg in health_ok:
                    st.markdown(f"✅ {msg}")
    else:
        with st.expander("🩺 Data Health Check — όλα εντάξει ✅", expanded=False):
            for msg in health_ok:
                st.markdown(f"✅ {msg}")

    if not is_assistant_mode:
        # Feature 10: Near-target banner / confetti
        if is_target_hit:
            st.balloons()
            st.markdown('<div class="near-target-banner">🏆 ΣΤΟΧΟΣ ΕΠΙΤΕΥΧΘΗΚΕ! Συγχαρητήρια! 🎉</div>', unsafe_allow_html=True)
        elif is_near_target:
            st.markdown(f'<div class="near-target-banner">⚡ ΤΕΛΙΚΟ PUSH — Απομένουν μόνο {remaining_to_target:,.0f}€ για τον στόχο!</div>', unsafe_allow_html=True)

        # Feature 3: Post-Campaign Summary mode — μόνο όταν ΟΝΤΩΣ έκλεισε στις 15:00
        if is_closed and total_billed_net > 0:
            achievement_pct = total_billed_net / max(1, target_val) * 100 if target_val > 0 else 0
            never_ordered   = df_members_raw[~df_members_raw['NameClean'].isin(names_with_any_order)]
            vip_never       = never_ordered[never_ordered['Tier'].isin(['DIAMOND','PLATINUM','GOLD'])]
            calib_note = f" (Calibration factor: ×{calibration_factor:.2f})" if calibration_factor != 1.0 else ""
            st.markdown(f"""
            <div class="post-campaign-box">
                <h2 style='color:#10b981;margin:0'>📊 Post-Campaign Summary — {selected_camp}</h2>
                <p style='font-size:1.1em;margin:10px 0'>
                    Τελικές Πωλήσεις: <b style='color:#ff69b4'>{total_billed_net:,.0f}€</b>
                    &nbsp;|&nbsp; Στόχος: <b>{target_val:,.0f}€</b>
                    &nbsp;|&nbsp; Επίτευξη: <b style='color:{"#10b981" if achievement_pct>=100 else "#ffc107"}'>{achievement_pct:.1f}%</b>
                </p>
                <p style='color:#94a3b8;font-size:0.9em'>
                    Ενεργά Μέλη: {unique_orders_count} &nbsp;|&nbsp;
                    Δεν παρήγγειλαν ποτέ: {len(never_ordered)} μέλη
                    {f"&nbsp;|&nbsp; VIP που χάθηκαν: {len(vip_never)}" if len(vip_never)>0 else ""}
                    {calib_note}
                </p>
            </div>
            """, unsafe_allow_html=True)
            if not vip_never.empty:
                st.warning(f"🚨 **VIP που δεν παρήγγειλαν ποτέ:** {', '.join(vip_never['Ονοματεπώνυμο'].head(10).tolist())}")
    
        # ======================================================
        # LAST-DAY RUSH BANNER — countdown & ιστορική ώθηση
        # ======================================================
        if is_final_day and not is_closed:
            h_left = int(hours_left_precise)
            m_left = int((hours_left_precise - h_left) * 60)
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#ff6b35 0%,#d63384 100%);
                        border-radius:12px;padding:14px 20px;margin-bottom:14px;
                        box-shadow:0 4px 20px rgba(214,51,132,0.4);'>
                <p style='margin:0;color:white;font-size:16px;font-weight:bold;'>
                    🔥 ΤΕΛΕΥΤΑΙΑ ΗΜΕΡΑ — Κλείνει στις 15:00 ({h_left}ω {m_left}λ απομένουν)
                </p>
                <p style='margin:4px 0 0;color:white;font-size:13px;opacity:0.9;'>
                    Ιστορικά, η τελευταία μέρα φέρνει <b>~{avg_last_day_sales_pct:.0%}</b> των συνολικών πωλήσεων
                    και <b>~{avg_last_day_actives_pct:.0%}</b> των ενεργών μελών
                    {'(βάσει πραγματικών ημερομηνιών)' if has_last_day_data else '(εκτίμηση — πρόσθεσε στήλη ημερομηνίας για ακρίβεια)'}.
                    Αναμενόμενο boost σήμερα: <b>+{avg_last_day_sales_pct * total_billed_net:,.0f}€</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif is_closed:
            st.markdown(f"""
            <div style='background:#2d2d3d;border-radius:12px;padding:12px 20px;margin-bottom:14px;border:1px solid #444;'>
                <p style='margin:0;color:#aaa;font-size:14px;'>⚫ Η καμπάνια έκλεισε στις 15:00. Τα παρακάτω είναι τα τελικά αποτελέσματα.</p>
            </div>
            """, unsafe_allow_html=True)
        elif days_left <= 2 and days_left > 0:
            st.markdown(f"""
            <div style='background:#3d2d1d;border-radius:10px;padding:10px 18px;margin-bottom:14px;border:1px solid #ffc107;'>
                <p style='margin:0;color:#ffc107;font-size:13px;'>
                    ⏰ {days_left} μέρες απομένουν. Η τελευταία μέρα ιστορικά φέρνει ~{avg_last_day_sales_pct:.0%} των πωλήσεων — κρατήστε δύναμη για το τελικό push.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================
        # ENSEMBLE FORECAST PANEL — 3 μοντέλα ξεχωριστά
        # ======================================================
        st.markdown("### 🔮 Ensemble Forecast")

        # === DIAGNOSTIC PANEL — εντοπισμός πηγής απόκλισης Monte Carlo ===
        with st.expander("🔬 Διαγνωστικά Monte Carlo (debug)", expanded=False):
            d1, d2, d3 = st.columns(3)
            d1.metric("Εναπομείναντα μέλη", f"{n_remaining}")
            d1.metric("Σύνολο μελών", f"{total_members_count}")
            d2.metric("Μ.Ο. Πιθανότητας", f"{float(np.mean(member_probs)):.1%}" if n_remaining > 0 else "—")
            d2.metric("Μ.Ο. Πρόβλεψης/μέλος", f"{float(np.mean(member_pred_vals)):,.0f}€" if n_remaining > 0 else "—")
            d3.metric("Άθροισμα Expected (Σp×v)", f"{float(np.sum(member_probs * member_pred_vals)):,.0f}€" if n_remaining > 0 else "—")
            d3.metric("time_passed_ratio", f"{time_passed_ratio:.2f}")
            _dt = locals().get('data_trust', 0.0)
            _ht = locals().get('hist_trust', 0.0)
            _pw = locals().get('pacing_w', 0.0)
            _stp = locals().get('sales_time_pct', None)
            _pr = locals().get('pacing_reliable', False)
            st.caption(
                f"total_billed_net={total_billed_net:,.0f}€ | val_pros_timologisi={val_pros_timologisi:,.0f}€ | "
                f"days_passed={days_passed} | days_left={days_left} | is_final_day={is_final_day} | is_closed={is_closed} | "
                f"data_trust={_dt:.2f} | hist_trust={_ht:.2f} | pacing_w={_pw:.2f} | "
                f"sales_time_pct={_stp if _stp else 'N/A'} | pacing_reliable={_pr}"
            )
            st.caption(
                (
                    f"📊 hist_totals (τελικά σύνολα ιστορικών καμπανιών, με τη σειρά): "
                    f"{[f'{v:,.0f}€' for v in hist_totals]} | "
                    f"historical_avg_total={historical_avg_total:,.0f}€ | historical_min={min(hist_totals):,.0f}€"
                ) if hist_totals else "📊 hist_totals: (κενό — καμία ιστορική καμπάνια δεν εντοπίστηκε)"
            )
            if n_remaining > 0:
                top10_idx = np.argsort(-member_probs * member_pred_vals)[:10]
                debug_rows = []
                for i in top10_idx:
                    debug_rows.append({
                        'Μέλος': name_to_original.get(names_not_ordered[i], names_not_ordered[i]),
                        'Πιθανότητα': f"{member_probs[i]:.1%}",
                        'Πρόβλεψη €': f"{member_pred_vals[i]:,.0f}",
                        'Expected €': f"{member_probs[i]*member_pred_vals[i]:,.0f}"
                    })
                st.markdown("**Top 10 συνεισφορά στο expected remaining:**")
                st.dataframe(pd.DataFrame(debug_rows), use_container_width=True, hide_index=True)

        # Σειρά agreement indicator
        agr_icon, agr_label, agr_detail = ens_agreement
        st.markdown(
            f"<div style='padding:8px 14px;border-radius:8px;background:var(--surface-1,#1e1e2e);"
            f"border:1px solid #333;margin-bottom:10px;font-size:13px;'>"
            f"{agr_icon} <b>Συμφωνία μοντέλων:</b> {agr_label} — {agr_detail}"
            f"</div>",
            unsafe_allow_html=True
        )

        # Automatic Sanity Alert — όταν η συμφωνία είναι χαμηλή, δίνουμε συγκεκριμένη
        # προτεινόμενη ενέργεια αντί για απλή προειδοποίηση χωρίς καθοδήγηση
        if agr_icon == "🔴":
            suggestions = []
            if not (date_col and '_OrderDate' in df_sales_all.columns):
                suggestions.append("Πρόσθεσε στήλη ημερομηνίας στο Φύλλο 1 — το Pacing Model λειτουργεί χωρίς αυτήν σε λιγότερο ακριβή λειτουργία.")
            if len(historical_camps) < 3:
                suggestions.append("Χρειάζονται τουλάχιστον 3 ιστορικές καμπάνιες για αξιόπιστο Historical Trend.")
            if not suggestions:
                suggestions.append("Άνοιξε το '🔬 Διαγνωστικά Monte Carlo' παραπάνω για να δεις ποιο μοντέλο αποκλίνει και γιατί.")
            st.markdown(
                "<div style='padding:10px 14px;border-radius:8px;background:#3d1d1d;"
                "border:1px solid #dc3545;margin-bottom:10px;font-size:13px;'>"
                "⚠️ <b>Χαμηλή συμφωνία μοντέλων εντοπίστηκε.</b> Προτεινόμενες ενέργειες:<br>"
                + "<br>".join(f"&nbsp;&nbsp;• {s}" for s in suggestions) +
                "</div>",
                unsafe_allow_html=True
            )

        ec1, ec2, ec3, ec4 = st.columns([2, 2, 2, 2])

        # Μοντέλο 1: Monte Carlo ML
        mc_delta = f"{(ens_mc_p50 - total_billed_net):+,.0f}€ vs τώρα"
        ec1.metric(
            label=f"🤖 Monte Carlo ML  ({ens_weights['MC']}%)",
            value=f"{ens_mc_p50:,.0f}€",
            delta=mc_delta,
            help=f"Βάσει ML πιθανοτήτων 5.000 προσομοιώσεων. Εύρος P25–P75: {ens_mc_p25:,.0f}–{ens_mc_p75:,.0f}€"
        )

        # Μοντέλο 2: Ιστορικό Trend
        hist_delta = f"{(ens_hist_p50 - total_billed_net):+,.0f}€ vs τώρα"
        ec2.metric(
            label=f"📊 Ιστορικό Trend  ({ens_weights['Hist']}%)",
            value=f"{ens_hist_p50:,.0f}€",
            delta=hist_delta,
            help=f"Βάσει EWMA ιστορικών καμπανιών. Εύρος P25–P75: {ens_hist_p25:,.0f}–{ens_hist_p75:,.0f}€"
        )

        # Μοντέλο 3: Pacing
        pac_delta = f"{(ens_pacing_p50 - total_billed_net):+,.0f}€ vs τώρα"
        stability_note = " | 🔒 Σταθεροποιημένο κοντά στο ιστορικό (νωρίς στον μήνα)" if (time_passed_ratio < 0.30 or not pacing_reliable) else ""
        ec3.metric(
            label=f"⚡ Pacing Model  ({ens_weights['Pacing']}%)",
            value=f"{ens_pacing_p50:,.0f}€",
            delta=pac_delta,
            help=f"Βάσει % πωλήσεων που ιστορικά έχει έρθει ΕΩΣ σήμερα. Εύρος: {ens_pacing_p25:,.0f}–{ens_pacing_p75:,.0f}€{stability_note}"
        )

        # Ensemble (blend)
        ens_delta = f"{(final_forecast - total_billed_net):+,.0f}€ vs τώρα"
        ec4.metric(
            label="✨ Ensemble (blend)",
            value=f"{final_forecast:,.0f}€",
            delta=ens_delta,
            help=f"Σταθμισμένος συνδυασμός και των 3 μοντέλων. Εύρος: {pred_pessimistic:,.0f}–{pred_optimistic:,.0f}€"
        )

        # Οπτικοποίηση — grouped bar chart των 3 μοντέλων με εύρη
        fig_ens = go.Figure()

        models  = ["Monte Carlo ML", "Ιστορικό Trend", "Pacing Model", "✨ Ensemble"]
        p50s    = [ens_mc_p50, ens_hist_p50, ens_pacing_p50, final_forecast]
        p25s    = [ens_mc_p25, ens_hist_p25, ens_pacing_p25, pred_pessimistic]
        p75s    = [ens_mc_p75, ens_hist_p75, ens_pacing_p75, pred_optimistic]
        colors  = ['#7360f2', '#00e5ff', '#ffc107', '#ff69b4']
        weights = [ens_weights['MC'], ens_weights['Hist'], ens_weights['Pacing'], 100]

        for i, (m, p50, p25, p75, col, w) in enumerate(zip(models, p50s, p25s, p75s, colors, weights)):
            # Error bar = P25–P75 εύρος
            err_minus = p50 - p25
            err_plus  = p75 - p50
            fig_ens.add_trace(go.Bar(
                name=m, x=[m], y=[p50],
                marker_color=col,
                error_y=dict(type='data', symmetric=False,
                             array=[err_plus], arrayminus=[err_minus],
                             color=col, thickness=2, width=8),
                text=[f"{p50:,.0f}€<br><span style='font-size:10px'>({w}%)</span>"],
                textposition='outside',
                width=0.5
            ))

        # Γραμμές αναφοράς
        fig_ens.add_hline(y=total_billed_net, line_dash='dot', line_color='#28a745',
                          annotation_text=f"Τρέχον {total_billed_net:,.0f}€",
                          annotation_position="top left",
                          annotation_font_color='#28a745')
        if target_val > 0:
            fig_ens.add_hline(y=target_val, line_dash='dash', line_color='#ffc107',
                              annotation_text=f"Στόχος {target_val:,.0f}€",
                              annotation_position="top right",
                              annotation_font_color='#ffc107')

        fig_ens.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=320,
            margin=dict(t=30, b=10, l=0, r=0),
            showlegend=False,
            yaxis=dict(title='Εκτιμώμενο Τελικό Σύνολο (€)'),
            bargap=0.3
        )
        st.plotly_chart(fig_ens, use_container_width=True)

        # Daily pace κάτω από το chart
        st.markdown(
            f"<div class='daily-box'>"
            f"<p style='margin:0;color:white;'>🎯 Στόχος Ημέρας: <b>{daily_required:,.0f}€</b>"
            f" &nbsp;|&nbsp; Ανάγκη: ~<b>{max(0,int(orders_needed))}</b> ενεργά άτομα"
            f" &nbsp;|&nbsp; Εύρος Ensemble: <b>{pred_pessimistic:,.0f}–{pred_optimistic:,.0f}€</b></p>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Feature 9: KPI vs καλύτερη καμπάνια
        if best_camp_total > 0:
            vs_best_pct = (total_billed_net - best_camp_total) / best_camp_total * 100
            best_note = f" | 🏅 vs Best ({best_camp_key}): {'↑' if vs_best_pct>0 else '↓'}{abs(vs_best_pct):.0f}% ({best_camp_total:,.0f}€)"
        else:
            best_note = ""

        # Confidence Score Bar
        margin_of_error_val = (pred_optimistic - pred_pessimistic) / 2.0
        margin_of_error_pct = (margin_of_error_val / final_forecast) if final_forecast > 0 else 0.0

        # Feature 5: Seasonality — εντοπισμός μήνα καμπάνιας & ιστορική σύγκριση ίδιου μήνα
        try:
            camp_month = int(str(selected_camp)[-2:])
            same_month_camps = [ck for ck in hist_camp_sorted if int(str(ck)[-2:]) == camp_month]
            same_month_totals = [campaign_stats[ck]['total_net'] for ck in same_month_camps if ck in campaign_stats]
            seasonality_note = ""
            if same_month_totals:
                same_month_avg = np.mean(same_month_totals)
                season_diff = (final_forecast - same_month_avg) / max(1, same_month_avg) * 100
                month_names = {1:'Ιαν',2:'Φεβ',3:'Μαρ',4:'Απρ',5:'Μαΐ',6:'Ιουν',
                               7:'Ιουλ',8:'Αυγ',9:'Σεπ',10:'Οκτ',11:'Νοε',12:'Δεκ'}
                mn = month_names.get(camp_month, str(camp_month))
                arrow = "↑" if season_diff > 0 else "↓"
                seasonality_note = f" | 📅 Εποχ. {mn}: {arrow}{abs(season_diff):.0f}% vs ίδιο μήνα ({same_month_avg:,.0f}€ ιστ. μ.ο.)"
        except Exception:
            seasonality_note = ""

        st.markdown(f"""
        <div class="confidence-box">
            <span>{confidence_emoji} Αξιοπιστία Πρόβλεψης: <b>{confidence_text}</b> — {confidence_detail}</span>
            <span>📉 Στατιστικό Σφάλμα (MoE): <b>± {margin_of_error_pct:.1%}</b></span>
            <span>📈 Ιστορικό Conv. Rate: <b>{historical_conversion_rate:.0%}</b></span>
            <span>🛒 Ιστ. Μ.Ο. Καλαθιού: <b>{historical_avg_basket:.0f}€</b>{seasonality_note}{best_note}</span>
        </div>
        """, unsafe_allow_html=True)

        progress_pct = min(100.0, (total_billed_net / target_val) * 100) if target_val > 0 else 0
        bar_color = "#d63384" if progress_pct < 80 else "#28a745"

        # Progress bars για όλους τους στόχους
        actives_pct   = min(100.0, unique_orders_count / max(1, goal_actives) * 100) if goal_actives > 0 else 0
        # Διαγραφές = μόνο όσοι από τη λίστα ΔΕΝ έχουν παραγγείλει (ίδια λογική με tab Διαγραφών)
        curr_removals = len(df_removals_raw[~df_removals_raw['NameClean'].isin(names_with_any_order)])

        st.markdown(f"**Πρόοδος Στόχου Πωλήσεων: {progress_pct:.1f}%**")
        st.markdown(f"""
            <div style="width:100%;background:#333;border-radius:10px;margin-bottom:8px;">
                <div style="width:{progress_pct}%;background:{bar_color};height:22px;border-radius:10px;"></div>
            </div>
        """, unsafe_allow_html=True)

        if goal_actives > 0:
            act_color = "#28a745" if actives_pct >= 80 else "#ffc107" if actives_pct >= 50 else "#dc3545"
            st.markdown(f"**Πρόοδος Actives: {unique_orders_count} / {goal_actives} ({actives_pct:.1f}%)**")
            st.markdown(f"""
                <div style="width:100%;background:#333;border-radius:10px;margin-bottom:18px;">
                    <div style="width:{actives_pct}%;background:{act_color};height:14px;border-radius:10px;"></div>
                </div>
            """, unsafe_allow_html=True)

        # Metrics row — ένα καθαρό row με όλα τα βασικά
        col_count = 4 + (1 if goal_actives > 0 else 0) + (1 if goal_removals > 0 else 0)
        met_cols = st.columns(col_count)
        ci = 0
        met_cols[ci].metric("💰 Πωλήσεις (Τιμολ.)", f"{total_billed_net:,.0f} €",
            delta=f"{mom_sales_delta:+.1f}% vs ίδια μέρα" if same_day_nets or prev_camp_key else None,
            help=f"Ιστορικό ΕΩΣ {today_day}η: {hist_same_day_net:,.0f}€" if same_day_nets else None)
        ci += 1
        met_cols[ci].metric("👥 Ενεργά Άτομα", f"{unique_orders_count}" + (f" / {goal_actives}" if goal_actives > 0 else ""),
            delta=f"{mom_members_delta:+d} vs ίδια μέρα" if same_day_nets or prev_camp_key else None)
        ci += 1
        met_cols[ci].metric("⏳ Προς Τιμολόγηση", f"{val_pros_timologisi:,.0f} €")
        ci += 1
        met_cols[ci].metric("📊 AI Forecast (P50)", f"{final_forecast:,.0f} €")
        ci += 1
        if goal_actives > 0:
            gap_actives = goal_actives - unique_orders_count
            met_cols[ci].metric("🎯 Gap Actives", f"{max(0, gap_actives)}",
                delta=f"{actives_pct:.0f}% ολοκληρώθηκε")
            ci += 1
        if goal_removals > 0:
            rem_diff = curr_removals - goal_removals
            if rem_diff > 0:
                rem_status = f"⚠️ +{rem_diff} πάνω από στόχο"
                rem_color = "#dc3545"
            elif rem_diff < 0:
                rem_status = f"✅ {abs(rem_diff)} κάτω από στόχο"
                rem_color = "#28a745"
            else:
                rem_status = "🎯 Ακριβώς στον στόχο"
                rem_color = "#ffc107"
            met_cols[ci].metric("🗑️ Διαγραφές", f"{curr_removals} / {goal_removals}")
            st.markdown(
                f"<div style='margin:-8px 0 12px 0;font-size:12px;'>"
                f"<span style='color:{rem_color}'>{rem_status}</span>"
                f"<span style='color:#666;margin-left:10px;font-size:11px'>(χωρίς παραγγελία)</span></div>",
                unsafe_allow_html=True
            )

        vips = df_member_summary[(df_member_summary['Ποσό_Net'] >= 217.74) & (df_member_summary['NameClean'].isin(real_billed_names))].sort_values('Ποσό_Net', ascending=False)
        if not vips.empty:
            vip_txt = " | ".join([f"**{r['Ονοματεπώνυμο']}** ({r['Ποσό_Net']:.0f}€)" for _, r in vips.iterrows()])
            st.markdown(f'<div class="vip-box">🌟 <b>VIP EXCELLENCE:</b> {vip_txt}</div>', unsafe_allow_html=True)

        df_missing_vips = df_members_raw[
            (~df_members_raw['NameClean'].isin(names_with_any_order)) & 
            (df_members_raw['Tier'].isin(['DIAMOND', 'PLATINUM', 'GOLD']))
        ].copy()
        if not df_missing_vips.empty:
            missing_vips_txt = " | ".join([f"{r['Ονοματεπώνυμο']} ({r['Tier']})" for _, r in df_missing_vips.head(15).iterrows()])
            st.markdown(f'<div class="watchlist-box">🚨 <b>VIP WATCHLIST (Σε Κίνδυνο):</b> {missing_vips_txt}</div>', unsafe_allow_html=True)

    # Tabs
    names_accounted = names_with_any_order.union(set(df_call_list_ekkremeis['NameClean']))
    rem_set = set(df_removals_raw['NameClean'])
    
    df_potentials = df_members_raw[~df_members_raw['NameClean'].isin(names_accounted)].copy()
    # SmartScore βελτιωμένο: λαμβάνει υπόψη prediction + reliability + risk
    df_potentials['SmartScore'] = df_potentials.apply(lambda r: 
        (4 if r['NameClean'] in rem_set else 0) + 
        (3 if r['NameClean'] in member_predictions and member_predictions[r['NameClean']]['predicted'] > historical_avg_basket else 0) +
        (2 if r['NameClean'] in member_predictions else 0) +
        (1 if r['NameClean'] in sheet4_history else 0), axis=1)
    df_potentials = df_potentials.sort_values('SmartScore', ascending=False)
    
    df_rem_clean = df_removals_raw[~df_removals_raw['NameClean'].isin(names_with_any_order)].copy()

    # === Ταξινόμηση τρεχουσών διαγραφών: πιο "ελπιδοφόρες" πρώτα ===
    # Score βασισμένο σε: πιθανότητα παραγγελίας (ml_prob) × εκτιμώμενη αξία,
    # με bonus αν έχει tier upgrade signal ή πρόσφατη ανοδική τάση
    def removal_return_score(name):
        pred = member_predictions.get(name)
        if not pred:
            return 0.0
        base = pred.get('ml_prob', 0) * pred.get('predicted', 0)
        if pred.get('trend_factor', 0) > 0.05:
            base *= 1.15  # bonus: ανοδική τάση
        if name in tier_upgrade_notes:
            base *= 1.10  # bonus: αποδίδει πάνω από το tier της
        return base

    df_rem_clean['ReturnScore'] = df_rem_clean['NameClean'].apply(removal_return_score)
    df_rem_clean['ReturnProb']  = df_rem_clean['NameClean'].apply(
        lambda n: member_predictions.get(n, {}).get('ml_prob', 0))
    df_rem_clean = df_rem_clean.sort_values('ReturnScore', ascending=False)

    # === Κοινή σταθερά για Additions & Καλές Διαγραφές Ιστορικού ===
    # Και τα δύο tabs μοιράζονται την ΙΔΙΑ φιλοσοφία απουσίας: 3+ συνεχόμενες
    # ιστορικές καμπάνιες χωρίς παραγγελία, πριν την τρέχουσα.
    MIN_ABSENCE_STREAK = 3

    # === Καλές Διαγραφές Ιστορικού ===
    # ΙΔΙΑ ΦΙΛΟΣΟΦΙΑ με τα Additions: μέλη που απουσιάζουν ΤΟΥΛΑΧΙΣΤΟΝ 3 συνεχόμενες
    # ιστορικές καμπάνιες (ίδιος υπολογισμός absence_len με το tab Additions). Η ΜΟΝΗ
    # διαφορά: εδώ ΔΕΝ πρέπει να έχουν παραγγείλει ούτε στην ΤΡΕΧΟΥΣΑ καμπάνια —
    # αν είχαν παραγγείλει τώρα, θα ήταν ήδη Additions, όχι εδώ. Δηλαδή αυτό το tab
    # είναι ακριβώς η "δεξαμενή υποψηφίων" από την οποία αντλούν τα Additions, μείον
    # όσους ήδη επέστρεψαν φέτος.
    _last_period_idx_gpr = len(historical_camps) - 1

    good_past_removals = []
    if len(historical_camps) >= MIN_ABSENCE_STREAK:
        for n, entries in history_detailed.items():
            entry_periods = {e['period_idx'] for e in entries}
            if not entry_periods:
                continue
            last_active_period = max(entry_periods)
            # ΙΔΙΟΣ τύπος με τα Additions: μόνο ιστορικές καμπάνιες ανάμεσα στην
            # τελευταία παραγγελία και την τρέχουσα (χωρίς +1 — η τρέχουσα δεν
            # μετράει ως απουσία, αλλά εδώ ούτε καν έχει γίνει "επιστροφή" ακόμα)
            absence_len = _last_period_idx_gpr - last_active_period
            if absence_len < MIN_ABSENCE_STREAK:
                continue

            # ΚΡΙΣΙΜΗ ΔΙΑΦΟΡΑ από τα Additions: εδώ ΔΕΝ πρέπει να έχει καμία
            # παραγγελία (ούτε billed ούτε pending) στην τρέχουσα καμπάνια —
            # αν είχε, θα ήταν ήδη στο tab Additions, όχι εδώ.
            if n in names_with_any_order:
                continue

            entries_sorted = sorted(entries, key=lambda x: x['period_idx'])
            values = [e['net_value'] for e in entries_sorted if e['net_value'] > 0]
            if not values:
                continue
            n_orders = len(values)
            avg_basket = float(np.mean(values))
            best_basket = float(np.max(values))
            last_period = entries_sorted[-1]['period_idx']

            # Ποιοτικό φίλτρο — "καλή" διαγραφή σημαίνει αξιόλογο ιστορικό, όχι απλά απουσία
            if n_orders >= 2 and avg_basket >= historical_avg_basket * 0.6:
                orig_name = None
                match_rows = df_sales_all[df_sales_all['NameClean'] == n]
                if not match_rows.empty:
                    orig_name = match_rows.iloc[0].get('Ονοματεπώνυμο', n)
                    # Τηλέφωνο από την πιο πρόσφατη γνωστή γραμμή πωλήσεων (μπορεί να μην
                    # είναι πια στο Φύλλο4, οπότε το μόνο διαθέσιμο τηλέφωνο είναι εδώ)
                    phone_rows = match_rows[match_rows.get('Τηλέφωνο').notna()] if 'Τηλέφωνο' in match_rows.columns else match_rows.iloc[0:0]
                    phone_val = phone_rows.iloc[-1]['Τηλέφωνο'] if not phone_rows.empty else None
                else:
                    orig_name = n
                    phone_val = None
                good_past_removals.append({
                    'NameClean': n,
                    'Ονοματεπώνυμο': orig_name,
                    'Τηλέφωνο': phone_val,
                    'Παραγγελίες': n_orders,
                    'Μ.Ο. Καλάθι': round(avg_basket, 0),
                    'Best Καλάθι': round(best_basket, 0),
                    'Τελευταία Περίοδος': last_period,
                    'Καμπάνιες Απουσίας': absence_len,
                })

    df_good_past_removals = pd.DataFrame(good_past_removals)
    if not df_good_past_removals.empty:
        df_good_past_removals = df_good_past_removals.sort_values(
            ['Μ.Ο. Καλάθι', 'Παραγγελίες'], ascending=[False, False]
        ).reset_index(drop=True)

    # === ΕΠΑΝΑΤΟΠΟΘΕΤΗΣΕΙΣ (Win-Backs) ===
    # Μέλη που είχαν ΤΟΥΛΑΧΙΣΤΟΝ 3 συνεχόμενες ΙΣΤΟΡΙΚΕΣ καμπάνιες απουσίας
    # (χωρίς καμία παραγγελία) ΠΡΙΝ την τρέχουσα — η τρέχουσα ΔΕΝ μετράει ως απουσία,
    # είναι η "επιστροφή". Αν κάποια έλειψε μόνο 2 ιστορικές καμπάνιες και τώρα (3η
    # συνολικά, μετρώντας και την τρέχουσα) έβαλε παραγγελία, ΔΕΝ μετράει — χρειάζονται
    # 3 πλήρεις απουσίες ΠΡΙΝ από την επιστροφή. (MIN_ABSENCE_STREAK ορίστηκε παραπάνω.)

    winback_rows = []
    if len(historical_camps) >= MIN_ABSENCE_STREAK:
        last_period_idx = len(historical_camps) - 1  # το πιο πρόσφατο ΙΣΤΟΡΙΚΟ period (πριν την τρέχουσα)
        for n in names_with_any_order:
            entries = history_detailed.get(n, [])
            entry_periods = {e['period_idx'] for e in entries}

            if not entry_periods:
                # ΔΕΝ έχει καμία εγγραφή ΜΕΣΑ στο διαθέσιμο ιστορικό παράθυρο (π.χ. το
                # ιστορικό ξεκινάει από 202601, αλλά αυτό το μέλος παράγγειλε τελευταία
                # φορά πριν από αυτό — ή δεν έχει καθόλου προηγούμενη καταγεγραμμένη
                # παραγγελία). Ανεξάρτητα από την τρέχουσα ετικέτα tier (π.χ. "New
                # Business"), η ίδια λογική ισχύει για όλους: καμία εγγραφή στο
                # διαθέσιμο παράθυρο + παραγγελία τώρα = μετράει στα Additions, με
                # το διάστημα απουσίας να επισημαίνεται ως "άγνωστο, τουλάχιστον Χ"
                # μέσω του 🕳️ badge στο UI.
                absence_len = last_period_idx + 1  # τουλάχιστον όλο το διαθέσιμο παράθυρο + η τρέχουσα απουσίαζε
                absence_is_exact = False
                older_vals = []
            else:
                last_active_period = max(entry_periods)
                # absence_len = πόσες ΙΣΤΟΡΙΚΕΣ καμπάνιες πέρασαν χωρίς παραγγελία, ΑΠΟΚΛΕΙΣΤΙΚΑ
                # ανάμεσα στην τελευταία παραγγελία και την τρέχουσα καμπάνια (όχι +1, η
                # τρέχουσα δεν είναι απουσία — είναι η επιστροφή).
                absence_len = last_period_idx - last_active_period
                absence_is_exact = True
                older_vals = [e['net_value'] for e in entries if e['net_value'] > 0]

            if absence_len < MIN_ABSENCE_STREAK:
                continue

            # ΚΡΙΣΙΜΟ: η τρέχουσα παραγγελία πρέπει να ανήκει ΡΗΤΑ στο tab
            # "Τιμολογημένες" (real_billed_names) ή "Προς Τιμολόγηση" (pros_timologisi_names) —
            # χρησιμοποιούμε απευθείας τα ήδη-φιλτραρισμένα DataFrames αυτών των tabs
            # (df_billed_only, df_pros_timologisi) ως πηγή αλήθειας, αντί να ξαναχτίζουμε
            # σύνθετα masks πάνω στο df_curr (που μπορεί να αποκλείουν σωστές εγγραφές
            # αν ένα μέλος έχει πολλαπλές γραμμές με διαφορετικό status).
            is_billed  = n in real_billed_names
            is_pending = n in pros_timologisi_names

            if not (is_billed or is_pending):
                continue

            curr_val = 0.0
            orig_name = n
            phone_val = None
            if is_billed:
                b_row = df_billed_only[df_billed_only['NameClean'] == n]
                if not b_row.empty:
                    curr_val = b_row['Ποσό_Net'].sum()
                    orig_name = b_row.iloc[0].get('Ονοματεπώνυμο', n)
                    phone_val = b_row.iloc[0].get('Τηλέφωνο')
            if curr_val <= 0 and is_pending:
                p_row = df_pros_timologisi[df_pros_timologisi['NameClean'] == n]
                if not p_row.empty:
                    curr_val = p_row['Ποσό_Net'].sum()
                    orig_name = p_row.iloc[0].get('Ονοματεπώνυμο', n)
                    phone_val = p_row.iloc[0].get('Τηλέφωνο')
            if curr_val <= 0:
                continue

            winback_rows.append({
                'NameClean': n,
                'Ονοματεπώνυμο': orig_name,
                'Τηλέφωνο': phone_val,
                'Τρέχουσα Αξία': round(curr_val, 0),
                'Παλιό Μ.Ο. Καλάθι': round(float(np.mean(older_vals)), 0) if older_vals else None,
                'Καμπάνιες Απουσίας': absence_len,
                'Ακριβές Διάστημα': absence_is_exact,
            })

    df_winbacks = pd.DataFrame(winback_rows)
    if not df_winbacks.empty:
        df_winbacks = df_winbacks.sort_values('Καμπάνιες Απουσίας', ascending=False).reset_index(drop=True)

    # === Δυναμική λίστα tabs — στη Λειτουργία Βοηθού, τα μη-διαθέσιμα tabs
    # (AI Advisor, Προς Τιμολόγηση, Τιμολογημένες, Additions, Adjustments) ΔΕΝ
    # εμφανίζονται καν στη μπάρα — όχι απλώς "κλειδωμένα" μέσα τους. Το tab_idx
    # χαρτογραφεί συμβολικό όνομα → πραγματική θέση στο tabs[], που αλλάζει
    # ανάλογα με το ποια tabs συμπεριλαμβάνονται.
    _tab_defs = [
        ('ai_advisor',    "🧠 AI Advisor & Analytics",                              False),
        ('smart_rank',    "🔥 Smart Rank",                                          True),
        ('pending',       f"⏳ Προς Τιμολόγηση ({len(df_pros_timologisi)})",         False),
        ('billed',        f"🚚 Τιμολογημένες ({len(df_billed_only)})",               False),
        ('ekkremeis',     f"📞 Εκκρεμείς ({len(df_call_list_ekkremeis)})",           True),
        ('removals',      f"⚠️ Διαγραφές ({len(df_rem_clean)})",                    True),
        ('good_removals', f"💎 Καλές Διαγραφές Ιστορικού ({len(df_good_past_removals)})", True),
        ('additions',     f"🎉 Additions ({len(df_winbacks)})",                     False),
        ('today',         "⭐ Σήμερα",                                              True),
        ('adjustments',   f"⚙️ Adjustments ({len(df_adjustments)})",                False),
        ('credit_check',  f"🏦 Πιστωτικός Έλεγχος ({len(df_empty_status)})",        True),
    ]
    _visible_tab_defs = [t for t in _tab_defs if (t[2] or not is_assistant_mode)]
    tab_idx = {key: i for i, (key, _, _) in enumerate(_visible_tab_defs)}
    tabs = st.tabs([label for _, label, _ in _visible_tab_defs])


    def render_list(df, context, show_notes=False):
        search_q = st.text_input("🔍 Αναζήτηση", key=f"search_{context}", placeholder="Πληκτρολόγησε όνομα...")
        if search_q:
            df = df[df['Ονοματεπώνυμο'].str.contains(search_q, case=False, na=False)]
        if df.empty:
            st.info("Δεν βρέθηκαν αποτελέσματα.")
            return
        for i, r in df.iterrows():
            row_key = f"{context}_{i}"
            if row_key in st.session_state.sent_ids: continue
            n = r['NameClean']
            h_val = get_smart_value(n, r['Ονοματεπώνυμο'])
            pred_info = member_predictions.get(n)
            trend_str = rel_str = ci_str = tier_note = ""
            if pred_info:
                tf = pred_info['trend_factor']
                trend_str = " ↑" if tf > 0.05 else (" ↓" if tf < -0.05 else "")
                rel_str   = f" | Αξιοπιστία: {pred_info['reliability']:.0%}"
                p25 = pred_info.get('p25', pred_info['predicted'] * 0.70)
                p75 = pred_info.get('p75', pred_info['predicted'] * 1.30)
                ci_str = f" | Εύρος: {p25:.0f}–{p75:.0f}€"
            if n in tier_upgrade_notes:
                tier_note = f" | {tier_upgrade_notes[n]}"
            note_text = member_notes.get(n, "")
            return_badge = ""
            if context == "rem" and pred_info:
                rp = pred_info.get('ml_prob', 0)
                if rp >= 0.5:
                    return_badge = f" 🟢 {rp:.0%} πιθανότητα"
                elif rp >= 0.25:
                    return_badge = f" 🟡 {rp:.0%} πιθανότητα"
                else:
                    return_badge = f" 🔴 {rp:.0%} πιθανότητα"
            # Τηλέφωνο — απαραίτητο για επικοινωνία, εμφανίζεται ΠΑΝΤΑ (και στις δύο λειτουργίες)
            phone_raw = r.get('TelClean')
            phone_digits = re.sub(r'\D', '', str(phone_raw)) if pd.notna(phone_raw) else ""
            phone_display = str(phone_raw) if pd.notna(phone_raw) and str(phone_raw).strip() else "— χωρίς τηλέφωνο"
            # Λειτουργία Βοηθού: καμία μνεία ποσού/€ πουθενά — μόνο τάση/πιθανότητα/σημείωση
            if is_assistant_mode:
                label = f"**{r['Ονοματεπώνυμο']}** — 📞 {phone_display}{trend_str}{return_badge}{' 📝' if note_text else ''}"
                caption_text = f"{rel_str.lstrip(' |')}{tier_note}".strip(" |")
            else:
                label = f"**{r['Ονοματεπώνυμο']}** — 📞 {phone_display} — ~{h_val:.0f}€{trend_str}{return_badge}{' 📝' if note_text else ''}"
                caption_text = f"Εκτίμηση: ~{h_val:.0f}€{trend_str}{rel_str}{ci_str}{tier_note}"
            with st.expander(label, expanded=False):
                mc1, mc2 = st.columns([4, 1])
                with mc1:
                    if phone_digits:
                        st.markdown(f"📞 [**{phone_display}**](tel:{phone_digits})", unsafe_allow_html=False)
                    if caption_text:
                        st.caption(caption_text)
                    if note_text:
                        st.markdown(f'<span class="note-badge">📝 {note_text}</span>', unsafe_allow_html=True)
                    if show_notes:
                        new_note = st.text_input("Σημείωση:", value=note_text,
                                                  key=f"note_{row_key}", placeholder="π.χ. θα παραγγείλει αύριο...")
                        if new_note != note_text:
                            save_note(n, new_note)
                            member_notes[n] = new_note
                            st.rerun()
                with mc2:
                    if st.button("✓ Ok", key=f"btn_{row_key}"):
                        mark_contacted(row_key)
                        st.rerun()

    if 'ai_advisor' in tab_idx:
        with tabs[tab_idx['ai_advisor']]:
            if is_assistant_mode:
                st.info("🙋 Μη διαθέσιμο σε λειτουργία βοηθού (στόχοι/οικονομικά στοιχεία).")
            else:
                st.subheader("🤖 AI Tactical Advisor")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### Στρατηγική Ημέρας")
                    if target_val > 0:
                        if final_forecast > target_val * 1.05:
                            st.success("Το ML μοντέλο δείχνει ότι ο στόχος έχει **ασφαλίσει**. Η πιθανότητα επιτυχίας είναι άνω του 95%. Επικεντρωθείτε σε upsells για ρεκόρ πωλήσεων.")
                        elif final_forecast > target_val:
                            st.info("Το ML μοντέλο δείχνει οριακή επιτυχία στόχου. Απαιτείται στενή παρακολούθηση των εκκρεμών παραγγελιών.")
                        else:
                            st.warning(f"Κίνδυνος Στόχου! Το ML μοντέλο προβλέπει έλλειμμα {target_val - final_forecast:,.0f}€. Πρέπει να ενεργοποιηθούν άμεσα πελάτες με υψηλό Propensity Score.")
                    churn_risk = df_potentials[df_potentials['NameClean'].apply(lambda n: member_predictions.get(n, {}).get('ml_prob', 1) < 0.3 and member_predictions.get(n, {}).get('predicted', 0) > 100)]
                    if not churn_risk.empty:
                        names = ", ".join(churn_risk['Ονοματεπώνυμο'].head(3))
                        st.error(f"**Κίνδυνος Διαρροής (High Value):** {names}. Έχουν κάτω από 30% πιθανότητα να παραγγείλουν βάσει του αλγορίθμου.")
                    upsell = df_potentials[df_potentials['NameClean'].apply(lambda n: member_predictions.get(n, {}).get('ml_prob', 0) > 0.75 and member_predictions.get(n, {}).get('predicted', 0) < 50)]
                    if not upsell.empty:
                        st.success(f"**Ευκαιρίες Upsell:** Εντοπίστηκαν {len(upsell)} μέλη με σίγουρη παραγγελία αλλά χαμηλό καλάθι. Προτείνετε προσφορές!")
                with c2:
                    st.markdown("#### 🎯 VIP Propensity Matrix")
                    scatter_data = []
                    for _, r in df_potentials.iterrows():
                        n = r['NameClean']
                        p = member_predictions.get(n, {})
                        prob = p.get('ml_prob', 0)
                        val = p.get('predicted', 0)
                        if val > 30:
                            scatter_data.append({'Name': r['Ονοματεπώνυμο'], 'Value': val, 'Probability': prob * 100, 'Tier': r['Tier']})
                    if scatter_data:
                        df_sc = pd.DataFrame(scatter_data)
                        fig_scatter = px.scatter(df_sc, x="Value", y="Probability", color="Tier",
                                                 hover_name="Name", template="plotly_dark",
                                                 labels={"Value": "Αναμενόμενη Αξία (€)", "Probability": "Πιθανότητα (ML %)"})
                        fig_scatter.update_traces(marker=dict(size=12, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
                        fig_scatter.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
                        st.plotly_chart(fig_scatter, use_container_width=True)

    # ΚΡΙΣΙΜΟ: αυτές οι δύο γραμμές ΔΕΝ ανήκουν στο tab "AI Advisor" — είναι
    # προετοιμασία δεδομένων για το tab "Smart Rank" που ακολουθεί, και πρέπει
    # να εκτελούνται ΠΑΝΤΑ (ακόμα κι όταν το AI Advisor tab είναι κρυμμένο σε
    # λειτουργία βοηθού), αλλιώς το Smart Rank σκάει με NameError.
    df_potentials_returning = df_potentials[df_potentials['NameClean'].isin(member_predictions.keys())]
    df_potentials_new       = df_potentials[~df_potentials['NameClean'].isin(member_predictions.keys())]

    with tabs[tab_idx['smart_rank']]:
        sr1, sr2 = st.tabs([
            f"📋 Με Ιστορικό ({len(df_potentials_returning)})",
            f"🆕 Νέα Μέλη ({len(df_potentials_new)})"
        ])
        with sr1:
            render_list(df_potentials_returning.head(40), "smart_ret", show_notes=True)
        with sr2:
            st.caption("⚠️ Χωρίς ιστορικό — πρόβλεψη βασισμένη σε tier μέσο όρο.")
            render_list(df_potentials_new.head(40), "smart_new", show_notes=True)

    if 'pending' in tab_idx:
        with tabs[tab_idx['pending']]:
            if is_assistant_mode:
                st.info("🙋 Μη διαθέσιμο σε λειτουργία βοηθού (οικονομικά στοιχεία).")
            elif not df_pros_timologisi.empty:
                df_disp = df_pros_timologisi.copy()
                df_disp['Εκτίμηση'] = df_disp.apply(lambda r: r['Ποσό_Net'] if r['Ποσό_Net'] > 0 else get_smart_value(r['NameClean'], r['Ονοματεπώνυμο']), axis=1)
                st.dataframe(
                    df_disp[['Ονοματεπώνυμο', 'Ποσό_Net', 'Εκτίμηση', 'Τηλέφωνο']],
                    use_container_width=True, hide_index=True,
                    column_config={
                        "Εκτίμηση": st.column_config.ProgressColumn("Εκτίμηση Αξίας (€)", help="Πιθανή αξία", format="%.0f", min_value=0, max_value=600),
                        "Ποσό_Net": st.column_config.NumberColumn("Τρέχον Ποσό (€)", format="%.2f €")
                    }
                )
            else:
                st.info("Καμία παραγγελία σε αναμονή στο σύστημα.")

    if 'billed' in tab_idx:
        with tabs[tab_idx['billed']]:
            if is_assistant_mode:
                st.info("🙋 Μη διαθέσιμο σε λειτουργία βοηθού (οικονομικά στοιχεία).")
            else:
                max_val = float(df_billed_only['Ποσό_Net'].max() if not df_billed_only.empty else 600)

                # Feature 1: Member Score Card — κάνεις κλικ σε μέλος και βλέπεις το πλήρες ιστορικό
                sc_search = st.text_input("🔍 Αναζήτηση μέλους", key="sc_search", placeholder="Πληκτρολόγησε όνομα...")
                df_billed_disp = df_billed_only.copy()
                if sc_search:
                    df_billed_disp = df_billed_disp[df_billed_disp['Ονοματεπώνυμο'].str.contains(sc_search, case=False, na=False)]

                for _, row in df_billed_disp.sort_values('Ποσό_Net', ascending=False).iterrows():
                    n = row['NameClean']
                    label = f"**{row['Ονοματεπώνυμο']}** — {row['Ποσό_Net']:,.0f}€"
                    with st.expander(label, expanded=False):
                        sc1, sc2, sc3 = st.columns(3)

                        # Ιστορικό παραγγελιών ανά καμπάνια
                        hist_entries = history_detailed.get(n, [])
                        hist_vals = [e['net_value'] for e in sorted(hist_entries, key=lambda x: x['period_idx'])]
                        hist_camps_member = historical_camps[:len(hist_vals)]

                        sc1.metric("📦 Καμπάνιες", f"{len(hist_vals)}/{len(historical_camps)}")
                        sc2.metric("💰 Μέσο Καλάθι", f"{np.mean(hist_vals):,.0f}€" if hist_vals else "—")
                        sc3.metric("🏆 Best", f"{max(hist_vals):,.0f}€" if hist_vals else "—")

                        pred = member_predictions.get(n, {})
                        if pred:
                            p1, p2, p3 = st.columns(3)
                            tf = pred.get('trend_factor', 0)
                            trend_lbl = "↑ Ανοδικό" if tf > 0.05 else ("↓ Καθοδικό" if tf < -0.05 else "→ Σταθερό")
                            p1.metric("📈 Τάση", trend_lbl)
                            p2.metric("🎯 Αξιοπιστία", f"{pred.get('reliability',0):.0%}")
                            p3.metric("🤖 Πιθανότητα", f"{pred.get('ml_prob',0):.0%}")

                        # Streak (συνεχόμενες καμπάνιες)
                        if hist_vals:
                            streak = 0
                            for v in reversed(hist_vals):
                                if v > 0: streak += 1
                                else: break
                            st.caption(f"🔥 Streak: {streak} συνεχόμενες καμπάνιες | Tier: {row.get('_Tier','—')} | {tier_upgrade_notes.get(n,'')}")

                        # Mini sparkline ιστορικού
                        if len(hist_vals) >= 2:
                            fig_mini = go.Figure(go.Scatter(
                                x=list(range(len(hist_vals))), y=hist_vals,
                                mode='lines+markers', line=dict(color='#ff69b4', width=2),
                                marker=dict(size=6), fill='tozeroy',
                                fillcolor='rgba(255,105,180,0.1)'
                            ))
                            fig_mini.update_layout(
                                height=100, margin=dict(l=0,r=0,t=0,b=0),
                                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
                                xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=True)
                            )
                            st.plotly_chart(fig_mini, use_container_width=True)

    with tabs[tab_idx['ekkremeis']]: render_list(df_call_list_ekkremeis, "todo", show_notes=True)

    with tabs[tab_idx['removals']]:
        st.caption("📊 Ταξινομημένες με τις πιο **ελπιδοφόρες** πρώτα (πιθανότητα × εκτιμώμενη αξία).")
        if not df_rem_clean.empty:
            high_hope = df_rem_clean[df_rem_clean['ReturnProb'] >= 0.5]
            if not high_hope.empty:
                st.success(f"🎯 {len(high_hope)} μέλη με **πάνω από 50% πιθανότητα** να ξαναπαραγγείλουν — ξεκίνα από αυτές.")
        render_list(df_rem_clean, "rem", show_notes=True)

    with tabs[tab_idx['good_removals']]:
        st.caption(
            f"💎 Ίδια φιλοσοφία με τα Additions: μέλη χωρίς παραγγελία τις τελευταίες "
            f"**{MIN_ABSENCE_STREAK}+ καμπάνιες**, με αξιόλογο ιστορικό (2+ παραγγελίες, καλάθι τουλάχιστον "
            "στο μέσο όρο) — αλλά **ΔΕΝ έχουν ξαναπαραγγείλει ακόμα** ούτε στην τρέχουσα καμπάνια. "
            "Είναι η «δεξαμενή» από την οποία προκύπτουν μελλοντικά Additions — καλή ευκαιρία να τις καλέσεις πρώτος/η."
        )
        if df_good_past_removals.empty:
            st.info("Δεν εντοπίστηκαν μέλη με αξιόλογο ιστορικό που να πληρούν τα κριτήρια.")
        else:
            gpr_search = st.text_input("🔍 Αναζήτηση", key="search_gpr", placeholder="Πληκτρολόγησε όνομα...")
            df_gpr_disp = df_good_past_removals
            if gpr_search:
                df_gpr_disp = df_gpr_disp[df_gpr_disp['Ονοματεπώνυμο'].astype(str).str.contains(gpr_search, case=False, na=False)]

            for _, row in df_gpr_disp.iterrows():
                n = row['NameClean']
                note_text = member_notes.get(n, "")
                phone_raw = row.get('Τηλέφωνο')
                phone_digits = re.sub(r'\D', '', str(phone_raw)) if pd.notna(phone_raw) else ""
                phone_display = str(phone_raw) if pd.notna(phone_raw) and str(phone_raw).strip() else "— χωρίς τηλέφωνο"
                if is_assistant_mode:
                    label = f"**{row['Ονοματεπώνυμο']}** — 📞 {phone_display} — {int(row['Παραγγελίες'])} παραγγελίες, {int(row.get('Καμπάνιες Απουσίας', 0))} καμπ. απουσίας{' 📝' if note_text else ''}"
                else:
                    label = f"**{row['Ονοματεπώνυμο']}** — 📞 {phone_display} — Μ.Ο. {row['Μ.Ο. Καλάθι']:,.0f}€ ({int(row['Παραγγελίες'])} παραγγελίες, {int(row.get('Καμπάνιες Απουσίας', 0))} καμπ. απουσίας){' 📝' if note_text else ''}"
                with st.expander(label, expanded=False):
                    gc1, gc2 = st.columns([4, 1])
                    with gc1:
                        if phone_digits:
                            st.markdown(f"📞 [**{phone_display}**](tel:{phone_digits})", unsafe_allow_html=False)
                        if is_assistant_mode:
                            st.caption(
                                f"Παραγγελίες ιστορικά: {int(row['Παραγγελίες'])} | "
                                f"Καμπάνιες απουσίας: {int(row.get('Καμπάνιες Απουσίας', 0))} | "
                                f"Τελευταία γνωστή περίοδος: {row['Τελευταία Περίοδος']}"
                            )
                        else:
                            st.caption(
                                f"Μ.Ο. καλάθι: {row['Μ.Ο. Καλάθι']:,.0f}€ | Best: {row['Best Καλάθι']:,.0f}€ | "
                                f"Παραγγελίες ιστορικά: {int(row['Παραγγελίες'])} | "
                                f"Καμπάνιες απουσίας: {int(row.get('Καμπάνιες Απουσίας', 0))} | "
                                f"Τελευταία γνωστή περίοδος: {row['Τελευταία Περίοδος']}"
                            )
                        if note_text:
                            st.markdown(f'<span class="note-badge">📝 {note_text}</span>', unsafe_allow_html=True)
                        new_note = st.text_input("Σημείωση:", value=note_text,
                                                  key=f"note_gpr_{n}", placeholder="π.χ. δεν θέλει πια, μετακόμισε...")
                        if new_note != note_text:
                            save_note(n, new_note)
                            member_notes[n] = new_note
                            st.rerun()
                    with gc2:
                        row_key = f"gpr_{n}"
                        if st.button("✓ Ok", key=f"btn_{row_key}"):
                            mark_contacted(row_key)
                            st.rerun()

    if 'additions' in tab_idx:
        with tabs[tab_idx['additions']]:
            st.caption(
                f"🎉 Μέλη χωρίς παραγγελία τις τελευταίες **{MIN_ABSENCE_STREAK}+ καμπάνιες** (συμπεριλαμβανομένων "
                "όσων δεν έχουν καθόλου καταγεγραμμένο ιστορικό — π.χ. New Business) που **ΤΩΡΑ έβαλαν "
                "παραγγελία**. Καλή ευκαιρία να τα κρατήσεις ενεργά."
            )

            if not is_assistant_mode:
                with st.expander("🔬 Διαγνωστικά Win-Backs (debug)", expanded=False):
                    st.caption(f"historical_camps (πλήθος): {len(historical_camps)} | last_period_idx: {len(historical_camps)-1}")
                    st.caption(f"names_with_any_order (σύνολο): {len(names_with_any_order)} | real_billed_names: {len(real_billed_names)} | pros_timologisi_names: {len(pros_timologisi_names)}")

                    # --- Αναζήτηση συγκεκριμένου ονόματος σε ΟΛΕΣ τις πηγές δεδομένων ---
                    name_probe = st.text_input("🔎 Έλεγξε συγκεκριμένο όνομα (π.χ. ΣΑΜΕΡΚΑ)", key="winback_name_probe")
                    if name_probe:
                        probe_clean = smart_clean_name(name_probe)
                        st.code(f"Κανονικοποιημένο: '{probe_clean}'")

                        # Βρες πιθανά matches με "περιέχει" αντί ακριβές match (πιάνει τυχόν διαφορές)
                        probe_tokens = set(probe_clean.split())
                        all_names_pool = set(df_members_raw['NameClean']) | set(history_detailed.keys()) | set(df_curr['NameClean'])
                        fuzzy_matches = [nm for nm in all_names_pool if probe_tokens & set(nm.split())]

                        if not fuzzy_matches:
                            st.warning("Δεν βρέθηκε καμία εγγραφή με αυτά τα tokens πουθενά (μέλη, ιστορικό, ή τρέχουσα καμπάνια).")
                        for fm in fuzzy_matches:
                            st.markdown(f"**Match: `{fm}`**")
                            in_members   = fm in set(df_members_raw['NameClean'])
                            in_history   = fm in history_detailed
                            in_billed    = fm in real_billed_names
                            in_pending   = fm in pros_timologisi_names
                            in_curr      = fm in set(df_curr['NameClean'])
                            st.write(
                                f"- Στη λίστα μελών (Φύλλο 1, τρέχουσα): {'✅' if in_members else '❌'}\n"
                                f"- Έχει ιστορικό (history_detailed): {'✅' if in_history else '❌'}\n"
                                f"- Στο df_curr (τρέχουσα καμπάνια, raw): {'✅' if in_curr else '❌'}\n"
                                f"- Είναι Τιμολογημένη (real_billed_names): {'✅' if in_billed else '❌'}\n"
                                f"- Είναι Προς Τιμολόγηση (pros_timologisi_names): {'✅' if in_pending else '❌'}"
                            )
                            if in_history:
                                ent = sorted(history_detailed[fm], key=lambda x: x['period_idx'])
                                st.write(f"  Ιστορικές περίοδοι: {[(e['period_idx'], round(e['net_value'])) for e in ent]}")
                                last_act = max(e['period_idx'] for e in ent)
                                st.write(f"  last_active_period={last_act} | υπολογισμένη απουσία={len(historical_camps)-1-last_act}")
                            if in_curr:
                                rows = df_curr[df_curr['NameClean'] == fm][['Status_Clean', 'Ποσό_Net']]
                                st.dataframe(rows, use_container_width=True, hide_index=True)
                        st.divider()

                        # === Έλεγχος raw ιστορικού sheet (πριν την ομαδοποίηση) για πιθανές
                        # παραλλαγές ονόματος που δεν ταυτοποιήθηκαν με το NameClean ===
                        st.markdown("**Αναζήτηση σε ΟΛΟ το df_sales_all (raw, με όλες τις καμπάνιες) — πιθανές παραλλαγές:**")
                        raw_token_matches = df_sales_all[
                            df_sales_all['NameClean'].apply(lambda x: bool(probe_tokens & set(str(x).split())))
                        ]
                        if raw_token_matches.empty:
                            st.warning("Καμία γραμμή στο raw sales sheet δεν ταιριάζει με αυτά τα tokens — πιθανώς διαφορετική γραφή ονόματος στο Excel.")
                        else:
                            distinct_raw_names = raw_token_matches['NameClean'].unique()
                            st.write(f"Βρέθηκαν {len(distinct_raw_names)} διαφορετικές παραλλαγές NameClean στο raw sheet:")
                            for rn in distinct_raw_names:
                                camp_list = sorted(raw_token_matches[raw_token_matches['NameClean'] == rn][camp_col].unique())
                                st.write(f"  • `{rn}` — εμφανίζεται σε καμπάνιες: {camp_list}")

                    diag_rows = []
                    for n in names_with_any_order:
                        entries = history_detailed.get(n, [])
                        entry_periods = {e['period_idx'] for e in entries}
                        if not entry_periods:
                            reason = "Κανένα ιστορικό (νέο μέλος)"
                            absence_len = None
                        else:
                            last_active = max(entry_periods)
                            absence_len = (len(historical_camps) - 1) - last_active
                            if absence_len < MIN_ABSENCE_STREAK:
                                reason = f"Απουσία μόνο {absence_len} < {MIN_ABSENCE_STREAK}"
                            else:
                                is_billed = n in real_billed_names
                                is_pending = n in pros_timologisi_names
                                if not (is_billed or is_pending):
                                    reason = "Δεν είναι ούτε billed ούτε pending"
                                else:
                                    curr_val = 0.0
                                    if is_billed:
                                        b_row = df_billed_only[df_billed_only['NameClean'] == n]
                                        curr_val = b_row['Ποσό_Net'].sum() if not b_row.empty else 0.0
                                    if curr_val <= 0 and is_pending:
                                        p_row = df_pros_timologisi[df_pros_timologisi['NameClean'] == n]
                                        curr_val = p_row['Ποσό_Net'].sum() if not p_row.empty else 0.0
                                    reason = "✅ ΠΕΡΝΑΕΙ" if curr_val > 0 else f"curr_val={curr_val} (≤0)"
                        orig = df_members_raw[df_members_raw['NameClean'] == n]['Ονοματεπώνυμο']
                        orig = orig.iloc[0] if not orig.empty else n
                        diag_rows.append({'Όνομα': orig, 'Απουσία': absence_len, 'Λόγος': reason})

                    df_diag = pd.DataFrame(diag_rows)
                    # Δείξε μόνο όσα έχουν τουλάχιστον κάποιο ιστορικό (πιο σχετικά για debug)
                    df_diag_relevant = df_diag[df_diag['Απουσία'].notna()].sort_values('Απουσία', ascending=False)
                    st.dataframe(df_diag_relevant, use_container_width=True, hide_index=True)

            if df_winbacks.empty:
                st.info("Δεν εντοπίστηκαν επανατοποθετήσεις σε αυτή την καμπάνια (ή δεν υπάρχουν αρκετές ιστορικές καμπάνιες για σύγκριση).")
            else:
                n_unknown_duration = int((~df_winbacks['Ακριβές Διάστημα']).sum()) if 'Ακριβές Διάστημα' in df_winbacks.columns else 0
                if is_assistant_mode:
                    st.metric("🎉 Σύνολο Επανατοποθετήσεων", f"{len(df_winbacks)}")
                else:
                    wb_total_value = df_winbacks['Τρέχουσα Αξία'].sum()
                    wb1, wb2 = st.columns(2)
                    wb1.metric("🎉 Σύνολο Επανατοποθετήσεων", f"{len(df_winbacks)}")
                    wb2.metric("💰 Αξία που Ξανακερδήθηκε", f"{wb_total_value:,.0f}€")
                if n_unknown_duration > 0:
                    st.caption(
                        f"ℹ️ {n_unknown_duration} από αυτές έχουν διάστημα απουσίας **πέρα από το διαθέσιμο ιστορικό** "
                        f"(δεν έχουμε δεδομένα πόσο ακριβώς πριν παράγγειλαν τελευταία φορά — εμφανίζονται με 🕳️ badge)."
                    )

                wb_search = st.text_input("🔍 Αναζήτηση", key="search_wb", placeholder="Πληκτρολόγησε όνομα...")
                df_wb_disp = df_winbacks
                if wb_search:
                    df_wb_disp = df_wb_disp[df_wb_disp['Ονοματεπώνυμο'].astype(str).str.contains(wb_search, case=False, na=False)]

                for _, row in df_wb_disp.iterrows():
                    n = row['NameClean']
                    note_text = member_notes.get(n, "")
                    is_exact = row.get('Ακριβές Διάστημα', True)
                    absence_str = f"{int(row['Καμπάνιες Απουσίας'])}+ (🕳️ πέρα από ιστορικό)" if not is_exact else f"{int(row['Καμπάνιες Απουσίας'])}"
                    phone_raw = row.get('Τηλέφωνο')
                    phone_digits = re.sub(r'\D', '', str(phone_raw)) if pd.notna(phone_raw) else ""
                    phone_display = str(phone_raw) if pd.notna(phone_raw) and str(phone_raw).strip() else "— χωρίς τηλέφωνο"
                    if is_assistant_mode:
                        label = f"🎉 **{row['Ονοματεπώνυμο']}** — 📞 {phone_display} — απουσίαζε {absence_str} καμπάνιες{' 📝' if note_text else ''}"
                    else:
                        label = (
                            f"🎉 **{row['Ονοματεπώνυμο']}** — 📞 {phone_display} — απουσίαζε {absence_str} καμπάνιες, "
                            f"τώρα: {row['Τρέχουσα Αξία']:,.0f}€{' 📝' if note_text else ''}"
                        )
                    with st.expander(label, expanded=False):
                        if phone_digits:
                            st.markdown(f"📞 [**{phone_display}**](tel:{phone_digits})", unsafe_allow_html=False)
                        if is_assistant_mode:
                            st.caption(f"Καμπάνιες απουσίας: {absence_str}")
                        else:
                            basket_str = f"{row['Παλιό Μ.Ο. Καλάθι']:,.0f}€" if pd.notna(row['Παλιό Μ.Ο. Καλάθι']) else "Άγνωστο (πριν το διαθέσιμο ιστορικό)"
                            st.caption(
                                f"Τρέχουσα παραγγελία: {row['Τρέχουσα Αξία']:,.0f}€ | "
                                f"Παλιό μέσο καλάθι: {basket_str} | "
                                f"Καμπάνιες απουσίας: {absence_str}"
                            )
                        if not is_exact:
                            st.info("Το ιστορικό σου ξεκινάει αργότερα από την τελευταία γνωστή παραγγελία αυτού του μέλους — πιθανότατα απουσίαζε για ακόμα περισσότερο καιρό από ό,τι δείχνει ο αριθμός.")
                        if note_text:
                            st.markdown(f'<span class="note-badge">📝 {note_text}</span>', unsafe_allow_html=True)
                        new_note = st.text_input("Σημείωση:", value=note_text,
                                                  key=f"note_wb_{n}", placeholder="π.χ. τι την έκανε να επιστρέψει...")
                        if new_note != note_text:
                            save_note(n, new_note)
                            member_notes[n] = new_note
                            st.rerun()

    with tabs[tab_idx['today']]:
        st.caption(
            "⭐ Ένα ενιαίο check-list: οι πιο σημαντικές επαφές σήμερα, συνδυάζοντας Smart Rank, "
            "Διαγραφές υψηλής πιθανότητας, και σιωπηλά VIP — ταξινομημένα με ένα κοινό score."
        )

        action_rows = []
        # Πηγή 1: Smart Rank top δυναμικά μέλη (όσα δεν έχουν παραγγείλει ακόμα)
        for _, r in df_potentials.head(120).iterrows():
            n = r['NameClean']
            # ΡΗΤΟΣ έλεγχος ασφαλείας: αν έχει ήδη παραγγελία (τιμολογημένη ή σε
            # αναμονή) στην τρέχουσα καμπάνια, ΔΕΝ μπαίνει στη λίστα κλήσεων —
            # ανεξάρτητα από το αν το df_potentials το είχε ήδη φιλτράρει.
            if n in names_with_any_order:
                continue
            pred = member_predictions.get(n, {})
            score = pred.get('ml_prob', 0) * pred.get('predicted', 0)
            if score > 5:
                detail = f"{pred.get('ml_prob',0):.0%} πιθανότητα" if is_assistant_mode else f"~{pred.get('predicted',0):.0f}€ | {pred.get('ml_prob',0):.0%} πιθανότητα"
                action_rows.append({
                    'NameClean': n, 'Ονοματεπώνυμο': r['Ονοματεπώνυμο'], 'Τηλέφωνο': r.get('TelClean'),
                    'Κατηγορία': '🔥 Smart Rank', 'Score': score,
                    'Λεπτομέρεια': detail
                })
        # Πηγή 2: Διαγραφές με υψηλή πιθανότητα επιστροφής
        for _, r in df_rem_clean.iterrows():
            n = r['NameClean']
            if n in names_with_any_order:
                continue
            if r.get('ReturnProb', 0) >= 0.35:
                action_rows.append({
                    'NameClean': n, 'Ονοματεπώνυμο': r['Ονοματεπώνυμο'], 'Τηλέφωνο': r.get('Τηλέφωνο'),
                    'Κατηγορία': '⚠️ Διαγραφή', 'Score': r.get('ReturnScore', 0),
                    'Λεπτομέρεια': f"{r.get('ReturnProb',0):.0%} πιθανότητα επιστροφής"
                })
        # Πηγή 3: Σιωπηλά VIP (ήδη υπολογισμένα στο alerts block ως silent_vips)
        for name_orig, absent_count, vip_phone in (silent_vips if 'silent_vips' in dir() else []):
            action_rows.append({
                'NameClean': name_orig, 'Ονοματεπώνυμο': name_orig, 'Τηλέφωνο': vip_phone,
                'Κατηγορία': '🔇 Σιωπηλό VIP', 'Score': absent_count * 50,
                'Λεπτομέρεια': f"Απουσιάζει {absent_count} καμπάνιες"
            })

        if not action_rows:
            st.info("Δεν εντοπίστηκαν προτεραιότητες για σήμερα — είτε όλα τα μέλη έχουν ήδη παραγγείλει, είτε δεν υπάρχουν αρκετά δεδομένα.")
        else:
            df_action = pd.DataFrame(action_rows).sort_values('Score', ascending=False)
            df_action = df_action.drop_duplicates(subset='NameClean', keep='first').head(40).reset_index(drop=True)

            st.metric("📋 Προτεινόμενες επαφές σήμερα", f"{len(df_action)}")

            for i, row in df_action.iterrows():
                n = row['NameClean']
                row_key = f"today_{n}"
                if row_key in st.session_state.sent_ids:
                    continue
                note_text = member_notes.get(n, "")
                phone_raw = row.get('Τηλέφωνο')
                phone_digits = re.sub(r'\D', '', str(phone_raw)) if pd.notna(phone_raw) else ""
                phone_display = str(phone_raw) if pd.notna(phone_raw) and str(phone_raw).strip() else "— χωρίς τηλέφωνο"
                c1, c2 = st.columns([5, 1])
                c1.write(f"**{i+1}. {row['Ονοματεπώνυμο']}** — {row['Κατηγορία']}")
                if phone_digits:
                    c1.markdown(f"📞 [**{phone_display}**](tel:{phone_digits})", unsafe_allow_html=False)
                else:
                    c1.caption(f"📞 {phone_display}")
                c1.caption(f"{row['Λεπτομέρεια']}{' | 📝 ' + note_text if note_text else ''}")
                if c2.button("✓ Ok", key=f"btn_{row_key}"):
                    mark_contacted(row_key)
                    st.rerun()
                st.divider()

    if 'adjustments' in tab_idx:
        with tabs[tab_idx['adjustments']]:
            if is_assistant_mode:
                st.info("🙋 Μη διαθέσιμο σε λειτουργία βοηθού (οικονομικά στοιχεία).")
            else:
                st.caption(
                    "⚙️ Γραμμές με **αρνητικό ποσό** στην τρέχουσα καμπάνια — διορθώσεις, επιστροφές, "
                    "ή ακυρώσεις μετά από τιμολόγηση. Αυτές δεν προσμετρώνται πουθενά αλλού στην εφαρμογή, "
                    "αλλά επηρεάζουν το πραγματικό καθαρό αποτέλεσμα."
                )
                if df_adjustments.empty:
                    st.success("✅ Δεν υπάρχουν adjustments (αρνητικά ποσά) σε αυτή την καμπάνια.")
                else:
                    total_adj = df_adjustments['Ποσό_Net'].sum()
                    adj1, adj2 = st.columns(2)
                    adj1.metric("⚙️ Σύνολο Adjustments", f"{len(df_adjustments)}")
                    adj2.metric("💸 Συνολικό Ποσό", f"{total_adj:,.2f} €", delta_color="inverse")

                    adj_search = st.text_input("🔍 Αναζήτηση", key="search_adj", placeholder="Πληκτρολόγησε όνομα...")
                    df_adj_disp = df_adjustments
                    if adj_search:
                        df_adj_disp = df_adj_disp[df_adj_disp['Ονοματεπώνυμο'].astype(str).str.contains(adj_search, case=False, na=False)]

                    st.dataframe(
                        df_adj_disp[['Ονοματεπώνυμο', 'Ποσό_Net', 'Κατάσταση']].rename(
                            columns={'Ποσό_Net': 'Ποσό (€)'}
                        ),
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Ποσό (€)": st.column_config.NumberColumn(format="%.2f €")
                        }
                    )

                    # Ομαδοποίηση ανά μέλος αν κάποιο έχει πάνω από 1 adjustment
                    member_adj_counts = df_adjustments.groupby('Ονοματεπώνυμο')['Ποσό_Net'].agg(['count', 'sum'])
                    multi_adj = member_adj_counts[member_adj_counts['count'] > 1]
                    if not multi_adj.empty:
                        st.markdown("**⚠️ Μέλη με περισσότερα από 1 adjustment:**")
                        for name, row in multi_adj.iterrows():
                            st.caption(f"• {name}: {int(row['count'])} adjustments, σύνολο {row['sum']:,.2f}€")

    with tabs[tab_idx['credit_check']]:
        st.caption(
            "🏦 Παραγγελίες της τρέχουσας καμπάνιας **χωρίς καμία τιμή** στη στήλη Κατάσταση. "
            "Κατά πάσα πιθανότητα έχουν «κολλήσει» σε **πιστωτικό έλεγχο** και δεν έχουν προχωρήσει "
            "ούτε σε «Παρελήφθη» ούτε σε τιμολόγηση — άξιζε να τις παρακολουθείς ξεχωριστά."
        )
        if df_empty_status.empty:
            st.success("✅ Καμία παραγγελία με κενή κατάσταση σε αυτή την καμπάνια.")
        else:
            if is_assistant_mode:
                st.metric("🏦 Σύνολο σε Πιστωτικό Έλεγχο", f"{len(df_empty_status)}")
            else:
                cc1, cc2 = st.columns(2)
                cc1.metric("🏦 Σύνολο σε Πιστωτικό Έλεγχο", f"{len(df_empty_status)}")
                cc_val = df_empty_status['Ποσό_Net'].sum()
                cc2.metric("💰 Συνολικό Ποσό (αν προχωρήσουν)", f"{cc_val:,.2f} €")

            cc_search = st.text_input("🔍 Αναζήτηση", key="search_credit_check", placeholder="Πληκτρολόγησε όνομα...")
            df_cc_disp = df_empty_status
            if cc_search:
                df_cc_disp = df_cc_disp[df_cc_disp['Ονοματεπώνυμο'].astype(str).str.contains(cc_search, case=False, na=False)]

            if is_assistant_mode:
                st.dataframe(
                    df_cc_disp[['Ονοματεπώνυμο', 'Τηλέφωνο']],
                    use_container_width=True, hide_index=True
                )
            else:
                st.dataframe(
                    df_cc_disp[['Ονοματεπώνυμο', 'Ποσό_Net', 'Τηλέφωνο']].rename(
                        columns={'Ποσό_Net': 'Ποσό (€)'}
                    ).sort_values('Ποσό (€)', ascending=False),
                    use_container_width=True, hide_index=True,
                    column_config={
                        "Ποσό (€)": st.column_config.NumberColumn(format="%.2f €")
                    }
                )

    # === ΛΕΙΤΟΥΡΓΙΑ ΒΟΗΘΟΥ: σταματάμε εδώ ===
    # Ό,τι χρειάζεται η βοηθός (Διαγραφές, Additions, Πιστωτικός Έλεγχος, Smart
    # Rank — όλα με αναζήτηση/σημειώσεις/✓Ok) έχει ήδη εμφανιστεί στα tabs παραπάνω.
    # Όλα τα παρακάτω (charts, ensemble forecast breakdown, cohort analysis, tier
    # sparklines, what-if simulator κλπ) είναι analytics που δεν τη χρειάζεται —
    # τα παραλείπουμε για πιο γρήγορη, καθαρή σελίδα.
    if is_assistant_mode:
        st.divider()
        st.info("🙋 Λειτουργία Βοηθού ενεργή — τα detailed analytics/charts είναι κρυμμένα. Απενεργοποίησε το toggle στο sidebar για πλήρη προβολή.")
        st.stop()

    # CHARTS AREA
    st.divider()
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.subheader("🎯 Probability Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = final_forecast,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Πιθανό Κλείσιμο (P50)"},
            delta = {'reference': target_val, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, max(target_val * 1.2, pred_max_potential)], 'tickwidth': 1},
                'bar': {'color': "#d63384"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, target_val], 'color': '#330000'},
                    {'range': [target_val, pred_max_potential], 'color': '#003300'}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': target_val}}))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_chart2:
        st.subheader("📊 Forecast Breakdown")
        fig_pie = px.pie(
            names=['Τιμολογημένα', 'Προς Τιμολόγηση', 'Αναμ. Μέλη', 'Υπόλοιπο Στόχου'],
            values=[
                total_billed_net,
                val_pros_timologisi,
                max(0, expected_remaining),
                max(0, target_val - total_billed_net - val_pros_timologisi - expected_remaining)
            ],
            hole=0.4, template="plotly_dark", 
            color_discrete_sequence=['#28a745', '#ffc107', '#17a2b8', '#dc3545']
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ==========================================
    # FEATURE 1: CAMPAIGN COMPARISON CHART
    # ==========================================
    st.divider()
    st.subheader(f"📈 Campaign Comparison — Ιστορική Εξέλιξη (Σήμερα: {today_day}η ημέρα)")
    st.caption(f"💡 Η γαλάζια γραμμή (◆) δείχνει τι είχε τιμολογηθεί ΕΩΣ την **{today_day}η ημέρα** σε κάθε ιστορική καμπάνια — άμεση σύγκριση με τη σημερινή πρόοδο.")
    
    camp_comp_data = []
    for camp_key in sorted(campaign_stats.keys()):
        s = campaign_stats[camp_key]
        sd_net, sd_mem = get_same_day_stats(camp_key, today_day)
        camp_comp_data.append({
            'Καμπάνια': str(camp_key),
            'Τελικές Πωλήσεις (€)': s['total_net'],
            'Ίδια Ημέρα (€)': sd_net if sd_net > 0 else None,
            'Ενεργά Μέλη': s['unique_members'],
            'Μ.Ο. Καλαθιού (€)': s['avg_basket'],
            'Τύπος': 'Ιστορικό'
        })
    # Προσθήκη τρέχουσας καμπάνιας (πραγματικό + πρόβλεψη)
    camp_comp_data.append({
        'Καμπάνια': str(selected_camp) + ' (Τώρα)',
        'Τελικές Πωλήσεις (€)': total_billed_net,
        'Ίδια Ημέρα (€)': total_billed_net,  # τρέχουσα = same-day by definition
        'Ενεργά Μέλη': unique_orders_count,
        'Μ.Ο. Καλαθιού (€)': total_billed_net / max(1, unique_orders_count),
        'Τύπος': 'Τρέχουσα'
    })
    camp_comp_data.append({
        'Καμπάνια': str(selected_camp) + ' (AI)',
        'Τελικές Πωλήσεις (€)': final_forecast,
        'Ίδια Ημέρα (€)': None,
        'Ενεργά Μέλη': round(expected_final_orders),
        'Μ.Ο. Καλαθιού (€)': final_forecast / max(1, expected_final_orders),
        'Τύπος': 'AI Πρόβλεψη'
    })
    
    df_camp_comp = pd.DataFrame(camp_comp_data)
    
    cc1, cc2 = st.columns([2, 1])
    with cc1:
        color_map = {'Ιστορικό': '#7360f2', 'Τρέχουσα': '#ffc107', 'AI Πρόβλεψη': '#ff69b4'}
        fig_comp = go.Figure()
        for typ, color in color_map.items():
            df_t = df_camp_comp[df_camp_comp['Τύπος'] == typ]
            fig_comp.add_trace(go.Bar(
                x=df_t['Καμπάνια'], y=df_t['Τελικές Πωλήσεις (€)'],
                name=typ, marker_color=color,
                text=[f"{v:,.0f}€" for v in df_t['Τελικές Πωλήσεις (€)']],
                textposition='outside'
            ))
        # Same-day γραμμή για ιστορικές καμπάνιες
        df_hist_sd = df_camp_comp[(df_camp_comp['Τύπος'] == 'Ιστορικό') & (df_camp_comp['Ίδια Ημέρα (€)'].notna())]
        if not df_hist_sd.empty:
            fig_comp.add_trace(go.Scatter(
                x=df_hist_sd['Καμπάνια'],
                y=df_hist_sd['Ίδια Ημέρα (€)'],
                mode='markers+lines',
                name=f'Ίδια Ημέρα ({today_day}η)',
                marker=dict(color='#00e5ff', size=10, symbol='diamond'),
                line=dict(color='#00e5ff', dash='dot', width=2),
            ))
            # Προσθήκη τρέχουσας ημέρας στη γραμμή
            curr_row = df_camp_comp[df_camp_comp['Τύπος'] == 'Τρέχουσα']
            if not curr_row.empty:
                fig_comp.add_trace(go.Scatter(
                    x=curr_row['Καμπάνια'],
                    y=curr_row['Ίδια Ημέρα (€)'],
                    mode='markers',
                    name='Σήμερα',
                    marker=dict(color='#ff69b4', size=14, symbol='star'),
                    showlegend=False
                ))
        fig_comp.add_hline(y=target_val, line_dash="dash", line_color="#ff4444",
                           annotation_text=f"Στόχος: {target_val:,.0f}€",
                           annotation_position="top right")
        fig_comp.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', height=350,
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    with cc2:
        st.markdown("**📊 Στατιστικά Καμπανιών**")
        for row in camp_comp_data:
            icon = "🟣" if row['Τύπος'] == 'Ιστορικό' else ("🟡" if row['Τύπος'] == 'Τρέχουσα' else "💗")
            st.markdown(f"{icon} **{row['Καμπάνια']}**: {row['Τελικές Πωλήσεις (€)']:,.0f}€ | {row['Ενεργά Μέλη']} μέλη")

    # ==========================================
    # FEATURE 1b: TIER PERFORMANCE vs ΙΣΤΟΡΙΚΟ
    # ==========================================
    st.divider()
    st.subheader("💎 Απόδοση ανά Tier — Τρέχουσα vs Ιστορικό")

    tier_perf_data = []
    for t in ['DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE']:
        hist_val = _dynamic_tier_baskets.get(t, 0)
        curr_val = curr_tier_baskets.get(t, 0)
        # Τρέχον πλήθος μελών που έχουν τιμολογηθεί για αυτό το tier
        curr_count = len(df_billed_only[df_billed_only['_Tier'] == t])
        # Ιστορικό πλήθος (μέσος όρος από όλες τις καμπάνιες)
        hist_count_vals = []
        for ck in hist_camp_sorted:
            df_ck = df_sales_all[df_sales_all[camp_col] == ck].copy()
            df_ck['_StatusTmp'] = df_ck[status_col_global].apply(remove_accents).str.upper()
            df_ck = df_ck[~df_ck['_StatusTmp'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
            bm_ck = df_ck['_StatusTmp'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
            df_ck_billed = df_ck[bm_ck & (df_ck['Ποσό_Net'] > 0.01)].copy()
            df_ck_billed['_Tier'] = df_ck_billed['NameClean'].map(name_to_tier_curr).fillna('STANDARD')
            cnt = len(df_ck_billed[df_ck_billed['_Tier'] == t]['NameClean'].unique())
            if cnt > 0:
                hist_count_vals.append(cnt)
        hist_count_avg = round(np.mean(hist_count_vals)) if hist_count_vals else 0

        if hist_val > 0 or curr_val > 0:
            tier_perf_data.append({
                'Tier': t,
                'Τρέχον Καλάθι (€)': curr_val,
                'Ιστορικό Καλάθι (€)': hist_val,
                'Τρέχον Πλήθος': curr_count,
                'Ιστορικό Πλήθος (μ.ο.)': hist_count_avg,
            })

    if tier_perf_data:
        df_tier_perf = pd.DataFrame(tier_perf_data)

        tp1, tp2 = st.columns(2)

        with tp1:
            st.markdown("**Μ.Ο. Καλαθιού ανά Tier**")
            fig_tier_basket = go.Figure()
            fig_tier_basket.add_trace(go.Bar(
                name='Ιστορικό μ.ο.',
                x=df_tier_perf['Tier'],
                y=df_tier_perf['Ιστορικό Καλάθι (€)'],
                marker_color='#7360f2',
                text=[f"{v:,.0f}€" if v > 0 else "—" for v in df_tier_perf['Ιστορικό Καλάθι (€)']],
                textposition='outside'
            ))
            fig_tier_basket.add_trace(go.Bar(
                name='Τρέχουσα',
                x=df_tier_perf['Tier'],
                y=df_tier_perf['Τρέχον Καλάθι (€)'],
                marker_color='#ffc107',
                text=[f"{v:,.0f}€" if v > 0 else "—" for v in df_tier_perf['Τρέχον Καλάθι (€)']],
                textposition='outside'
            ))
            fig_tier_basket.update_layout(
                barmode='group', template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(t=30, b=0, l=0, r=0),
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            st.plotly_chart(fig_tier_basket, use_container_width=True)

        with tp2:
            st.markdown("**Ενεργά Μέλη ανά Tier**")
            fig_tier_count = go.Figure()
            fig_tier_count.add_trace(go.Bar(
                name='Ιστορικό μ.ο.',
                x=df_tier_perf['Tier'],
                y=df_tier_perf['Ιστορικό Πλήθος (μ.ο.)'],
                marker_color='#7360f2',
                text=df_tier_perf['Ιστορικό Πλήθος (μ.ο.)'],
                textposition='outside'
            ))
            fig_tier_count.add_trace(go.Bar(
                name='Τρέχουσα',
                x=df_tier_perf['Tier'],
                y=df_tier_perf['Τρέχον Πλήθος'],
                marker_color='#ffc107',
                text=df_tier_perf['Τρέχον Πλήθος'],
                textposition='outside'
            ))
            fig_tier_count.update_layout(
                barmode='group', template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(t=30, b=0, l=0, r=0),
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            st.plotly_chart(fig_tier_count, use_container_width=True)

        # Συνοπτικός πίνακας με delta
        st.markdown("**📋 Συνοπτική Σύγκριση**")
        rows_html = ""
        for _, r in df_tier_perf.iterrows():
            icon = tier_icons.get(r['Tier'], '•')
            if r['Ιστορικό Καλάθι (€)'] > 0 and r['Τρέχον Καλάθι (€)'] > 0:
                d = (r['Τρέχον Καλάθι (€)'] - r['Ιστορικό Καλάθι (€)']) / r['Ιστορικό Καλάθι (€)'] * 100
                col = "#28a745" if d >= 0 else "#dc3545"
                arrow = "↑" if d >= 0 else "↓"
                delta_str = f"<span style='color:{col}'>{arrow}{abs(d):.0f}%</span>"
            else:
                delta_str = "<span style='color:#888'>—</span>"

            cnt_d = r['Τρέχον Πλήθος'] - r['Ιστορικό Πλήθος (μ.ο.)']
            cnt_col = "#28a745" if cnt_d >= 0 else "#dc3545"
            cnt_str = f"<span style='color:{cnt_col}'>{cnt_d:+d}</span>" if r['Ιστορικό Πλήθος (μ.ο.)'] > 0 else "—"

            rows_html += (
                f"<tr>"
                f"<td>{icon} <b>{r['Tier']}</b></td>"
                f"<td>{r['Τρέχον Καλάθι (€)']:,.0f}€</td>"
                f"<td>{r['Ιστορικό Καλάθι (€)']:,.0f}€</td>"
                f"<td>{delta_str}</td>"
                f"<td>{r['Τρέχον Πλήθος']}</td>"
                f"<td>{r['Ιστορικό Πλήθος (μ.ο.)']}</td>"
                f"<td>{cnt_str}</td>"
                f"</tr>"
            )
        st.markdown(f"""
        <table style='width:100%;border-collapse:collapse;font-size:13px;'>
          <thead>
            <tr style='color:#94a3b8;border-bottom:1px solid #333;'>
              <th style='text-align:left;padding:6px'>Tier</th>
              <th>Καλάθι Τώρα</th><th>Καλάθι Ιστορικό</th><th>Δ% Καλάθι</th>
              <th>Μέλη Τώρα</th><th>Μέλη Ιστ.</th><th>Δ Μέλη</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

    # ==========================================
    # FEATURE 2: TOP CONTRIBUTORS LEADERBOARD (Feature 9 enhanced)
    # ==========================================
    st.divider()
    st.subheader("🏆 Top Contributors — Leaderboard")

    if not df_billed_only.empty:
        top10 = df_billed_only.sort_values('Ποσό_Net', ascending=False).head(10).reset_index(drop=True)
        max_net = float(top10['Ποσό_Net'].max())

        for rank, (_, row) in enumerate(top10.iterrows(), 1):
            pct = row['Ποσό_Net'] / max(1, max_net)
            medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
            bar_filled = int(pct * 30)
            bar_str = "█" * bar_filled + "░" * (30 - bar_filled)
            # Feature 9: ιστορικό μέλους
            n = row['NameClean']
            hist_camps = sum(1 for ck in hist_camp_sorted
                             if n in set(df_sales_all[df_sales_all[camp_col]==ck]['NameClean']))
            hist_vals = [df_sales_all[(df_sales_all[camp_col]==ck) & (df_sales_all['NameClean']==n)]['Ποσό_Net'].sum()
                         for ck in hist_camp_sorted]
            hist_vals = [v for v in hist_vals if v > 0]
            best_val = max(hist_vals) if hist_vals else 0
            trend_arrow = ""
            if len(hist_vals) >= 2:
                trend_arrow = " ↑" if hist_vals[-1] > hist_vals[-2] else " ↓"
            hist_str = f" | {hist_camps}/{len(hist_camp_sorted)} καμπ. | Best: {best_val:,.0f}€{trend_arrow}" if hist_camps > 0 else ""
            st.markdown(
                f"{medal} **{row['Ονοματεπώνυμο']}** &nbsp;&nbsp;"
                f"`{bar_str}` &nbsp;&nbsp; **{row['Ποσό_Net']:,.0f}€**"
                f"<span style='color:#888;font-size:12px'>{hist_str}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("Δεν υπάρχουν τιμολογημένες παραγγελίες ακόμα.")

    # ==========================================
    # FEATURE 4: COHORT ANALYSIS
    # ==========================================
    st.divider()
    st.subheader("👥 Cohort Ανάλυση — Retention Μελών")

    if len(hist_camp_sorted) >= 2:
        cohort_data = []
        current_actives = real_billed_names
        for ck in hist_camp_sorted:
            df_ck = df_sales_all[df_sales_all[camp_col] == ck]
            df_ck_st = df_ck[df_ck[status_col_global].apply(remove_accents).str.upper().str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)]
            prev_actives = set(df_ck_st[df_ck_st['Ποσό_Net'] > 0]['NameClean'])
            returning = len(current_actives & prev_actives)
            total_curr = len(current_actives) if current_actives else 1
            new_members = len(current_actives - prev_actives)
            cohort_data.append({
                'Καμπάνια': str(ck),
                'Επιστρέφοντες': returning,
                'Νέοι': new_members,
                '% Retention': round(returning / max(1, total_curr) * 100, 1)
            })

        df_cohort = pd.DataFrame(cohort_data)
        co1, co2 = st.columns(2)
        with co1:
            fig_cohort = go.Figure()
            fig_cohort.add_trace(go.Bar(name='Επιστρέφοντες', x=df_cohort['Καμπάνια'],
                                         y=df_cohort['Επιστρέφοντες'], marker_color='#7360f2'))
            fig_cohort.add_trace(go.Bar(name='Νέοι', x=df_cohort['Καμπάνια'],
                                         y=df_cohort['Νέοι'], marker_color='#ffc107'))
            fig_cohort.update_layout(barmode='stack', template='plotly_dark', height=280,
                                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      margin=dict(t=10,b=0,l=0,r=0),
                                      legend=dict(orientation='h', yanchor='bottom', y=1.02))
            st.plotly_chart(fig_cohort, use_container_width=True)
        with co2:
            fig_ret = go.Figure(go.Scatter(
                x=df_cohort['Καμπάνια'], y=df_cohort['% Retention'],
                mode='lines+markers+text', text=[f"{v}%" for v in df_cohort['% Retention']],
                textposition='top center', line=dict(color='#ff69b4', width=2),
                marker=dict(size=10, color='#ff69b4')
            ))
            fig_ret.update_layout(template='plotly_dark', height=280,
                                   paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   margin=dict(t=10,b=0,l=0,r=0),
                                   yaxis=dict(range=[0,110], title='% Retention'))
            st.caption("📊 % Retention: πόσοι από τους τρέχοντες ήταν active και σε ιστορική καμπάνια")
            st.plotly_chart(fig_ret, use_container_width=True)

        # === TEAM HEALTH SCORE ===
        # Συνολικός δείκτης 0-100: retention + tier growth + removal rate + member growth
        avg_retention = float(df_cohort['% Retention'].mean())
        removal_rate = len(df_rem_clean) / max(1, len(df_members_raw)) * 100
        member_growth = (len(df_members_raw) - len(historical_all_names.intersection(current_member_names))) if 'historical_all_names' in dir() else 0
        avg_growth_pct = ((hist_totals[-1] - hist_totals[0]) / max(1, hist_totals[0]) * 100 / max(1, len(hist_totals)-1)) if len(hist_totals) >= 2 else 0

        retention_score = min(100, avg_retention)
        removal_score = max(0, 100 - removal_rate * 3)  # κάθε 1% διαγραφών -3 πόντοι
        growth_score = min(100, max(0, 50 + avg_growth_pct * 3))  # 0% growth = 50, +10% = 80

        team_health = round(retention_score * 0.4 + removal_score * 0.3 + growth_score * 0.3)
        health_color = "#28a745" if team_health >= 70 else ("#ffc107" if team_health >= 50 else "#dc3545")
        health_label = "Υγιής" if team_health >= 70 else ("Μέτρια" if team_health >= 50 else "Χρειάζεται προσοχή")

        st.markdown(
            f"<div style='padding:14px 18px;border-radius:10px;background:var(--surface-1,#1e1e2e);"
            f"border:1px solid {health_color};margin:14px 0;'>"
            f"<span style='font-size:14px;color:#888;'>🏥 TEAM HEALTH SCORE</span><br>"
            f"<span style='font-size:28px;font-weight:bold;color:{health_color};'>{team_health}/100</span>"
            f"<span style='font-size:14px;color:{health_color};margin-left:10px;'>{health_label}</span><br>"
            f"<span style='font-size:12px;color:#888;'>Retention: {avg_retention:.0f}% | Διαγραφές: {removal_rate:.1f}% | Ανάπτυξη: {avg_growth_pct:+.1f}%/καμπάνια</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # === YEAR-OVER-YEAR ΣΥΓΚΡΙΣΗ ===
    # Αν υπάρχουν αρκετά δεδομένα (12+ ιστορικές καμπάνιες), σύγκριση με ίδιο μήνα πέρυσι
    try:
        curr_month = int(str(selected_camp)[-2:])
        curr_year = int(str(selected_camp)[:4])
        last_year_camp = f"{curr_year-1}{curr_month:02d}"
        last_year_stats = campaign_stats.get(int(last_year_camp)) or campaign_stats.get(last_year_camp)
        if last_year_stats and len(historical_camps) >= 10:
            yoy_delta = (total_billed_net - last_year_stats['total_net']) / max(1, last_year_stats['total_net']) * 100
            yoy_color = "#28a745" if yoy_delta >= 0 else "#dc3545"
            st.markdown(
                f"<div style='padding:10px 16px;border-radius:8px;background:var(--surface-1,#1e1e2e);"
                f"border:1px solid #333;margin-bottom:14px;font-size:13px;'>"
                f"📅 <b>Year-over-Year:</b> {total_billed_net:,.0f}€ φέτος vs {last_year_stats['total_net']:,.0f}€ πέρυσι ({last_year_camp}) — "
                f"<span style='color:{yoy_color}'>{yoy_delta:+.1f}%</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    except Exception:
        pass

    # ==========================================
    # FEATURE 3: FORECAST ACCURACY TRACKER
    # ==========================================
    if len(forecast_history) >= 2:
        st.divider()
        st.subheader("🎯 Forecast Accuracy — Εξέλιξη Πρόβλεψης")
        fh_dates = sorted(forecast_history.keys())
        fh_vals  = [forecast_history[d] for d in fh_dates]
        fig_fh = go.Figure()
        fig_fh.add_trace(go.Scatter(
            x=fh_dates, y=fh_vals, mode='lines+markers',
            name='AI Forecast P50', line=dict(color='#ff69b4', width=2),
            marker=dict(size=8)
        ))
        if target_val > 0:
            fig_fh.add_hline(y=target_val, line_dash='dash', line_color='#ffc107',
                              annotation_text=f"Στόχος {target_val:,.0f}€", annotation_position="top left")
        fig_fh.add_hline(y=total_billed_net, line_dash='dot', line_color='#28a745',
                          annotation_text=f"Τρέχον {total_billed_net:,.0f}€", annotation_position="bottom right")
        fig_fh.update_layout(template='plotly_dark', height=260,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              margin=dict(t=10,b=0,l=0,r=0),
                              xaxis_title='Ημερομηνία', yaxis_title='Πρόβλεψη (€)')
        st.plotly_chart(fig_fh, use_container_width=True)
        st.caption("Κάθε σημείο = η AI πρόβλεψη εκείνης της ημέρας. Παρατηρείς πώς σταθεροποιείται καθώς προχωρά η καμπάνια.")

    # ==========================================
    # FEATURE 10: SPARKLINE ανά TIER
    # ==========================================
    st.divider()
    st.subheader("📈 Tier Sparklines — Εξέλιξη Πωλήσεων ανά Tier")

    spark_data = {t: [] for t in tier_order}
    for ck in hist_camp_sorted:
        df_ck2 = df_sales_all[df_sales_all[camp_col] == ck].copy()
        df_ck2['_st'] = df_ck2[status_col_global].apply(remove_accents).str.upper()
        df_ck2 = df_ck2[~df_ck2['_st'].str.contains('ΑΚΥΡ|ΑΠΟΡ|CANCEL|REJECT', na=False)]
        bm2 = df_ck2['_st'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
        df_ck2_b = df_ck2[bm2 & (df_ck2['Ποσό_Net'] > 0)].copy()
        df_ck2_b['_Tier'] = df_ck2_b['NameClean'].map(name_to_tier_curr).fillna('STANDARD')
        member_sums = df_ck2_b.groupby(['_Tier','NameClean'])['Ποσό_Net'].sum().reset_index()
        tier_avgs = member_sums.groupby('_Tier')['Ποσό_Net'].mean()
        for t in tier_order:
            spark_data[t].append(tier_avgs.get(t, None))

    # Προσθήκη τρέχουσας καμπάνιας
    for t in tier_order:
        spark_data[t].append(curr_tier_baskets.get(t, None))
    x_labels = [str(k) for k in hist_camp_sorted] + [str(selected_camp) + ' ▶']

    fig_spark = go.Figure()
    spark_colors = {'DIAMOND':'#00e5ff','PLATINUM':'#c0c0c0','GOLD':'#ffd700','SILVER':'#a8a9ad','BRONZE':'#cd7f32'}
    for t in tier_order:
        vals = spark_data[t]
        if any(v is not None for v in vals):
            fig_spark.add_trace(go.Scatter(
                x=x_labels, y=vals, mode='lines+markers',
                name=f"{tier_icons.get(t,'')} {t}",
                line=dict(color=spark_colors.get(t,'#fff'), width=2),
                marker=dict(size=8), connectgaps=True
            ))
    fig_spark.update_layout(template='plotly_dark', height=300,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             margin=dict(t=10,b=0,l=0,r=0),
                             yaxis_title='Μ.Ο. Καλαθιού (€)',
                             legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig_spark, use_container_width=True)
    st.caption("Εξέλιξη μέσου καλαθιού ανά tier σε όλες τις καμπάνιες. Το ▶ = τρέχουσα.")

    # ==========================================
    # FEATURE 11: WHAT-IF SIMULATOR
    # ==========================================
    st.divider()
    st.subheader("🔬 What-If Simulator")
    wf1, wf2, wf3 = st.columns(3)
    with wf1:
        extra_diamond = st.slider("💎 Επιπλέον Diamond", 0, 10, 0)
    with wf2:
        extra_gold = st.slider("🥇 Επιπλέον Gold", 0, 20, 0)
    with wf3:
        extra_silver = st.slider("🪙 Επιπλέον Silver/Bronze", 0, 30, 0)

    whatif_gain = (
        extra_diamond * _dynamic_tier_baskets.get('DIAMOND', _TIER_FALLBACK_DEFAULTS['DIAMOND']) +
        extra_gold    * _dynamic_tier_baskets.get('GOLD',    _TIER_FALLBACK_DEFAULTS['GOLD']) +
        extra_silver  * _dynamic_tier_baskets.get('SILVER',  _TIER_FALLBACK_DEFAULTS['SILVER'])
    )
    whatif_forecast = final_forecast + whatif_gain
    whatif_gap = whatif_forecast - target_val

    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("📊 Νέα Πρόβλεψη", f"{whatif_forecast:,.0f}€",
               delta=f"+{whatif_gain:,.0f}€ από ενεργοποιήσεις")
    wc2.metric("🎯 Gap vs Στόχο", f"{abs(whatif_gap):,.0f}€",
               delta="✅ Στόχος επιτυγχάνεται" if whatif_gap >= 0 else f"Ακόμα {abs(whatif_gap):,.0f}€ μακριά")
    wc3.metric("👥 Συνολικά Νέα Άτομα", f"+{extra_diamond+extra_gold+extra_silver}")
    if whatif_gain > 0:
        st.caption(f"💡 Αν ενεργοποιηθούν {extra_diamond+extra_gold+extra_silver} επιπλέον μέλη, η πρόβλεψη αυξάνεται κατά **{whatif_gain:,.0f}€** (βάσει ιστορικού μ.ο. καλαθιού ανά tier).")

    # ==========================================
    # FEATURE 3: DAILY BURN RATE HEATMAP
    # ==========================================
    st.divider()
    st.subheader("📅 Daily Burn Rate — Εκτίμηση Ημερήσιου Στόχου")
    
    br1, br2, br3, br4 = st.columns(4)

    # === ΔΙΟΡΘΩΣΗ: σωστός υπολογισμός ρυθμών ===
    # Πρόβλημα 1: ο "Τρέχων Ρυθμός" ήταν μέσος όρος ΟΛΟΥ του μήνα (total/days_passed),
    # όχι ο πραγματικός σημερινός ρυθμός — παραπλανητικό label.
    # Πρόβλημα 2: ο "Απαιτούμενος Ρυθμός" διαιρούσε με days_left_precise (κλασματικές
    # ώρες), οπότε όταν απομένουν π.χ. 6 ώρες, remaining/0.25 εκτόξευε το νούμερο σε
    # "ρυθμό/μέρα" εξωπραγματικό — σωστό μαθηματικά για extrapolation αλλά λάθος ως label.
    hours_passed_total = max(1.0, days_passed * 24 - (hours_left_precise if not is_closed else 0))

    # Τρέχων ρυθμός: μέσος όρος ΣΗΜΕΡΙΝΗΣ ημέρας μόνο (όχι όλου του μήνα)
    # Υπολογισμός πωλήσεων που έγιναν ΣΗΜΕΡΑ (αν υπάρχει στήλη ημερομηνίας)
    today_sales = 0.0
    if date_col and '_OrderDate' in df_sales_all.columns:
        df_today = df_sales_all[df_sales_all[camp_col] == selected_camp].copy()
        df_today['_OrderDate'] = pd.to_datetime(df_today['_OrderDate'], errors='coerce')
        df_today['_st3'] = df_today[status_col_global].apply(remove_accents).str.upper()
        bm3 = df_today['_st3'].str.contains('ΤΙΜΟΛΟΓ|ΠΑΡΑΔΟΔ|ΠΑΡΑΔΟΘ', na=False)
        today_sales = df_today[bm3 & (df_today['_OrderDate'].dt.date == date.today())]['Ποσό_Net'].sum()

    if today_sales > 0:
        current_daily_rate = today_sales
        current_rate_label = "Σήμερα"
    else:
        # Fallback: μέσος όρος ολόκληρης της καμπάνιας ως τώρα (ξεκάθαρο label)
        current_daily_rate = total_billed_net / max(1, days_passed)
        current_rate_label = "Μ.Ο. Καμπάνιας"

    # Απαιτούμενος ρυθμός: εκφράζεται σωστά ανάλογα με το πόσος χρόνος απομένει
    if is_closed:
        required_daily_rate = 0.0
        required_rate_unit = "—"
    elif days_left_precise < 1.0:
        # Λιγότερο από 1 μέρα απομένει — δείξε ανά ΩΡΑ, όχι ανά "μέρα"
        required_daily_rate = remaining_to_target / max(0.1, hours_left_precise)
        required_rate_unit = "€/ώρα"
    else:
        required_daily_rate = remaining_to_target / max(1.0, days_left_precise)
        required_rate_unit = "€/μέρα"

    feasibility_ratio = required_daily_rate / max(1, current_daily_rate) if required_rate_unit == "€/μέρα" else \
                         (required_daily_rate * 24) / max(1, current_daily_rate)  # κανονικοποίηση σε ίδια μονάδα για σύγκριση
    
    if feasibility_ratio <= 1.0:
        burn_color = "#28a745"
        burn_label = "✅ Εύκολο"
    elif feasibility_ratio <= 1.5:
        burn_color = "#ffc107"
        burn_label = "⚡ Εφικτό"
    elif feasibility_ratio <= 2.5:
        burn_color = "🔶"
        burn_label = "⚠️ Δύσκολο"
    else:
        burn_color = "#dc3545"
        burn_label = "🔥 Κρίσιμο"
    
    br1.metric("📅 Μέρες Που Πέρασαν", f"{days_passed}")
    br2.metric("⏳ Μέρες που Απομένουν", f"{days_left}" if days_left_precise >= 1 else f"{hours_left_precise:.1f}ω")
    br3.metric(f"💰 Τρέχων Ρυθμός ({current_rate_label})", f"{current_daily_rate:,.0f}€")
    br4.metric(f"🎯 Απαιτούμενος Ρυθμός", f"{required_daily_rate:,.0f}{required_rate_unit}",
               delta=f"{feasibility_ratio:.1f}× {burn_label}")
    
    # Οπτικό heatmap ημερών
    if campaign_duration_est > 0:
        st.markdown("**Πρόοδος Καμπάνιας (ανά μέρα):**")
        day_html = ""
        for d in range(1, campaign_duration_est + 1):
            # ΔΙΟΡΘΩΣΗ: το days_passed ήδη μετράει ΣΥΜΠΕΡΙΛΑΜΒΑΝΟΜΕΝΗΣ της σημερινής
            # ημέρας (π.χ. σήμερα 27/07 από αρχή μήνα 1/07 → days_passed=27). Ο παλιός
            # κώδικας έλεγχε `d <= days_passed` για "περασμένες" ΚΑΙ ξεχωριστά
            # `d == days_passed + 1` για "σήμερα" — αυτό σήμαινε ότι η σημερινή μέρα (27)
            # εμφανιζόταν ως ήδη περασμένη, και η ΕΠΟΜΕΝΗ μέρα (28) επισημαινόταν
            # λανθασμένα ως "Σήμερα". Τώρα: d < days_passed = περασμένη,
            # d == days_passed = σήμερα, d > days_passed = μέλλον.
            if d < days_passed:
                # Μέρα που πέρασε — χρώμα ανάλογα με ρυθμό
                daily_val = total_billed_net / max(1, days_passed)
                target_daily = target_val / campaign_duration_est
                intensity = min(1.0, daily_val / max(1, target_daily))
                r = int(40 + intensity * 60)
                g = int(160 + intensity * 80)
                b = int(40)
                bg = f"rgb({r},{g},{b})"
                day_html += f"<span title='Ημέρα {d}' style='display:inline-block;width:22px;height:22px;background:{bg};border-radius:4px;margin:2px;font-size:10px;line-height:22px;text-align:center;color:white;'>{d}</span>"
            elif d == days_passed:
                # Σήμερα
                day_html += f"<span title='Σήμερα' style='display:inline-block;width:22px;height:22px;background:#ff69b4;border-radius:4px;margin:2px;font-size:10px;line-height:22px;text-align:center;color:white;border:2px solid white;'>{d}</span>"
            else:
                # Μέλλον
                day_html += f"<span title='Ημέρα {d}' style='display:inline-block;width:22px;height:22px;background:rgba(255,255,255,0.08);border-radius:4px;margin:2px;font-size:10px;line-height:22px;text-align:center;color:#666;'>{d}</span>"
        st.markdown(f"<div style='line-height:2;'>{day_html}</div>", unsafe_allow_html=True)
        st.caption("🟢 Ημέρες με καλό ρυθμό | 💗 Σήμερα | ⬜ Εναπομένουσες ημέρες")

    # ==========================================
    # ΑΝΑΛΥΤΙΚΗ ΑΝΑΦΟΡΑ ΚΑΜΠΑΝΙΑΣ (για παρουσιάσεις)
    # Συλλέγει ΟΛΑ τα διαθέσιμα νούμερα που υπολογίστηκαν σε όλη τη διάρκεια
    # του rendering. Χρησιμοποιεί locals().get() ώστε αν κάποια μεταβλητή δεν
    # υπολογίστηκε (π.χ. γιατί κάποιο section δεν είχε αρκετά δεδομένα), το
    # αντίστοιχο section του report απλά παραλείπεται αντί να σκάσει.
    # ==========================================
    st.divider()
    st.subheader("📑 Αναφορά Καμπάνιας — Ανάλυση σε Βάθος")
    st.caption("Ημερήσια εξέλιξη πωλήσεων & ενεργών μελών από την αρχή της καμπάνιας, εξέλιξη πρόβλεψης, adjustments, tier ανάλυση, retention και top performers — σε ένα PDF έτοιμο για παρουσίαση.")

    _lv = locals()

    # === DAILY TIMELINE: πωλήσεις & ενεργά μέλη ΑΝΑ ΗΜΕΡΑ από την αρχή της καμπάνιας ===
    daily_timeline = None
    if date_col and '_OrderDate' in df_sales_all.columns:
        df_tl = df_curr[billed_status_mask & positive_orders_mask].copy()
        df_tl['_OrderDate'] = pd.to_datetime(df_sales_all.loc[df_tl.index, '_OrderDate'], errors='coerce')
        df_tl = df_tl.dropna(subset=['_OrderDate'])
        if not df_tl.empty:
            df_tl['_Day'] = df_tl['_OrderDate'].dt.date
            daily_sales = df_tl.groupby('_Day')['Ποσό_Net'].sum().sort_index()
            daily_names = df_tl.groupby('_Day')['NameClean'].apply(set).sort_index()

            daily_timeline = []
            cum_sales = 0.0
            seen_names = set()
            # Same-day ιστορικό για σύγκριση ανά ημέρα (χρησιμοποιεί την ήδη υπάρχουσα get_same_day_stats)
            for d, sales_that_day in daily_sales.items():
                cum_sales += sales_that_day
                seen_names |= daily_names.get(d, set())
                day_of_month = d.day
                hist_sd_net, hist_sd_mem = (0, 0)
                try:
                    if same_day_nets:  # χρησιμοποιούμε το ήδη υπολογισμένο EWMA ιστορικό ΕΩΣ αυτή τη μέρα
                        # Προσεγγιστικό ιστορικό ΕΩΣ την ημέρα d, βάσει ίδιου μηχανισμού με get_same_day_stats
                        sd_vals = []
                        for ck in hist_camp_sorted:
                            v, _m = get_same_day_stats(ck, day_of_month)
                            if v > 0:
                                sd_vals.append(v)
                        if sd_vals:
                            hist_sd_net = float(np.mean(sd_vals))
                except Exception:
                    pass
                daily_timeline.append({
                    'date': d.strftime('%d/%m'),
                    'daily_sales': sales_that_day,
                    'cum_sales': cum_sales,
                    'daily_actives': len(daily_names.get(d, set())),
                    'cum_actives': len(seen_names),
                    'hist_same_day': hist_sd_net,
                })

    # === FORECAST TIMELINE: εξέλιξη της AI πρόβλεψης ημέρα-με-ημέρα ===
    forecast_timeline = None
    if forecast_history:
        fh_sorted = sorted(forecast_history.items())
        forecast_timeline = [{'date': d, 'forecast': v} for d, v in fh_sorted]

    # === ADJUSTMENTS σύνοψη ===
    adjustments_summary = None
    if not df_adjustments.empty:
        adjustments_summary = {
            'count': len(df_adjustments),
            'total': float(df_adjustments['Ποσό_Net'].sum()),
            'rows': [
                {'name': r['Ονοματεπώνυμο'], 'amount': r['Ποσό_Net']}
                for _, r in df_adjustments.sort_values('Ποσό_Net').head(15).iterrows()
            ]
        }

    tier_breakdown_data = None
    if _lv.get('curr_tier_baskets') and _lv.get('_dynamic_tier_baskets'):
        tier_breakdown_data = []
        for t in ['DIAMOND', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE']:
            curr_v = _lv['curr_tier_baskets'].get(t)
            hist_v = _lv['_dynamic_tier_baskets'].get(t)
            if curr_v or hist_v:
                cnt = len(_lv['df_billed_only'][_lv['df_billed_only']['_Tier'] == t]) if _lv.get('df_billed_only') is not None else 0
                tier_breakdown_data.append({'tier': t, 'curr': curr_v or 0, 'hist': hist_v or 0, 'count': cnt})

    top_performers_data = None
    if _lv.get('top10') is not None and not _lv['top10'].empty:
        top_performers_data = [
            {'name': r['Ονοματεπώνυμο'], 'value': r['Ποσό_Net']} for _, r in _lv['top10'].iterrows()
        ]

    report_data = {
        'campaign': str(selected_camp),
        'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'status_label': "✅ Κλειστή" if is_closed else ("🔴 Τελευταία Ημέρα" if is_final_day else "🟢 Σε Εξέλιξη"),
        'total_sales': total_billed_net,
        'target': target_val if target_val > 0 else None,
        'achievement_pct': (total_billed_net / target_val * 100) if target_val > 0 else None,
        'forecast': final_forecast if not is_closed else None,
        'actives': unique_orders_count,
        'goal_actives': _lv.get('goal_actives'),
        'no_order_count': len(_lv.get('df_no_order', [])),
        'vip_missing': _lv.get('missing_vip_count', 0),
        'removals_count': len(_lv.get('df_rem_clean', [])),
        'goal_removals': _lv.get('goal_removals'),
        'mom_delta': _lv.get('mom_sales_delta'),
        'best_camp_total': _lv.get('best_camp_total') if _lv.get('best_camp_total', 0) > 0 else None,
        'yoy_delta': _lv.get('yoy_delta'),
        'tier_breakdown': tier_breakdown_data,
        'team_health': _lv.get('team_health'),
        'retention_pct': _lv.get('avg_retention'),
        'winbacks_count': len(_lv.get('df_winbacks', [])) if _lv.get('df_winbacks') is not None else None,
        'winbacks_value': _lv.get('wb_total_value'),
        'top_performers': top_performers_data,
        'calibration_factor': _lv.get('calibration_factor') if _lv.get('calibration_factor', 1.0) != 1.0 else None,
        'daily_timeline': daily_timeline,
        'forecast_timeline': forecast_timeline,
        'adjustments': adjustments_summary,
        'days_passed': days_passed,
        'days_left': days_left,
        'campaign_duration_est': campaign_duration_est,
    }

    try:
        report_pdf_bytes = create_campaign_report_pdf(report_data)
        if report_pdf_bytes:
            st.download_button(
                label="📥 Κατέβασμα Αναλυτικής Αναφοράς (PDF)",
                data=report_pdf_bytes,
                file_name=f"Avon_Report_{selected_camp}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ Για δημιουργία PDF αναφοράς εγκαταστήστε το fpdf2: `pip install fpdf2`")
    except Exception as report_err:
        st.warning(f"Δεν κατέστη δυνατή η δημιουργία του report: {report_err}")

    # ==========================================
    # ΛΙΣΤΑ ΕΠΙΚΟΙΝΩΝΙΑΣ ΓΙΑ ΒΟΗΘΟ
    # Ενιαίο Excel με ΟΛΕΣ τις λίστες που χρειάζονται τηλεφωνική επικοινωνία —
    # έτοιμο να προωθηθεί σε βοηθό για κλήσεις. Χτίζεται εδώ (τέλος του script)
    # επειδή χρειάζεται δεδομένα από tabs που υπολογίζονται αργότερα στη ροή
    # (Διαγραφές, VIP Watchlist, Καλές Διαγραφές Ιστορικού, Πιστωτικός Έλεγχος).
    # ==========================================
    st.divider()
    st.subheader("📞 Λίστα Επικοινωνίας — για τη Βοηθό σου")
    st.caption("Ένα αρχείο με όλες τις λίστες που χρειάζονται τηλεφωνική επικοινωνία, ταξινομημένες κατά προτεραιότητα, έτοιμο να προωθήσεις.")

    def build_contact_list_export():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 1. Διαγραφές — πιο ελπιδοφόρες πρώτα
            if not df_rem_clean.empty:
                df_out = df_rem_clean.copy()
                df_out['Πιθανότητα Επιστροφής'] = (df_out['ReturnProb'] * 100).round(0).astype(int).astype(str) + '%'
                df_out[['Ονοματεπώνυμο', 'Τηλέφωνο', 'Πιθανότητα Επιστροφής']]\
                    .to_excel(writer, sheet_name='Διαγραφές - Κάλεσε', index=False)

            # 2. VIP που δεν έχουν παραγγείλει μέσα στον μήνα
            if not df_missing_vips.empty:
                df_out = df_missing_vips.copy()
                df_out['Εκτίμηση Αξίας'] = df_out['Ονοματεπώνυμο'].apply(get_manual_fallback).round(0)
                df_out[['Ονοματεπώνυμο', phone_col_main, 'Tier', 'Εκτίμηση Αξίας']]\
                    .rename(columns={phone_col_main: 'Τηλέφωνο'})\
                    .sort_values('Εκτίμηση Αξίας', ascending=False)\
                    .to_excel(writer, sheet_name='VIP Χωρίς Παραγγελία', index=False)

            # 3. Καλές Διαγραφές Ιστορικού — παλιά καλά μέλη εκτός τρέχουσας λίστας
            if not df_good_past_removals.empty:
                df_good_past_removals[['Ονοματεπώνυμο', 'Τηλέφωνο', 'Μ.Ο. Καλάθι', 'Παραγγελίες']]\
                    .sort_values('Μ.Ο. Καλάθι', ascending=False)\
                    .to_excel(writer, sheet_name='Καλές Διαγραφές Ιστορικού', index=False)

            # 4. Πιστωτικός Έλεγχος — κολλημένες παραγγελίες
            if not df_empty_status.empty:
                df_empty_status[['Ονοματεπώνυμο', 'Τηλέφωνο', 'Ποσό_Net']]\
                    .rename(columns={'Ποσό_Net': 'Ποσό (€)'})\
                    .sort_values('Ποσό (€)', ascending=False)\
                    .to_excel(writer, sheet_name='Πιστωτικός Έλεγχος', index=False)

            # 5. Top Smart Rank — υψηλής αξίας μέλη που δεν έχουν παραγγείλει ακόμα
            if not df_potentials.empty:
                sr_rows = []
                for _, r in df_potentials.head(50).iterrows():
                    n = r['NameClean']
                    pred = member_predictions.get(n, {})
                    val = pred.get('predicted', 0)
                    if val > 30:
                        sr_rows.append({
                            'Ονοματεπώνυμο': r['Ονοματεπώνυμο'],
                            'Τηλέφωνο': r.get(phone_col_main),
                            'Εκτίμηση Αξίας': round(val, 0),
                            'Πιθανότητα': f"{pred.get('ml_prob',0):.0%}"
                        })
                if sr_rows:
                    pd.DataFrame(sr_rows).sort_values('Εκτίμηση Αξίας', ascending=False)\
                        .to_excel(writer, sheet_name='Smart Rank - Κάλεσε', index=False)
        return output.getvalue()

    try:
        contact_bytes = build_contact_list_export()
        st.download_button(
            label="📞 Κατέβασμα Λίστας Επικοινωνίας (Excel)",
            data=contact_bytes,
            file_name=f"Contact_List_{selected_camp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.caption("Περιλαμβάνει: Διαγραφές, VIP χωρίς παραγγελία, Καλές Διαγραφές Ιστορικού, Πιστωτικό Έλεγχο, Smart Rank — όλα με τηλέφωνο, ταξινομημένα κατά προτεραιότητα.")
    except Exception as contact_err:
        st.warning(f"Δεν κατέστη δυνατή η δημιουργία της λίστας επικοινωνίας: {contact_err}")

except Exception as e:
    st.error(f"⚠️ Κρίσιμο Σφάλμα: {e}")
