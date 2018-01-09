@echo off
for /F "tokens=* usebackq" %%i in (`where python`) do (
  set python_path=%%i
)

%python_path% script.py %~nx1 %~nx2