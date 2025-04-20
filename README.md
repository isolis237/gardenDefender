fine tuned small image detection model to protect the goods

- app/ directory contains api src code (dont forget requirements.txt)

- fine_tuning/ contains script to initiate fine tuning run on dataset included

- testing/ contains files for testing models on `real life` data for continuous improvement


To run:

- docker compose up --build 
    > (working directory mounted by default to prevent constant rebuilding)

- docker exec -it api bash
    > get into container and run whatever with `python ./<file_name>`