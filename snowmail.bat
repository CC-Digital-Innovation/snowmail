@echo OFF
rem How to run a Python script in a given conda environment from a batch file.

rem It doesn't require:
rem - conda to be in the PATH
rem - cmd.exe to be initialized with conda init

rem Define here the path to your conda installation
set CONDAPATH=C:\ProgramData\Anaconda3
rem Define here the name of the environment
set ENVNAME=base

rem The following command activates the base environment.
rem call C:\ProgramData\Miniconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate the conda environment
rem Using call is required here, see: https://stackoverflow.com/questions/24678144/conda-environments-and-bat-files
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

rem Change working directory to app director
call cd C:\local\src\dev\snowmail

rem Variables
set NAME=%1
set SUBJECT=%2
set BODY=%3
set EMAIL=%4
set SUBJECT_CMD=%5
set SUBJECT_INC=%6
set BODY_CMD=%7
set BODY_INC=%8

if /i %SUBJECT_CMD%=="status" set CMD="status"
if /i %BODY_CMD%=="status" set CMD="status"
if /i %SUBJECT_CMD%=="update" set CMD="update"
if /i %BODY_CMD%=="update" set CMD="update"

set INC=%SUBJECT_INC%

rem What action is being prefromed?
IF /i %CMD%=="status" goto CASE_STATUS
IF /i %CMD%=="update" goto CASE_STATUS
ELSE goto CASE_CREATE

rem Case statements
:CASE_STATUS
    rem Run a python script in that environment
    call python snowmail.py %CMD% --incident %INC% --name %NAME%  --email %EMAIL%
    GOTO END
:CASE_UPDAE
    call python snowmail.py %CMD% --incident %INC% --name %NAME% --email %EMAIL% --subject %SUBJECT% --body %BODY%
    GOTO END
:CASE_CREASE
    call python snowmail.py %CMD% --name %NAME% --email %EMAIL% --subject %SUBJECT% --body %BODY%
    GOTO END

:END
    rem Deactivate the environment
    call conda deactivate

    rem Close command prompt window
    exit

rem If conda is directly available from the command line then the following code works.
rem call activate someenv
rem python script.py
rem conda deactivate

rem One could also use the conda run command
rem conda run -n someenv python script.py