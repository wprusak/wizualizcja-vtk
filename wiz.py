import vtk
from pathlib import Path

colors = vtk.vtkNamedColors()



aRenderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)


iRen = vtk.vtkRenderWindowInteractor()
iRen.SetRenderWindow(renWin)

dirname = Path("inner-ear-2018-02/image-volumes")
filename = dirname/"Ear-CT.nrrd"



reader = vtk.vtkNrrdReader()
reader.SetFileName(filename)

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

outlineData = vtk.vtkOutlineFilter()
outlineData.SetInputConnection(reader.GetOutputPort())

mapOutline = vtk.vtkPolyDataMapper()
mapOutline.SetInputConnection(outlineData.GetOutputPort())

outline = vtk.vtkActor()
outline.SetMapper(mapOutline)
outline.GetProperty().SetColor(colors.GetColor3d("Black"))


# ustawienie lookup tables 

bwLut = vtk.vtkLookupTable()
bwLut.SetTableRange(0, 2000)
bwLut.SetSaturationRange(0, 0)
bwLut.SetHueRange(0, 0)
bwLut.SetValueRange(0, 1)
bwLut.Build()  

# mapowanie danych z użyciem LUT
bwcolors = vtk.vtkImageMapToColors()
bwcolors.SetInputConnection(reader.GetOutputPort())
bwcolors.SetLookupTable(bwLut)
bwcolors.Update()

# stworzenie trzech actorów i ustawienie ich pozycji 
sagittal = vtk.vtkImageActor()
sagittal.GetMapper().SetInputConnection(bwcolors.GetOutputPort())
sagittal.SetDisplayExtent(255, 255, 0, 512, 0, 414)


axial = vtk.vtkImageActor()
axial.GetMapper().SetInputConnection(bwcolors.GetOutputPort())
axial.SetDisplayExtent(0, 512, 0, 512, 207, 207)

coronal = vtk.vtkImageActor()
coronal.GetMapper().SetInputConnection(bwcolors.GetOutputPort())
coronal.SetDisplayExtent(0, 512, 255, 255, 0, 414)



aCamera = vtk.vtkCamera()
aCamera.SetViewUp(0, 0, -1)
aCamera.SetPosition(0, -1, 0)
aCamera.SetFocalPoint(0, 0, 0)
aCamera.ComputeViewPlaneNormal()
aCamera.Azimuth(30.0)
aCamera.Elevation(30.0)

    # Actors are added to the renderer. An initial camera view is created.
    # The Dolly() method moves the camera towards the FocalPoint,
    # thereby enlarging the image.
aRenderer.AddActor(outline)
aRenderer.AddActor(sagittal)
aRenderer.AddActor(axial)
aRenderer.AddActor(coronal)
#aRenderer.AddActor(skin)
aRenderer.SetActiveCamera(aCamera)
aRenderer.ResetCamera()
aRenderer.SetBackground(colors.GetColor3d("Blue"))

aCamera.Dolly(1.5)



iRen.Initialize()
iRen.Start()