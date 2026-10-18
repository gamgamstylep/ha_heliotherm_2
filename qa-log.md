# Q&A log

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
