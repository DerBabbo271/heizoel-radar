# Heizöl-Radar: iPhone-Einrichtung

## Status
Das Widget ist vorbereitet, aber **noch kein automatischer Heizölpreisabruf aktiv**.
Ohne verifizierte Daten erscheint „Preis nicht verfügbar“.

## Scriptable
1. Öffne Scriptable und dein Skript „Heizöl Radar“.
2. Ersetze den bisherigen Code durch den Inhalt von [scriptable/heizoel.js](scriptable/heizoel.js).
3. Tippe auf ▶ und prüfe die Vorschau.
4. Halte den iPhone-Sperrbildschirm gedrückt → Anpassen → Sperrbildschirm.
5. Füge unter der Uhr ein rechteckiges Scriptable-Widget hinzu und wähle „Heizöl Radar“.

## Daten
[prices.json](prices.json) ist die zentrale JSON-Datei. Es dürfen nur nachweislich aktuelle, vollständig inklusive Mehrwertsteuer und Lieferkosten berechnete Preise für **2.000 Liter nach 90552** mit `status: "ok"` veröffentlicht werden. `checked_at` ist ein ISO-8601-Zeitstempel, `source_url` die belegte Angebotsquelle.

## GitHub Actions
Der Workflow führt täglich einen Prüflauf aus. **Er ruft noch keine Heizölpreise ab.** Dazu muss erst eine geeignete, zulässige Quelle verifiziert und der Adapter implementiert werden.
