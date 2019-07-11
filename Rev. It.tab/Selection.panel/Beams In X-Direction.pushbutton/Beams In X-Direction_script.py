__doc__ = 'This script selects the beams in the x direction.'
__author__ = 'Ibrahim Saad'
__title__ = 'Beams In\nX-Direction'

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from System.Collections.Generic import List



doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

beams = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
beamsx = []

for beam in beams:
    #Beam Location and curve generation
    lc = beam.Location
    curve = lc.Curve
    
    #Beam Direction
    dir = curve.Direction
    
    #beams in X-dir has a vector of a Y component is zero or close to zero (dont know why exactly)
    #so we use the int() function to round the value to zero. Same goes for the Y-dir.
    if int(dir.Y) == 0:
        beamsx.append(beam.Id)
    

xcollection = List[ElementId](beamsx)

sel = uidoc.Selection
sel.SetElementIds(xcollection)
