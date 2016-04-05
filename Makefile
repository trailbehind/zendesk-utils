#
# Usage:
#     make dev
#     make build

help:
	@echo 'Makefile for zendesk-utils                      '
	@echo '                                                                '
	@echo '   make dev                      Run /bin/bash in a machine that can run these utils'

.PHONY: dev build

IMAGE_NAME = gaiagps/zendesk-utils

dev: build
	docker run --privileged --rm -ti -v `pwd`:/zendesk-utils gaiagps/zendesk-utils /bin/bash

build:
	docker build -t $(IMAGE_NAME) .
