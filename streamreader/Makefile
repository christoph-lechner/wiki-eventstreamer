.PHONY: build

GIT_INFO := $(shell git describe --dirty --always --tags)

build:
	# docker compose build --no-cache --build-arg GIT_INFO=$(GIT_INFO)
	docker compose build --build-arg GIT_INFO=$(GIT_INFO)

up: build
	docker compose up
