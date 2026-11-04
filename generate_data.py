"""Generates mock data and builds nextgen.db (applicants, interns, hackathon_scores)."""
import sqlite3, random
from datetime import date, timedelta
import pandas as pd

random.seed(42)
DOMAINS = ["Data Science", "AI/ML", "Web Development", "Cybersecurity", "UI/UX Design"]
UNIVERSITIES = ["Shah Abdul Latif University", "University of Karachi", "NED University",
                "Mehran University", "LUMS", "COMSATS", "IBA Karachi", "Quaid-i-Azam University"]
FIRST = ["Ali","Sara","Ahmed","Fatima","Hassan","Ayesha","Bilal","Zainab","Usman","Hira",
         "Imran","Maria","Omar","Noor","Kashif","Sana","Faisal","Mehwish","Tariq","Rabia"]
LAST = ["Khan","Channa","Memon","Shaikh","Ansari","Malik","Siddiqui","Abbasi","Qureshi","Baloch"]
# per-domain base chance of being selected / completing / mean score (gives varied results)
SEL = {"Data Science":.45,"AI/ML":.40,"Web Development":.55,"Cybersecurity":.35,"UI/UX Design":.50}
COMP = {"Data Science":.85,"AI/ML":.78,"Web Development":.80,"Cybersecurity":.70,"UI/UX Design":.88}
MEAN = {"Data Science":80,"AI/ML":78,"Web Development":74,"Cybersecurity":72,"UI/UX Design":82}

applicants, interns, scores = [], [], []
iid = 1
for aid in range(1, 301):
    dom = random.choice(DOMAINS)
    r = random.random()
    status = "Selected" if r < SEL[dom] else ("Rejected" if r < SEL[dom] + .35 else "Under Review")
    applicants.append((aid, f"{random.choice(FIRST)} {random.choice(LAST)}", dom,
                       random.choice(UNIVERSITIES),
                       (date(2026,1,1)+timedelta(days=random.randint(0,60))).isoformat(), status))
    if status == "Selected":
        done = random.random() < COMP[dom]
        interns.append((iid, aid, dom, (date(2026,3,1)+timedelta(days=random.randint(0,14))).isoformat(),
                        "Completed" if done else "Dropped Out"))
        if done and random.random() < .92:  # not every completer reached the hackathon
            scores.append((iid, round(min(100, max(40, random.gauss(MEAN[dom], 10))), 1), dom))
        iid += 1

conn = sqlite3.connect("nextgen.db")
conn.executescript("""
DROP TABLE IF EXISTS hackathon_scores; DROP TABLE IF EXISTS interns; DROP TABLE IF EXISTS applicants;
CREATE TABLE applicants (applicant_id INTEGER PRIMARY KEY, name TEXT, domain TEXT, university TEXT,
    application_date TEXT, status TEXT CHECK(status IN ('Under Review','Selected','Rejected')));
CREATE TABLE interns (intern_id INTEGER PRIMARY KEY, applicant_id INTEGER REFERENCES applicants(applicant_id),
    domain TEXT, start_date TEXT, completion_status TEXT CHECK(completion_status IN ('Completed','Dropped Out')));
CREATE TABLE hackathon_scores (intern_id INTEGER REFERENCES interns(intern_id), score REAL, domain TEXT);
""")
conn.executemany("INSERT INTO applicants VALUES (?,?,?,?,?,?)", applicants)
conn.executemany("INSERT INTO interns VALUES (?,?,?,?,?)", interns)
conn.executemany("INSERT INTO hackathon_scores VALUES (?,?,?)", scores)
conn.commit()
for t in ["applicants","interns","hackathon_scores"]:
    print(t, pd.read_sql(f"SELECT COUNT(*) n FROM {t}", conn).n[0], "rows")
conn.close()
