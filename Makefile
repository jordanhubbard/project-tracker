# Developer-facing shortcuts for the supported Literate AI lifecycle.
# The generated application remains governed by its selected JavaScript/npm Flavors.

COMPONENT       ?= components/tracker
MODEL           ?= claude-fable-5-1
HOST            ?= 127.0.0.1
PORT            ?= 8765
LITAI           ?= litai
LIFECYCLE       ?= ./scripts/litai-service.sh
BUILD_FLAGS     ?= --update-receipt
TEST_FLAGS      ?= --update-receipt
SERVICE_ARGS    ?= ["service","--host","$(HOST)","--port","$(PORT)"]
DEMO_ARGS       ?= ["service","--host","$(HOST)","--port","$(PORT)","--demo"]

.DEFAULT_GOAL := help

.PHONY: all help doctor status validate check lock plan build test test-toolchain verify run start demo

all: build

help:
	@printf '%s\n' \
		'Project Tracker developer commands:' \
		'  make build      Lock, build, test, export, and update the receipt' \
		'  make run        Run the last successful export in the foreground' \
		'  make demo       Run the export with an isolated demo workspace' \
		'  make test       Run the supported test lifecycle and update the receipt' \
		'  make test-toolchain  Check supported and rejected Git versions' \
		'  make check      Validate project authority and verify declared gates' \
		'  make plan       Show the exact generation plan after refreshing the lock' \
		'  make doctor     Inspect the host and coding-provider setup' \
		'  make status     Show the current Literate AI project state' \
		'' \
		'Common overrides:' \
		'  MODEL=<model> HOST=<address> PORT=<port> COMPONENT=<path>' \
		'  BUILD_FLAGS="..." TEST_FLAGS="..." SERVICE_ARGS="[...]"'

doctor:
	$(LITAI) doctor

status:
	$(LITAI) status

validate:
	$(LITAI) project validate

check: validate verify

lock:
	$(LIFECYCLE) lock $(COMPONENT)

plan: lock
	$(LIFECYCLE) plan $(COMPONENT) --model $(MODEL)

build: lock
	$(LIFECYCLE) build $(COMPONENT) --model $(MODEL) $(BUILD_FLAGS)

test: lock
	$(LIFECYCLE) test $(COMPONENT) --model $(MODEL) $(TEST_FLAGS)

test-toolchain:
	./scripts/check-git-version.sh 'git version 2.30.0'
	./scripts/check-git-version.sh 'git version 2.50.1 (Apple Git-155)'
	./scripts/check-git-version.sh "$$(git --version)"
	./scripts/check-git-version.sh 'git version 3.0.0'
	! ./scripts/check-git-version.sh 'git version 2.29.9'
	! ./scripts/check-git-version.sh 'git unknown'

verify:
	$(LITAI) verify

run start:
	$(LIFECYCLE) run $(COMPONENT) '$(SERVICE_ARGS)'

demo:
	$(LIFECYCLE) run $(COMPONENT) '$(DEMO_ARGS)'
