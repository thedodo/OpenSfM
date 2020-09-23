# SV4VI-ICG

ICG source code für das street-view for the visually impaired (SV4VI) Projekt. Die baseline bildet OpenSfM von Mapillary (siehe unten). Dieses repository ist ein fork. 
**ICG-main.py** (in diesem Ordner) dient als Einstiegspunkt für alle weiteren Funktionalitäten. Hinweis: Diese und alle weiteren Funktionen sind in python3 geschrieben. Ist dies lokal nicht der Standard, sondern python2 müssen alle Funktionen mit python3 statt python aufgerufen werden.

Nachdem das repository lokal gedownloaded/geklont wurde, muss einmalig für die Installation folgendes ausgeführt werden (nur unter Ubuntu 18.04 getestet):

- python ICG-main.py --build

Da hier sehr viel eingerichtet und installiert wird, kann dieser Schritt (je nach Hardware) auch bis zu einer Stunde dauern. Dieser Schritt muss nur einmal(!) ausgeführt werden. Ob die Einrichtung funktioniert hat, kann mit:

- python ICG-main.py --test 

getestet werden. Bekommt man die Meldung: **Die Einrichtung hat funktioniert!** hat alles geklappt. Bei **Leider scheint etwas schief gelaufen zu sein. Bitte kontrolliere die log-files!** ist etwas schief gegangen. Bitte sie dir *log_test.txt* für mehr Information an oder kontaktiere uns. 

Hat alles geklappt kann man die neue Funktionalität mit: 

- python ICG-main.py --test_loc

testen. Hierbei werden folgende Schritte ausgeführt:

- Es wird ein von uns erstellter Testdatensatz der Inffeldgasse heruntergeladen. Dieser besteht aus ~300 Bildern und einem zugehörigen CVS Datei welche die Lat/Lon Metadaten beinhaltet. 
- Die Bilder werden geo-referenziert (Lat/Lon wird als Metadaten in das JPEG Format gespeichert). Dies ist ein notwendiger Zwischenschritt für alle weiteren Schritte.
- Es wird eine 3D-Rekonstruktion aus den Bildern erstellt. Da jedes Bild mit jedem getestet wird, kann dies je nach Hardware sehr lange dauern.
- Anschließend wird die Rekonstruktion von XYZ-Koordinaten in Lat/Lon-Koordinaten überführt.
- Ein zufälliges Bild wird ausgewählt und anhand der Punktwolke lokalisiert. Das Ergebnis wird auf die Konsole ausgegeben.
- Anschließend wird von der Punktwolke noch ein Abbild von der Vogelperspektive gemacht. Dieses wird abgespeichert.


Alle Schritte können auch einzeln mit folgenden Befehlen ausgeführt werden. Eine Liste von allen möglichen Befehlen kann mit **python ICG-main.py --help** angesehen werden: 

- python ICG-main.py --gps2jpg /lokaler/pfad/zu/jpegundcvs. Diese Funktion wird verwendet um die GPS Koordinaten der CVS Datei in den Bildern als Metadatei abzuspeichern. Dieser Schritt ist notwendig um später die Lokalisierung im richtigen Koordinatensystem durchführen zu können. Dieser Schritt sollte **VOR** der Rekonstruktion gemacht werden. 

- python ICG-main.py --reconstruct lokaler/pfad/zu/bildern. Funktion zur 3D Rekonstruktion einer Sequenz von Bildern. Hier werden die Bilder zuerst in den entsprechenden Ordner kopiert (*./data/name/images/*) und anschließend die entsprechenden Funktionen zur Rekonstruktion aufgerufen. Je nach Hardware und Anzahl/Auflösung der Bildern kann es lange dauern. Die 3D-Rekonstruktion kann dann in *./data/name/undistorted/depthmaps/merged.ply* angesehen werden.


- python ICG-main.py --georef_ply /OSfM_data_path. Wird verwendet um eine Transformation der 3D Rekonstruktion von XYZ zu GPS zu machen. Die Funktionen 'python ICG-main.py --gps2jpg' und 'python ICG-main.py --reconstruct' sind beides Vorbedingungen.


==========================================================================
#### README von Mappillary zu OpenSfM:

OpenSfM [![Build Status](https://travis-ci.org/mapillary/OpenSfM.svg?branch=master)](https://travis-ci.org/mapillary/OpenSfM)
=======

## Overview
OpenSfM is a Structure from Motion library written in Python. The library serves as a processing pipeline for reconstructing camera poses and 3D scenes from multiple images. It consists of basic modules for Structure from Motion (feature detection/matching, minimal solvers) with a focus on building a robust and scalable reconstruction pipeline. It also integrates external sensor (e.g. GPS, accelerometer) measurements for geographical alignment and robustness. A JavaScript viewer is provided to preview the models and debug the pipeline.

<p align="center">
  <img src="https://docs.opensfm.org/_images/berlin_viewer.jpg" />
</p>

Checkout this [blog post with more demos](http://blog.mapillary.com/update/2014/12/15/sfm-preview.html)


## Getting Started

* [Building the library][]
* [Running a reconstruction][]
* [Documentation][]


[Building the library]: https://docs.opensfm.org/building.html (OpenSfM building instructions)
[Running a reconstruction]: https://docs.opensfm.org/using.html (OpenSfM usage)
[Documentation]: https://docs.opensfm.org  (OpenSfM documentation)

## License
OpenSfM is BSD-style licensed, as found in the LICENSE file.
