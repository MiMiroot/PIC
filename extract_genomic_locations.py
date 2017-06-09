"""
author: CJH
function: extract gene information for gene annotation files, like gtf file.
"""

import sys
import argparse

parser = argparse.ArgumentParser(prog='Gene Info extraction')
parser.add_argument('--gtf', type=str, help="the gene annotation file")
parser.add_argument('--TSSup', type=int, help="the distance upstream of TSS")
parser.add_argument('--TSSdown', type=int, help="the distance downstream of TSS")
parser.add_argument('--GBdown', type=int, help="the distance downstream of the end of gene body")
parser.add_argument('--gsize',type=str,help="the chromosome size of the genome, each line: chromosome[tab]length(bp)[Enter]")
args = parser.parse_args()

annotation_file = open(args.gtf, 'r')
allgeneoutput = open("gene_info.txt", 'w')  #output all gene information
allgenetss = open("gene_tss.bed", 'w')  #output TSS region of all genes
allgenebody = open("gene_GB.bed", 'w')

chr_file = open(args.gsize,'r')
chr_length = {}
for line in chr_file:
	content = line.strip().split('\t')
	chr_length[content[0]] = int(content[1])
chr_file.close()

for line in annotation_file.readlines():
	content = line.strip().split('\t')
	if content[2] == 'transcript':
		nameinfo = content[8].split(";")
		chromosome = content[0]
		location1 = content[3]
		location2 = content[4]
		score = content[5]
		strand = content[6]
		if not chromosome in chr_length:  #this is a check in order to abandon genes whose chr is not in the gsize file.
			continue
		for attri in nameinfo:
			if attri.strip().startswith('gene_id'):
				gene_id = attri.strip().split('"')[1]
			if attri.strip().startswith('gene_name'):
				gene_name = attri.strip().split('"')[1]
			if attri.strip().startswith('transcript_id'):
				transcript_id = attri.strip().split('"')[1]
		allgeneoutput.write(chromosome + '\t' + location1 + '\t' + location2 + '\t' + transcript_id + '\t' +
							score + '\t' + strand + '\t' + gene_id + '\t' + gene_name + '\n')
		if strand == '+':
			start0 = int(location1) - args.TSSup + 1
			end0 = int(location1) + args.TSSdown - 1
			if start0 < 0:
				start0 = 0
			allgenetss.write(chromosome + '\t' + str(start0) + '\t' + str(end0) + '\t' + transcript_id + '\t' + score + '\t' + strand + '\n')
			start1 = end0
			end1 = int(location2) + args.GBdown -1
			if end1 > chr_length[chromosome]:
				end1 = chr_length[chromosome]			
			allgenebody.write(chromosome + '\t' + str(start1) + '\t' + str(end1) + '\t' + transcript_id + '\t' + score + '\t' + strand + '\n')
		elif strand == "-":
			end0 = int(location2) + args.TSSup -1
			start0 = int(location2) - args.TSSdown + 1
			if start0 > chr_length[chromosome]:
				start0 = chr_length[chromosome]
			allgenetss.write(chromosome + '\t' + str(start0) + '\t' + str(end0) + '\t' + transcript_id + '\t' + score + '\t' + strand + '\n')
			end1 = end0
			start1 = int(location1) - args.GBdown + 1
			if end1 < 0:
				end1 = 0
			allgenebody.write(chromosome + '\t' + str(start1) + '\t' + str(end1) + '\t' + transcript_id + '\t' + score + '\t' + strand + '\n')

annotation_file.close()
allgeneoutput.close()
allgenetss.close()
allgenebody.close()
