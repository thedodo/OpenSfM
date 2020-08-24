# SV4VI-ICG

ICG source code für das street-view for the visually impaired (SV4VI) Projekt.

Verwendung:

Nachdem das repository lokal gedownloaded/geklont wurde, muss einmalig für die Installation folgendes ausgeführt werden (nur unter Ubuntu 18.04 getestet).
In der Konsole in diesem Ordner:

- chmod +x install_opensfm.sh
- sh install_opensfm.sh 
  - Dieses Skript sollte alle Abhängigkeiten automatisch installieren. Dieser Vorgang kann je nach Architektur einige Minuten dauern.
- Nachdem das Skript ohne Fehler durchgelaufen ist, kann die Installation mit sh test_install.sh getestet werden.
  - chmod +x test_install.sh
  - sh test_install.sh
- Wenn alles geklappt hat, sollte sich in /pfad/zu/opensfm/data/lund/undistorted/depthmaps/ eine Datei namens merged.ply befinden.
  - Die 3D Reconstruktion kann mit beliebigen Programm geöffnet werden, z.B.: 
    - CloudCompare: https://www.danielgm.net/cc/
    - Meshlab: https://www.meshlab.net/


Geplante Features: 

- Experimentaler Zweig:
  - MonoDepth: Berechnung der Tiefe mit nur einem Bild (kein stereo Bild). Genauigkeit von ca. 0.5m (Idee: wenn man anhand von GPS Daten benachbarte Bilder hat, könnte man Stereo machen? Problem ist die Rektifizierung)
  - Deeplabv3+ mit MobileNet Backbone Image Segmentation: Instance segmentation anstatt Objekterkennung. Liefert information über die Szene.
