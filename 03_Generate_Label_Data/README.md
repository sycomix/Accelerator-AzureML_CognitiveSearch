# Review the knowledge store projections

Once your indexer has run successfully, validate that the knowledge store should have a new container `labeled-data` with a JSON blob for each document in your datasource. We are going to transform the JSON blobs to a CSV matching the data required to train the model

## Transform JSON blobs to CSV

Run the [Generate_NER_Label_Data](./Generate_NER_Label_Data.ipynb) notebook to:

1. Read each blob from the `labeled-data` container.
2. Transform the blobs into dataframe with the contents and column names matching the expected input for the model
3. Upload to a new container `labeled-data-df`

## Use the transformed data as an AML dataset

In the next step, we'll leverage this labeled data as a dataset in Azure Machine Learning.

## Wrap up

1. Your labeled dataset is now available for training the model.
