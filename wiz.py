import vtk
from pathlib import Path
import os


# funkcja tworząca LUT do segmentów
def create_lut(colors):
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(141)
    lut.SetTableRange(0,140)
    lut.Build()
    
    lut.SetTableValue(0, colors.GetColor4d('Black'))
    lut.SetTableValue(3, colors.GetColor4d('white')) 
    lut.SetTableValue(4, colors.GetColor4d('beige')) 
    lut.SetTableValue(5, colors.GetColor4d('orange'))  
    lut.SetTableValue(9, colors.GetColor4d('misty_rose'))  
    lut.SetTableValue(10, colors.GetColor4d('plum'))  
    lut.SetTableValue(12, colors.GetColor4d('tomato'))  
    lut.SetTableValue(14, colors.GetColor4d('raspberry'))  
    lut.SetTableValue(17, colors.GetColor4d('banana'))  
    lut.SetTableValue(19, colors.GetColor4d('peru'))  
    lut.SetTableValue(21, colors.GetColor4d('pink'))  
    lut.SetTableValue(23, colors.GetColor4d('powder_blue')) 
    lut.SetTableValue(24, colors.GetColor4d('carrot'))  
    lut.SetTableValue(25, colors.GetColor4d('wheat'))  
    lut.SetTableValue(28, colors.GetColor4d('violet'))  
    lut.SetTableValue(140, colors.GetColor4d('white'))  
    return lut 

def create_iso_surface_actor(file_name, tissue):
    areader = vtk.vtkNrrdReader()
    areader.SetFileName(file_name)
    areader.Update()

    select_tissue = vtk.vtkImageThreshold()
    select_tissue.ThresholdBetween(tissue, tissue)
    select_tissue.SetInValue(255)
    select_tissue.SetOutValue(0)
    select_tissue.SetInputConnection(areader.GetOutputPort())

    gaussian_radius = 1
    gaussian_standard_deviation = 2.0
    gaussian = vtk.vtkImageGaussianSmooth()
    gaussian.SetStandardDeviations(gaussian_standard_deviation, gaussian_standard_deviation,
                                   gaussian_standard_deviation)
    gaussian.SetRadiusFactors(gaussian_radius, gaussian_radius, gaussian_radius)
    gaussian.SetInputConnection(select_tissue.GetOutputPort())

    # iso_value = 63.5
    iso_value = 127.5

    try:
        iso_surface = vtk.vtkFlyingEdges3D()
    except AttributeError:
        iso_surface = vtk.vtkMarchingCubes()

    iso_surface.SetInputConnection(gaussian.GetOutputPort())
    iso_surface.ComputeScalarsOff()
    iso_surface.ComputeGradientsOff()
    iso_surface.ComputeNormalsOff()
    iso_surface.SetValue(0, iso_value)

    smoothing_iterations = 20
    pass_band = 0.001
    feature_angle = 60.0
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputConnection(iso_surface.GetOutputPort())
    smoother.SetNumberOfIterations(smoothing_iterations)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(feature_angle)
    smoother.SetPassBand(pass_band)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOff()
    smoother.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(iso_surface.GetOutputPort())
    normals.SetFeatureAngle(feature_angle)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(normals.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor

colors = vtk.vtkNamedColors()



aRenderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)


iRen = vtk.vtkRenderWindowInteractor()
iRen.SetRenderWindow(renWin)

# określenie ścieżki do plików 
#dirname = Path(os.path.realpath(os.path.dirname(__file__)))/"inner-ear-2018-2"/"image-volumes"


os.chdir(Path(__file__).resolve().parent)
dirname = Path("inner-ear-2018-02/image-volumes")




filename = dirname/"Ear-CT.nrrd"  # ścieżka do raw data
segfilename = dirname/"Ear-seg.nrrd"# ścieżka do segmentacji 



reader = vtk.vtkNrrdReader()
reader.SetFileName(filename)

segmentreader = vtk.vtkNrrdReader()
segmentreader.SetFileName(segfilename)

# do wywalenia prawdopodobnie 

skinExtractor = vtk.vtkMarchingCubes()
skinExtractor.SetInputConnection(reader.GetOutputPort())
skinExtractor.SetValue(0, 1000)

skinMapper = vtk.vtkPolyDataMapper()
skinMapper.SetInputConnection(skinExtractor.GetOutputPort())
skinMapper.ScalarVisibilityOff()

skin = vtk.vtkActor()
skin.SetMapper(skinMapper)
#skin.GetProperty().SetDiffuseColor(colors.GetColor3d("SkinColor"))
skin.GetProperty().SetOpacity(.3)

# Dotąd 


# tworzenie obrysu
outlineData = vtk.vtkOutlineFilter()
outlineData.SetInputConnection(reader.GetOutputPort())

mapOutline = vtk.vtkPolyDataMapper()
mapOutline.SetInputConnection(outlineData.GetOutputPort())

outline = vtk.vtkActor()
outline.SetMapper(mapOutline)
outline.GetProperty().SetColor(colors.GetColor3d("Black"))


# ustawienie lookup tables 

bwLut = vtk.vtkLookupTable()
bwLut.SetTableRange(0, 4000)
bwLut.SetSaturationRange(0, 0)
bwLut.SetHueRange(0, 0)
bwLut.SetValueRange(0, 1)
bwLut.Build()  

# mapowanie danych z użyciem LUT
bwcolors = vtk.vtkImageMapToColors()
bwcolors.SetInputConnection(reader.GetOutputPort())
bwcolors.SetLookupTable(bwLut)
bwcolors.Update()

# stworzenie trzech actorów do płaszczyzn ortogonalnych i ustawienie ich pozycji 
sagittal = vtk.vtkImageActor()
sagittal.GetMapper().SetInputConnection(bwcolors.GetOutputPort())
sagittal.SetDisplayExtent(255, 255, 0, 511, 0, 413)


axial = vtk.vtkImageActor()
axial.GetMapper().SetInputConnection(bwcolors.GetOutputPort())
axial.SetDisplayExtent(0, 511, 0, 511, 207, 207)

coronal = vtk.vtkImageActor()
coronal.GetMapper().SetInputConnection(bwcolors.GetOutputPort())
coronal.SetDisplayExtent(0, 511, 255, 255, 0, 413)


# ustawienie segmentlut 
segment_lut = create_lut(colors)

#mapowanie segmentów z użyciem lut
segmentcolors = vtk.vtkImageMapToColors()
segmentcolors.SetInputConnection(segmentreader.GetOutputPort())
segmentcolors.SetLookupTable(segment_lut)
segmentcolors.Update()

# stworzenie actora do segmentów (ustawienie pozycju pokrywającej się płaszczyzną coronal 
# i opacity na 0.7)
segmentscoronal = vtk.vtkImageActor()
segmentscoronal.GetMapper().SetInputConnection(segmentcolors.GetOutputPort())
segmentscoronal.SetDisplayExtent(0, 511, 255, 255, 0, 413)
segmentscoronal.GetProperty().SetOpacity(.8)

segmentsaxial = vtk.vtkImageActor()
segmentsaxial.GetMapper().SetInputConnection(segmentcolors.GetOutputPort())
segmentsaxial.SetDisplayExtent(0, 511, 0, 511, 207, 207)
segmentsaxial.GetProperty().SetOpacity(.8)

segmentssagittal = vtk.vtkImageActor()
segmentssagittal.GetMapper().SetInputConnection(segmentcolors.GetOutputPort())
segmentssagittal.SetDisplayExtent(255, 255, 0, 511, 0, 413)
segmentssagittal.GetProperty().SetOpacity(.8)

# tissue actor 

tissueactor = create_iso_surface_actor(segfilename,17)
tissueactor.GetProperty().SetDiffuseColor(segment_lut.GetTableValue(17)[:3])
tissueactor.GetProperty().SetDiffuse(1.0)
tissueactor.GetProperty().SetSpecular(.5)
tissueactor.GetProperty().SetSpecularPower(100)

tissueactor1 = create_iso_surface_actor(segfilename,4)
tissueactor1.GetProperty().SetDiffuseColor(segment_lut.GetTableValue(4)[:3])
tissueactor1.GetProperty().SetDiffuse(1.0)
tissueactor1.GetProperty().SetSpecular(.5)
tissueactor1.GetProperty().SetSpecularPower(100)


tissueactor2 = create_iso_surface_actor(segfilename,10)
tissueactor2.GetProperty().SetDiffuseColor(segment_lut.GetTableValue(10)[:3])
tissueactor2.GetProperty().SetDiffuse(1.0)
tissueactor2.GetProperty().SetSpecular(.5)
tissueactor2.GetProperty().SetSpecularPower(100)

tissueactor3 = create_iso_surface_actor(segfilename,140)
tissueactor3.GetProperty().SetDiffuseColor(segment_lut.GetTableValue(140)[:3])
tissueactor3.GetProperty().SetDiffuse(1.0)
tissueactor3.GetProperty().SetSpecular(.5)
tissueactor3.GetProperty().SetSpecularPower(100)

tissueactor4 = create_iso_surface_actor(segfilename,14)
tissueactor4.GetProperty().SetDiffuseColor(segment_lut.GetTableValue(14)[:3])
tissueactor4.GetProperty().SetDiffuse(1.0)
tissueactor4.GetProperty().SetSpecular(.5)
tissueactor4.GetProperty().SetSpecularPower(100)


# ustawienie kamery
aCamera = vtk.vtkCamera()
aCamera.SetViewUp(0, 0, -1)
aCamera.SetPosition(0, -1, 0)
aCamera.SetFocalPoint(0, 0, 0)
aCamera.ComputeViewPlaneNormal()
aCamera.Azimuth(30.0)
aCamera.Elevation(30.0)


# dodanie actorów do renderera 
aRenderer.AddActor(outline)

aRenderer.AddActor(sagittal)
aRenderer.AddActor(axial)
aRenderer.AddActor(coronal)

aRenderer.AddActor(segmentscoronal)
aRenderer.AddActor(segmentsaxial)
aRenderer.AddActor(segmentssagittal)

aRenderer.AddActor(tissueactor)
aRenderer.AddActor(tissueactor1)
aRenderer.AddActor(tissueactor2)
aRenderer.AddActor(tissueactor3)
aRenderer.AddActor(tissueactor4)

#aRenderer.AddActor(skin)
aRenderer.SetActiveCamera(aCamera)
aRenderer.ResetCamera()
aRenderer.SetBackground(colors.GetColor3d("Blue"))

aCamera.Dolly(1.5)



iRen.Initialize()
iRen.Start()

