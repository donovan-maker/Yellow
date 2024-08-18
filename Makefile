MAIN = src/main.yell
JSON = src/main.json

main:
	@echo Compiling $(MAIN) into $(JSON)
	@python main.py -i $(MAIN) -o $(JSON)
	@echo Running $(MAIN) through $(JSON)
	@python main.py -i $(JSON) -r