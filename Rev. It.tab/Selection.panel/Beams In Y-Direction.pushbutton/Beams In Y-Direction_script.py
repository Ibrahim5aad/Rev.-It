__doc__ = 'This script selects the beams in the y direction.'
__author__ = 'Ibrahim Saad'
__title__ = 'Beams In\nY-Direction'

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from System.Collections.Generic import List


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

beams = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
beamsy = []

for beam in beams:
    #Beam Location and curve generation
    lc = beam.Location
    curve = lc.Curve  #returns a line curve
    
    #Beam Direction
    dir = curve.Direction  #returns a vector 
    
    #beams in Y-dir has a vector of a X component is zero or close to zero (dont know why exactly)
    #so we use the int() function to round the value to zero.
    if int(dir.X) == 0:
        beamsy.append(beam.Id)



ycollection = List[ElementId](beamsy)

sel = uidoc.Selection
sel.SetElementIds(ycollection)
