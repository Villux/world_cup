#!/bin/bash

for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
do
    echo "Run match-level simulation loop $i for score prediction"
    python3 run_score_model_simulation.py --actual --limited-features
done

for j in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
do
    echo "Run match-level simulation loop $j for outcome prediction"
    python3 run_outcome_model_simulation.py --actual --limited-features
done

echo "Finished running simulation"