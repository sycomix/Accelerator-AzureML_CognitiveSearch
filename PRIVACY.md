# Privacy

When you deploy this template, Microsoft is able to identify the installation of the software with the Azure resources that are deployed. Microsoft is able to correlate the Azure resources that are used to support the software. Microsoft collects this information to provide the best experiences with their products and to operate their business. The data is collected and governed by Microsoft's privacy policies, which can be found at https://privacy.microsoft.com/en-us/privacystatement.

To disable this, simply remove the following section from the deployment template json file before deploying the resources to Azure. Note that each deployment option mentioned [here](https://github.com/microsoft/Accelerator-AzureML_CognitiveSearch) refers to one of the deployment template json files mentioned in this folder.

```json
{
    "apiVersion": "2018-02-01",
    "name": "pid-416d0e47-324f-5c9e-8dde-f9fc4a92c091",
    "type": "Microsoft.Resources/deployments",
    "properties": {
        "mode": "Incremental",
        "template": {
            "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "resources": []
        }
    }
}
```

You can see more information on this at https://docs.microsoft.com/en-us/azure/marketplace/azure-partner-customer-usage-attribution.
