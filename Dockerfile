FROM ubuntu:18.04
 
ENV PYTHON_VERSION 3.7.3
ENV HOME /root
# PYTHON
ENV PYTHON_ROOT $HOME/local/bin/python-$PYTHON_VERSION
ENV PATH $PYTHON_ROOT/bin:$PATH
ENV PYENV_ROOT $HOME/.pyenv
# Jupyter Notebook config
ENV JUPYTER_CONFIG /root/.jupyter/jupyter_notebook_config.py
 
RUN apt-get update && apt-get upgrade -y \
 && apt-get install -y tzdata
# timezone setting
ENV TZ=Asia/Tokyo
RUN apt-get install -y tzdata \
    build-essential \
    curl \
    git \
    libbz2-dev \
    libcurl4-openssl-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libpq-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    llvm \
    make \
    r-base \
    tk-dev \
    unzip \
    vim \
    wget \
    xz-utils \
    zlib1g-dev \
 && apt-get autoremove -y && apt-get clean \
 && git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT \
 && $PYENV_ROOT/plugins/python-build/install.sh \
 && /usr/local/bin/python-build -v $PYTHON_VERSION $PYTHON_ROOT \
 && rm -rf $PYENV_ROOT

 # install additional packages
COPY ./requirements.txt requirements.txt
RUN pip install -U pip && pip install -r requirements.txt \
 && jupyter notebook --generate-config --allow-root \
 && echo "c.NotebookApp.ip = '0.0.0.0'" >> ${JUPYTER_CONFIG} \
 && echo "c.NotebookApp.port = 8000" >> ${JUPYTER_CONFIG} \
 && echo "c.NotebookApp.open_browser = False" >> ${JUPYTER_CONFIG} \
 && echo "c.NotebookApp.allow_root = True" >> ${JUPYTER_CONFIG} \
 && echo "c.NotebookApp.token = ''" >> ${JUPYTER_CONFIG} \
 && echo "c.NotebookApp.iopub_data_rate_limit=10000000000" >> ${JUPYTER_CONFIG} \
 && echo "c.MultiKernelManager.default_kernel_name = 'python3.6'" >> ${JUPYTER_CONFIG} \
 && echo "c.IPKernelApp.pylab = 'inline'" >> ${JUPYTER_CONFIG} \
 && echo "c.InlineBackend.figure_formats = {'png', 'retina'}" >> ${JUPYTER_CONFIG} \
 && Rscript -e "install.packages(c('repr', 'IRdisplay', 'evaluate', 'crayon', 'pbdZMQ', 'devtools', 'uuid', 'digest'))" \
 && Rscript -e "devtools::install_github('IRkernel/IRkernel')" \
 && Rscript -e "IRkernel::installspec()"

