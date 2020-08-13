import regeng

if __name__ == "__main__" :
	
	pattern = input("Enter with the regex pattern: ")
	rgx = regeng.Regex(pattern)
	
	while True:
		try :
			print(rgx.match(input("Enter with the expression to be evaluated: ")))
		
		except EOFError:
			break
	
