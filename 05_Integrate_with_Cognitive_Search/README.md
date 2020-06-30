# Integrate the Custom Skill with Search

Now that we have a endpoint for Azure ML service for NER, we will configure Cognitive Search to integrate with  deployed Azure ML service for NER


### Configure Congnitive Search

Run the "Add NER Skill" notebook to:

1. Create a datasource pointing to the demodata blob storage container
2. Create a skillset that uses the Markdown Parser Skill and BERT NER AML Skill
3. Define the knowledge store projections to export your data
4. Define the index we will populate with the enriched data
5. Define and run the indexer

To successfully  run the notebook, you will need to set the following variables:

1. `search_service_name` set to the name of your Cognitive Search service
2. `api_key` set to the api key for the search service
3. `cog_svcs_key` set to the cognitive services resource that was deployed. You will not be billed for any cognitive services, but the key is required
4. `STORAGEACCOUNTNAME` set to the storage account name that contains the dataset.
5. `STORAGEACCOUNTKEY` set to the storage account key
6. `datasource_container` set to the container that has the dataset. In this case it is "labelgendata".
7. `markdown_skill_fn` Set to the Markdown skill url. You can get this from Azure Portal.
8. `inference_URL` URL of the AKS endpoint that refers to BERT NER model

### Test the results

Once all the cells in the notebook have run successfully, check your indexer status to validate that it ran successfully.



## Next Steps

Now you're ready to view your enriched search index. You can use search explorer in the Azure portal to view the index, use the search API call within or postman, or spin up the [Web UI](https://github.com/Azure-Samples/azure-search-knowledge-mining/tree/master/02%20-%20Web%20UI%20Template) to see the index.