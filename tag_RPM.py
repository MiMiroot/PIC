"""
author: CJH
function: calculate RPM for genomic regions (TSS, GB), prepared for pausing calculation.
count up total number of reads and divided number by 1000,000 -- it's the 'per million' scaling factor.
divide read counts by 'per million' scaling factor. this normalizes for sequencing depth, giving you reads per million (RPM).
"""

import sys,os
import argparse

parser = argparse.ArgumentParser(prog='Calculation RPM for regions')
parser.add_argument('--chip',type=str,help="BAM files for ChIP-seq")
parser.add_argument('--input',type=str,help="BAM files for input ChIP-seq")
parser.add_argument('--min',type=str,default=20,help="Skip alignments with MAPQ smaller than INT[20]")
parser.add_argument('--tss',type=str,help="bed file for tss regions")
parser.add_argument('--gb',type=str,help="bed file for gene body regions")
args = parser.parse_args()

#calculate the scaling factor (RPM)
ChIP_BAM = os.popen('samtools view -q ' + args.min + ' -c ' + args.chip)
for line in ChIP_BAM:
	ChIP_total = line.strip()
Input_BAM = os.popen('samtools view -q ' + args.min + ' -c ' + args.input)
for line in Input_BAM:
	Input_total = line.strip()
scaling_ChIP = float(float(ChIP_total)/1000000)
scaling_Input = float(float(Input_total)/1000000)
print 'The scaling factor for ChIP is ', str(scaling_ChIP)
print 'The scaling factor for Input is ', str(scaling_Input)

#calculate the tag counts for each regions.
print 'calculating read counts...'
os.system('samtools view -bq ' + args.min + ' ' + args.chip + ' |bedtools bamtobed -i stdin > ChIP-trim.bed')
os.system('samtools view -bq ' + args.min + ' ' + args.input + ' |bedtools bamtobed -i stdin > Input-trim.bed')
os.system('coverageBed -a ' + args.tss + ' -b ChIP-trim.bed > ChIP-tss-count-raw.txt')
os.system('coverageBed -a ' + args.tss + ' -b Input-trim.bed > Input-tss-count-raw.txt')
os.system('coverageBed -a ' + args.gb + ' -b ChIP-trim.bed > ChIP-gb-count-raw.txt')
os.system('coverageBed -a ' + args.gb + ' -b Input-trim.bed > Input-gb-count-raw.txt')


#check in each count file, gene list is consistent.
def gene_list_total(count_file):
	infile = os.popen('wc ' + count_file)
	for line in infile:
		counts = line.strip().split(' ')[0]
	infile.close()
	return counts

ChIP_tss_count = gene_list_total('ChIP-tss-count-raw.txt')
Input_tss_count = gene_list_total('Input-tss-count-raw.txt')
ChIP_gb_count = gene_list_total('ChIP-gb-count-raw.txt')
Input_gb_count = gene_list_total('Input-gb-count-raw.txt')
temp = [ChIP_tss_count, Input_tss_count, ChIP_gb_count, Input_gb_count]
if not len(set(temp)) == 1:
	print 'gene list is not the same!!!!'
else:
	print 'gene list is the same!'
	raw_list = ['ChIP-tss-count-raw.txt', 'Input-tss-count-raw.txt', 'ChIP-gb-count-raw.txt', 'Input-gb-count-raw.txt']
	os.system('cut -f 4 ChIP-tss-count-raw.txt > part1')
	os.system('cut -f 1-3 ChIP-tss-count-raw.txt > part2')
	os.system('cut -f 1-3 ChIP-gb-count-raw.txt > part3')
	os.system('cut -f 6 ChIP-gb-count-raw.txt > part4')
	os.system('cut -f 7 ChIP-tss-count-raw.txt > part5')
	os.system('cut -f 7 Input-tss-count-raw.txt > part6')
	os.system('cut -f 7 ChIP-gb-count-raw.txt > part7')
	os.system('cut -f 7 Input-gb-count-raw.txt > part8')
	os.system('paste part1 part2 part3 part4 part5 part6 part7 part8 > tag_count.txt')
	os.system('rm part*')
	#normalize the read counts ( the sixth column by scaling_ChIP or scaling_Input)
	infile = open('tag_count.txt','r')
	outfile = open('tag_count_normalize.txt','w')
	outfile.write("gene_id\tchr\tstart\tend\tchr\tstart\tend\tstrand\tChIP_tss\tInput_tss\tChIP_gb\tInput_gb\n")
	for line in infile:
		content = line.strip().split('\t')
		c1 = str(float(content[8])/scaling_ChIP)
		c2 = str(float(content[9])/scaling_Input)
		c3 = str(float(content[10])/scaling_ChIP)
		c4 = str(float(content[11])/scaling_Input)
		outfile.write('\t'.join(content[:8]) + '\t' + c1 + '\t' + c2 + '\t' + c3 + '\t' + c4 + '\n')
	infile.close()
	outfile.close()
	os.system('rm  ChIP-trim.bed Input-trim.bed ChIP-tss-count-raw.txt Input-tss-count-raw.txt ChIP-gb-count-raw.txt Input-gb-count-raw.txt')
print 'done.'
