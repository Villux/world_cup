#!/bin/bash

for i in 1 2 3 4 5 6 7 8 9 10
do
    if [ "$1" = "score" ]
    then
        echo "Run simulation loop $i for score prediction"
        python3 run_score_model_simulation.py
    else
        echo "Run simulation loop $i for outcome prediction"
        python3 run_outcome_model_simulation.py
    fi
done

echo "Finished running simulation"