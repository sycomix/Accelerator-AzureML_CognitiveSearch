# Build the Knowledge Mining enrichment pipeline

Now that the label skill has been deployed, we will create an [enrichment pipeline in Cognitive Search](https://docs.microsoft.com/en-us/azure/search/cognitive-search-concept-intro) to call the skill and generate the training dataset. You'll create the enrichment pipeline using the [CogSearchInitializer](CogSearchInitializer.ipynb) Jupyter Notebook, but first you'll need to upload your data to Azure Blob Storage.

## Create a dataset

Find a dataset you want to work with. For this example, we use the [azure-docs](https://github.com/MicrosoftDocs/azure-docs)  Github repo. A portion of the files from azure-docs repo is included with this repo in the [SampleData](../SampleData/) folder. 
If you plan to use the sample data provided with this solution, do the following
1. [SampleData](../SampleData/) folder has a zip file. Extract the files from the zip file into the folder.
2. Create a blob storage container "labelgendata" in the storage account created during the resource deployment.
3. Upload the files from SampleData folder into labelgendata container. 


## Create the enrichment pipeline

Run the [02_Initialize_Cognitive_Search.ipynb](02_Initialize_Cognitive_Search.ipynb) notebook to:

1. Create a datasource pointing to the dataset you just uploaded
2. Create a skillset that uses the label skill we created in the previous step
3. Define the knowledge store projections to export your data
4. Define the index we will populate with the enriched data
5. Define and run the indexer

To successfully run the notebook, you will need to set the following variables at the top of the notebook:

1. `search_service_name` set to the name of your Cognitive Search service
2. `api_key` set to the api key for the search service
3. `cog_svcs_key` set to the cognitive services resource that was deployed. You will not be billed for any cognitive services, but the key is required
4. `STORAGEACCOUNTNAME` set to the storage account name that contains the dataset
5. `STORAGEACCOUNTKEY` set to the storage account key
6. `datasource_container` set to the container that has the dataset. In this case it is "labelgendata".
7. `webapp` set to the webapp URL of the label skill deployed in the previous step
8. `markdown_skill_fn` Set to the Markdown skill url. You can get this from Azure Portal.

### Test the results

Once all the cells in the notebook have run successfully, check your indexer status to validate that it ran successfully.

## Wrap up

1. You now have a labeled dataset that you can use with Azure Machine Learning to create a custom NER (named entity recognizer) model.
