**Fine tuned small image detection model to protect the goods**
-
  

**Container that contains code for 3 primary uses:**

1)  `app/` - contains python code to host fastapi and run image processing using opencv & yolo image detection models

  

2)  `fine_tuning/` - contains script to initiate fine tuning run on included dataset which follows yolo format

  

3)  `testing/` - contains a script to benchmark test images against supplied models (speed & accuracy) & script for running basic inference

  
  

**To run:**

  

`docker compose up --build`

> Note: working directory mounted by default to avoid constant rebuilding

  

`docker exec -it <container-name> bash`

> Note: run `docker ps` to see what `<container-name>` is

  

get into container and run whatever with `python ./<file_name>`

> Note: working directory is project root so either specify file path or cd into each specific directory


