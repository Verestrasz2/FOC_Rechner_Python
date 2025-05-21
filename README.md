# FOC-Rechner für Pfeile (mit GUI)

Ein einfaches Python-Tool zur Berechnung des **FOC (Front of Center)** eines Pfeils auf Basis seiner Bauteile – mit grafischer Darstellung und interaktiver Benutzeroberfläche.

---

##  Funktionen

- **Eingabe per Spinboxen** mit Pfeiltasten für:
  - Schaftlänge (in Zoll)
  - Gewicht von Schaft, Spitze, Insert, Federn, Nocke (in Grain)
- **Automatische Umrechnung** in metrische Einheiten (g und mm)
- **Berechnung des Schwerpunkts und FOC-Werts**
- **Entry-Felder für Beschreibungen und Kennzeichnung**
- **Speichern und verwalten von Presets**
- **Grafische Darstellung** des Pfeils mit Schwerpunkt & Mitte
- **Ergebnisse in zwei Einheiten**:
  - `Grain / Zoll`
  - `Gramm / Millimeter` (per Button umschaltbar)

---

##  Voraussetzungen

- Python **3.7+**
- Abhängigkeiten:
  ```bash
  pip install matplotlib
  pip install openpyxl
