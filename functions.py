import vtk

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