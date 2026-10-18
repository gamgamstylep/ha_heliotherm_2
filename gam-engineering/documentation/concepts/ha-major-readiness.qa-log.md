# HA version readiness — Q&A log

Verbatim log of the grilling rounds for [ha-major-readiness.md](ha-major-readiness.md). Questions outside this concept are in [../qa-log.md](../qa-log.md).

## 2026-10-18

- **Q11 - Feature-Umfang:** Was gehört zu „bereit für die nächsten großen HA-Versionen“?
  - Antwort: "Veraltete APIs ersetzen (Recommended), CI: hassfest + HACS (Recommended), Modernisieren (Recommended), Release-Hygiene (Recommended)"
- **Q12 - Feature-Ziel:** Passt dieses Feature-Ziel (≤200 Zeichen, dient G-1 „lauffähig auf jeder aktuellen HA-Version“)?
  - Antwort: "Übernehmen (Recommended)"
- **Q13 - Tests:** Sollen automatisierte Tests (pytest-homeassistant-custom-component) in die CI?
  - Antwort: "Ja, an den Nahtstellen (Recommended)"
- **Q14 - Releases:** In wie vielen Schritten soll das ausgeliefert werden?
  - Antwort: "Zwei Releases (Recommended)"
- **Q15 - HACS:** Wie soll die Integration über HACS verteilt werden?
  - Antwort: "Custom Repository (Recommended)"
- **Q16 - INVEST (Valuable/Small) für v1.2.0:** „runtime_data“ allein bringt Nutzern kaum sichtbaren Nutzen, „runtime_data + Coordinator“ zusammen hat Gewicht 8. Wie schneiden?
  - Antwort: "Eine Story, zwei Slices (Recommended)"
