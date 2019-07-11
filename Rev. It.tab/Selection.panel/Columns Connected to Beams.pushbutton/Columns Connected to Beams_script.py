__doc__ = 'This script selects all the columns that are connected to beams'
__author__ = 'Ibrahim Saad'
__title__ = 'Columns\nConnected to Beams'

from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from System.Collections.Generic import List
import math

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

beams = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
cols = []

for beam in beams:
    #Beam Location
    lc = beam.Location
    curve = lc.Curve
    
    p = curve.GetEndPoint(0)
    param = curve.GetEndParameter(0)
    transform = curve.ComputeDerivatives(param, False)
    tangent = transform.BasisX
    
    
 
    # Use bounding box to determine elevation of
    # bottom of beam and how far downwards to 
    # offset location line -- one inch below 
    # beam bottom.
      
    bb = beam.get_BoundingBox( None )
    
    inch = 1.0/12.0
    beamBottom = bb.Min.Z
    
    arcCenter = XYZ(p.X, p.Y, beamBottom - inch)
    
    plane = Plane(tangent, arcCenter)
    
    profileLoop = CurveLoop()
    
    arc1 = Arc.Create(plane, inch, 0, math.pi)
    
    arc2 = Arc.Create(plane, inch, math.pi, 2*math.pi)
    
    profileLoop.Append(arc1)
    profileLoop.Append(arc2)
    
    loops = []
    loops.append(profileLoop)
    
    
    
    q = curve.GetEndPoint(1)
    v = q - p
    solid = GeometryCreationUtilities.CreateExtrusionGeometry(loops, v, v.GetLength())

    beamIntersectFilter = ElementIntersectsSolidFilter(solid)
    
    col = FilteredElementCollector(doc).WhereElementIsNotElementType().OfCategory(BuiltInCategory.OST_StructuralColumns).WherePasses(beamIntersectFilter).ToElementIds()
    
    cols.append(col)
    

colsFinal = []

for a in cols:
    for b in a:
        colsFinal.append(b)

collection = List[ElementId](colsFinal)

sel = uidoc.Selection
sel.SetElementIds(collection)
a = sel.GetElementIds()
TaskDialog.Show("Selection of Columns", "{} columns are connected to beams.".format(len(a)))

