#!/bin/bash
UUID=$(uuidgen)
echo "$UUID" > /etc/machine-id
