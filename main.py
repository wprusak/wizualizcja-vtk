import vtk
from pathlib import Path
import os
from functions import create_lut, create_iso_surface_actor,make_slider_widget,SliderProperties,SliderCB


colors = vtk.vtkNamedColors()

#ustawienie rendererów, okna i interaktora

aRenderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)
ren_2 = vtk.vtkRenderer()
renWin.AddRenderer(ren_2)

aRenderer.SetViewport(0.0, 0.0, 0.7, 1.0)
ren_2.SetViewport(0.7, 0.0, 1, 1)

iRen = vtk.vtkRenderWindowInteractor()
iRen.SetRenderWindow(renWin)

# określenie ścieżki do plików 

os.chdir(Path(__file__).resolve().parent)
dirname = Path("inner-ear-2018-02/image-volumes")
filename = dirname/"Ear-CT.nrrd"  # ścieżka do raw data
segfilename = dirname/"Ear-seg.nrrd"# ścieżka do segmentacji 


reader = vtk.vtkNrrdReader()
reader.SetFileName(filename)

segmentreader = vtk.vtkNrrdReader()
segmentreader.SetFileName(segfilename)

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

# ustawienie tissue actors 
tissues = [4,10,14,17,140,23]
tissueactors = []

for tissue in tissues :
    tissueactor = create_iso_surface_actor(segfilename,tissue)
    tissueactor.GetProperty().SetDiffuseColor(segment_lut.GetTableValue(tissue)[:3])
    tissueactor.GetProperty().SetDiffuse(1.0)
    tissueactor.GetProperty().SetSpecular(.5)
    tissueactor.GetProperty().SetSpecularPower(100)
    tissueactors.append(tissueactor)


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

for tissueact in tissueactors:
    aRenderer.AddActor(tissueact)

aRenderer.SetActiveCamera(aCamera)
aRenderer.ResetCamera()
aRenderer.SetBackground(colors.GetColor3d("LightSteelBlue"))
ren_2.SetBackground(colors.GetColor3d("MidnightBlue"))
aCamera.Dolly(1.5)

slider_properties = SliderProperties()
slider_properties.value_initial = .4
slider_properties.title = "Labirynth opacity"

slider_properties.p1 = [0.05, .55]
slider_properties.p2 = [0.25, .55]
cb = SliderCB(tissueactors[1].GetProperty())

slider_widget = make_slider_widget(slider_properties, colors, segment_lut, 10)
slider_widget.SetInteractor(iRen)
slider_widget.SetAnimationModeToAnimate()
slider_widget.EnabledOn()
slider_widget.SetCurrentRenderer(ren_2)
slider_widget.AddObserver(vtk.vtkCommand.InteractionEvent, cb)


renWin.SetSize(1280,720)
renWin.SetWindowName('Wizualizacja')
trackball_style  = vtk.vtkInteractorStyleTrackballCamera()
iRen.SetInteractorStyle(trackball_style)

iRen.Initialize()
iRen.Start()

