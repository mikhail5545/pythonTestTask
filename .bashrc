alias activate="source $(poetry env info --path)/bin/activate"
alias test="poetry run pytest tests/"
alias run="poetry run uvicorn main:app --reload"