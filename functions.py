import vtk

def create_lut(colors):
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(141)
    lut.SetTableRange(0,140)
    lut.Build()
    
    lut.SetTableValue(0, colors.GetColor4d('Black')) # background 
    lut.SetTableValue(3, colors.GetColor4d('white')) # Temporal Bone
    lut.SetTableValue(4, colors.GetColor4d('beige')) # Tympanic membrane 
    lut.SetTableValue(5, colors.GetColor4d('orange'))  # facial nerve 
    lut.SetTableValue(9, colors.GetColor4d('misty_rose'))  #Cochlear Nerve
    lut.SetTableValue(10, colors.GetColor4d('plum'))  #Labirynth
    lut.SetTableValue(12, colors.GetColor4d('tomato'))  #Fenestra rotunda 
    lut.SetTableValue(14, colors.GetColor4d('raspberry'))  #Incus bone
    lut.SetTableValue(17, colors.GetColor4d('banana'))  #Stapes bone
    lut.SetTableValue(19, colors.GetColor4d('peru'))  #Tensor Tympani muscule
    lut.SetTableValue(21, colors.GetColor4d('pink'))  #Internal Jugular vein
    lut.SetTableValue(23, colors.GetColor4d('powder_blue')) #Osseous spiral lamina
    lut.SetTableValue(24, colors.GetColor4d('carrot'))  #Internal Carotd Artery 
    lut.SetTableValue(25, colors.GetColor4d('wheat'))  # Vestibular nerve 
    lut.SetTableValue(28, colors.GetColor4d('violet'))  # Stapedius muscle
    lut.SetTableValue(140, colors.GetColor4d('white'))  # Malleus bone
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

    gaussian_radius = 2
    gaussian_standard_deviation = 3.0
    gaussian = vtk.vtkImageGaussianSmooth()
    gaussian.SetStandardDeviations(gaussian_standard_deviation, gaussian_standard_deviation,
                                   gaussian_standard_deviation)
    gaussian.SetRadiusFactors(gaussian_radius, gaussian_radius, gaussian_radius)
    gaussian.SetInputConnection(select_tissue.GetOutputPort())

    iso_value = 63.5
    # iso_value = 127.5

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

class SliderProperties:
    tube_width = 0.008
    slider_length = 0.008
    title_height = 0.01
    label_height = 0.01

    value_minimum = 0.0
    value_maximum = 1.0
    value_initial = 1.0

    p1 = [0.1, 0.1]
    p2 = [0.3, 0.1]

    title = None

    title_color = 'MistyRose'
    value_color = 'Cyan'
    slider_color = 'Coral'
    selected_color = 'Lime'
    bar_color = 'Yellow'
    bar_ends_color = 'Gold'

def make_slider_widget(properties, colors, lut, idx):
    slider = vtk.vtkSliderRepresentation2D()

    slider.SetMinimumValue(properties.value_minimum)
    slider.SetMaximumValue(properties.value_maximum)
    slider.SetValue(properties.value_initial)
    slider.SetTitleText(properties.title)

    slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider.GetPoint1Coordinate().SetValue(properties.p1[0], properties.p1[1])
    slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider.GetPoint2Coordinate().SetValue(properties.p2[0], properties.p2[1])

    slider.SetTubeWidth(properties.tube_width)
    slider.SetSliderLength(properties.slider_length)
    slider.SetTitleHeight(properties.title_height)
    slider.SetLabelHeight(properties.label_height)

    # Set the color properties

    slider.GetTubeProperty().SetColor(colors.GetColor3d(properties.bar_color))
    slider.GetCapProperty().SetColor(colors.GetColor3d(properties.bar_ends_color))
    slider.GetSliderProperty().SetColor(colors.GetColor3d(properties.slider_color))
    slider.GetSelectedProperty().SetColor(colors.GetColor3d(properties.selected_color))
    slider.GetLabelProperty().SetColor(colors.GetColor3d(properties.value_color))
    if idx in range(0, 140):
        slider.GetTitleProperty().SetColor(lut.GetTableValue(idx)[:3])
        slider.GetTitleProperty().ShadowOff()
    else:
        slider.GetTitleProperty().SetColor(colors.GetColor3d(properties.title_color))

    slider_widget = vtk.vtkSliderWidget()
    slider_widget.SetRepresentation(slider)

    return slider_widget

    
class SliderCB:
    def __init__(self, actor_property):
        self.actorProperty = actor_property

    def __call__(self, caller, ev):
        slider_widget = caller
        value = slider_widget.GetRepresentation().GetValue()
        self.actorProperty.SetOpacity(value)