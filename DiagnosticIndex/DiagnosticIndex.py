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
        self.dictCSVFile = dict()
        self.directoryList = list()
        self.groupSelected = set()

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
        #          Tab: Creation of CSV File for Classification Groups
        self.collapsibleButton_creationCSVFile = self.logic.get('CollapsibleButton_creationCSVFile')
        self.spinBox_group = self.logic.get('spinBox_group')
        self.directoryButton_creationCSVFile = self.logic.get('DirectoryButton_creationCSVFile')
        self.stackedWidget_manageGroup = self.logic.get('stackedWidget_manageGroup')
        self.pushButton_addGroup = self.logic.get('pushButton_addGroup')
        self.pushButton_removeGroup = self.logic.get('pushButton_removeGroup')
        self.pushButton_modifyGroup = self.logic.get('pushButton_modifyGroup')
        self.directoryButton_exportCSVFile = self.logic.get('DirectoryButton_exportCSVFile')
        self.pushButton_exportCSVfile = self.logic.get('pushButton_exportCSVfile')
        #          Tab: Creation of New Classification Groups
        self.collapsibleButton_creationClassificationGroups = self.logic.get('CollapsibleButton_creationClassificationGroups')
        self.pathLineEdit_NewGroups = self.logic.get('PathLineEdit_NewGroups')
        self.pathLineEdit_IncreaseExistingData = self.logic.get('PathLineEdit_IncreaseExistingData')
        self.collapsibleGroupBox_previewVTKFiles = self.logic.get('CollapsibleGroupBox_previewVTKFiles')
        self.checkableComboBox_ChoiceOfGroup = self.logic.get('CheckableComboBox_ChoiceOfGroup')
        self.tableWidget_VTKFiles = self.logic.get('tableWidget_VTKFiles')
        self.pushButton_previewVTKFiles = self.logic.get('pushButton_previewVTKFiles')
        self.pushButton_compute = self.logic.get('pushButton_compute')
        self.directoryButton_exportNewClassification = self.logic.get('DirectoryButton_exportNewClassification')
        self.pushButton_exportNewClassification = self.logic.get('pushButton_exportNewClassification')
        #          Tab: Selection Classification Groups
        self.collapsibleButton_SelectClassificationGroups = self.logic.get('CollapsibleButton_SelectClassificationGroups')
        self.pathLineEdit_selectionClassificationGroups = self.logic.get('PathLineEdit_selectionClassificationGroups')
        self.spinBox_healthyGroup = self.logic.get('spinBox_healthyGroup')
        #          Tab: Preview of Classification Groups
        self.collapsibleButton_previewClassificationGroups = self.logic.get('CollapsibleButton_previewClassificationGroups')
        self.pushButton_previewGroups = self.logic.get('pushButton_previewGroups')
        self.MRMLTreeView_classificationGroups = self.logic.get('MRMLTreeView_classificationGroups')
        #          Tab: Select Input Data
        self.collapsibleButton_selectInputData = self.logic.get('CollapsibleButton_selectInputData')
        self.MRMLNodeComboBox_VTKFile = self.logic.get('MRMLNodeComboBox_VTKFile')
        self.checkBox_fileInGroups = self.logic.get('checkBox_fileInGroups')
        self.pushButton_applyTMJtype = self.logic.get('pushButton_applyTMJtype')
        #          Tab: Result / Analysis
        self.collapsibleButton_Result = self.logic.get('CollapsibleButton_Result')

        # Widget Configuration

        #     disable/enable and hide/show widget
        self.spinBox_healthyGroup.setDisabled(True)
        self.pushButton_previewGroups.setDisabled(True)
        self.pathLineEdit_IncreaseExistingData.setDisabled(True)
        self.pushButton_compute.setDisabled(True)
        self.pushButton_compute.setDisabled(True)
        self.directoryButton_exportNewClassification.setDisabled(True)
        self.pushButton_exportNewClassification.setDisabled(True)
        self.checkBox_fileInGroups.setDisabled(True)
        self.checkableComboBox_ChoiceOfGroup.setDisabled(True)
        self.tableWidget_VTKFiles.setDisabled(True)
        self.pushButton_previewVTKFiles.setDisabled(True)

        #     configuration of qMRMLNodeComboBox
        self.MRMLNodeComboBox_VTKFile.setMRMLScene(slicer.mrmlScene)

        #     initialisation of the stackedWidget to display the button "add group"
        self.stackedWidget_manageGroup.setCurrentIndex(0)

        #     spinbox configuration
        self.spinBox_group.setMinimum(1)
        self.spinBox_group.setMaximum(1)
        self.spinBox_group.setValue(1)

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
        self.tableWidget_VTKFiles.setColumnCount(4)
        self.tableWidget_VTKFiles.setHorizontalHeaderLabels([' VTK files ', ' Group ', ' Visualization ', 'Color'])
        self.tableWidget_VTKFiles.setColumnWidth(0, 200)
        horizontalHeader = self.tableWidget_VTKFiles.horizontalHeader()
        horizontalHeader.setStretchLastSection(False)
        horizontalHeader.setResizeMode(0,qt.QHeaderView.Stretch)
        horizontalHeader.setResizeMode(1,qt.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(2,qt.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(3,qt.QHeaderView.ResizeToContents)
        self.tableWidget_VTKFiles.verticalHeader().setVisible(False)

        # ------------------------------------------------------------------------------------
        #                                   CONNECTIONS
        # ------------------------------------------------------------------------------------
        #          Tab: Creation of CSV File for Classification Groups
        self.collapsibleButton_creationCSVFile.connect('clicked()', lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_creationCSVFile))
        self.spinBox_group.connect('valueChanged(int)', self.onManageGroup)
        self.pushButton_addGroup.connect('clicked()', self.onAddGroupForCreationCSVFile)
        self.pushButton_removeGroup.connect('clicked()', self.onRemoveGroupForCreationCSVFile)
        self.pushButton_modifyGroup.connect('clicked()', self.onModifyGroupForCreationCSVFile)
        self.pushButton_exportCSVfile.connect('clicked()', self.onExportForCreationCSVFile)
        #          Tab: Creation of New Classification Groups
        self.collapsibleButton_creationClassificationGroups.connect('clicked()', lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_creationClassificationGroups))
        self.pathLineEdit_NewGroups.connect('currentPathChanged(const QString)', self.onNewGroups)
        self.pathLineEdit_IncreaseExistingData.connect('currentPathChanged(const QString)', self.onIncreaseExistingData)
        self.checkableComboBox_ChoiceOfGroup.connect('checkedIndexesChanged()', self.onSelectedVTKFileForPreview)
        self.pushButton_previewVTKFiles.connect('clicked()', self.onPreviewVTKFiles)
        self.pushButton_compute.connect('clicked()', self.onComputeNewClassification)
        self.pushButton_exportNewClassification.connect('clicked()', self.onExportNewClassificationGroups)
        #          Tab: Selection of Classification Groups
        self.collapsibleButton_SelectClassificationGroups.connect('clicked()', lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_SelectClassificationGroups))
        self.pathLineEdit_selectionClassificationGroups.connect('currentPathChanged(const QString)', self.onSelectionClassificationGroups)
        #          Tab: Preview of Classification Groups
        self.collapsibleButton_previewClassificationGroups.connect('clicked()', lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_previewClassificationGroups))
        self.pushButton_previewGroups.connect('clicked()', self.onPreviewClassificationGroup)
        #          Tab: Select Input Data
        self.collapsibleButton_selectInputData.connect('clicked()', lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_selectInputData))
        self.MRMLNodeComboBox_VTKFile.connect('currentNodeChanged(vtkMRMLNode*)', self.onEnableOption)
        self.checkBox_fileInGroups.connect('clicked()', self.onCheckFileInGroups)
        self.pushButton_applyTMJtype.connect('clicked()', self.onComputeTMJtype)
        #          Tab: Result / Analysis
        self.collapsibleButton_Result.connect('clicked()', lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_Result))

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

    # Only one tab can be display at the same time:
    #   When one tab is opened all the other tabs are closed
    def onSelectedCollapsibleButtonOpen(self, selectedCollapsibleButton):
        if selectedCollapsibleButton.isChecked():
            collapsibleButtonList = [self.collapsibleButton_creationCSVFile, self.collapsibleButton_creationClassificationGroups, self.collapsibleButton_SelectClassificationGroups, self.collapsibleButton_previewClassificationGroups, self.collapsibleButton_selectInputData ,self.collapsibleButton_Result]
            for collapsibleButton in collapsibleButtonList:
                collapsibleButton.setChecked(False)
            selectedCollapsibleButton.setChecked(True)

    # ---------------------------------------------------- #
    # Tab: Creation of CSV File for Classification Groups
    # ---------------------------------------------------- #

    def onManageGroup(self):
        if self.spinBox_group.maximum == self.spinBox_group.value:
            self.stackedWidget_manageGroup.setCurrentIndex(0)
        else:
            self.stackedWidget_manageGroup.setCurrentIndex(1)
            if (self.spinBox_group.maximum - 1) == self.spinBox_group.value:
                self.pushButton_removeGroup.show()
            else:
                self.pushButton_removeGroup.hide()
            # Update the path of the directory button
            if len(self.directoryList) > 0:
                self.directoryButton_creationCSVFile.directory = self.directoryList[self.spinBox_group.value - 1]

    def onAddGroupForCreationCSVFile(self):
        # Error message
        directory = self.directoryButton_creationCSVFile.directory.encode('utf-8')
        if directory in self.directoryList:
            index = self.directoryList.index(directory) + 1
            slicer.util.errorDisplay('Path of directory already used for the group ' + str(index))
            return

        # Add the paths of vtk files to the dictionary
        self.logic.addGroupToDictionary(self.dictCSVFile, directory, self.directoryList, self.spinBox_group.value)

        # Increment of the number of the group in the spinbox
        self.spinBox_group.blockSignals(True)
        self.spinBox_group.setMaximum(self.spinBox_group.value + 1)
        self.spinBox_group.setValue(self.spinBox_group.value + 1)
        self.spinBox_group.blockSignals(False)

        # Message for the user
        slicer.util.delayDisplay("Group Added")

    def onRemoveGroupForCreationCSVFile(self):
        # Remove the paths of vtk files to the dictionary
        self.logic.removeGroupToDictionary(self.dictCSVFile, self.directoryList, self.spinBox_group.value)

        # Decrement of the maximum of the spinbox
        self.spinBox_group.blockSignals(True)
        self.spinBox_group.setMaximum(self.spinBox_group.maximum - 1)
        self.spinBox_group.blockSignals(False)

        # Change the buttons "remove group" and "modify group" in "add group"
        self.stackedWidget_manageGroup.setCurrentIndex(0)

        # Message for the user
        slicer.util.delayDisplay("Group removed")

    def onModifyGroupForCreationCSVFile(self):
        # Error message
        directory = self.directoryButton_creationCSVFile.directory.encode('utf-8')
        if directory in self.directoryList:
            index = self.directoryList.index(directory) + 1
            slicer.util.errorDisplay('Path of directory already used for the group ' + str(index))
            return

        # Remove the paths of vtk files to the dictionary
        self.logic.removeGroupToDictionary(self.dictCSVFile, self.directoryList, self.spinBox_group.value)

        # Add the paths of vtk files to the dictionary
        self.logic.addGroupToDictionary(self.dictCSVFile, directory, self.directoryList, self.spinBox_group.value)

        # Message for the user
        slicer.util.delayDisplay("Group modified")

    def onExportForCreationCSVFile(self):
        # Path of the csv file
        directory = self.directoryButton_exportCSVFile.directory.encode('utf-8')
        filepath = directory + '/VTKFilesToCreateClassificationGroups.csv'

        # Message if the csv fil already exists
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        if os.path.exists(filepath):
            messageBox.setText('File ' + filepath + ' already exists!')
            messageBox.setInformativeText('Do you want to replace it ?')
            messageBox.setStandardButtons( messageBox.No | messageBox.Yes)
            choice = messageBox.exec_()
            if choice == messageBox.No:
                return

        # Creation of the CSV File
        self.logic.creationCSVFileForClassificationGroups(filepath, self.dictCSVFile)

        # Inisalization of the first tab
        self.spinBox_group.setMaximum(1)
        self.spinBox_group.setValue(1)
        self.stackedWidget_manageGroup.setCurrentIndex(0)
        self.directoryButton_creationCSVFile.directory = qt.QDir.homePath() + '/Desktop'
        self.directoryButton_exportCSVFile.directory = qt.QDir.homePath() + '/Desktop'

        # Initialization of:
        #     - the dictionary containing all the paths of the vtk groups
        #     - the list containing all the paths of the different directories
        self.directoryList = list()
        self.dictCSVFile = dict()

        # Load automatically the CSV file in the pathline in the tab "Creation of New Classification Groups"
        self.pathLineEdit_NewGroups.setCurrentPath(filepath)

    # ---------------------------------------------------- #
    #     Tab: Creation of New Classification Groups
    # ---------------------------------------------------- #

    def onNewGroups(self):
        print "------New Groups PathLine------"
        # Re-initialization of the dictionary containing all the vtk files which will be used to create a new Classification Groups
        self.dictVTKFiles = dict()

        # Check if the path exists:
        if not os.path.exists(self.pathLineEdit_NewGroups.currentPath):
            return

        # Download the CSV file
        self.logic.readCSVFile(self.pathLineEdit_NewGroups.currentPath)
        condition = self.logic.creationDictVTKFiles(self.dictVTKFiles)

        # If the file is not conformed:
        # Re-initialization of the dictionary containing all the data which will be used to create a new Classification Groups
        if not condition:
            self.dictVTKFiles = dict()
            self.pathLineEdit_NewGroups.setCurrentPath(" ")
            return

        # Update the option for the preview of the vtk files in Shape Population Viewer
        self.logic.updateOptionPreviewVTKFiles(self.dictVTKFiles, self.checkableComboBox_ChoiceOfGroup, self.tableWidget_VTKFiles)

        # Enable/disable buttons
        self.checkableComboBox_ChoiceOfGroup.setEnabled(True)
        self.tableWidget_VTKFiles.setEnabled(True)
        self.pushButton_previewVTKFiles.setEnabled(True)
        self.pushButton_compute.setEnabled(True)

    def onIncreaseExistingData(self):
        print "------Increase Existing Data PathLine------"
        # Check if the path exists:
        if not os.path.exists(self.pathLineEdit_IncreaseExistingData.currentPath):
            return

        # Download the CSV file
        self.logic.readCSVFile(self.pathLineEdit_IncreaseExistingData.currentPath)

        if os.path.exists(self.pathLineEdit_selectionClassificationGroups.currentPath):
            self.dictVTKFiles = self.dictGroups
            self.dictGroups = dict()
            condition = self.logic.creationDictVTKFiles(self.dictVTKFiles)
            # If the file is not conformed:
            # Re-initialization of the dictionary containing all the data which will be used to create a new Classification Groups
            if not condition:
                self.dictVTKFiles = dict()
                self.pathLineEdit_IncreaseExistingData.setCurrentPath(" ")
                return
        else:
            # Error:
            slicer.util.errorDisplay('No Existing Data to increase')

        # Update the option for the preview of the vtk files in Shape Population Viewer
        self.logic.updateOptionPreviewVTKFiles(self.dictVTKFiles, self.checkableComboBox_ChoiceOfGroup, self.tableWidget_VTKFiles)

        # Enable/disable buttons
        self.checkableComboBox_ChoiceOfGroup.setEnabled(True)
        self.tableWidget_VTKFiles.setEnabled(True)
        self.pushButton_previewVTKFiles.setEnabled(True)
        self.pushButton_compute.setEnabled(True)

    def onSelectedVTKFileForPreview(self):
        # Update the checkbox in the qtableWidget of each vtk file
        index = self.checkableComboBox_ChoiceOfGroup.currentIndex
        for row in range(0,self.tableWidget_VTKFiles.rowCount):
             # group
            widget = self.tableWidget_VTKFiles.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1
            if group == (index + 1):
                # check the checkBox
                widget = self.tableWidget_VTKFiles.cellWidget(row, 2)
                tuple = widget.children()
                checkBox = tuple[1]
                checkBox.blockSignals(True)
                item = self.checkableComboBox_ChoiceOfGroup.model().item(index, 0)
                if item.checkState():
                    checkBox.setChecked(True)
                    self.groupSelected.add(index + 1)
                else:
                    checkBox.setChecked(False)
                    self.groupSelected.discard(index + 1)
                checkBox.blockSignals(False)

        # Update the checkbox in the qtableWidget of each vtk file
        colorTransferFunction = self.logic.creationColorTransfer(self.groupSelected)
        self.updateColorForSPV(colorTransferFunction)

    def onGroupValueChanged(self):
        # Uptade the dictionary where the VTK files are sorted by groups
        self.logic.onComboBoxTableValueChanged(self.dictVTKFiles, self.tableWidget_VTKFiles)
        # Update the checkable combobox
        self.onCheckBoxTableValueChanged()

    def onCheckBoxTableValueChanged(self):
        self.groupSelected = set()
        # Update the checkable comboBox which allow to select what groups the user wants to display in SPV
        self.checkableComboBox_ChoiceOfGroup.blockSignals(True)
        allcheck = True
        for cle, value in self.dictVTKFiles.items():
            item = self.checkableComboBox_ChoiceOfGroup.model().item(cle - 1, 0)
            if not value == []:
                for vtkFile in value:
                    filename = os.path.basename(vtkFile)
                    for row in range(0,self.tableWidget_VTKFiles.rowCount):
                        qlabel = self.tableWidget_VTKFiles.cellWidget(row, 0)
                        if qlabel.text == filename:
                            # check the checkBox in the table
                            widget = self.tableWidget_VTKFiles.cellWidget(row, 2)
                            tuple = widget.children()
                            checkBox = tuple[1]
                            if not checkBox.checkState():
                                allcheck = False
                                item.setCheckState(0)
                            else:
                                self.groupSelected.add(cle)
                if allcheck:
                    item.setCheckState(2)
            else:
                item.setCheckState(0)
            allcheck = True
        self.checkableComboBox_ChoiceOfGroup.blockSignals(False)

        # Update the color in the qtableWidget which will display in SPV
        colorTransferFunction = self.logic.creationColorTransfer(self.groupSelected)
        self.updateColorForSPV(colorTransferFunction)

    def updateColorForSPV(self, colorTransferFunction):
        # Update the color in the table associating at each groups
        for row in range(0,self.tableWidget_VTKFiles.rowCount):
            # group
            widget = self.tableWidget_VTKFiles.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1

            # checkbox
            widget = self.tableWidget_VTKFiles.cellWidget(row, 2)
            tuple = widget.children()
            checkBox = qt.QCheckBox()
            checkBox = tuple[1]

            if checkBox.isChecked():
                # color
                rgb = colorTransferFunction.GetColor(group)
                widget = self.tableWidget_VTKFiles.cellWidget(row, 3)
                self.tableWidget_VTKFiles.item(row,3).setBackground(qt.QColor(rgb[0]*255,rgb[1]*255,rgb[2]*255))
            else:
                self.tableWidget_VTKFiles.item(row,3).setBackground(qt.QColor(255,255,255))

    def onPreviewVTKFiles(self):
        print "------Preview VTK Files------"
        if os.path.exists(self.pathLineEdit_NewGroups.currentPath) or os.path.exists(self.pathLineEdit_IncreaseExistingData.currentPath):
            # Creation of a color map to visualize each group with a different color in ShapePopulationViewer
            self.logic.addColorMap(self.tableWidget_VTKFiles, self.dictVTKFiles)

            # Creation of a CSV file to download the vtk files in ShapePopulationViewer
            filePathCSV = slicer.app.temporaryPath + '/' + 'VTKFilesPreview_OAIndex.csv'
            self.logic.creationCSVFileForSPV(filePathCSV, self.tableWidget_VTKFiles, self.dictVTKFiles)
            parameters = {}
            parameters["CSVFile"] = filePathCSV
            launcherSPV = slicer.modules.launcher
            slicer.cli.run(launcherSPV, None, parameters, wait_for_completion=True)

            # Remove the vtk files previously created in the temporary directory of Slicer
            for key, value in self.dictVTKFiles.items():
                self.logic.removeDataInTemporaryDirectory(key, value)

    def onComputeNewClassification(self):
        for key, value in self.dictVTKFiles.items():
            # Delete all the array in vtk file
            self.logic.deleteArray(key, value)

            if len(value) > 1:
                # Create the datalist to Statismo
                datalist = self.logic.creationTXTFile(key, value)

                # Call Statismo
                self.logic.computeMean(key, datalist)

                # Remove the files previously created in temporary directory
                self.logic.removeDataInTemporaryDirectory(key, value)

            # Storage of the means for each group
            self.logic.storageMean(self.dictGroups, key)

        self.directoryButton_exportNewClassification.setEnabled(True)
        self.pushButton_exportNewClassification.setEnabled(True)

    def onExportNewClassificationGroups(self):
        print "-----Export Mean Group"

        # Message if files already exist
        directory = self.directoryButton_exportNewClassification.directory.encode('utf-8')
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        filePathExisting = list()

        CSVfilePath = directory + "/NewClassificationGroups.csv"
        if os.path.exists(CSVfilePath):
            filePathExisting.append(CSVfilePath)
        for key, value in self.dictGroups.items():
            VTKFilename = os.path.basename(value[0])
            VTKFilePath = directory + '/' + VTKFilename
            if os.path.exists(VTKFilePath):
                filePathExisting.append(VTKFilePath)
        if len(filePathExisting) > 0:
            if len(filePathExisting) == 1:
                text = 'File ' + filePathExisting[0] + ' already exists!'
                informativeText = 'Do you want to replace it ?'
            elif len(filePathExisting) > 1:
                text = 'These files are already exist: \n'
                for path in filePathExisting:
                    text = text + path + '\n'
                    informativeText = 'Do you want to replace them ?'
            messageBox.setText(text)
            messageBox.setInformativeText(informativeText)
            messageBox.setStandardButtons( messageBox.No | messageBox.Yes)
            choice = messageBox.exec_()
            if choice == messageBox.No:
                return

        # Save the CSV File and the means of each group
        self.logic.saveNewClassificationGroups(CSVfilePath, directory, self.dictGroups)
        self.dictGroups = dict()

        # Message for the user
        slicer.util.delayDisplay("Files Saved")

        # Load automatically the CSV file in the pathline in the tab "Selection of Classification Groups"
        self.pathLineEdit_selectionClassificationGroups.setCurrentPath(CSVfilePath)

    # ---------------------------------------------------- #
    #        Tab: Selection of Classification Groups
    # ---------------------------------------------------- #

    def onSelectionClassificationGroups(self):
        print "------Selection Classification Groups PathLine------"
        # Re-initialization of the dictionary containing the Classification Groups
        self.dictGroups = dict()

        # Check if the path exists:
        if not os.path.exists(self.pathLineEdit_selectionClassificationGroups.currentPath):
            return

        # Read CSV File:
        self.logic.readCSVFile(self.pathLineEdit_selectionClassificationGroups.currentPath)
        condition1 = self.logic.creationDictVTKFiles(self.dictGroups)

        # Check if there is one VTK Files for one group
        condition2 = self.logic.checkCSVFile(self.dictGroups)
        #    If the file is not conformed:
        #    Re-initialization of the dictionary containing the Classification Groups
        if not (condition1 and condition2):
            self.dictGroups = dict()
            self.pathLineEdit_selectionClassificationGroups.setCurrentPath(" ")
            return

        # Enable/disable buttons
        self.spinBox_healthyGroup.setEnabled(True)
        self.pushButton_previewGroups.setEnabled(True)
        self.MRMLTreeView_classificationGroups.setEnabled(True)

    # ---------------------------------------------------- #
    #     Tab: Preview of Classification Groups
    # ---------------------------------------------------- #

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
                for group in self.dictGroups.keys():
                    filename = self.dictGroups.get(group, None)
                    if os.path.splitext(os.path.basename(filename[0]))[0] == model.GetName():
                        if self.spinBox_healthyGroup.value == group:
                            disp.SetColor(1, 1, 1)
                            disp.VisibilityOn()
                        else:
                            disp.SetColor(1, 0, 0)
                            disp.VisibilityOff()
                        disp.SetOpacity(0.8)
                        break
                    disp.VisibilityOff()
        # Center the 3D view of the scene
        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        threeDView.resetFocalPoint()

    # ---------------------------------------------------- #
    #               Tab: Select Input Data
    # ---------------------------------------------------- #

    def onEnableOption(self):
        currentNode = self.MRMLNodeComboBox_VTKFile.currentNode()
        if currentNode == None:
            self.checkBox_fileInGroups.setDisabled(True)
        elif os.path.exists(self.pathLineEdit_NewGroups.currentPath) or os.path.exists(self.pathLineEdit_IncreaseExistingData.currentPath):
            self.checkBox_fileInGroups.setEnabled(True)

        # Check if the selected file is in the groups used to create the classification groups
        self.onCheckFileInGroups()

    def onCheckFileInGroups(self):
        # Check if the selected file is in the groups used to create the classification groups
        if self.checkBox_fileInGroups.isChecked():
            node = self.MRMLNodeComboBox_VTKFile.currentNode()
            if not node == None:
                vtkfileToFind = node.GetName() + '.vtk'
                find = self.logic.actionOnDictionary(self.dictVTKFiles, vtkfileToFind, None, 'find')
                if find == False:
                    slicer.util.errorDisplay('The selected file is not a file used to create the Classification Groups!')
                    self.checkBox_fileInGroups.setChecked(False)

    def onComputeTMJtype(self):
        print "------Compute the TMJ Type of a patient------"
        # Check if the user gave the data used to compute the TMJ type of the patient:
        # - VTK input data
        # - CSV file containing the Classification Groups
        if not os.path.exists(self.pathLineEdit_selectionClassificationGroups.currentPath):
            slicer.util.errorDisplay('Miss the CSV file containing the Classification Groups')
            return
        if self.MRMLNodeComboBox_VTKFile.currentNode() == None:
            slicer.util.errorDisplay('Miss the VTK Input Data')
            return

        # If the selected file is in the groups used to create the classification groups
        if self.checkBox_fileInGroups.isChecked():
            #      Remove the file in the dictionary used to compute the classification groups
            listSaveVTKFiles = list()
            vtkfileToRemove = self.MRMLNodeComboBox_VTKFile.currentNode().GetName() + '.vtk'
            listSaveVTKFiles = self.logic.actionOnDictionary(self.dictVTKFiles, vtkfileToRemove, listSaveVTKFiles, 'remove')

            #      Copy the Classification Groups
            dictGroupsTemp = dict()
            dictGroupsTemp = self.dictGroups
            self.dictGroups = dict()

            #      Re-compute the new classification
            self.onComputeNewClassification()

        # Define the TMJ type of a patient
        # TODO: call the CLI to define the TMJ type of a patient

        # If the selected file is in the groups used to create the classification groups
        if self.checkBox_fileInGroups.isChecked():
            #      Add the file previously removed to the dictionary used to create the classification groups
            self.logic.actionOnDictionary(self.dictVTKFiles, vtkfileToRemove, listSaveVTKFiles, 'add')
            #      Recovery the Classification Groups previously saved
            self.dictGroups = dictGroupsTemp

# ------------------------------------------------------------------------------------
#                                   ALGORITHM
# ------------------------------------------------------------------------------------


class DiagnosticIndexLogic(ScriptedLoadableModuleLogic):
    def __init__(self, interface):
        self.interface = interface
        self.table = vtk.vtkTable
        self.colorBar = {'Point1': [0, 0, 1, 0], 'Point2': [0.5, 1, 1, 0], 'Point3': [1, 1, 0, 0]}

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

    def addGroupToDictionary(self, dictCSVFile, directory, directoryList, group):
        # Fill a dictionary which contains the vtk files for the classification groups sorted by group
        valueList = list()
        for file in os.listdir(directory):
            if file.endswith(".vtk"):
                filepath = directory + '/' + file
                valueList.append(filepath)
        dictCSVFile[group] = valueList

        # Add the path of the directory
        directoryList.insert((group - 1), directory)

    def removeGroupToDictionary(self, dictCSVFile, directoryList, group):
        # Remove the group from the dictionary
        dictCSVFile.pop(group, None)

        # Remove the path of the directory
        directoryList.pop(group - 1)


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
                return False
            value = dictVTKFiles.get(self.table.GetValue(i,1).ToInt(), None)
            if value == None:
                tempList = list()
                tempList.append(self.table.GetValue(i,0).ToString())
                dictVTKFiles[self.table.GetValue(i,1).ToInt()] = tempList
            else:
                value.append(self.table.GetValue(i,0).ToString())
        return True

        # Check
        # print "Number of Groups in CSV Files: " + str(len(dictVTKFiles))
        # for i in range(1, len(dictVTKFiles) + 1):
        #     value = dictVTKFiles.get(i, None)
        #     print "Groupe: " + str(i)
        #     print "VTK Files: " + str(value)

        # Set the Maximum value of spinBox_healthyGroup at the max groups possible
        self.interface.spinBox_healthyGroup.setMaximum(len(dictVTKFiles))

    def checkCSVFile(self, dict):
        for value in dict.values():
            if len(value) > 1:
                slicer.util.errorDisplay('There are more than one vtk file by groups')
                return False
        return True

    def addColorMap(self, table, dictVTKFiles):
        for key, value in dictVTKFiles.items():
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

                # New Array
                numPts = polyDataCopy.GetPoints().GetNumberOfPoints()
                arrayName = "DisplayClassificationGroup"
                hasArrayInt = pointData.HasArray(arrayName)
                if hasArrayInt == 1:
                    pointData.RemoveArray(arrayName)
                arrayToAdd = vtk.vtkDoubleArray()
                arrayToAdd.SetName(arrayName)
                arrayToAdd.SetNumberOfComponents(1)
                arrayToAdd.SetNumberOfTuples(numPts)
                for i in range(0, numPts):
                    arrayToAdd.InsertTuple1(i, key)
                pointData.AddArray(arrayToAdd)

                # Save in the temporary directory in Slicer the vtk file with a new array
                # for the visualization in Shape Population Viewer
                writer = vtk.vtkPolyDataWriter()
                filepath = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
                writer.SetFileName(filepath)
                if vtk.VTK_MAJOR_VERSION <= 5:
                    writer.SetInput(polyDataCopy)
                else:
                    writer.SetInputData(polyDataCopy)
                writer.Update()
                writer.Write()

    def creationCSVFileForSPV(self, filename, table, dictVTKFiles):
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
                pathVTKFile = slicer.app.temporaryPath + '/' + vtkFile
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

                # Column 3:
                table.setItem(row, 3, qt.QTableWidgetItem())
                table.item(row,3).setBackground(qt.QColor(255,255,255))

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

    def creationColorTransfer(self, groupSelected):
        # Creation of the color transfer function with the updated range
        colorTransferFunction = vtk.vtkColorTransferFunction()
        if len(groupSelected) > 0:
            groupSelectedList = list(groupSelected)
            rangeColorTransfer = [groupSelectedList[0], groupSelectedList[len(groupSelectedList) - 1]]
            colorTransferFunction.AdjustRange(rangeColorTransfer)
            for key, value in self.colorBar.items():
                # postion on the current arrow
                x = (groupSelectedList[len(groupSelectedList) - 1] - groupSelectedList[0]) * value[0] + groupSelectedList[0]
                # color of the current arrow
                r = value[1]
                g = value[2]
                b = value[3]
                colorTransferFunction.AddRGBPoint(x,r,g,b)
        return colorTransferFunction

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
            if len(value) > 1:
                filename = os.path.basename(vtkFile)
            else:
                filename = 'meanGroup' + str(key) + '.vtk'
            filepath = slicer.app.temporaryPath + '/' + filename
            self.saveVTKFile(polyDataCopy, filepath)

    def saveVTKFile(self, polydata, filepath):
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(filepath)
        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(polydata)
        else:
            writer.SetInputData(polydata)
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
        if os.path.exists(dataListPath):
            os.remove(dataListPath)

        # remove of 'groupX.h5'
        outputFilePath = slicer.app.temporaryPath + '/' + filename + '.h5'
        if os.path.exists(outputFilePath):
            os.remove(outputFilePath)

        # remove of samplePC1.vtk and randomsample.vtk
        path = slicer.app.temporaryPath + '/samplePC1.vtk'
        if os.path.exists(path):
            os.remove(path)
        path = slicer.app.temporaryPath + '/randomsample.vtk'
        if os.path.exists(path):
            os.remove(path)

        # remove of all the vtk file
        for vtkFile in value:
            filepath = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
            if os.path.exists(filepath):
                os.remove(filepath)

    def storageMean(self, dictGroups, key):
        filename = "meanGroup" + str(key)
        meanPath = slicer.app.temporaryPath + '/' + filename + '.vtk'
        value = list()
        value.append(meanPath)
        dictGroups[key] = value

    def creationCSVFileForClassificationGroups(self, filePath, dictForCSV):
        print "creationCSVFileForClassificationGroups"
        file = open(filePath, 'w')
        cw = csv.writer(file, delimiter=',')
        cw.writerow(['VTK Files', 'Group'])
        for key, value in dictForCSV.items():
            for VTKPath in value:
                cw.writerow([VTKPath, str(key)])
        file.close()

    def saveNewClassificationGroups(self, CSVfilePath, directory, dictGroups):
        dictForCSV = dict()
        for key, value in dictGroups.items():
            if os.path.exists(value[0]):
                # Read VTK File
                reader = vtk.vtkDataSetReader()
                reader.SetFileName(value[0])
                reader.ReadAllVectorsOn()
                reader.ReadAllScalarsOn()
                reader.Update()
                polyData = reader.GetOutput()
                VTKFilename = os.path.basename(value[0])
                VTKFilePath = directory + '/' + VTKFilename
                self.saveVTKFile(polyData, VTKFilePath)
                valueList = list()
                valueList.append(VTKFilePath)
                dictForCSV[key] = valueList
        self.creationCSVFileForClassificationGroups(CSVfilePath, dictForCSV)

    def actionOnDictionary(self, dict, file, listSaveVTKFiles, action):
        # Remove vtkfile to the dictionary dict and return the key if it was found or None if it's not
        if action == 'remove' or action == 'find':
            if not file == None:
                for key, value in dict.items():
                    for vtkFile in value:
                        filename = os.path.basename(vtkFile)
                        if filename == file:
                            if action == 'remove':
                                value.remove(vtkFile)
                                listSaveVTKFiles.append(key)
                                listSaveVTKFiles.append(vtkFile)
                                return listSaveVTKFiles
                            return True
            return False

        # Add vtkfile to the dictionary dict at the given key
        if action == 'add':
            if not listSaveVTKFiles == None and not file == None:
                value = dict.get(listSaveVTKFiles[0], None)
                value.append(listSaveVTKFiles[1])


class DiagnosticIndexTest(ScriptedLoadableModuleTest):
    pass
