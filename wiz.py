import vtk
from pathlib import Path

aRenderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)


iRen = vtk.vtkRenderWindowInteractor()
iRen.SetRenderWindow(renWin)

dirname = Path("inner-ear-2018-02/image-volumes")
filename = dirname/"Ear-CT.nrrd"

#filename = "C:\\Users\\Wicia\\Desktop\\wizualizacja projekt\\inner-ear-2018-02\\image-volumes\\Ear-CT.nrrd"

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
#outline.GetProperty().SetColor(colors.GetColor3d("Black"))


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
aRenderer.AddActor(skin)
aRenderer.SetActiveCamera(aCamera)
aRenderer.ResetCamera()
aCamera.Dolly(1.5)



iRen.Initialize()
iRen.Start()