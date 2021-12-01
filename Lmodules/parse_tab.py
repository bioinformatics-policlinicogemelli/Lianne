

#####################################
# NAME: parse_tab.py
# AUTHOR: Luciano Giaco'
# Date: 01/12/2021
version = "0.1"
# ===================================

import os
import pandas as pd

def main(tab_file):
	tab_df = pd.read_csv(tab_file, sep='\t', skiprows = 56)
	
	print(tab_df.head())
	canonical = tab_df[tab_df["CANONICAL"] == 'YES']
	no_intron = canonical[canonical['Consequence'] != "intron_variant"]
	print(canonical)
	print(no_intron)

	egfr = no_intron[no_intron["SYMBOL"] == 'EGFR']
	egfr = egfr.to_csv("egfr.csv", index=False)

if __name__ == '__main__':
	tab_file = os.sys.argv[1]
	main(tab_file)