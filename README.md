# DBGenerator

Project of a generator of fake sqlite databases. It can creates a database with random table and random population or can import an existing schema and populate it.
The Docker execute the sqlite database and provide a service on the specified port (default 8080). It is also possible to specify a passowrd to access the database.

## Prerequisites and installation

#### Prerequisites

- docker
- python3
- [llama.cpp](https://python.langchain.com/docs/integrations/llms/llamacpp)

#### Build and Installation

- run:
  
  ```
  pip install -r requirements.txt
  
  chmod 777 buildDBGenerator.sh
  
  chmod 777 runDB.sh
  ```
- download llm models into ../llama.cpp/models/:
    -    [dolphin2.1-openorca-7b.Q4_K_M.gguf](https://huggingface.co/TheBloke/Dolphin2.1-OpenOrca-7B-GGUF/blob/main/dolphin2.1-openorca-7b.Q4_K_M.gguf)
    -   [llama-2-7b-chat.Q4_K_M.gguf](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.Q4_K_M.gguf)

- get Mockaroo API's key by creating an Account on [the official website](https://www.mockaroo.com/). The key will be available at "My API Key" in My Account section.

- in the path_and_api_key.txt file set up the absolute path of the llama.cpp/models/ folder (abs_path/llama.cpp/models/) and the Mockaroo key

These steps are enough to setup the environment properly. Now we can run the script.

#### Run

For creating/importing the DB and build the docker image run:

```
./buildDGGenerator.sh
```

For running the docker image:

```
./runDB.sh
```

The fake DB will be now avaiable locally on port 8080(by default). You can specify `-p <port>` if you want to change the port.


