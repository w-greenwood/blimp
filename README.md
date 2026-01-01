# Blimp Tool

![Screenshot of tool](./example.png)

## Running

`make`

Installs all dependancies to a venv and runs the program. Depends on python3.

## Controls

- Arrow keys + PgUp/PgDn to pitch, yaw and roll

- -/+ keys to zoom in and out

- T to toggle transparency

## Constants

Constants are in `config.py`, currenly the envelope material is Mylar.

## Todo

- Add seam allowence to weight calculation, measured in m offset outwards from the spline which can be used to work out the weight of the allowence.

- Add center of lift and center of mass calculation

- Bake-in the weights into the polygons so that all moves `shapes.py -> envelope.py -> display.py`

- Rename the polygon class

- Add the CFD solver (Lattice-Bosman)

- Re-validate the volume calculator, seems weirdly low

- Make the pattern renderer

- Make the packing solver for working out how much material would be needed approx.


- Add the GUI elements to ajust the spline in real-time
