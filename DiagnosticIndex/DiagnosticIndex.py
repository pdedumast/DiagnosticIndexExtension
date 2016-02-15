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
        row = 0
        index = self.checkableComboBox_ChoiceOfGroup.currentIndex
        for cle, value in self.dictVTKFiles.items():
            if cle == index + 1:
                for vtkFile in value:
                    # check the checkBox
                    widget = self.tableWidget_VTKFile.cellWidget(row, 2)
                    tuple = widget.children()
                    checkBox = tuple[1]
                    checkBox.blockSignals(True)
                    item = self.checkableComboBox_ChoiceOfGroup.model().item(index,0)
                    if item.checkState():
                        checkBox.setChecked(True)
                    else:
                        checkBox.setChecked(False)
                    checkBox.blockSignals(False)
                    row = row + 1
            else:
                row = row + len(value)

    def onCheckBoxTableValueChanged(self):
        row = 0
        self.checkableComboBox_ChoiceOfGroup.blockSignals(True)
        allcheck = True
        for cle, value in self.dictVTKFiles.items():
            item = self.checkableComboBox_ChoiceOfGroup.model().item(cle - 1, 0)
            for vtkFile in value:
                # check the checkBox
                widget = self.tableWidget_VTKFile.cellWidget(row, 2)
                tuple = widget.children()
                checkBox = tuple[1]
                checkBox.blockSignals(True)
                if not checkBox.checkState():
                    item.setCheckState(0)
                    allcheck = False
                checkBox.blockSignals(False)
                row = row + 1
            if allcheck:
                item.setCheckState(2)
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
        # print "Number of VTK Files in CSV Files: " + str(len(dictVTKFiles))
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
        #  Export fields on different csv files
        file = open(filename, 'w')
        cw = csv.writer(file, delimiter=',')
        cw.writerow(['VTK Files'])
        row = 0
        for cle, value in dictVTKFiles.items():
            for vtkFile in value:
                # check the checkBox
                widget = table.cellWidget(row, 2)
                tuple = widget.children()
                checkBox = qt.QCheckBox()
                checkBox = tuple[1]
                if checkBox.isChecked():
                    cw.writerow([vtkFile])
                row = row + 1
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
                labelGroup = qt.QLabel(str(cle))
                labelGroup.setAlignment(0x84)
                table.setCellWidget(row, 1, labelGroup)

                # Column 2:
                widget = qt.QWidget()
                layout = qt.QHBoxLayout(widget)
                checkBox = qt.QCheckBox()
                layout.addWidget(checkBox)
                layout.setAlignment(0x84)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                table.setCellWidget(row, 2, widget)
                checkBox.connect('stateChanged(int)', lambda: self.interface.onCheckBoxTableValueChanged())
                row = row + 1

class DiagnosticIndexTest(ScriptedLoadableModuleTest):
    pass
