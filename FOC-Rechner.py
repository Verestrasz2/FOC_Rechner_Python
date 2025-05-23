import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Label
from tkinter import filedialog
import openpyxl

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import json
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk  # Pillow wird benötigt

import glob
import os

import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Button
import requests
from packaging import version

# Lokale Version
__version__ = "1.1.0"

# GitHub-Rohdaten-Links
VERSION_URL = "https://raw.githubusercontent.com/Verestrasz2/FOC_Rechner_Python/master/version.txt"
SCRIPT_URL  = "https://raw.githubusercontent.com/Verestrasz2/FOC_Rechner_Python/master/FOC-Rechner.py"


def get_latest_version():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"Fehler beim Versionsabruf: {e}")
    return None

def is_update_available(local_version, remote_version):
    return version.parse(remote_version) > version.parse(local_version)

def update_script():
    try:
        response = requests.get(SCRIPT_URL)
        if response.status_code == 200:
            with open("FOC_Rechner.py", "w", encoding="utf-8") as f:
                f.write(response.text)
            messagebox.showinfo("Update abgeschlossen", "Das Skript wurde erfolgreich aktualisiert.\nBitte starte es neu.")
        else:
            messagebox.showerror("Update-Fehler", "Das Update konnte nicht heruntergeladen werden.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Update: {e}")

def show_update_dialog(latest_version):
    update_window = Toplevel()
    update_window.title("Update verfügbar")
    update_window.geometry("400x150")  # Größe anpassen
    update_window.resizable(False, False)

    Label(update_window, text=f"Eine neue Version ({latest_version}) ist verfügbar.", font=("Arial", 12)).pack(pady=10)
    Label(update_window, text="Möchtest du jetzt updaten?", font=("Arial", 10)).pack()

    def confirm_update():
        update_window.destroy()  # Fenster schließen
        update_script()

    Button(update_window, text="Ja, Update durchführen", command=confirm_update, width=25).pack(pady=5)
    Button(update_window, text="Nein", command=update_window.destroy, width=25).pack()

def check_for_update_gui(label):
    latest = get_latest_version()
    if latest:
        if is_update_available(__version__, latest):
            label.config(text=f"Update verfügbar: {latest}")
            show_update_dialog(latest)
        else:
            label.config(text="Du hast die neueste Version.")
    else:
        label.config(text="Update-Prüfung fehlgeschlagen.")

# GUI-Setup
def start_gui():
    root = tk.Tk()
    root.title("FOC Rechner")
    root.geometry("400x300")  # Fenstergröße für dein Hauptfenster

    version_label = tk.Label(root, text="Version wird geprüft...", fg="blue", font=("Arial", 10))
    version_label.pack(pady=10)

    # Hier kommen andere GUI-Elemente wie Buttons etc.
    # ...

    root.after(200, lambda: check_for_update_gui(version_label))
    root.mainloop()

if __name__ == "__main__":
    start_gui()



def preset_laden_auswahl():
    name = preset_var.get()
    if not name:
        return

    filepath = f"preset_{name}.json"
    if not os.path.exists(filepath):
        messagebox.showerror("Fehler", "Preset-Datei nicht gefunden.")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            preset = json.load(f)

        werte = preset.get("werte", [])
        notizen = preset.get("notizen", [])

        for spin, val in zip(spinboxes, werte):
            spin.delete(0, "end")
            spin.insert(0, val)

        for entry, note in zip(entryboxen, notizen):
            entry.delete(0, "end")
            entry.insert(0, note)
            entry.config(fg="black")  # falls Placeholder aktiv war

        messagebox.showinfo("Preset geladen", f"'{name}' wurde geladen.")

    except Exception as e:
        messagebox.showerror("Fehler", f"Preset konnte nicht geladen werden:\n{e}")

def lade_verfügbare_presets():
    files = glob.glob("preset_*.json")
    return [os.path.splitext(os.path.basename(f))[0].replace("preset_", "") for f in files]


def preset_speichern():
    # Name für das Preset erfragen
    name = simpledialog.askstring("Preset speichern", "Gib einen Namen für das Preset ein:")

    if not name:
        return

    preset = {
        "werte": [s.get() for s in spinboxes],
        "notizen": [e.get() for e in entryboxen],
    }

    if letzte_werte:
        _, _, foc, _ = letzte_werte
        preset["foc"] = round(foc, 2)

    with open(f"preset_{name}.json", "w", encoding="utf-8") as f:
        json.dump(preset, f, indent=2)

    messagebox.showinfo("Gespeichert", f"Preset '{name}' wurde gespeichert.")
    preset_dropdown['values'] = lade_verfügbare_presets()

def set_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg="grey")

    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(fg="black")

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="grey")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

GRAIN_TO_GRAM = 0.06479891
INCH_TO_MM = 25.4

letzte_werte = None


def berechne_foc(länge_mm, gewicht_schaft, gewicht_spitze, gewicht_insert, gewicht_federn, gewicht_nocke):
    pos_spitze_insert = 0
    pos_schaft = länge_mm / 2
    pos_federn_nocke = länge_mm

    gesamtgewicht = gewicht_schaft + gewicht_spitze + gewicht_insert + gewicht_federn + gewicht_nocke


    x_spitze_insert = (gewicht_spitze + gewicht_insert) * pos_spitze_insert
    x_schaft = gewicht_schaft * pos_schaft
    x_federn_nocke = (gewicht_federn + gewicht_nocke) * pos_federn_nocke

    schwerpunkt = länge_mm-((x_spitze_insert + x_schaft + x_federn_nocke) / gesamtgewicht)
    halbe_länge = länge_mm / 2
    foc = ((schwerpunkt - halbe_länge) / länge_mm) * 100

    return gesamtgewicht, schwerpunkt, foc

def zeichne_pfeil(länge, schwerpunkt):
    fig, ax = plt.subplots(figsize=(8, 1.5))
    ax.set_xlim(-20, länge + 20)
    ax.set_ylim(-1, 1)

    ax.plot([0, länge], [0, 0], linewidth=8, color='saddlebrown', solid_capstyle='butt')
    ax.axvline(länge / 2, color='blue', linestyle='--', label="Mitte", linewidth=2)
    ax.arrow( -2,0,-4,0)
    ax.axvline(schwerpunkt, color='red', linestyle='-', label="Schwerpunkt", linewidth=2)
    ax.text(länge / 1.95, 0.2, "Mitte", color='blue', ha='left')
    ax.text(länge*0.99, -0.4, "Spitze", color='orange', ha='left')
    ax.text(-1, -0.4, "Nocke", color='orange', ha='left')
    ax.text(schwerpunkt*1.01, -0.4, f"SP: {schwerpunkt:.1f} mm", color='red', ha='left')
    ax.axis('off')
    ax.legend(loc='upper right')
    return fig

def bild_anzeigen_fenster():
    top = tk.Toplevel(root)
    top.title("compound-spine-chart")

    try:
        # Bildpfad anpassen
        bildpfad = "compound-spine-chart-2023.jpg"  # <--- Hier deinen Dateinamen einsetzen!
        bild = Image.open(bildpfad)
        bild = bild.resize((1000, 800), Image.Resampling.LANCZOS)
        bild_tk = ImageTk.PhotoImage(bild)

        label = tk.Label(top, image=bild_tk)
        label.image = bild_tk  # Referenz behalten, sonst wird Bild nicht angezeigt
        label.pack(padx=10, pady=10)

    except Exception as e:
        tk.Label(top, text=f"Fehler beim Laden des Bildes:\n{e}", fg="red").pack(padx=10, pady=10)

def berechne_und_anzeigen():
    global letzte_werte

    try:
        länge_inch = float(spin_länge.get())
        gewicht_schaft_gr = float(spin_schaft.get())
        gewicht_spitze_gr = float(spin_spitze.get())
        gewicht_insert_gr = float(spin_insert.get())
        gewicht_federn_gr = float(spin_federn.get())
        gewicht_nocke_gr = float(spin_nocke.get())

        länge_mm = länge_inch * INCH_TO_MM
        gewicht_schaft = gewicht_schaft_gr * GRAIN_TO_GRAM
        gewicht_spitze = gewicht_spitze_gr * GRAIN_TO_GRAM
        gewicht_insert = gewicht_insert_gr * GRAIN_TO_GRAM
        gewicht_federn = gewicht_federn_gr * GRAIN_TO_GRAM
        gewicht_nocke = gewicht_nocke_gr * GRAIN_TO_GRAM

        gesamtgewicht, schwerpunkt, foc = berechne_foc(
            länge_mm, gewicht_schaft, gewicht_spitze, gewicht_insert, gewicht_federn, gewicht_nocke
        )

        letzte_werte = (gesamtgewicht, schwerpunkt, foc, länge_mm)

        # Neue Berechnung: Spitze + Insert zusammenrechnen
        spitze_insert_grain = gewicht_spitze_gr + gewicht_insert_gr

        result_label.config(text=(
            f"Gesamtgewicht: {gesamtgewicht / GRAIN_TO_GRAM:.1f} grain\n"
            f"Spitze + Insert: {spitze_insert_grain:.1f} grain\n"
            f"Schwerpunkt: {schwerpunkt / INCH_TO_MM:.2f} inch\n"
            f"FOC: {foc:.2f} %\n"

        ))

        for widget in chart_frame.winfo_children():
            widget.destroy()

        fig = zeichne_pfeil(länge_mm, schwerpunkt)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except ValueError:
        messagebox.showerror("Fehler", "Bitte gültige Zahlen eingeben.")



def anzeigen_metrisch():
    global letzte_werte
    if letzte_werte is None:
        messagebox.showinfo("Info", "Bitte zuerst berechnen.")
        return

    gesamtgewicht, schwerpunkt, foc, länge_mm = letzte_werte

    result_label.config(text=(
        f"Gesamtgewicht: {gesamtgewicht:.2f} g\n"
        f"Schwerpunkt: {schwerpunkt:.1f} mm\n"
        f"FOC: {foc:.2f} %"
    ))
def eingaben_speichern():
    daten = []
    beschriftungen = [
        "Länge des Schafts (Zoll)",
        "Gewicht des Schafts (Grain)",
        "Gewicht der Spitze (Grain)",
        "Gewicht des Inserts (Grain)",
        "Gewicht der Federn (Grain)",
        "Gewicht der Nocke (Grain)",
    ]

    for i in range(len(spinboxes)):
        wert = spinboxes[i].get()
        text = entryboxen[i].get()
        daten.append((beschriftungen[i], wert, text))

    # Optional: berechnete Werte anhängen
    berechnung_info = []
    if letzte_werte:
        gesamtgewicht, schwerpunkt, foc, länge_mm = letzte_werte
        berechnung_info = [
            ("Gesamtgewicht (grain)", f"{gesamtgewicht / GRAIN_TO_GRAM:.1f}", ""),
            ("Schwerpunkt (inch)", f"{schwerpunkt / INCH_TO_MM:.2f}", ""),
            ("FOC (%)", f"{foc:.2f}", "")
        ]

    # Datei speichern
    # Standard-Dateiname vorbereiten mit FOC-Wert
    default_filename = "foc_daten"

    if letzte_werte:
        _, _, foc, _ = letzte_werte
        foc_str = f"{foc:.2f}".replace(".", "_")  # z. B. 12.34 → 12_34
        default_filename = f"foc_{foc_str}"

    filepath = filedialog.asksaveasfilename(
        initialfile=default_filename,
        defaultextension=".txt",
        filetypes=[("Textdatei", "*.txt"), ("Excel-Datei", "*.xlsx")],
        title="Eingaben speichern unter..."
    )

    if not filepath:
        return

    try:
        if filepath.endswith(".txt"):
            with open(filepath, "w", encoding="utf-8") as f:
                for label, wert, text in daten:
                    f.write(f"{label}: {wert} - Hinweis: {text}\n")
                if berechnung_info:
                    f.write("\n--- Berechnete Werte ---\n")
                    for label, wert, _ in berechnung_info:
                        f.write(f"{label}: {wert}\n")

        elif filepath.endswith(".xlsx"):
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "FOC Eingaben"

            ws.append(["Bezeichnung", "Wert", "Hinweis"])
            for zeile in daten:
                ws.append(zeile)

            if berechnung_info:
                ws.append(["", "", ""])  # Leerzeile
                ws.append(["Berechnete Werte", "", ""])
                for zeile in berechnung_info:
                    ws.append(zeile)

            wb.save(filepath)

        messagebox.showinfo("Gespeichert", f"Die Daten wurden gespeichert:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")



# GUI
root = tk.Tk()
root.title("Pfeil-Manager")


# Labels und Spinboxen
label_texts = [
    ("Länge des Schafts (Zoll):", 30, 40, 0.5),
    ("Gewicht des Schafts (Grain):", 270, 500, 1),
    ("Gewicht der Spitze (Grain):", 120, 300, 1),
    ("Gewicht des Inserts (Grain):", 20, 100, 1),
    ("Gewicht der Federn (Grain):", 1, 30, 0.5),
    ("Gewicht der Nocke (Grain):", 1, 30, 0.5),
]
placeholder_texts = [
    "Schaft Typ/Bezeichnung",
    "Schaft grain per inch",
    "Spitzen Typ/Bezeichnung",
    "Insert Typ/Bezeichnung",
    "Vains Typ/Bezeichnung",
    "Nocke Typ/Bezeichnung"
]


spinboxes = []
entryboxen = []

for i, (label, from_, to, step) in enumerate(label_texts):
    tk.Label(root, text=label).grid(row=i + 1, column=0, sticky="e", padx=1, pady=1)

    spin = tk.Spinbox(root, from_=from_, to=to, increment=step, width=10, bg= "lightgreen")
    spin.grid(row=i + 1, column=1, padx=1, pady=5)
    spinboxes.append(spin)

    entry = tk.Entry(root, width=30)
    entry.grid(row=i + 1, column=2, padx=1, pady=5 ,sticky="w")

    # 🎯 Hier individuellen Placeholder einsetzen
    set_placeholder(entry, placeholder_texts[i])


    def gewicht_schaft_aus_eingabe_berechnen():
        try:
            grain_per_inch = float(entryboxen[1].get())
            länge_inch = float(spin_länge.get())
            gesamtgewicht = grain_per_inch * länge_inch
            spin_schaft.delete(0, "end")
            spin_schaft.insert(0, f"{gesamtgewicht:.1f}")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gültige Zahlen eingeben (Länge oder GPI).")


    entryboxen.append(entry)

(spin_länge, spin_schaft, spin_spitze, spin_insert, spin_federn, spin_nocke) = spinboxes

# Buttons
tk.Button(root, text="FOC berechnen", command=berechne_und_anzeigen, relief="raised",bd=4,font=("Arial",10)).grid(row=7, column=0, columnspan=1, pady=10,sticky="e")
tk.Button(root, text="In mm & g umrechnen", command=anzeigen_metrisch).grid(row=7, column=1, columnspan=1, pady=15, padx=10,sticky="w")
tk.Button(root, text="Speichern als txt/xlsx", command=eingaben_speichern).grid(row=7, column=2, columnspan=1, pady=5,sticky="w")
tk.Button(root, text="compound-spine-chart", command=bild_anzeigen_fenster).grid(row=7, column=2, pady=5, sticky="e", padx=5)
tk.Button(root, text="Preset speichern", command=preset_speichern).grid(row=9, column=1,padx=5, pady=5,sticky="w")
# Lade-Button
tk.Button(root, text="Preset laden", command=preset_laden_auswahl).grid(row=9, column=1, padx=5,sticky="e")

tk.Button(root, text="Preset laden", command=preset_laden_auswahl)
tk.Button(root, text="convert", command=gewicht_schaft_aus_eingabe_berechnen).grid(row=2, column=1, padx=5, pady=5,sticky="e")

# Ergebnis
result_label = tk.Label(root, text="", font=("Arial", 12), justify="left")
result_label.grid(row=8, column=0, columnspan=3, pady=10)

from tkinter import ttk

# Variable für Auswahl
preset_var = tk.StringVar()
preset_dropdown = ttk.Combobox(root, textvariable=preset_var, width=30)
preset_dropdown['values'] = lade_verfügbare_presets()
preset_dropdown.grid(row=9, column=2, columnspan=1, pady=5,sticky="w")

# Begrüßungstext (erstmal unsichtbar)
hallo_label = tk.Label(root, text="Schussgenuss mit den Bögner Boys©", font=("Arial", 10, "italic"), fg="darkorange", anchor="se")

# Grafik
chart_frame = tk.Frame(root)
chart_frame.grid(row=10, column=0, columnspan=4)

# Starte GUI
berechne_und_anzeigen()  # ➕ Automatische FOC-Berechnung bei Programmstart
root.mainloop()

# Start GUI
root.mainloop()
