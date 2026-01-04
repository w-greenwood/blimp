AIR_DENSITY = 1.225 # kg per m^3
AIR_PRESSURE = 100129 # Pa
"""
density is @ 15 deg at 1 atm
See: https://www.engineeringtoolbox.com/air-density-specific-weight-d_600.html

pressure is @ 15 deg at 100m
See: https://www.mide.com/air-pressure-at-altitude-calculator
"""

H2_DENSITY = 0.0841
"""
This is @ 15 deg at 1 bara
See: https://www.engineeringtoolbox.com/hydrogen-H2-density-specific-weight-temperature-pressure-d_2044.html
"""

"""
PVC: 918 (https://www.matweb.com/search/datasheet.aspx?matguid=35691707c40445388b94db19e000c50a&ckck=1)
MYLAR: 1390 (https://laminatedplastics.com/mylar.pdf)
"""
ENVELOPE_DENSITY = 948 # kg per m^3
ENVELOPE_THICKNESS = 0.00025 # m (0.25 mm)
ENVELOPE_ELASTICITY = 35000000 # Pa
""" ^^^
This is the modulus of elasticity

This is a guess at the moment based on the PVC datasheet above, but it has a
wide tolerance. I would sugest that this is mesured.
"""
TEST_PRESSURE = 110000 # Pa
MAX_PRESSURE = 120000 # Pa
# guessed this

# ==============================================================================
# Pattern related config

# For generating the cutting patterns

SEAM_WIDTH = 0.02 # m (2 cm)
MATERIAL_WIDTH = 1.5 # m
