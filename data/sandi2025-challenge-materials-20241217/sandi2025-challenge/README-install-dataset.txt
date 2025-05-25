Speak & Improve Challenge 2025 Dataset Installation Instructions
================================================================

This file describes the steps to complete the installation for the Speak & Improve Challenge 2025.

1. The audio files for the Dev and Train set must be downloaded separately
- there are 13 files (2 for Dev, 11 for Train) to limit the size of any single file
- each file will unzip into data/flac/dev/ or data/flac/train/ and should be unzipped in this directory
  or a soft link made to it here with the name "data"
- download links:

https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.dev.01.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.dev.02.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.01.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.02.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.03.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.04.P1.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.04.P3.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.04.P4.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.04.P5.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.05.P1.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.05.P3.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.05.P4.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/audio/data.flac.train.05.P5.zip  

2. (Optional) the models required to run the provided baseline pipeline need to be downloaded separately
- the files will unzip into sandi2025-challenge/sandi-models/ so should be unzipped so that
  sandi-models/ is in this directory
- download links: 

https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/models/sandi2025-challenge-dd-model.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/models/sandi2025-challenge-gec-model.zip
https://speak-and-improve-corpus-2025.s3.eu-west-1.amazonaws.com/models/sandi2025-challenge-sla-models.zip

3. To run the scoring tools and the baseline-pipeline two miniconda environments need to be created:
- "sandi-all" and "sandi-dd"
- See envs/README.txt for instructions on creating the environments
- Once installed, set $CONDA_PATH in envs/sandi-dd-env.sh and envs/sandi-all-env.sh to point
  to your local miniconda installation

Questions?
- Please report any issues or problems in downloading the dataset by emailing: support@speakandimprove.com
- All other queries: email Mengjie Qian mq227@cam.ac.uk and Kate Knill kmk1001@cam.ac.uk

