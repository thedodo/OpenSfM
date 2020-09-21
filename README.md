# SV4VI-ICG

ICG source code für das street-view for the visually impaired (SV4VI) Projekt. Die baseline bildet OpenSfM von Mapillary (siehe unten). Dieses repository ist ein fork. 
ICG-main.py (in diesem Ordner) dient als Einstiegspunkt für alle weiteren Funktionalitäten. Hinweis: Diese und alle weiteren Funktionen sind in python3 geschrieben. Ist dies lokal nicht der Standard, sondern python2 müssen alle Funktionen mit python3 statt python aufgerufen werden.

Nachdem das repository lokal gedownloaded/geklont wurde, muss einmalig für die Installation folgendes ausgeführt werden (nur unter Ubuntu 18.04 getestet):

- python ICG-main.py --build

Da hier sehr viel eingerichtet und installiert wird, kann dieser Schritt (je nach Hardware) auch bis zu einer Stunde dauern. Dieser Schritt muss nur einmal(!) ausgeführt werden. Ob die Einrichtung funktioniert hat, kann mit:

- python ICG-main.py --test 

getestet werden. Bekommt man die Meldung: <bold>Die Einrichtung hat funktioniert!</bold> hat alles geklappt. Bei <bold>Leider scheint etwas schief gelaufen zu sein. Bitte kontrolliere die log-files!</bold> ist etwas schief gegangen. Bitte sie dir 'log_test.txt' für mehr Information an oder kontaktiere uns. 





===================================================================================================================================================

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
