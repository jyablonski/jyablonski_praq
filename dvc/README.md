# DVC

DVC is a tool that helps track large datasets and ML models alongside your code. This enables you to clone a repo and have all of the datasets, checkpoints, and models available in your workspace.

It uses Cloud Remote Storage such as S3 to store your source data and other various files used throughout your ML Model Building process. It also stores `.dvc` metadata files that can be checked into Git which point to those files in Remote Storage so Engineers and Data Scientists can pull the files down from Cloud Storage into their local file system to run various tests and pipelines.

- This enables you to store large files in something like S3, and not have to check them into Git

DVC-tracked data can be added to a variety of storage systems referred to as "remotes".

- Remotes can be your local file system, or S3 etc.


DVC stores information in a special `.dvc` file under `data/data.xml.dvc` which is a human readable metadata file as a placeholder for the original dataset which we dont want to check into git.

- To recap, the original CSV file or whatever is added to the gitignore
- The `.dvc` file is created as a placeholder to reference that CSV File.

``` sh
dvc init

# dvc init --subdir

dvc get https://github.com/iterative/dataset-registry \
          get-started/data.xml -o data/data.xml

dvc add data/data.xml
```


## Local File System

``` sh
mkdir /tmp/dvcstore

# local route
dvc remote add -d myremote /tmp/dvcstore

# s3 route
dvc remote add -d storage s3://mybucket/dvcstore

dvc push

dvc pull

cp data/data.xml /tmp/data.xml
cat /tmp/data.xml >> data/data.xml

# after making data changes, you have to add the file again to tell it to track the latest version
# and then run dvc push
dvc add data/data.xml
dvc push

git checkout HEAD~1 data/data.xml.dvc
dvc checkout

git commit data/data.xml.dvc -m "Revert dataset updates"
```

Once DVC-tracked data and models are stored remotely, they can be downloaded with dvc pull when needed (e.g. in other copies of this project). Usually, we run it after `git pull` or `git clone`.

The Git <> DVC stuff kinda confuses me. I think we'll have to play around with this a bit more to understand the interaction there. 


## Data Pipelines

[Guide](https://dvc.org/doc/start/data-pipelines/data-pipelines)

``` sh
virtualenv venv && echo "venv" > .gitignore

source venv/bin/activate
pip install -r src/requirements.txt

dvc stage add -n prepare \
                -p prepare.seed,prepare.split \
                -d src/prepare.py -d data/data.xml \
                -o data/prepared \
                python src/prepare.py data/data.xml

dvc stage add -n featurize \
                -p featurize.max_features,featurize.ngrams \
                -d src/featurization.py -d data/prepared \
                -o data/features \
                python src/featurization.py data/prepared data/features

dvc stage add -n train \
                -p train.seed,train.n_est,train.min_split \
                -d src/train.py -d data/features \
                -o model.pkl \
                python src/train.py data/features model.pkl

dvc repro

dvc dag
```

DVC Stages are processing steps in a Data Pipeline. 1 or more Stages create a Pipeline. Stages allow connecting code to its corresponding data input + output.

After running the dvc stage add block above, a `dvc.yaml` file is generated that includes info about the command we want to run, its dependencies, and outputs.


``` yaml
stages:
  prepare:
    cmd: python src/prepare.py data/data.xml
    deps:
    - data/data.xml
    - src/prepare.py
    params:
    - prepare.seed
    - prepare.split
    outs:
    - data/prepared

```

`dvc repro` can be ran to run the pipeline. It automatically is able to track which stages it's already ran and haven't changed so it can skip them and only run the changed stages.

`dvc.lock` file is automatically generated and acts as a state file. Never modify this file, the tool will handle it for you.

`dvc dag` can be ran to view a directed acyclic graph of your pipeline and its stages.