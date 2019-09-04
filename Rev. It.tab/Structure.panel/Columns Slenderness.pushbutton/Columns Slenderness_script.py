__doc__ = 'This script calculates the slenderness ratio of the columns, writes a comment specifying if its short or long column and overides columns colors based on some color criteria'
__author__ = 'Ibrahim Saad'
__title__ = 'Columns\nSlenderness'


import math
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.UI import *
from System.Collections.Generic import List
from Autodesk.Revit.DB.Structure.StructuralSections import StructuralSectionUtils


doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


def all_elements_of_category(category):
	
    """returns a collection of elements of a passed category"""
    
    return FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()


def set_parameter_by_name(element, parameterName, value):
	
    """set a new value for the passed parameter name    
    for the passed element"""
    
    element.LookupParameter(parameterName).Set(value)



def get_cols_to_beams(beams):
    
    """pass a list of beams to this function and
       it will return a list of columns Ids that is 
       connected to this list of beams"""
       
    colsbi = []
    colsb = []
    
    for beam in beams:
        #Beam location and curve
        lc = beam.Location
        curve = lc.Curve
        
        p = curve.GetEndPoint(0)
        param = curve.GetEndParameter(0)
        transform = curve.ComputeDerivatives(param, False)
        tangent = transform.BasisX
        
        
     
        # Use bounding box to determine elevation of
        # bottom of beam
          
        bb = beam.get_BoundingBox( None )
        inch = 1.0/12.0
        beamBottom = bb.Min.Z
        
        #The centre of the arcs is 1 ince below the beam bottom 
        arcCenter = XYZ(p.X, p.Y, beamBottom - inch)
        
        #Construct a plane for the arc by an origin = arcCenter and a normal vetor = tangent
        plane = Plane(tangent, arcCenter)
        
        #Create the chain of curves
        profileLoop = CurveLoop()
        
        #Construct the circular arcs by passing the plane, the radius = inch, the start and end angles
        arc1 = Arc.Create(plane, inch, 0, math.pi)
        arc2 = Arc.Create(plane, inch, math.pi, 2*math.pi)
        
        #Append the arcs to the loop
        profileLoop.Append(arc1)
        profileLoop.Append(arc2)
        
        loops = []
        loops.append(profileLoop)
        
        q = curve.GetEndPoint(1)
        
        #The direction vector
        v = q - p
        
        #Constuct the solid by passing the loops,the direction and the length
        solid = GeometryCreationUtilities.CreateExtrusionGeometry(loops, v, v.GetLength())

        #Define an element filter based on the intersection of a given solid
        beamIntersectFilter = ElementIntersectsSolidFilter(solid)
        
        #Collect the column instances that pass the intersection filter
        col = FilteredElementCollector(doc).WhereElementIsNotElementType().OfCategory(BuiltInCategory.OST_StructuralColumns).WherePasses(beamIntersectFilter).ToElementIds()
        
        colsbi.append(col)
        
        for i in colsbi:
            for j in i:
                colsb.append(j)
        
        
    return colsb



def k(column):

    """a function returns a list
       of kx and ky; coefficients that
       depend on the end conditions of the
       columns in x and y directions"""

    
    if column in cx:
        ky = 1.5
        if bdepth >= xdict[column]:
            kx = 1.2
        else:
            kx = 1.5

    elif column in cy:
        kx = 1.5
        if bdepth >= ydict[column]:
            ky = 1.2
        else:
            ky = 1.5
    elif column in cxy:
        if bdepth >= ydict[column] and bdepth >= xdict[column]:
            kx = 1.2
            ky = 1.2
        if bdepth >= ydict[column] and bdepth < xdict[column]:
            kx = 1.5
            ky = 1.2
        if bdepth < ydict[column] and bdepth >= xdict[column]:
            kx = 1.2
            ky = 1.5
        if bdepth < ydict[column] and bdepth < xdict[column]:
            kx = 1.5
            ky = 1.5
                
    elif column in cn:
        kx = 1.5
        ky = 1.5
            
            
    return [kx, ky]


def clearheight(column):
    
    h = int(30.48*column.LookupParameter("Length").AsDouble())
    
    if column.Id in cx:
        hx = h - bdepth
        hy = h - sdepth
    
    if column.Id in cy:
        hx = h - sdepth
        hy = h - bdepth
    
    if column.Id in cxy:
        hx = h - bdepth
        hy = h - bdepth
        
    if column.Id in cn:
        hx = h - sdepth
        hy = h - sdepth
        
    return [hx, hy]
    

beams = all_elements_of_category(BuiltInCategory.OST_StructuralFraming) # all beams
cols = all_elements_of_category(BuiltInCategory.OST_StructuralColumns)  # all columns

beamsx = []  #Beams in X-Dir
beamsy = []  #Beams in Y-Dir
for beam in beams:
    #Beam Location
    lc = beam.Location
    curve = lc.Curve
    
    dir = curve.Direction #returns a vector 
    
    if int(dir.Y) == 0:    
        beamsx.append(beam)
        
    if int(dir.X) == 0:
        beamsy.append(beam) 


colsbx = get_cols_to_beams(beamsx)  
colsby = get_cols_to_beams(beamsy)


#Somehow those lists contains some elements that are not family instances of type column
#when using the len function you will find that the lists have more elements than expected to return
#I dont know what exactly are these that return with the columns
#but when selected you only get the beams
#so here is a way to filter down the results by setting and getting the element ids

xcollection = List[ElementId](colsbx)
sel1 = uidoc.Selection
sel1.SetElementIds(xcollection)
xcol = sel1.GetElementIds()    

ycollection = List[ElementId](colsby)
sel2 = uidoc.Selection
sel2.SetElementIds(ycollection)
ycol = sel2.GetElementIds()    
 

cx1= []      
cy1 = []           
for x in xcol:
    cx1.append(x) 
for y in ycol:
    cy1.append(y)
 

 
#filter down column with beams in x-dir only, y-dir only and both directions

cxy = []          #List of Column Ids that are connected to beams in both directions
cx = []           #List of Column Ids that are connected to beams in X-direction only
cy = []           #List of Column Ids that are connected to beams in Y-direction only


for c in cx1:
    if c in cy1:
        cxy.append(c)
    
for c in cx1: 
    if c not in cy1:
        cx.append(c)
    
for c in cy1:
    if c not in cx1:
        cy.append(c)
        
cb = cx + cy + cxy
cn = []

for c in cols:
    if c.Id not in cb:
        cn.append(c.Id)



#Getting the dimensions of the columns in x and y directions its bounding box properties
#and making dictionaries of the x dim and y dim of columns
#     key  =  Column Id
#     value  =  X or Y dimensions
    
xdict = {}
ydict = {}
        
for cc in cols:
    box = cc.get_BoundingBox(doc.ActiveView)
    dimx = box.Max.X - box.Min.X
    dimy = box.Max.Y - box.Min.Y
    
    xdict[cc.Id] = int(dimx*30.48)
    ydict[cc.Id] = int(dimy*30.48)
    

#Getting the beam depth
bbox = beams[0].get_BoundingBox(doc.ActiveView) 
bdepth = int(30.48*(bbox.Max.Z - bbox.Min.Z)) #in centimeters


#Getting the slab thikness
slab = all_elements_of_category(BuiltInCategory.OST_StructuralFraming)
sbox = slab[0].get_BoundingBox(doc.ActiveView)
sdepth = int(30.48*(sbox.Max.Z - sbox.Min.Z)) #in centimeters




      

colorx = Color(255, 0, 0)
colory = Color(0, 255, 0)
colorxy = Color(0, 0, 255)

#Getting the Solid Fill pattern
fillpatterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
solidfill = None
for pattern in fillpatterns:
    if pattern.GetFillPattern().IsSolidFill:
        solidfill= pattern


t1 = Transaction(doc, "Create New View")
t1.Start()


#Creating a new 3D View to override the its Visibility/Graphics  
views = FilteredElementCollector(doc).OfClass(ViewFamilyType)
for view in views:
    if view.ViewFamily == ViewFamily.ThreeDimensional:
        new3d = View3D.CreateIsometric(doc, view.Id)
        new3d.Name = "Columns Slenderness Check"
        new3d.get_Parameter(BuiltInParameter.MODEL_GRAPHICS_STYLE).Set(4)

#Hiding the Analytical Model elements in the new view
for cat in new3d.Document.Settings.Categories:
    if cat.get_AllowsVisibilityControl(new3d):
        if cat.CategoryType == CategoryType.AnalyticalModel:
            new3d.SetVisibility(cat, False)
 
t1.Commit()

#Set the new veiw as the Active View
uidoc.RequestViewChange(new3d)
uidoc.ActiveView = new3d


#Start anothe transaction to override the graphics settings of the columns
#based on the Slenderness Ratio
 
t2 = Transaction(doc, "Columns Slenderness via Colors")
t2.Start()

ovgx = OverrideGraphicSettings()
ovgy = OverrideGraphicSettings()
ovgxy = OverrideGraphicSettings()

ovgx.SetProjectionFillColor(colorx)
ovgy.SetProjectionFillColor(colory)
ovgxy.SetProjectionFillColor(colorxy)

ovgx.SetProjectionFillPatternId(solidfill.Id)
ovgy.SetProjectionFillPatternId(solidfill.Id)
ovgxy.SetProjectionFillPatternId(solidfill.Id)

ovgx.SetSurfaceTransparency(60)
ovgy.SetSurfaceTransparency(60)
ovgxy.SetSurfaceTransparency(60)


for column in cols:
    list = []
    
    kxdir = k(column.Id)[0]
    kydir = k(column.Id)[1]
    hxdir = clearheight(column)[0]
    hydir = clearheight(column)[1]
    thx = xdict[column.Id]
    thy = ydict[column.Id]
    
    
    lambdax = (kxdir*hxdir)/thx
    lambday = (kydir*hydir)/thy
    
    list.append(kxdir)
    list.append(kydir)
    list.append(hxdir)
    list.append(hydir)
    list.append(thx)
    list.append(thy)
    list.append(lambdax)
    list.append(lambday)
    

    if lambdax < 10 and lambday < 10:
        set_parameter_by_name(column, "Comments", "Short in both directions.")
        
    if lambdax < 10 and lambday > 10 and lambday < 23:
        set_parameter_by_name(column, "Comments", "X-dir: Short, Y-dir: Long")
    
    if lambdax < 10 and lambday > 23:
        set_parameter_by_name(column, "Comments", "X-dir: Short, Y-dir: Redesign")
        doc.ActiveView.SetElementOverrides(column.Id, ovgy)
        
    
    if lambdax > 10 and lambdax < 23 and lambday < 10:
        set_parameter_by_name(column, "Comments", "X-dir: Long, Y-Dir: Short")
    
    if lambdax > 10 and lambdax < 23 and lambday > 10 and lambday < 23:
        set_parameter_by_name(column, "Comments", "Long in both directions.")
    
    if lambdax > 10 and lambdax < 23 and lambday > 23:
        set_parameter_by_name(column, "Comments", "X-dir: Long, Y-dir: Redesign")
        doc.ActiveView.SetElementOverrides(column.Id, ovgy)
    
    if lambdax > 23 and lambday < 10:
        set_parameter_by_name(column, "Comments", "X-dir: Redesign, Y-dir: Short")
        doc.ActiveView.SetElementOverrides(column.Id, ovgx)
    
    if lambdax > 23 and lambday > 10 and lambday < 23:
        set_parameter_by_name(column, "Comments", "X-dir: Redesign, Y-dir: Long")
        doc.ActiveView.SetElementOverrides(column.Id, ovgx)
    
    if lambdax > 23 and lambday > 23:
        set_parameter_by_name(column, "Comments", "Redesign for both directions.")
        doc.ActiveView.SetElementOverrides(column.Id, ovgxy)

t2.Commit()