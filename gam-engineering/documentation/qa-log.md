# Q&A log

Verbatim log of every question outside concept work (setup, delivery, settings) and its answer. Concept questions live in the concept's own `.qa-log.md`.

## 2026-10-18 — Fix Modbus timeout handling

- **Q1 - HA-Neustart:** Der Fix liegt auf der HA-Samba-Freigabe (Backup im Scratchpad). Für den Test muss Home Assistant neu starten (~1 Min. Ausfall aller Automationen). Jetzt neu starten?
  - Antwort: "Jetzt neu starten (Empfohlen)"
- **Q2 - Git:** Wie sollen die Code-Änderungen ins Repo (aktuell auf main, Remote GitHub)?
  - Antwort: "Branch, Commit + Push"
- **Q3 - CLAUDE.md:** Soll im Projekt festgehalten werden, dass jede Session mit /gam-engineering startet?
  - Antwort: "In CLAUDE.md"
- **Q4 - Was geht nicht:** Stand jetzt (17:36): HA läuft fehlerfrei, Entitäten 'unavailable', die Pumpe (10.19.0.70:502) beantwortet weiterhin keine Modbus-Anfrage – auch direkt vom PC nicht. Worauf bezieht sich 'geht nicht'?
  - Antwort: "starte gerade die wärmepumpe neu. kann man eine entität machen. wärmpepumpe nicht erreichbar?"
- **Q5 - Modbus-Freigabe:** Wurde an der Wärmepumpe/WebControl um den 16.10. etwas geändert (Firmware-Update, Netzwerk, Modbus-Einstellung, Stromausfall)?
  - Antwort: "Nicht bekannt (Empfohlen)"
- **Q6 - HA-Neustart:** Die neue heliotherm_config.json liegt auf HA, wird aber erst nach einem Neustart geladen (~1 Min. Ausfall). Jetzt neu starten?
  - Antwort: "Jetzt neu starten (Empfohlen)"
- **Q7 - Merge:** Branch fix/modbus-timeout-handling (5 Commits) → main, lokaler Merge (--no-ff) + Push, kein MR (Repo hat keine CI; Test erfolgte live in HA). Mergen?
  - Antwort: "Jetzt mergen"

## 2026-10-18 — Setup for "HA major version readiness"

- **Q8 - Projektziel G-1:** Kein GOAL.md vorhanden. Welches Projektziel (max. 200 Zeichen) soll gelten?
  - Antwort: "Vorschlag übernehmen (Recommended)"
- **Q9 - Prozessumfang:** Wie viel gam-engineering-Struktur soll das Projekt bekommen?
  - Antwort: "Schlank (Recommended)"
- **Q10 - Branch-Modell (P-GIT-9):** Es gibt nur main, kein dev. Welches Modell?
  - Antwort: "trunk (Recommended)"
- **Q18 - Merge:** Branch concept/ha-major-readiness (1 Commit, nur Doku + .claude/settings.json + CLAUDE.md) → main (trunk), lokaler Merge --no-ff + Push, kein PR, keine CI. Mergen?
  - Antwort: "Jetzt mergen"
