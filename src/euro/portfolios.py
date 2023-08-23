
import re

def extract_tickers_and_shares(file_path):
	with open(file_path, 'r') as f:
		lines = f.readlines()

	results = []

	# Regular expression to match the pattern of the ticker followed by a number.
	pattern = re.compile(r'^([A-Z]+)\s+(\d+)')

	for line in lines:
		match = pattern.match(line.strip())
		if match:
			ticker = match.group(1)
			shares = int(match.group(2))
			results.append((ticker, shares))

	return results














