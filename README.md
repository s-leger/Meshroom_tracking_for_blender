# Meshroom tracking import for blender
Import Meshroom camera tracking solution into blender 2.8

Usage
* Create a meshroom project 
* Add your movie as image sequence 
* Solve at least until Structure from motion (Sfm)
* Import cameras.sfm into blender (MeshroomCache/StructureFromMotion/xxx/cameras.sfm)
* Import your surface as obj, using same axis order than in camera importer

Note: default axis order are -Z Forward and Y up

This addon solve alembic import issue for animated camera
