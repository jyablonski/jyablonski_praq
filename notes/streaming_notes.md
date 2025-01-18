# Architectures

## Lambda
The Lambda architecture involves 3 components:
    * Batch Layer which precomputes all historical data.
    * Streaming Layer which computes all data since the last batch update
    * Serving Layer where the two compute layers above are merged to display aggregated data.


Any issues or errors in the Streaming Layer can get fixed when that data is ran through the batch layer the following run cycle.

Other nuances like maybe you have an ML model that gets updated in the batch layer every day but is used to provide predictions in the streaming layer.

Batch layer can be ran once a day or on a faster interval than that.  Take into consideration cost.

The Batch + Streaming layer means 2 different codebases have to be maintained.

## Kappa
Kappa Architecture is fully event based and involves fully fledged event sourcing.  There is no batch layer.  It handles all real-time transactional and analytical workloads.  You perform everything with 1 codebase.  
    * You only do reprocessing when your processing code changes to recompute the results.
    * Single source of truth.

Things can get very complex when there are issues or hotfixes that need to be applied and you're forced to replay a large chunk of streaming events.  This is a lot more engineering and developer intensive work than the Lambda architecture.

## Acks