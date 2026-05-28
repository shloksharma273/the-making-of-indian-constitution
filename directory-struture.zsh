```zsh
#!/usr/bin/env zsh

# Create the main graphRAG directory
# mkdir -p graphRAG

# Navigate into the main directory
# cd graphRAG

# Create the data subdirectories
mkdir -p data/debates data/constitutions data/books

# Create the processed subdirectories
mkdir -p processed/debates processed/constitutions processed/books

# Create the embeddings directory
mkdir embeddings

# Navigate into the pipelines directory and create files
mkdir -p pipelines
touch pipelines/debate_pipeline.py pipelines/constitution_pipeline.py pipelines/book_pipeline.py

# Navigate into the utils directory and create files
mkdir -p utils
touch utils/chunking.py utils/embedding.py utils/cleaners.py utils/metadata.py

# Navigate into the models directory and create a file
mkdir -p models
touch models/schemas.py

# Create the main.py file at the root level of graphRAG
touch main.py

echo "Directory structure created successfully!"
```
