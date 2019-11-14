import adsk.core, adsk.fusion, adsk.cam, traceback, math, os.path

handlers = []

class NBELButtonPressedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            cmd = args.command
            inputs = cmd.commandInputs
             
            #NumberOfLinks = inputs.addValueInput('_Links','Number of links: ',' ',adsk.core.ValueInput.createByReal(0))

            #if int(NumberOfLinks.value) == 2 :
            # Adding all the different features to the dialog box

            #Selecting edges for first link
            selectionInput1 = inputs.addSelectionInput('selection_1', 'Select first circular edge for first link', 'Select a circular edge')
            selectionInput1.setSelectionLimits(1,1)
            selectionInput1.addSelectionFilter('CircularEdges')
            selectionInput2 = inputs.addSelectionInput('selection_2', 'Select second circular edge for first link', 'Select a circular edge')
            selectionInput2.setSelectionLimits(1,1)
            selectionInput2.addSelectionFilter('CircularEdges')

            #Display first link length
            inputs.addTextBoxCommandInput('textBox1', 'First Link length', '', 2, True)

            #Selecting edges for second link
            selectionInput3 = inputs.addSelectionInput('selection_3', 'Select first circular edge for second link', 'Select a circular edge')
            selectionInput3.setSelectionLimits(1,1)
            selectionInput4 = inputs.addSelectionInput('selection_4', 'Select second circular edge for second link', 'Select a circular edge')
            selectionInput4.setSelectionLimits(1,1)
            selectionInput4.addSelectionFilter('CircularEdges')

            #Display second link length
            inputs.addTextBoxCommandInput('textBox2', 'second Link length', '', 2, True)

            #Enter the values for the x and y coordinates
            Xposition = inputs.addValueInput('_X', 'Coordenate X: ','',adsk.core.ValueInput.createByReal(10))
            Yposition = inputs.addValueInput('_Y', 'Coordenate Y: ','',adsk.core.ValueInput.createByReal(5))

            #Selecting first joint for move the robotic arm
            selectionInput5 = inputs.addSelectionInput('selection_5', 'Select first joint', 'Select a revolute joint')
            selectionInput5.setSelectionLimits(1,1)
            selectionInput5.addSelectionFilter('Joints')

            #Display First Angle
            inputs.addTextBoxCommandInput('textBox3', 'First Angle', '', 2, True)

            #Selecting second joint for move the robotic arm
            selectionInput6 = inputs.addSelectionInput('selection_6', 'Select second joint', 'Select a revolute joint')
            selectionInput6.setSelectionLimits(1,1)
            selectionInput6.addSelectionFilter('Joints')

            #Display second Angle
            inputs.addTextBoxCommandInput('textBox4', 'Second Angle', '', 2, True)

            onInputChanged = NBELDialogInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)



        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class NBELDialogInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui  = app.userInterface
        try:
            command = args.firingEvent.sender

            point1 = None
            point2 = None
            point3 = None
            point4 = None

            Xposition = command.commandInputs.itemById('_X').value
            Yposition = command.commandInputs.itemById('_Y').value
            
            #First Link
            selectionInput = command.commandInputs.itemById('selection_1')
            if selectionInput.selectionCount > 0:
                selection1 = selectionInput.selection(0).entity
                geom1 = selection1.geometry
                if geom1.objectType == adsk.core.Circle3D.classType():
                    point1 = geom1.center
            selectionInput = command.commandInputs.itemById('selection_2')
            if selectionInput.selectionCount > 0:
                selection2 = selectionInput.selection(0).entity
                geom2 = selection2.geometry
                if geom2.objectType == adsk.core.Circle3D.classType():
                    point2 = geom2.center
            
            #Second Link        
            selectionInput = command.commandInputs.itemById('selection_3')
            if selectionInput.selectionCount > 0:
                selection3 = selectionInput.selection(0).entity
                geom3 = selection3.geometry
                if geom3.objectType == adsk.core.Circle3D.classType():
                    point3 = geom3.center
            selectionInput = command.commandInputs.itemById('selection_4')
            if selectionInput.selectionCount > 0:
                selection4 = selectionInput.selection(0).entity
                geom4 = selection4.geometry
                if geom4.objectType == adsk.core.Circle3D.classType():
                    point4 = geom4.center

            
    
            if point1 and point2:
                distance = getDistanceBetweenPoints(point1, point2)
                textBox = command.commandInputs.itemById('textBox1')
                textBox.text = str(distance)
            if point3 and point4:
                distance2 = getDistanceBetweenPoints2(point3, point4)
                textBox2 = command.commandInputs.itemById('textBox2')
                textBox2.text = str(distance2)
            if point1 and point2 and point3 and point4:
                Angle_1 = getAngle1(point1, point2, point3, point4, Xposition, Yposition)
                textBox3 = command.commandInputs.itemById('textBox3')
                textBox3.text = str(Angle_1)
                Angle_2 = getAngle2(point1, point2, point3, point4, Xposition, Yposition)
                textBox4 = command.commandInputs.itemById('textBox4')
                textBox4.text = str(Angle_2)
            

            #First Joint
            selectionInput = command.commandInputs.itemById('selection_5')
            if selectionInput.selectionCount > 0:
                selection5 = selectionInput.selection(0).entity
                joint :adsk.fusion.Joint = selection5

                for v in range(0,int(Angle_1),2):
                    joint.angle.expression = str(v)
                    app.activeViewport.refresh()

            #Second Joint
            selectionInput = command.commandInputs.itemById('selection_6')
            if selectionInput.selectionCount > 0:
                selection6 = selectionInput.selection(0).entity
                joint :adsk.fusion.Joint = selection6

                for v in range(0,int(Angle_2),2):
                    joint.angle.expression = str(v)
                    app.activeViewport.refresh()

        except:
            if ui:
                ui.messageBox('Input change failed:\n{}'.format(traceback.format_exc()))

def getDistanceBetweenPoints(point1, point2) -> float:
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        lengthBetweenPoints = point1.distanceTo(point2)
        unitsMgr = design.unitsManager
        displayBeltLength = unitsMgr.formatInternalValue(lengthBetweenPoints, unitsMgr.defaultLengthUnits, True)
        return displayBeltLength

    except:
        if ui:
            ui.messageBox('Get distance failed:\n{}'.format(traceback.format_exc()))

def getDistanceBetweenPoints2(point3, point4) -> float:
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        lengthBetweenPoints2 = point3.distanceTo(point4)
        unitsMgr = design.unitsManager
        displayBeltLength2 = unitsMgr.formatInternalValue(lengthBetweenPoints2, unitsMgr.defaultLengthUnits, True)
        return displayBeltLength2

    except:
        if ui:
            ui.messageBox('Get distance failed:\n{}'.format(traceback.format_exc()))

def getAngle1(point1, point2, point3, point4, Xposition, Yposition) -> float:
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        L1 = point1.distanceTo(point2)
        L2 = point3.distanceTo(point4)

        #Equations for inverse kinematics
        Hip = math.sqrt((Xposition * Xposition) + (Yposition * Yposition))

        Alpha = math.degrees(math.atan2(Xposition,Yposition))

        Beta = math.degrees(math.acos((( L1 * L1) - (L2 * L2) + (Hip * Hip))/(2 * L1 * Hip)))

        #First Angle to insert in first joint
        Angl1 = Alpha + Beta
        return Angl1

    except:
        if ui:
            ui.messageBox('Get distance failed:\n{}'.format(traceback.format_exc()))

def getAngle2(point1, point2, point3, point4, Xposition, Yposition) -> float:
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        L1 = point1.distanceTo(point2)
        L2 = point3.distanceTo(point4)

        #Equations for inverse kinematics
        Hip = math.sqrt((Xposition * Xposition) + (Yposition * Yposition))

        Alpha = math.degrees(math.atan2(Xposition,Yposition))

        Beta = math.degrees(math.acos((( L1 * L1) - (L2 * L2) + (Hip * Hip))/(2 * L1 * Hip)))

        #First Angle to insert in first joint
        Angl1 = Alpha + Beta

        Gamma = math.degrees(math.acos(((L1 * L1) + (L2 * L2) - (Hip * Hip))/ (2 * L1 * L2)))

        #Second Angle to insert in second joint
        AngL2 = Gamma - 180

        return AngL2

    except:
        if ui:
            ui.messageBox('Get distance failed:\n{}'.format(traceback.format_exc()))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Creating the button for the Belt Length Calculator
        # Get the command definitions collection
        commandDefinitions = ui.commandDefinitions

        
        # Add a button command definition to that collection
        NBELButtonDefinition = commandDefinitions.addButtonDefinition('NBELButton',
                                                                      'NBEL ROBOTICS',
                                                                      'This allows to determine the movement of a chain of joints to achieve that a final actuator is located in a specific position.',
                                                                      'resources')
        # Grabbing the correct toolbar panel to add the button to
        addinsToolbarPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        # Adding the belt button to the add-in toolbar panel
        NBELButtonControl = addinsToolbarPanel.controls.addCommand(NBELButtonDefinition, 'NBELButtonControl')
        # Making the button visible without having to use the dropdown
        NBELButtonControl.isPromotedByDefault = True
        NBELButtonControl.isPromoted = True

        # Setting up the handler if the belt button is pressed
        # Calling the class?
        NBELButtonPressed = NBELButtonPressedEventHandler()
        NBELButtonDefinition.commandCreated.add(NBELButtonPressed)
        handlers.append(NBELButtonPressed)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Deleting the belt button
        NBELButtonDefinition = ui.commandDefinitions.itemById('NBELButton')
        if NBELButtonDefinition:
            NBELButtonDefinition.deleteMe()
        addinsToolbarPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        NBELButtonControl = addinsToolbarPanel.controls.itemById('NBELButtonControl')
        if NBELButtonControl:
            NBELButtonControl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
