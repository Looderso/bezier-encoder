
.ONESHELL:
MAKEFLAGS += --always-make

ACTIVATE_CONDA_ENV=source $$(conda info --base)/etc/profile.d/conda.sh ;conda activate

env:
	rm -Rf "./env"
	mamba create --prefix ./env -y python=3.12
	$(ACTIVATE_CONDA_ENV) ./env ; pip install -e ".[dev]";
