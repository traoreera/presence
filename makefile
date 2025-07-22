PWD := $(shell pwd)
MAIN := $()/
.PHONY: all install script

install:
	@echo "Initialisation de l'environnement"
	@touch $(PWD)/.env
	@echo "BROKER_URL=2a94bbeb1f484944aea1327a5b2142bc.s1.eu.hivemq.cloud" >> $(PWD)/.env
	@echo "USERNAME=Admin10" >> $(PWD)/.env
	@echo "PASSWORD=Admin123A" >> $(PWD)/.env
	@echo "BROKER_PORT=8883" >> $(PWD)/.env

script:
	@chmod +x ./script/pre_commit.py
	@chmod +x ./script/run_pre_commit.py
	@chmod +x ./script/check_banned_words.py

runtimer:
	@mv presence.py ../../backgroundtask/presence.py