import sqlite3
import random

# 1. Connexion à la base de données SQLite finale
db_name = 'ucar_360_real_fr.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

print(f"Création de la base de données UCAR Ultime (Réelle + 360°) : {db_name}...")

# 2. CRÉATION DE TOUTES LES TABLES (Données + 360°)
cursor.executescript('''
    DROP TABLE IF EXISTS exam_results; DROP TABLE IF EXISTS grade_bands;
    DROP TABLE IF EXISTS hr_staff; DROP TABLE IF EXISTS enrollment_stats;
    DROP TABLE IF EXISTS research_metrics; DROP TABLE IF EXISTS finance_stats;
    DROP TABLE IF EXISTS infrastructure; DROP TABLE IF EXISTS esg_metrics;
    DROP TABLE IF EXISTS institutions;

    CREATE TABLE institutions (id INTEGER PRIMARY KEY AUTOINCREMENT, short_name TEXT NOT NULL, category TEXT NOT NULL);
    CREATE TABLE enrollment_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, institution_id INTEGER, academic_year INTEGER, enrolled_count INTEGER, new_intake INTEGER, dropout_rate REAL, repeat_rate REAL, graduates INTEGER, FOREIGN KEY (institution_id) REFERENCES institutions(id));
    CREATE TABLE hr_staff (id INTEGER PRIMARY KEY AUTOINCREMENT, institution_id INTEGER, category TEXT, active BOOLEAN, FOREIGN KEY (institution_id) REFERENCES institutions(id));
    CREATE TABLE research_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, year INTEGER, publications INTEGER, citations INTEGER, views INTEGER, top_10_percent_journals REAL);
    CREATE TABLE grade_bands (id INTEGER PRIMARY KEY, grade_band TEXT, sort_order INTEGER);
    CREATE TABLE exam_results (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, grade_band_id INTEGER, institution_id INTEGER, FOREIGN KEY (grade_band_id) REFERENCES grade_bands(id), FOREIGN KEY (institution_id) REFERENCES institutions(id));
    
    -- TABLES 360° --
    CREATE TABLE finance_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, institution_id INTEGER, academic_year INTEGER, budget_allocated REAL, budget_consumed REAL, FOREIGN KEY (institution_id) REFERENCES institutions(id));
    CREATE TABLE infrastructure (id INTEGER PRIMARY KEY AUTOINCREMENT, institution_id INTEGER, academic_year INTEGER, campus_surface_m2 INTEGER, amphitheater_seats INTEGER, lab_workstations INTEGER, FOREIGN KEY (institution_id) REFERENCES institutions(id));
    CREATE TABLE esg_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, institution_id INTEGER, academic_year INTEGER, carbon_footprint_tons REAL, energy_consumption_kwh REAL, FOREIGN KEY (institution_id) REFERENCES institutions(id));
''')

# 3. INSERTION DES INSTITUTIONS (Vraie liste du catalogue)
institutions_fr = [
    ('INSAT', 'Sciences de l\'Ingénieur'), ('EPT (École Poly)', 'Sciences de l\'Ingénieur'), 
    ('IHEC Carthage', 'Sciences Économiques'), ('SUP\'COM', 'Sciences de l\'Ingénieur'), 
    ('ENSTAB', 'Sciences de l\'Ingénieur'), ('ENICarthage', 'Sciences de l\'Ingénieur'),
    ('INAT', 'Sciences Agronomiques'), ('ISTIC (Borj Cedria)', 'Technologies'),
    ('ISSTE', 'Environnement'), ('ISTEUB', 'Urbanisme et Bâtiment'),
    ('ISSATM (Mateur)', 'Sciences Appliquées'), ('FSB', 'Sciences Fondamentales'),
    ('FSJPST', 'Sciences Juridiques'), ('ISL (Langues)', 'Langues'),
    ('INRAT', 'Recherche Agronomique'), ('INRGREF', 'Eaux et Forêts')
]
cursor.executemany("INSERT INTO institutions (short_name, category) VALUES (?, ?)", institutions_fr)
conn.commit()

cursor.execute("SELECT id FROM institutions")
inst_ids = [row[0] for row in cursor.fetchall()]

# 4. MÉTRIQUES DE RECHERCHE (Vraies données CarthageResearch 2024)
cursor.execute("INSERT INTO research_metrics (year, publications, citations, views, top_10_percent_journals) VALUES (2024, 1700, 1799, 22497, 14.6)")

# 5. PERSONNEL RH (Vraies données du Ministère)
print("Insertion des vraies données RH...")
staff_data = []
def distribute_staff(category_name, exact_count):
    for _ in range(exact_count):
        inst_id = random.choice(inst_ids)
        staff_data.append((inst_id, category_name, True))

distribute_staff("Professeur d'Enseignement Supérieur", 264)
distribute_staff("Maître de Conférences", 215)
distribute_staff("Maître-Assistant", 1291)
distribute_staff("Assistant", 549)
distribute_staff("Personnel Administratif (AATS)", 2100)
cursor.executemany("INSERT INTO hr_staff (institution_id, category, active) VALUES (?, ?, ?)", staff_data)

# 6. GÉNÉRATION 360° POUR CHAQUE INSTITUTION (2020-2024)
print("Génération de l'historique 360° (Inscriptions, Finance, Infra, ESG)...")
years = [2020, 2021, 2022, 2023, 2024]

for inst_id in inst_ids:
    base_students = random.randint(1200, 5000)
    base_budget = random.uniform(1_500_000, 6_000_000)
    surface = random.randint(15_000, 60_000)
    
    for year in years:
        # Inscriptions
        total_stu = int(base_students * random.uniform(0.98, 1.05))
        cursor.execute("INSERT INTO enrollment_stats (institution_id, academic_year, enrolled_count, new_intake, dropout_rate, repeat_rate, graduates) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (inst_id, year, total_stu, int(total_stu*0.2), round(random.uniform(2,8),1), round(random.uniform(5,12),1), int(total_stu*0.18)))
        # Finance
        allocated = round(base_budget * random.uniform(0.95, 1.10), 2)
        consumed = round(allocated * random.uniform(0.85, 1.05), 2)
        cursor.execute("INSERT INTO finance_stats (institution_id, academic_year, budget_allocated, budget_consumed) VALUES (?, ?, ?, ?)", (inst_id, year, allocated, consumed))
        # Infra
        cursor.execute("INSERT INTO infrastructure (institution_id, academic_year, campus_surface_m2, amphitheater_seats, lab_workstations) VALUES (?, ?, ?, ?, ?)", (inst_id, year, surface, int(surface/10), int(surface/50)))
        # ESG
        energy = round(surface * random.uniform(110, 140), 2)
        cursor.execute("INSERT INTO esg_metrics (institution_id, academic_year, carbon_footprint_tons, energy_consumption_kwh) VALUES (?, ?, ?, ?)", (inst_id, year, energy*0.0004, energy))
        
        base_students = total_stu
        base_budget = allocated

# 7. RÉSULTATS D'EXAMENS
print("Génération des résultats d'examens...")
grade_bands_fr = [(1, 'Excellent (≥16)', 1), (2, 'Très Bien (14-16)', 2), (3, 'Bien (12-14)', 3), (4, 'Assez Bien (10-12)', 4), (5, 'Passable (8-10)', 5), (6, 'Insuffisant (<8)', 6)]
cursor.executemany("INSERT INTO grade_bands (id, grade_band, sort_order) VALUES (?, ?, ?)", grade_bands_fr)

exam_data = []
for i in range(35000):
    band_id = random.choices([1, 2, 3, 4, 5, 6], weights=[5, 15, 30, 30, 15, 5])[0]
    exam_data.append((f"ETUD_{i:06d}", band_id, random.choice(inst_ids)))
cursor.executemany("INSERT INTO exam_results (student_id, grade_band_id, institution_id) VALUES (?, ?, ?)", exam_data)

conn.commit()
conn.close()
print("✅ SUCCÈS ! La base de données ultime 'ucar_360_real_fr.db' est prête.")