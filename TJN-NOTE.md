TJN Notes
---------

Looking at the jupyter notebooks and log parser modules.


Setup
-----
 - Note: Default install used Conda.  I just wanted simpler version based on
   pip and a list of requirements.

 - Create virtual env

    ```
        python3 -m venv venv-3.6
    ```

 - Activate venv and install packages

    ```
        source venv-3.6/bin/activate
        (venv-3.6)$ pip install --upgrade pip    # Otherwise got error on `Pillow` pkg
        (venv-3.6)$ pip install -r requirements.txt
    ```

 - Download/setup reframe (in `hpc-tests` topdir)

    ```
        git clone https://github.com/eth-cscs/reframe.git
        cd reframe
        ./bootstrap.sh
        ./bin/reframe -V
        cd ..
    ```

 - Set `PYTHONPATH` (from `hpc-tests` topdir)

    ```
        export PYTHONPATH=$PWD/modules:$PYTHONPATH
        export PYTHONPATH=$PWD/reframe:$PYTHONPATH
    ```

 - Setup jupyter notebook (shown using specific port)

    ```
        jupyter notebook --port 8800
    ```

 - Connect to jupyter

 - Open IMB notebook: http://localhost:8800/tree/apps/imb/IMB.ipynb

    - Ignore deprecation warnings
        ```
        WARNING: using the @rfm.run_after decorator from the rfm
        module is deprecated; please use the built-in decorator @run_after
        instead.  @rfm.run_after('compile')
        ```

        ```
        ipykernel_launcher.py:40: MatplotlibDeprecationWarning: The
        'basex' parameter of __init__() has been renamed 'base' since
        Matplotlib 3.3; support for the old name will be dropped
        two minor releases later.
        ```

 - NOTE: If get error about `datetime.fromisoformat()`
   this appears to be related to using older Python < 3.7.
   (See: [StackOverflow](https://stackoverflow.com/questions/60266554/type-object-datetime-datetime-has-no-attribute-fromisoformat))

   Work around is:

   ```
       pip install backports.datetime_fromisoformat
   ```

   Jupyter add following:

   ```
      # TJN: Hack around python3.6 not having datetime.fromisoformat()
      from backports.datetime_fromisoformat import MonkeyPatch
      MonkeyPatch.patch_fromisoformat()
   ```


ELK SSH
-------

 - SSH port fwds

   ```
     laptop:$ ssh -L 8800:localhost:8800 elk2
     elk2:$ ssh -L 8800:localhost:8800 elk
   ```

 - Browse jupter notebook from laptop

    ```
       localhost:8800
    ```

