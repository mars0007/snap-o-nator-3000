# snap-o-nator-3000
Intro to EC2 snapshot management 

## About

This is a small demo of how to manage instance snaps

## Config

snap uses the default profile created by AWS CLI

`aws configure`

## Running

`pipenv run python .\bin\snap.py <command> <subcommand> <--project=PROJECT>`

*command* is instances, volumes or snapshots 
*subcommand* is list, stop or start
*project* is optional
