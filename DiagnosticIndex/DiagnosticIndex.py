import os, sys
import csv
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from types import *


class DiagnosticIndex(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "DiagnosticIndex"
        parent.categories = ["Quantification"]
        parent.dependencies = []
        parent.contributors = ["Laura PASCAL (UofM)"]
        parent.helpText = """
            """
        parent.acknowledgementText = """
            This work was supported by the National
            Institutes of Dental and Craniofacial Research
            and Biomedical Imaging and Bioengineering of
            the National Institutes of Health under Award
            Number R01DE024450.
            """


class DiagnosticIndexWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # ---- Widget Setup ----

        # Global Variables
        self.logic = DiagnosticIndexLogic(self)
        self.dictVTKFiles = dict()
        self.dictGroups = dict()

        # Interface
        loader = qt.QUiLoader()
        moduleName = 'DiagnosticIndex'
        scriptedModulesPath = eval('slicer.modules.%s.path' % moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % moduleName)
        qfile = qt.QFile(path)
        qfile.open(qt.QFile.ReadOnly)

        widget = loader.load(qfile, self.parent)
        self.layout = self.parent.layout()
        self.widget = widget
        self.layout.addWidget(widget)

        #     global variables of the Interface:
        self.pathLineEdit_existingData = self.logic.get('PathLineEdit_existingData')
        self.pathLineEdit_NewGroups = self.logic.get('PathLineEdit_NewGroups')
        self.pathLineEdit_IncreaseExistingData = self.logic.get('PathLineEdit_IncreaseExistingData')
        self.collapsibleGroupBox_previewVTKFiles = self.logic.get('CollapsibleGroupBox_previewVTKFiles')
        self.checkableComboBox_ChoiceOfGroup = self.logic.get('CheckableComboBox_ChoiceOfGroup')
        self.tableWidget_VTKFile = self.logic.get('tableWidget_VTKFile')
        self.pushButton_previewVTKFiles = self.logic.get('pushButton_previewVTKFiles')
        self.pushButton_compute = self.logic.get('pushButton_compute')
        self.spinBox_healthyGroup = self.logic.get('spinBox_healthyGroup')
        self.pushButton_previewGroups = self.logic.get('pushButton_previewGroups')
        self.MRMLTreeView_classificationGroups = self.logic.get('MRMLTreeView_classificationGroups')

        # Widget Configuration

        #     disable/enable
        self.spinBox_healthyGroup.setDisabled(True)
        self.pushButton_previewGroups.setDisabled(True)
        self.pathLineEdit_IncreaseExistingData.setDisabled(True)
        self.pushButton_compute.setDisabled(True)
        self.collapsibleGroupBox_previewVTKFiles.setDisabled(True)
        self.pushButton_compute.setDisabled(True)

        #     tree view configuration
        headerTreeView = self.MRMLTreeView_classificationGroups.header()
        headerTreeView.setVisible(False)
        self.MRMLTreeView_classificationGroups.setMRMLScene(slicer.app.mrmlScene())
        self.MRMLTreeView_classificationGroups.sortFilterProxyModel().nodeTypes = ['vtkMRMLModelNode']
        self.MRMLTreeView_classificationGroups.setDisabled(True)
        sceneModel = self.MRMLTreeView_classificationGroups.sceneModel()
        # sceneModel.setHorizontalHeaderLabels(["Group Classification"])
        sceneModel.colorColumn = 1
        sceneModel.opacityColumn = 2
        headerTreeView.setStretchLastSection(False)
        headerTreeView.setResizeMode(sceneModel.nameColumn,qt.QHeaderView.Stretch)
        headerTreeView.setResizeMode(sceneModel.colorColumn,qt.QHeaderView.ResizeToContents)
        headerTreeView.setResizeMode(sceneModel.opacityColumn,qt.QHeaderView.ResizeToContents)

        #     table configuration
        self.tableWidget_VTKFile.setColumnCount(3)
        self.tableWidget_VTKFile.setHorizontalHeaderLabels([' VTK files ', ' Group ', ' Visualization '])
        self.tableWidget_VTKFile.setColumnWidth(0, 200)
        horizontalHeader = self.tableWidget_VTKFile.horizontalHeader()
        horizontalHeader.setStretchLastSection(False)
        horizontalHeader.setResizeMode(0,qt.QHeaderView.Stretch)
        horizontalHeader.setResizeMode(1,qt.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(2,qt.QHeaderView.ResizeToContents)
        self.tableWidget_VTKFile.verticalHeader().setVisible(False)

        # ------------------------------------------------------------------------------------
        #                                   CONNECTIONS
        # ------------------------------------------------------------------------------------
        self.pathLineEdit_existingData.connect('currentPathChanged(const QString)', self.onExistingData)
        self.pathLineEdit_NewGroups.connect('currentPathChanged(const QString)', self.onNewGroups)
        self.pathLineEdit_IncreaseExistingData.connect('currentPathChanged(const QString)', self.onIncreaseExistingData)
        self.checkableComboBox_ChoiceOfGroup.connect('checkedIndexesChanged()', self.onSelectedVTKFileForPreview)
        self.pushButton_previewVTKFiles.connect('clicked()', self.onPreviewVTKFiles)
        self.pushButton_compute.connect('clicked()', lambda: self.logic.onComputeNewClassification(self.dictVTKFiles, self.dictGroups))
        self.pushButton_previewGroups.connect('clicked()', self.onPreviewClassificationGroup)

        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.onCloseScene)

    # function called each time that the user "enter" in Diagnostic Index interface
    def enter(self):
        #TODO
        pass

    # function called each time that the user "exit" in Diagnostic Index interface
    def exit(self):
        #TODO
        pass

    # function called each time that the scene is closed (if Diagnostic Index has been initialized)
    def onCloseScene(self, obj, event):
        #TODO
        pass

    def onExistingData(self):
        print "------Existing Data PathLine------"

        # Read CSV File:
        self.logic.readCSVFile(self.pathLineEdit_existingData.currentPath)
        self.logic.creationDictVTKFiles(self.dictGroups)

        # check if there is one VTK Files for one group
        self.logic.checkCSVFile(self.dictGroups)

        # Enable/disable buttons
        self.enabledButtons()
        self.pathLineEdit_NewGroups.setDisabled(True)
        self.pathLineEdit_IncreaseExistingData.setEnabled(True)

    def onNewGroups(self):
        print "------New Groups PathLine------"
        # Download the CSV file
        self.logic.readCSVFile(self.pathLineEdit_NewGroups.currentPath)
        self.logic.creationDictVTKFiles(self.dictVTKFiles)

        # Update the option for the preview of the vtk files in Shape Population Viewer
        self.logic.updateOptionPreviewVTKFiles(self.dictVTKFiles, self.checkableComboBox_ChoiceOfGroup, self.tableWidget_VTKFile)

        # Enable/disable buttons
        self.enabledButtons()
        self.pathLineEdit_existingData.setDisabled(True)
        self.collapsibleGroupBox_previewVTKFiles.setEnabled(True)
        self.pushButton_compute.setEnabled(True)

    def enabledButtons(self):
        self.spinBox_healthyGroup.setEnabled(True)
        self.pushButton_previewGroups.setEnabled(True)
        self.MRMLTreeView_classificationGroups.setEnabled(True)

    def onIncreaseExistingData(self):
        print "------Increase Existing Data PathLine------"

        # Download the CSV file
        self.logic.readCSVFile(self.pathLineEdit_IncreaseExistingData.currentPath)

        if self.pathLineEdit_existingData.currentPath:
            self.dictVTKFiles = self.dictGroups
            self.dictGroups = dict()
            self.logic.creationDictVTKFiles(self.dictVTKFiles)
        else:
            # Error:
            slicer.util.errorDisplay('No Existing Data to increase')

        # Update the option for the preview of the vtk files in Shape Population Viewer
        self.logic.updateOptionPreviewVTKFiles(self.dictVTKFiles, self.checkableComboBox_ChoiceOfGroup, self.tableWidget_VTKFile)

        # Enable/disable buttons
        self.collapsibleGroupBox_previewVTKFiles.setEnabled(True)
        self.pushButton_compute.setEnabled(True)

    def onSelectedVTKFileForPreview(self):
        index = self.checkableComboBox_ChoiceOfGroup.currentIndex
        for row in range(0,self.tableWidget_VTKFile.rowCount):
             # group
            widget = self.tableWidget_VTKFile.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1
            if group == (index + 1):
                # check the checkBox
                widget = self.tableWidget_VTKFile.cellWidget(row, 2)
                tuple = widget.children()
                checkBox = tuple[1]
                checkBox.blockSignals(True)
                item = self.checkableComboBox_ChoiceOfGroup.model().item(index, 0)
                if item.checkState():
                    checkBox.setChecked(True)
                else:
                    checkBox.setChecked(False)
                checkBox.blockSignals(False)

    def onGroupValueChanged(self):
        # Uptade the dictionary where the VTK files are sorted by groups
        self.logic.onComboBoxTableValueChanged(self.dictVTKFiles, self.tableWidget_VTKFile)
        # Update the checkable combobox
        self.onCheckBoxTableValueChanged()

    def onCheckBoxTableValueChanged(self):
        self.checkableComboBox_ChoiceOfGroup.blockSignals(True)
        allcheck = True
        for cle, value in self.dictVTKFiles.items():
            item = self.checkableComboBox_ChoiceOfGroup.model().item(cle - 1, 0)
            if not value == []:
                for vtkFile in value:
                    filename = os.path.basename(vtkFile)
                    for row in range(0,self.tableWidget_VTKFile.rowCount):
                        qlabel = self.tableWidget_VTKFile.cellWidget(row, 0)
                        if qlabel.text == filename:
                            # check the checkBox
                            widget = self.tableWidget_VTKFile.cellWidget(row, 2)
                            tuple = widget.children()
                            checkBox = tuple[1]
                            if not checkBox.checkState():
                                allcheck = False
                                item.setCheckState(0)
                if allcheck:
                    item.setCheckState(2)
            else:
                item.setCheckState(0)
            allcheck = True
        self.checkableComboBox_ChoiceOfGroup.blockSignals(False)

    def onPreviewVTKFiles(self):
        print "------Preview VTK Files------"
        if self.pathLineEdit_NewGroups.currentPath or self.pathLineEdit_IncreaseExistingData.currentPath:
            filePathCSV = slicer.app.temporaryPath + '/' + 'VTKFilesPreview_OAIndex.csv'
            self.logic.creationCSVFile(filePathCSV, self.tableWidget_VTKFile, self.dictVTKFiles)
            parameters = {}
            parameters["CSVFile"] = filePathCSV
            launcherSPV = slicer.modules.launcher
            slicer.cli.run(launcherSPV, None, parameters)

    def onPreviewClassificationGroup(self):
        print "------Preview of the Classification Groups------"
        if self.spinBox_healthyGroup.value == 0:
            # ERROR:
            slicer.util.errorDisplay('Miss the number of the healthy group ')
        else:
            for i in self.dictGroups.keys():
                # print "Cle in dictionary: " + str(i)
                filename = self.dictGroups.get(i, None)
                # print "filename: " + filename
                loader = slicer.util.loadModel
                loader(filename[0])

            list = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
            end = list.GetNumberOfItems()
            # print "Number of Item: " + str(end)
            for i in range(3,end):
                model = list.GetItemAsObject(i)
                disp = model.GetDisplayNode()
                if self.spinBox_healthyGroup.value == (i - 2):
                    disp.SetColor(1, 1, 1)
                    disp.VisibilityOn()
                else:
                    disp.SetColor(1, 0, 0)
                    if i == 3:
                        disp.VisibilityOn()
                    else:
                        disp.VisibilityOff()
                disp.SetOpacity(0.8)
        # Center the 3D view of the scene
        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        threeDView.resetFocalPoint()

# ------------------------------------------------------------------------------------
#                                   ALGORITHM
# ------------------------------------------------------------------------------------


class DiagnosticIndexLogic(ScriptedLoadableModuleLogic):
    def __init__(self, interface):
        self.interface = interface
        self.table = vtk.vtkTable

    # === Convenience python widget methods === #
    def get(self, objectName):
        return self.findWidget(self.interface.widget, objectName)

    def findWidget(self, widget, objectName):
        if widget.objectName == objectName:
            return widget
        else:
            for w in widget.children():
                resulting_widget = self.findWidget(w, objectName)
                if resulting_widget:
                    return resulting_widget
            return None

    def readCSVFile(self, filename):
        print "CSV FilePath: " + filename
        CSVreader = vtk.vtkDelimitedTextReader()
        CSVreader.SetFieldDelimiterCharacters(",")
        CSVreader.SetFileName(filename)
        CSVreader.SetHaveHeaders(True)
        CSVreader.Update()

        self.table = CSVreader.GetOutput()

    def creationDictVTKFiles(self, dictVTKFiles):
        for i in range(0,self.table.GetNumberOfRows()):
            if not os.path.exists(self.table.GetValue(i,0).ToString()):
                slicer.util.errorDisplay('VTK file not found, path not good at lign ' + str(i+2))
                break
            value = dictVTKFiles.get(self.table.GetValue(i,1).ToInt(), None)
            if value == None:
                tempList = list()
                tempList.append(self.table.GetValue(i,0).ToString())
                dictVTKFiles[self.table.GetValue(i,1).ToInt()] = tempList
            else:
                value.append(self.table.GetValue(i,0).ToString())

        # Check
        # print "Number of Groups in CSV Files: " + str(len(dictVTKFiles))
        # for i in range(1, len(dictVTKFiles) + 1):
        #     value = dictVTKFiles.get(i, None)
        #     print "Groupe: " + str(i)
        #     print "VTK Files: " + str(value)


        # Set the Maximum value of spinBox_healthyGroup at the max groups possible
        self.interface.spinBox_healthyGroup.setMaximum(len(dictVTKFiles))

    def checkCSVFile(self, dictVTKFiles):
        for value in dictVTKFiles.values():
            if len(value) > 1:
                slicer.util.errorDisplay('There are more than one vtk file by groups')
                break

    def creationCSVFile(self, filename, table, dictVTKFiles):
        # Export fields on different csv files
        file = open(filename, 'w')
        cw = csv.writer(file, delimiter=',')
        cw.writerow(['VTK Files'])
        for row in range(0,table.rowCount):
            # check the checkBox
            widget = table.cellWidget(row, 2)
            tuple = widget.children()
            checkBox = qt.QCheckBox()
            checkBox = tuple[1]

            if checkBox.isChecked():
                # group
                widget = table.cellWidget(row, 1)
                tuple = widget.children()
                comboBox = qt.QComboBox()
                comboBox = tuple[1]
                group = comboBox.currentIndex + 1
                # filename of vtk file
                qlabel = table.cellWidget(row, 0)
                vtkFile = qlabel.text
                value = dictVTKFiles.get(group, None)
                if any(vtkFile in s for s in value):
                    pathList = [s for s in value if vtkFile in s]
                    pathVTKFile = pathList[0]
                    cw.writerow([pathVTKFile])
        file.close()

    def updateOptionPreviewVTKFiles(self, dictVTKFiles, checkableComboBox, table):
        row = 0
        for cle, value in dictVTKFiles.items():
            # Choice of group display in ShapePopulationViewer
            checkableComboBox.addItem("Group " + str(cle))
            # Table:
            for vtkFile in value:
                table.setRowCount(row + 1)
                # Column 0:
                filename = os.path.basename(vtkFile)
                labelVTKFile = qt.QLabel(filename)
                labelVTKFile.setAlignment(0x84)
                table.setCellWidget(row, 0, labelVTKFile)

                # Column 1:
                widget = qt.QWidget()
                layout = qt.QHBoxLayout(widget)
                comboBox = qt.QComboBox()
                comboBox.addItems(dictVTKFiles.keys())
                comboBox.setCurrentIndex(cle - 1)
                layout.addWidget(comboBox)
                layout.setAlignment(0x84)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                table.setCellWidget(row, 1, widget)
                comboBox.connect('currentIndexChanged(int)', self.interface.onGroupValueChanged)

                # Column 2:
                widget = qt.QWidget()
                layout = qt.QHBoxLayout(widget)
                checkBox = qt.QCheckBox()
                layout.addWidget(checkBox)
                layout.setAlignment(0x84)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                table.setCellWidget(row, 2, widget)
                checkBox.connect('stateChanged(int)', self.interface.onCheckBoxTableValueChanged)
                row = row + 1

    def onComboBoxTableValueChanged(self, dictVTKFiles, table):
        for row in range(0,table.rowCount):
            # group
            widget = table.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1
            # filename of vtk file
            qlabel = table.cellWidget(row, 0)
            vtkFile = qlabel.text
            # Find
            value = dictVTKFiles.get(group, None)
            if not any(vtkFile in s for s in value):
                for value in dictVTKFiles.values():
                    if any(vtkFile in s for s in value):
                        pathList = [s for s in value if vtkFile in s]
                        path = pathList[0]
                        value.remove(path)
                        newvalue = dictVTKFiles.get(group, None)
                        newvalue.append(path)
                        break

    def onComputeNewClassification(self, dictVTKFiles, dictGroups):
        for key, value in dictVTKFiles.items():
            # Delete all the array in vtk file
            self.deleteArray(key, value)

            if len(value) > 1:
                # Create the datalist to Statismo
                datalist = self.creationTXTFile(key, value)

                # Call Statismo
                self.computeMean(key, datalist)

                # Remove the files previously created in temporary directory
                self.removeDataInTemporaryDirectory(key, value)

            # Storage of the means for each group
            self.storageMean(dictGroups, key)

    def deleteArray(self, key, value):
        for vtkFile in value:
            # Read VTK File
            reader = vtk.vtkDataSetReader()
            reader.SetFileName(vtkFile)
            reader.ReadAllVectorsOn()
            reader.ReadAllScalarsOn()
            reader.Update()
            polyData = reader.GetOutput()
            polyDataCopy = vtk.vtkPolyData()
            polyDataCopy.DeepCopy(polyData)
            pointData = polyDataCopy.GetPointData()
            numAttributes = pointData.GetNumberOfArrays()
            for i in range(0, numAttributes):
                pointData.RemoveArray(0)
            # Save the vtk file without array in the temporary directory in Slicer
            writer = vtk.vtkPolyDataWriter()
            if len(value) > 1:
                filepath = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
            else:
                filepath = slicer.app.temporaryPath + '/meanGroup' + str(key) + '.vtk'
            writer.SetFileName(filepath)
            if vtk.VTK_MAJOR_VERSION <= 5:
                writer.SetInput(polyDataCopy)
            else:
                writer.SetInputData(polyDataCopy)
            writer.Update()
            writer.Write()

    def creationTXTFile(self, key, value):
        filename = "group" + str(key)
        dataListPath = slicer.app.temporaryPath + '/' + filename + '.txt'
        file = open(dataListPath, "w")
        for vtkFile in value:
            pathfile = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
            file.write(pathfile + "\n")
        file.close()
        return dataListPath

    def computeMean(self, key, datalist):
        print "----Compute the mean of each group:"
        # Call of Statismo (creation of hdf5 file)
        statismoBuildShapeModel = "/Users/lpascal/Applications/Statismo-static/statismo-build/Statismo-build/bin/statismo-build-shape-model"
        arguments = list()
        arguments.append("--data-list")
        arguments.append(datalist)
        arguments.append("--output-file")
        filename = "group" + str(key)
        outputFile = slicer.app.temporaryPath + '/' + filename + '.h5'
        arguments.append(outputFile)
        process = qt.QProcess()
        print "Calling " + os.path.basename(statismoBuildShapeModel) + " with this arguments: "
        print arguments
        process.start(statismoBuildShapeModel, arguments)
        process.waitForStarted()
        # print "state: " + str(process.state())
        process.waitForFinished()
        # print "error: " + str(process.error())

        # Read the hdf5 to have the mean of the group
        vtkBasicSamplingExample = "/Users/lpascal/Applications/Statismo-static/statismo-build/Statismo-build/bin/vtkBasicSamplingExample"
        arguments = list()
        modelname = outputFile
        arguments.append(modelname)
        resultdir = slicer.app.temporaryPath
        arguments.append(resultdir)
        process2 = qt.QProcess()
        print "Calling " + os.path.basename(vtkBasicSamplingExample) + " with this arguments:  "
        print arguments
        process2.start(vtkBasicSamplingExample, arguments)
        process2.waitForStarted()
        # print "state: " + str(process2.state())
        process2.waitForFinished()
        # print "error: " + str(process2.error())

        # Rename of the mean of the group
        oldname = slicer.app.temporaryPath + '/mean.vtk'
        newname = slicer.app.temporaryPath + '/meanGroup' + str(key) + '.vtk'
        os.rename(oldname, newname)

    def removeDataInTemporaryDirectory(self, key, value):
        # remove of 'groupX.txt'
        filename = "group" + str(key)
        dataListPath = slicer.app.temporaryPath + '/' + filename + '.txt'
        os.remove(dataListPath)

        # remove of 'groupX.h5'
        outputFilePath = slicer.app.temporaryPath + '/' + filename + '.h5'
        os.remove(outputFilePath)

        # remove of samplePC1.vtk and randomsample.vtk
        path = slicer.app.temporaryPath + '/samplePC1.vtk'
        os.remove(path)
        path = slicer.app.temporaryPath + '/randomsample.vtk'
        os.remove(path)

        # remove of all the vtk file
        for vtkFile in value:
            filepath = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
            os.remove(filepath)

    def storageMean(self, dictGroups, key):
        filename = "meanGroup" + str(key)
        meanPath = slicer.app.temporaryPath + '/' + filename + '.vtk'
        value = list()
        value.append(meanPath)
        dictGroups[key] = value

class DiagnosticIndexTest(ScriptedLoadableModuleTest):
    pass
