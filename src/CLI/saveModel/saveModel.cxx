#include "PCAModelBuilder.h"
#include "StatisticalModel.h"
#include "vtkPolyData.h"
#include <boost/scoped_ptr.hpp>
#include <iostream>
#include "vtkStandardMeshRepresenter.h"
#include "DataManager.h"
#include "vtkPolyDataReader.h"
#include "saveModelCLP.h"
#include <fstream>

using namespace statismo;
typedef vtkStandardMeshRepresenter RepresenterType;
typedef DataManager<vtkPolyData> DataManagerType;
typedef PCAModelBuilder<vtkPolyData> ModelBuilderType;
typedef StatisticalModel<vtkPolyData> StatisticalModelType;

vtkSmartPointer<vtkPolyData> loadVTKPolyData(const std::string& filename) {
    vtkSmartPointer<vtkPolyDataReader> reader = vtkSmartPointer<vtkPolyDataReader>::New();
    reader->SetFileName(filename.c_str());
    reader->Update();
    vtkSmartPointer<vtkPolyData> pd = vtkSmartPointer<vtkPolyData>::New();
    pd->ShallowCopy(reader->GetOutput());
    return pd;
}

int main(int argc, char ** argv)
{
    PARSE_ARGS;
    
    if(argc < 7)
    {
        std::cout << "Usage " << argv[0] << " [--groupnumber <int>] [--vtkfilelist <std::vector<std::string>>] [--resultdir <std::string>]" << std::endl;
        return 1;
    }
    
    vtkSmartPointer<vtkPolyData> reference = loadVTKPolyData(vtkfilelist[0]);
    boost::scoped_ptr<RepresenterType> representer(RepresenterType::Create(reference));
    boost::scoped_ptr<DataManagerType> dataManager(DataManagerType::Create(representer.get()));
    for(int j = 0; j < vtkfilelist.size(); j++)
    {
        dataManager->AddDataset(loadVTKPolyData(vtkfilelist[j]), vtkfilelist[j]);
    }
    boost::scoped_ptr<ModelBuilderType> modelBuilder(ModelBuilderType::Create());
    boost::scoped_ptr<StatisticalModelType> model(modelBuilder->BuildNewModel(dataManager->GetData(), 0.01));
    
    // Once we have built the model, we can save in the directory choosen by the user.
    std::string H5File = resultdir + "/G" + std::to_string(groupnumber) + ".h5";
    model->Save(H5File);
    std::cout << "Successfully saved shape model as " << "G" << groupnumber << ".h5" << std::endl;
    
    return 0;
}