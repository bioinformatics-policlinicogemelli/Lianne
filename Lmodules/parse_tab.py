

#####################################
# NAME: parse_tab.py
# AUTHOR: Luciano Giaco'
# Date: 01/12/2021
version = "0.1"
# ===================================

import os
import ast
import pandas as pd

def only_dict(d):
    '''
    Convert json string representation of dictionary to a python dict
    '''
    return ast.literal_eval(d)

def list_of_dicts(ld):
    '''
    Create a mapping of the tuples formed after 
    converting json strings of list to a python list   
    '''
    return dict([(list(d.values())[1], list(d.values())[0]) for d in ast.literal_eval(ld)])


def get_json(json_file):
	json_df = pd.read_json(json_file)
	# print(json_df.head())
	# print(json_df)

	# for col in json_df.columns:
	# 	print(col)

	# print(json_df["calculatedClassification"])
	# print(json_df["consequence"])
	# print(json_df["hgvsNomenclature"])
	# print(json_df["type"])
	# print(json_df["id"])
	classification = pd.json_normalize(json_df["calculatedClassification"])
	#vclassification.to_csv("UP01_tier.csv", index=False)
	print(json_df["calculatedClassification"])
	calculatedClassification = json_df["calculatedClassification"]

	c = 0
	TierI_subset = {k: v for k, v in json_df["calculatedClassification"].items() if v == "IID"}
	for k, v in json_df["calculatedClassification"].items():
		# print(v)
		if v["level"] == "IID":
			for e in json_df['hgvsNomenclature'][c]['cSyntaxes']:
				print(e)
		c = c + 1
	# print(TierI_subset)
	hgvsNomenclature = pd.json_normalize(json_df["hgvsNomenclature"])
	# hgvsNomenclature.to_csv("UP01_hgvs.csv", index=False)

	# print(hgvsNomenclature.index['gSyntax'])
	# gSyntax = pd.json_normalize(hgvsNomenclature["gSyntax"])
	# gSyntax.to_csv("UP01_gSyntax.csv", index=False)
	# d = only_dict(json_df)
	json_dict = json_df.to_dict(orient='records')
	# k = json_dict.keys()
	# first element
	# print('first element')
	# print('\n\n')
	# print(json_dict[0])
	# # dict hgvs
	# print('dict hgvs')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature'])
	# # dict cSyntaxes
	# print('dict cSyntaxes')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature']['cSyntaxes'])
	# # first element cSyntaxes
	# print('first element cSyntaxes')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature']['cSyntaxes'][0])
	# print('gene level')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature']['cSyntaxes'][0]['gene'])
	# print('gene name')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature']['cSyntaxes'][0]['gene']['symbol'])
	# print('pSyntax level')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature']['cSyntaxes'][0]['pSyntax'])
	# print('transcSyntax level')
	# print('\n\n')
	# print(json_dict[0]['hgvsNomenclature']['cSyntaxes'][0]['transcSyntax'])

	# ld = list_of_dicts(json_df)
	# print(ld)

	# A = json_normalize(df['calculatedClassification'].apply(only_dict).tolist()).add_prefix('calculatedClassification.')
	# B = json_normalize(df['hgvsNomenclature'].apply(list_of_dicts).tolist()).add_prefix('hgvsNomenclature.pos.') 

	# print(A)
	# print(B)

def main(tab_file):
	tab_df = pd.read_csv(tab_file, sep='\t', skiprows = 56)
	
	print(tab_df.head())
	canonical = tab_df[tab_df["CANONICAL"] == 'YES']
	no_intron = canonical[(canonical['Consequence'] != "intron_variant") & (canonical['Existing_variation'] != "-")]
	print(canonical)
	print(no_intron)

	egfr = no_intron[no_intron["SYMBOL"] == 'EGFR']
	egfr = egfr.to_csv("egfr.csv", index=False)

	brca2 = no_intron[no_intron["SYMBOL"] == 'BRCA2']
	brca2 = brca2.to_csv("brca2.csv", index=False)

if __name__ == '__main__':
	tab_file = os.sys.argv[1]
	# main(tab_file)
	get_json(tab_file)