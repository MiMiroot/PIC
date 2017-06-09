"""
author: CJH
funciton: calculate Pausing Index and make some fileterations (eg. strongest signal at TSS for different isoforms).
"""

import sys
import argparse

parser = argparse.ArgumentParser(prog='Calculation of Pausing Index')
parser.add_argument('--tags', type=str, help="tag counts for each gene")
parser.add_argument('--min', type=float, default=0.001, help="minimum ChIP signal at TSSR")
parser.add_argument('--longest', action='store_true')
parser.add_argument('--anno', type=str, help="offer gene symbols to gene_id")
args = parser.parse_args()

tag_file = open(args.tags, 'r')
anno_file = open(args.anno, 'r')
alloutput = open('all_gene_PI.txt', 'w')

name_match = dict()
for line in anno_file.readlines():
	content = line.strip().split('\t')
	if content[3] in name_match:
		print "duplicate ensembl name, stop."
		break
	else:
		name_match[content[3]] = [content[-2], content[-1]]
anno_file.close()

long_dir = dict()
strong_dir = dict()

for line in tag_file.readlines()[1:]:
	content = line.strip().split('\t')
	tempcount = [float(i) for i in content[8:]]
	if sum(tempcount) == 0:
		continue
	else:
		TSSR = int(content[3]) - int(content[2])
		GBR = int(content[6]) - int(content[5])
		ChIPTSS = float(content[8])
		InputTSS = float(content[9])
		ChIPGB = float(content[10])
		InputGB = float(content[11])
		TSS_signal = (ChIPTSS - InputTSS)/TSSR
		GB_signal = (ChIPGB - InputGB)/GBR
		if TSS_signal < 0 or GB_signal < 0:
			continue
		else:
			if GB_signal ==0:
				PI = TSS_signal/0.0000001
			else:
				PI = TSS_signal/GB_signal
			alloutput.write(content[0] + '\t' + '\t'.join(name_match[content[0]]) + '\t' + '\t'.join(content[1:]) + '\t' + str(PI) + '\n')
			if args.longest:
				symbol = name_match[content[0]][1]
				if symbol in long_dir:
					if (TSSR + GBR) > (long_dir[symbol][1] + long_dir[symbol][2]):
						long_dir[symbol] = [line.strip(), TSSR, GBR, str(PI)]
				else:
					long_dir[symbol] = [line.strip(), TSSR, GBR, str(PI)]
			else:
				symbol = name_match[content[0]][1]
				#print symbol
				if symbol in strong_dir:
					if TSS_signal > strong_dir[symbol][1]:
						strong_dir[symbol] = [line.strip(), TSS_signal, str(PI)]
				else:
					strong_dir[symbol] = [line.strip(), TSS_signal, str(PI)]
alloutput.close()


if args.longest:
	print "select the longest isoform..."
	longoutput = open('longest_PI.txt', 'w')
	longoutput.write('transcript_id\tgene_id\tgene_symbol\tchr\tTSSstart\tTSSend\tchr\tGBstart\t'
					 'GBend\tstrand\tChIPTSScount\tInputTSScount\tChIPGBcount\tInputGBcount\tPI\n')
	for key in long_dir:
		if long_dir[key][1] >= args.min:
			transcript_id = long_dir[key][0].strip().split('\t')[0]
			content = long_dir[key][0].strip().split('\t')
			longoutput.write(transcript_id + '\t' + '\t'.join(name_match[transcript_id]) + '\t' +
							 '\t'.join(content[1:]) + '\t' + long_dir[symbol][-1] + '\n')
	longoutput.close()
else:
	print "selecting isoform with the strongest RNAP2 ChIP-seq singal at TSSR..."
	strongoutput = open('strongest_PI.txt', 'w')
	strongoutput.write('transcript_id\tgene_id\tgene_symbol\tchr\tTSSstart\tTSSend\tchr\tGBstart\t'
					   'GBend\tstrand\tChIPTSScount\tInputTSScount\tChIPGBcount\tInputGBcount\tPI\n')
	for key in strong_dir:
		if strong_dir[key][1] >= args.min:
			transcript_id = strong_dir[key][0].strip().split('\t')[0]
			content = strong_dir[key][0].strip().split('\t')
			strongoutput.write(transcript_id + '\t' + '\t'.join(name_match[transcript_id]) + '\t' +
							   '\t'.join(content[1:]) + '\t' + strong_dir[key][-1] + '\n')
	strongoutput.close()
