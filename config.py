AIR_DENSITY = 1.225 # kg per m^3
"""
This is @ 15 deg at 1 atm
See: https://www.engineeringtoolbox.com/air-density-specific-weight-d_600.html
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

# ==============================================================================
# Pattern related config

# For generating the cutting patterns

SEAM_WIDTH = 0.02 # m (2 cm)
MATERIAL_WIDTH = 1.5 # m
