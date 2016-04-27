CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(computeShapeOALoads)

# Slicer
find_package(Slicer REQUIRED)

# VTK
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})

# Statismo
find_package(statismo REQUIRED)

# Slicer Execution Model
find_package(SlicerExecutionModel REQUIRED)
include(${SlicerExecutionModel_USE_FILE})
include(${GenerateCLP_USE_FILE})

# Link Statismo and VTK
#include_directories(${statismo_INCLUDE_DIRS})
#link_directories(${VTK_LIBRARY_DIRS} ${statismo_LIBRARY_DIRS})

#generateCLP(saveModel.cxx saveModel.xml)

set(INSTALL_RUNTIME_DEST ${SlicerExecutionModel_DEFAULT_CLI_INSTALL_RUNTIME_DESTINATION}/../hidden-cli-modules)

SEMMacroBuildCLI(
  NAME computeShapeOALoads
  EXECUTABLE_ONLY
  TARGET_LIBRARIES ${VTK_LIBRARIES} ${statismo_LIBRARIES} ${SlicerExecutionModel_LIBRARIES}
  INCLUDE_DIRECTORIES ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR}
  RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
  ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
  INSTALL_RUNTIME_DESTINATION ${INSTALL_RUNTIME_DEST}
  INSTALL_LIBRARY_DESTINATION lib
  INSTALL_ARCHIVE_DESTINATION lib
)