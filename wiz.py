import vtk
aRenderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)
iRen = vtk.vtkRenderWindowInteractor()
iRen.SetRenderWindow(renWin)
iRen.Initialize()
iRen.Start()