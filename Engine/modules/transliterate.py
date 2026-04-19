"""
SIRR Transliteration Utility — English to Arabic/Hebrew script.

Preprocessing utility for the web server. NOT a SIRR module.
Phonetic transliteration (not semantic translation) — consistent and
deterministic so letter-level numerology produces stable results.
"""
from __future__ import annotations


# ── Arabic Transliteration ──────────────────────────────────────────────

# Digraphs processed first (order matters: longest match wins)
_AR_DIGRAPHS: list[tuple[str, str]] = [
    ("SH", "\u0634"),   # ش
    ("TH", "\u062b"),   # ث
    ("KH", "\u062e"),   # خ
    ("GH", "\u063a"),   # غ
    ("DH", "\u0630"),   # ذ
    ("SS", "\u0635"),   # ص
    ("DD", "\u0636"),   # ض
    ("TT", "\u0637"),   # ط
    ("ZZ", "\u0638"),   # ظ
    ("AA", "\u0639"),   # ع
]

_AR_SINGLES: dict[str, str] = {
    "B": "\u0628",   # ب
    "T": "\u062a",   # ت
    "J": "\u062c",   # ج
    "H": "\u062d",   # ح
    "D": "\u062f",   # د
    "R": "\u0631",   # ر
    "Z": "\u0632",   # ز
    "S": "\u0633",   # س
    "F": "\u0641",   # ف
    "Q": "\u0642",   # ق
    "K": "\u0643",   # ك
    "L": "\u0644",   # ل
    "M": "\u0645",   # م
    "N": "\u0646",   # ن
    "W": "\u0648",   # و
    "Y": "\u064a",   # ي
    # Vowels (simplified — Arabic vowels as matres lectionis)
    "A": "\u0627",   # ا
    "I": "\u064a",   # ي
    "U": "\u0648",   # و
    "O": "\u0648",   # و
    "E": "\u064a",   # ي
    # Letters with no Arabic equivalent
    "P": "\u0628",   # ب (Pa → Ba)
    "V": "\u0641",   # ف (Va → Fa)
    "G": "\u062c",   # ج (Ga → Ja, Gulf convention)
    "C": "\u0643",   # ك (hard C → Kaf)
    "X": "\u0643\u0633",  # كس (KS)
}

# Common name overrides for highest-frequency names where phonetic
# transliteration fails or produces suboptimal results.
_AR_OVERRIDES: dict[str, str] = {
    "MUHAMMAD":  "\u0645\u062d\u0645\u062f",           # محمد
    "MOHAMMED":  "\u0645\u062d\u0645\u062f",           # محمد
    "MOHAMED":   "\u0645\u062d\u0645\u062f",           # محمد
    "AHMAD":     "\u0623\u062d\u0645\u062f",           # أحمد
    "AHMED":     "\u0623\u062d\u0645\u062f",           # أحمد
    "OMAR":      "\u0639\u0645\u0631",                 # عمر
    "ISMAIL":    "\u0625\u0633\u0645\u0627\u0639\u064a\u0644",  # إسماعيل
    "ISMAEL":    "\u0625\u0633\u0645\u0627\u0639\u064a\u0644",  # إسماعيل
    "IBRAHIM":   "\u0625\u0628\u0631\u0627\u0647\u064a\u0645",  # إبراهيم
    "ALI":       "\u0639\u0644\u064a",                 # علي
    "HUSSEIN":   "\u062d\u0633\u064a\u0646",           # حسين
    "HASSAN":    "\u062d\u0633\u0646",                 # حسن
    "FATIMA":    "\u0641\u0627\u0637\u0645\u0629",     # فاطمة
    "SARAH":     "\u0633\u0627\u0631\u0629",           # سارة
    "AISHA":     "\u0639\u0627\u0626\u0634\u0629",     # عائشة
    "MARYAM":    "\u0645\u0631\u064a\u0645",           # مريم
    "KHALID":    "\u062e\u0627\u0644\u062f",           # خالد
    "YUSUF":     "\u064a\u0648\u0633\u0641",           # يوسف
    "YOUSSEF":   "\u064a\u0648\u0633\u0641",           # يوسف
    "ABDALLAH":  "\u0639\u0628\u062f\u0627\u0644\u0644\u0647",  # عبدالله
    "ABDULLAH":  "\u0639\u0628\u062f\u0627\u0644\u0644\u0647",  # عبدالله
    # Common Western names (phonetic transliteration produces suboptimal results)
    "JOHN":      "\u062c\u0648\u0646",                 # جون
    "JAMES":     "\u062c\u064a\u0645\u0633",           # جيمس
    "MICHAEL":   "\u0645\u0627\u064a\u0643\u0644",     # مايكل
    "WILLIAM":   "\u0648\u0644\u064a\u0627\u0645",     # وليام
    "DAVID":     "\u062f\u0627\u0641\u064a\u062f",     # دافيد
    "ROBERT":    "\u0631\u0648\u0628\u0631\u062a",     # روبرت
    "RICHARD":   "\u0631\u064a\u062a\u0634\u0627\u0631\u062f",  # ريتشارد
    "THOMAS":    "\u062a\u0648\u0645\u0627\u0633",     # توماس
    "CHARLES":   "\u062a\u0634\u0627\u0631\u0644\u0632",  # تشارلز
    "JOSEPH":    "\u062c\u0648\u0632\u064a\u0641",     # جوزيف
    "GEORGE":    "\u062c\u0648\u0631\u062c",           # جورج
    "PETER":     "\u0628\u064a\u062a\u0631",           # بيتر
    "PAUL":      "\u0628\u0648\u0644",                 # بول
    "MARK":      "\u0645\u0627\u0631\u0643",           # مارك
    "DANIEL":    "\u062f\u0627\u0646\u064a\u0627\u0644",  # دانيال
    "MATTHEW":   "\u0645\u0627\u062b\u064a\u0648",     # ماثيو
    "ANTHONY":   "\u0623\u0646\u062a\u0648\u0646\u064a",  # أنتوني
    "STEVEN":    "\u0633\u062a\u064a\u0641\u0646",     # ستيفن
    "STEPHEN":   "\u0633\u062a\u064a\u0641\u0646",     # ستيفن
    "CHRISTOPHER": "\u0643\u0631\u064a\u0633\u062a\u0648\u0641\u0631",  # كريستوفر
    "JENNIFER":  "\u062c\u064a\u0646\u064a\u0641\u0631",  # جينيفر
    "ELIZABETH": "\u0625\u0644\u064a\u0632\u0627\u0628\u064a\u062b",  # إليزابيث
    "MARY":      "\u0645\u0627\u0631\u064a",           # ماري
    "JESSICA":   "\u062c\u064a\u0633\u064a\u0643\u0627",  # جيسيكا
    "KAREN":     "\u0643\u0627\u0631\u0646",           # كارن
    "LISA":      "\u0644\u064a\u0633\u0627",           # ليسا
    "NANCY":     "\u0646\u0627\u0646\u0633\u064a",     # نانسي
    "MARGARET":  "\u0645\u0627\u0631\u063a\u0631\u064a\u062a",  # مارغريت
    # Common surnames
    "JOHNSON":   "\u062c\u0648\u0646\u0633\u0648\u0646",  # جونسون
    "SMITH":     "\u0633\u0645\u064a\u062b",           # سميث
    "CHEN":      "\u062a\u0634\u0646",                 # تشن
    "WANG":      "\u0648\u0627\u0646\u063a",           # وانغ
    "LEE":       "\u0644\u064a",                       # لي
    "JONES":     "\u062c\u0648\u0646\u0632",           # جونز
    "BROWN":     "\u0628\u0631\u0627\u0648\u0646",     # براون
    "WILSON":    "\u0648\u064a\u0644\u0633\u0648\u0646",  # ويلسون
    "TAYLOR":    "\u062a\u0627\u064a\u0644\u0648\u0631",  # تايلور
    "ANDERSON":  "\u0623\u0646\u062f\u0631\u0633\u0648\u0646",  # أندرسون
    # ── Mohammed spelling variants (2026-04-18 expansion) ──
    "MOHAMMAD":  "\u0645\u062d\u0645\u062f",                    # محمد (O-variant)
    "MUHAMMED":  "\u0645\u062d\u0645\u062f",                    # محمد
    "MOHAMAD":   "\u0645\u062d\u0645\u062f",                    # محمد
    "MHMD":      "\u0645\u062d\u0645\u062f",                    # محمد (initials)
    # ── Names with emphatic letters phonetic fallback can't infer ──
    "WASEF":     "\u0648\u0627\u0635\u0641",                    # واصف
    "NASSER":    "\u0646\u0627\u0635\u0631",                    # ناصر
    "NASIR":     "\u0646\u0627\u0635\u0631",                    # ناصر
    "NASR":      "\u0646\u0635\u0631",                          # نصر
    "SALAH":     "\u0635\u0644\u0627\u062d",                    # صلاح
    "SADEQ":     "\u0635\u0627\u062f\u0642",                    # صادق
    "SADIQ":     "\u0635\u0627\u062f\u0642",                    # صادق
    "MANSOUR":   "\u0645\u0646\u0635\u0648\u0631",              # منصور
    # ── Common male given names ──
    "ABDELRAHMAN":   "\u0639\u0628\u062f\u0627\u0644\u0631\u062d\u0645\u0646",  # عبدالرحمن
    "ABDULRAHMAN":   "\u0639\u0628\u062f\u0627\u0644\u0631\u062d\u0645\u0646",  # عبدالرحمن
    "ABDELKARIM":    "\u0639\u0628\u062f\u0627\u0644\u0643\u0631\u064a\u0645",  # عبدالكريم
    "ABDULKARIM":    "\u0639\u0628\u062f\u0627\u0644\u0643\u0631\u064a\u0645",  # عبدالكريم
    "ABDELAZIZ":     "\u0639\u0628\u062f\u0627\u0644\u0639\u0632\u064a\u0632",  # عبدالعزيز
    "ABDULAZIZ":     "\u0639\u0628\u062f\u0627\u0644\u0639\u0632\u064a\u0632",  # عبدالعزيز
    "ABDELHADI":     "\u0639\u0628\u062f\u0627\u0644\u0647\u0627\u062f\u064a",  # عبدالهادي
    "ABDELNASSER":   "\u0639\u0628\u062f\u0627\u0644\u0646\u0627\u0635\u0631",  # عبدالناصر
    "ADEL":          "\u0639\u0627\u062f\u0644",                                # عادل
    "ADNAN":         "\u0639\u062f\u0646\u0627\u0646",                          # عدنان
    "ANAS":          "\u0623\u0646\u0633",                                      # أنس
    "BADR":          "\u0628\u062f\u0631",                                      # بدر
    "BILAL":         "\u0628\u0644\u0627\u0644",                                # بلال
    "FADI":          "\u0641\u0627\u062f\u064a",                                # فادي
    "FAHAD":         "\u0641\u0647\u062f",                                      # فهد
    "FAHD":          "\u0641\u0647\u062f",                                      # فهد
    "FAISAL":        "\u0641\u064a\u0635\u0644",                                # فيصل
    "FARES":         "\u0641\u0627\u0631\u0633",                                # فارس
    "FARIS":         "\u0641\u0627\u0631\u0633",                                # فارس
    "HAMZA":         "\u062d\u0645\u0632\u0629",                                # حمزة
    "HAMZAH":        "\u062d\u0645\u0632\u0629",                                # حمزة
    "HARITH":        "\u062d\u0627\u0631\u062b",                                # حارث
    "HATEM":         "\u062d\u0627\u062a\u0645",                                # حاتم
    "HATIM":         "\u062d\u0627\u062a\u0645",                                # حاتم
    "HOSSAM":        "\u062d\u0633\u0627\u0645",                                # حسام
    "HUSAM":         "\u062d\u0633\u0627\u0645",                                # حسام
    "ISSAM":         "\u0639\u0635\u0627\u0645",                                # عصام
    "ISSAT":         "\u0639\u0632\u0629",                                      # عزة
    "JAAFAR":        "\u062c\u0639\u0641\u0631",                                # جعفر
    "JAFAR":         "\u062c\u0639\u0641\u0631",                                # جعفر
    "JAMAL":         "\u062c\u0645\u0627\u0644",                                # جمال
    "KAMAL":         "\u0643\u0645\u0627\u0644",                                # كمال
    "KAREEM":        "\u0643\u0631\u064a\u0645",                                # كريم
    "KARIM":         "\u0643\u0631\u064a\u0645",                                # كريم
    "MAHMOUD":       "\u0645\u062d\u0645\u0648\u062f",                          # محمود
    "MAHMUD":        "\u0645\u062d\u0645\u0648\u062f",                          # محمود
    "MALEK":         "\u0645\u0627\u0644\u0643",                                # مالك
    "MALIK":         "\u0645\u0627\u0644\u0643",                                # مالك
    "MAZEN":         "\u0645\u0627\u0632\u0646",                                # مازن
    "MAZIN":         "\u0645\u0627\u0632\u0646",                                # مازن
    "MUSTAFA":       "\u0645\u0635\u0637\u0641\u0649",                          # مصطفى
    "MUSTAPHA":      "\u0645\u0635\u0637\u0641\u0649",                          # مصطفى
    "NABIL":         "\u0646\u0628\u064a\u0644",                                # نبيل
    "NADER":         "\u0646\u0627\u062f\u0631",                                # نادر
    "NADIR":         "\u0646\u0627\u062f\u0631",                                # نادر
    "NAJI":          "\u0646\u0627\u062c\u064a",                                # ناجي
    "NAWAF":         "\u0646\u0648\u0627\u0641",                                # نواف
    "OSAMA":         "\u0623\u0633\u0627\u0645\u0629",                          # أسامة
    "OUSAMA":        "\u0623\u0633\u0627\u0645\u0629",                          # أسامة
    "OSMAN":         "\u0639\u062b\u0645\u0627\u0646",                          # عثمان
    "OTHMAN":        "\u0639\u062b\u0645\u0627\u0646",                          # عثمان
    "UTHMAN":        "\u0639\u062b\u0645\u0627\u0646",                          # عثمان
    "QASIM":         "\u0642\u0627\u0633\u0645",                                # قاسم
    "QASEM":         "\u0642\u0627\u0633\u0645",                                # قاسم
    "RAED":          "\u0631\u0627\u0626\u062f",                                # رائد
    "RAID":          "\u0631\u0627\u0626\u062f",                                # رائد
    "RAMI":          "\u0631\u0627\u0645\u064a",                                # رامي
    "RAMZI":         "\u0631\u0645\u0632\u064a",                                # رمزي
    "RASHAD":        "\u0631\u0634\u0627\u062f",                                # رشاد
    "RASHED":        "\u0631\u0627\u0634\u062f",                                # راشد
    "RASHID":        "\u0631\u0627\u0634\u062f",                                # راشد
    "RAYYAN":        "\u0631\u064a\u0627\u0646",                                # ريان
    "SAAD":          "\u0633\u0639\u062f",                                      # سعد
    "SAAED":         "\u0633\u0639\u064a\u062f",                                # سعيد
    "SAEED":         "\u0633\u0639\u064a\u062f",                                # سعيد
    "SAID":          "\u0633\u0639\u064a\u062f",                                # سعيد
    "SALEEM":        "\u0633\u0644\u064a\u0645",                                # سليم
    "SALIM":         "\u0633\u0644\u064a\u0645",                                # سليم
    "SALMAN":        "\u0633\u0644\u0645\u0627\u0646",                          # سلمان
    "SAMEER":        "\u0633\u0645\u064a\u0631",                                # سمير
    "SAMIR":         "\u0633\u0645\u064a\u0631",                                # سمير
    "SAUD":          "\u0633\u0639\u0648\u062f",                                # سعود
    "SULTAN":        "\u0633\u0644\u0637\u0627\u0646",                          # سلطان
    "TALAL":         "\u0637\u0644\u0627\u0644",                                # طلال
    "TAMER":         "\u062a\u0627\u0645\u0631",                                # تامر
    "TAMIR":         "\u062a\u0627\u0645\u0631",                                # تامر
    "TAREQ":         "\u0637\u0627\u0631\u0642",                                # طارق
    "TAREK":         "\u0637\u0627\u0631\u0642",                                # طارق
    "TARIQ":         "\u0637\u0627\u0631\u0642",                                # طارق
    "WAEL":          "\u0648\u0627\u0626\u0644",                                # وائل
    "WAIL":          "\u0648\u0627\u0626\u0644",                                # وائل
    "WALEED":        "\u0648\u0644\u064a\u062f",                                # وليد
    "WALID":         "\u0648\u0644\u064a\u062f",                                # وليد
    "YAHYA":         "\u064a\u062d\u064a\u0649",                                # يحيى
    "YASEEN":        "\u064a\u0627\u0633\u064a\u0646",                          # ياسين
    "YASIN":         "\u064a\u0627\u0633\u064a\u0646",                          # ياسين
    "YASSIN":        "\u064a\u0627\u0633\u064a\u0646",                          # ياسين
    "YAZID":         "\u064a\u0632\u064a\u062f",                                # يزيد
    "ZAID":          "\u0632\u064a\u062f",                                      # زيد
    "ZAYD":          "\u0632\u064a\u062f",                                      # زيد
    "ZAKARIA":       "\u0632\u0643\u0631\u064a\u0627",                          # زكريا
    "ZAKI":          "\u0632\u0643\u064a",                                      # زكي
    "ZIAD":          "\u0632\u064a\u0627\u062f",                                # زياد
    "ZUHAIR":        "\u0632\u0647\u064a\u0631",                                # زهير
    # ── Common female given names ──
    "AMAL":      "\u0623\u0645\u0644",                          # أمل
    "AMINA":     "\u0623\u0645\u064a\u0646\u0629",              # أمينة
    "AMINAH":    "\u0623\u0645\u064a\u0646\u0629",              # أمينة
    "AMIRA":     "\u0623\u0645\u064a\u0631\u0629",              # أميرة
    "ASMA":      "\u0623\u0633\u0645\u0627\u0621",              # أسماء
    "ASMAA":     "\u0623\u0633\u0645\u0627\u0621",              # أسماء
    "DANA":      "\u062f\u0627\u0646\u0629",                    # دانة
    "DINA":      "\u062f\u064a\u0646\u0627",                    # دينا
    "DALIA":     "\u062f\u0627\u0644\u064a\u0627",              # داليا
    "FAIZA":     "\u0641\u0627\u064a\u0632\u0629",              # فايزة
    "HALA":      "\u0647\u0627\u0644\u0629",                    # هالة
    "HANAN":     "\u062d\u0646\u0627\u0646",                    # حنان
    "HIND":      "\u0647\u0646\u062f",                          # هند
    "HODA":      "\u0647\u062f\u0649",                          # هدى
    "HUDA":      "\u0647\u062f\u0649",                          # هدى
    "KHADIJA":   "\u062e\u062f\u064a\u062c\u0629",              # خديجة
    "KHADIJAH":  "\u062e\u062f\u064a\u062c\u0629",              # خديجة
    "LAILA":     "\u0644\u064a\u0644\u0649",                    # ليلى
    "LAYLA":     "\u0644\u064a\u0644\u0649",                    # ليلى
    "LATIFA":    "\u0644\u0637\u064a\u0641\u0629",              # لطيفة
    "LEILA":     "\u0644\u064a\u0644\u0629",                    # ليلة
    "LINA":      "\u0644\u064a\u0646\u0627",                    # لينا
    "LOBNA":     "\u0644\u0628\u0646\u0649",                    # لبنى
    "MAHA":      "\u0645\u0647\u0627",                          # مها
    "MAYA":      "\u0645\u0627\u064a\u0627",                    # مايا
    "MAYSOUN":   "\u0645\u064a\u0633\u0648\u0646",              # ميسون
    "MONA":      "\u0645\u0646\u0649",                          # منى
    "MUNA":      "\u0645\u0646\u0649",                          # منى
    "NADIA":     "\u0646\u0627\u062f\u064a\u0627",              # ناديا
    "NAWAL":     "\u0646\u0648\u0627\u0644",                    # نوال
    "NOOR":      "\u0646\u0648\u0631",                          # نور
    "NORA":      "\u0646\u0648\u0631\u0629",                    # نورة
    "NOURA":     "\u0646\u0648\u0631\u0629",                    # نورة
    "NOUR":      "\u0646\u0648\u0631",                          # نور
    "NUR":       "\u0646\u0648\u0631",                          # نور
    "RANIA":     "\u0631\u0627\u0646\u064a\u0627",              # رانيا
    "RASHA":     "\u0631\u0634\u0627",                          # رشا
    "REEM":      "\u0631\u064a\u0645",                          # ريم
    "RIM":       "\u0631\u064a\u0645",                          # ريم
    "RIMA":      "\u0631\u064a\u0645\u0627",                    # ريما
    "SABA":      "\u0633\u0628\u0623",                          # سبأ
    "SAMAR":     "\u0633\u0645\u0631",                          # سمر
    "SAMIRA":    "\u0633\u0645\u064a\u0631\u0629",              # سميرة
    "SARA":      "\u0633\u0627\u0631\u0629",                    # سارة
    "SHAIMA":    "\u0634\u064a\u0645\u0627\u0621",              # شيماء
    "SHAIMAA":   "\u0634\u064a\u0645\u0627\u0621",              # شيماء
    "SOMAYA":    "\u0633\u0645\u064a\u0629",                    # سمية
    "TASNEEM":   "\u062a\u0633\u0646\u064a\u0645",              # تسنيم
    "WAFA":      "\u0648\u0641\u0627\u0621",                    # وفاء
    "YASMIN":    "\u064a\u0627\u0633\u0645\u064a\u0646",        # ياسمين
    "YASMINE":   "\u064a\u0627\u0633\u0645\u064a\u0646",        # ياسمين
    "ZAHRA":     "\u0632\u0647\u0631\u0627\u0621",              # زهراء
    "ZAHRAA":    "\u0632\u0647\u0631\u0627\u0621",              # زهراء
    "ZAINA":     "\u0632\u064a\u0646\u0629",                    # زينة
    "ZEINAB":    "\u0632\u064a\u0646\u0628",                    # زينب
    "ZAYNAB":    "\u0632\u064a\u0646\u0628",                    # زينب
}


def _transliterate_word_arabic(word: str) -> str:
    """Transliterate a single word to Arabic script."""
    upper = word.upper().strip()
    if not upper:
        return ""

    # Check overrides first
    if upper in _AR_OVERRIDES:
        return _AR_OVERRIDES[upper]

    result = []
    i = 0
    while i < len(upper):
        # Try digraphs first
        matched = False
        if i + 1 < len(upper):
            pair = upper[i:i+2]
            for digraph, ar_char in _AR_DIGRAPHS:
                if pair == digraph:
                    result.append(ar_char)
                    i += 2
                    matched = True
                    break
        if matched:
            continue

        ch = upper[i]
        if ch in _AR_SINGLES:
            result.append(_AR_SINGLES[ch])
        # Skip spaces, hyphens, apostrophes — they don't map
        i += 1

    return "".join(result)


def transliterate_to_arabic(english_name: str) -> str:
    """
    Convert English name to Arabic script. Phonetic, not semantic.

    Each word is transliterated separately, then joined with spaces.
    Common names use curated overrides for accuracy.
    """
    if not english_name or not english_name.strip():
        return ""
    parts = english_name.strip().split()
    return " ".join(_transliterate_word_arabic(p) for p in parts if p.strip())


# ── Hebrew Transliteration ──────────────────────────────────────────────

_HE_DIGRAPHS: list[tuple[str, str]] = [
    ("SH", "\u05e9"),   # ש
    ("CH", "\u05d7"),   # ח
    ("TH", "\u05ea"),   # ת
    ("TS", "\u05e6"),   # צ
    ("TZ", "\u05e6"),   # צ
]

_HE_SINGLES: dict[str, str] = {
    "A": "\u05d0",   # א
    "B": "\u05d1",   # ב
    "G": "\u05d2",   # ג
    "D": "\u05d3",   # ד
    "H": "\u05d4",   # ה
    "V": "\u05d5",   # ו
    "W": "\u05d5",   # ו
    "Z": "\u05d6",   # ז
    "T": "\u05d8",   # ט
    "Y": "\u05d9",   # י
    "K": "\u05db",   # כ
    "L": "\u05dc",   # ל
    "M": "\u05de",   # מ
    "N": "\u05e0",   # נ
    "S": "\u05e1",   # ס
    "P": "\u05e4",   # פ
    "F": "\u05e4",   # פ
    "Q": "\u05e7",   # ק
    "R": "\u05e8",   # ר
    # Vowels (Hebrew uses matres lectionis sparingly)
    "I": "\u05d9",   # י
    "E": "\u05d9",   # י
    "O": "\u05d5",   # ו
    "U": "\u05d5",   # ו
    # No-equivalent letters
    "C": "\u05db",   # כ (hard C)
    "J": "\u05d2",   # ג (approximation)
    "X": "\u05db\u05e1",  # כס (KS)
}


def _transliterate_word_hebrew(word: str) -> str:
    """Transliterate a single word to Hebrew script."""
    upper = word.upper().strip()
    if not upper:
        return ""

    result = []
    i = 0
    while i < len(upper):
        matched = False
        if i + 1 < len(upper):
            pair = upper[i:i+2]
            for digraph, he_char in _HE_DIGRAPHS:
                if pair == digraph:
                    result.append(he_char)
                    i += 2
                    matched = True
                    break
        if matched:
            continue

        ch = upper[i]
        if ch in _HE_SINGLES:
            result.append(_HE_SINGLES[ch])
        i += 1

    return "".join(result)


def transliterate_to_hebrew(english_name: str) -> str:
    """
    Convert English name to Hebrew script. Phonetic, not semantic.

    Each word is transliterated separately, then joined with spaces.
    """
    if not english_name or not english_name.strip():
        return ""
    parts = english_name.strip().split()
    return " ".join(_transliterate_word_hebrew(p) for p in parts if p.strip())
