#!/bin/bash

versions=( 3.6 3.7 3.8 3.9 3.10 )

for i in "${!versions[@]}"
    do
         test_result=$(
         docker build -t "pkonfig" --build-arg VERSION="${versions[i]}" . \
         && docker run --rm pkonfig
         )
        echo "${versions[i]}" resulted with "$test_result"
        docker rmi pkonfig
    done
