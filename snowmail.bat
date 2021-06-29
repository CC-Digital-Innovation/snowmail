@echo ON

@REM Set applicaiton root
set app_root="C:\local\src\dev\snowmail"

@REM Set data and time for debug output
for /F "tokens=2" %%i in ('date /t') do set mydate=%%i
set mytime=%time%

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
call cd %app_root%
@REM DEBUG
echo "%mydate%:%mytime% | DEBUG | App root: %app_root%"


@REM Variables
set CMD=""
set NAME=%1
set SUBJECT=%2
set BODY=%3
set EMAIL=%4
set SUBJECT_CMD=%5
set SUBJECT_INC=%6
set BODY_CMD=%7
set BODY_INC=%8
set PHONE_NUM=%9


@REM DEBUG
@echo "%mydate%:%mytime% | DEBUG | Name: %NAME%"
@echo "%mydate%:%mytime% | DEBUG | Subject: %SUBJECT%"
@echo "%mydate%:%mytime% | DEBUG | Body: %BODY%"
@echo "%mydate%:%mytime% | DEBUG | Email: %EMAIL%"
@echo "%mydate%:%mytime% | DEBUG | Subject CMD: %SUBJECT_CMD%"
@echo "%mydate%:%mytime% | DEBUG | Subject INC: %SUBJECT_INC%"
@echo "%mydate%:%mytime% | DEBUG | Body CMD: %BODY_CMD%"
@echo "%mydate%:%mytime% | DEBUG | Body INC: %BODY_INC%"
@echo "%mydate%:%mytime% | DEBUG | Phone Number: %PHONE_NUM%"

@REM Set CMD and INC varaibles
if /i %SUBJECT_CMD%=="status" (set CMD="status") else (echo "%mydate%:%mytime% | DEBUG | SUbject CMD: NULL")
@REM if /i %BODY_CMD%=="status" (set CMD="status") else (echo "%mydate%:%mytime% | DEBUG | Body CMD: NULL")
if /i %SUBJECT_CMD%=="update" (set CMD="update") else (echo "%mydate%:%mytime% | DEBUG | SUbject CMD: NULL")
@REM if /i %BODY_CMD%=="update" (set CMD="update") else (echo "%mydate%:%mytime% | DEBUG | Body CMD: NULL")
if /i %CMD%=="" (set CMD="create") else (echo "%mydate%:%mytime% | DEBUG | CMD: %CMD%")

if /i %SUBJECT_INC%=="" (echo "%mydate%:%mytime% | DEBUG | SUbject INC: NULL") else (set INC=%SUBJECT_INC%)
if /i %BODY_INC%=="" (echo "%mydate%:%mytime% | DEBUG | BODY INC: NULL") else (set INC=%BODY_INC%)

@REM DEBUG
@echo "%mydate%:%mytime% | DEBUG | CMD: %CMD%"
@echo "%mydate%:%mytime% | DEBUG | INC: %INC%"

@REM Remove quotes from CMD
call :dequote CMD
@echo "%mydate%:%mytime% | DEBUG | CMD: %CMD%"
@REM Call CMD function
GOTO :%CMD%

exit /b %ERRORLEVEL%

@REM Functions

:dequote
    for /f "delims=" %%A in ('echo %%%1%%') do set %1=%%~A
    exit /b %ERRORLEVEL%

:status
    rem Run a python script in that environment
    echo "%mydate%:%mytime% | DEBUG | %CMD%, %INC%, %NAME%, %EMAIL%"
    start /wait python snowmail.py %CMD% --incident %INC% --name %NAME% --email %EMAIL% --phone %PHONE_NUM%
    echo %ERRORLEVEL%
    GOTO :END

:update
    echo "%mydate%:%mytime% | DEBUG | %CMD%, %INC%, %NAME%, %EMAIL%, %SUBJECT%, %BODY%"
    start /wait python snowmail.py %CMD% --incident %INC% --name %NAME% --email %EMAIL% --phone %PHONE_NUM% --subject %SUBJECT% --body %BODY%
    echo %ERRORLEVEL%
    GOTO :END

:create
    echo "%mydate%:%mytime% | DEBUG | %CMD%, %NAME%, %EMAIL%, %SUBJECT%, %BODY%"
    start /wait python snowmail.py %CMD% --name %NAME% --email %EMAIL% --phone %PHONE_NUM% --subject %SUBJECT% --body %BODY%
    echo %ERRORLEVEL%
    GOTO :END

:end
    rem Deactivate the environment
    call conda deactivate

    rem Close command prompt window
    exit /b %ERRORLEVEL%


rem Deactivate the environment
call conda deactivate

rem Close command prompt window
exit /b %ERRORLEVEL%


rem If conda is directly available from the command line then the following code works.
rem call activate someenv
rem python script.py
rem conda deactivate

rem One could also use the conda run command
rem conda run -n someenv python script.py


