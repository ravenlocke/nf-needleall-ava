#!/usr/bin/env python
	
import networkx as nx
from Bio import SeqIO

class SSN():
	def __init__(self, identity_file, fasta_records):
		self.identity_file = identity_file
		self.fasta_records = fasta_records
		self.G = nx.Graph()

	def build_graph(self):
		# Add nodes.
		for record in SeqIO.parse(self.fasta_records, 'fasta'):
			self.G.add_node(record.id, description=record.description)
	
		# Add eddges.
		with open(self.identity_file, 'r') as f:
			for line in f:
				n1, n2, identity = line.strip().split()
				self.G.add_edge(n1, n2, identity=float(identity))


	def write_gml(self, outfile):
		nx.write_gml(self.G, outfile)



a = SSN("${identities.name}", "${fasta_file.name}")
a.build_graph()
a.write_gml("identities.gml")
