: 第一引数はPythonスクリプトのファイル名、第二引数以降はスクリプトに渡す引数
@echo off
for /F "tokens=* usebackq" %%i in (`where python`) do (
  set python_path=%%i
)

set script_name=%~1
set args=
shift

:loop
if "%1"=="" goto final
set args=%args% %~1
shift
goto loop
:final
%python_path% %script_name% %args%