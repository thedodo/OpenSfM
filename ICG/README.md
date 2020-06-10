# SV4VI-ICG

ICG source code für das street-view for the visually impaired (SV4VI) Projekt.

Geplante Features: 

- Geo-Lokalisierung mit Bildern anhand von einer Bilder-Datenbank
- Experimentaler Zweig:
  - MonoDepth: Berechnung der Tiefe mit nur einem Bild (kein stereo Bild). Genauigkeit von ca. 0.5m (Idee: wenn man anhand von GPS Daten benachbarte Bilder hat, könnte man Stereo machen? Problem ist die Rektifizierung)
  - Deeplabv3+ mit MobileNet Backbone Image Segmentation: Instance segmentation anstatt Objekterkennung. Liefert information über die Szene.
