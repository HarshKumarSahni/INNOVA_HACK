# Makefile

.PHONY: all backend frontend dev

backend:
	cd backend && code .


frontend:
	cd frontend && code .

dev:
	cmd /c start cmd /k "make backend"
	cmd /c start cmd /k "make frontend"

