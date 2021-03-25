#!/usr/bin/env python3

import os as _os
import subprocess as _sp
import tempfile as _tf
import multiprocessing as _mp

from Bio import SeqIO as _sqio

_NEWLINE = """
"""

def set_global_lock(l):
	global lock
	lock = l

class NeedleAll():
	def __init__(self, outfile, gap_open_penalty=10, gap_extend_penalty=0.5, threshold=-1):
		self.outfile = outfile
		if _os.path.isfile(self.outfile):
			raise Exception("Outfile given already exists, please choose a new location")
		self.gap_open_penalty = gap_open_penalty
		self.gap_extend_penalty = gap_extend_penalty
		self.record_id_map = {}
		self.threshold = threshold

	def run_record(self, record_id, seqfile):
		print(record_id)
		with _tf.NamedTemporaryFile(suffix='.fasta') as aseq, \
                     _tf.NamedTemporaryFile(suffix='.fasta') as bseq, \
		     _tf.NamedTemporaryFile('r', suffix='.needleout') as needleout:
			keep_entry = False

			for record in _sqio.parse(seqfile, 'fasta'):
				if record.id == record_id:
					aseq.write(record.format('fasta').encode())
					keep_entry = True

				if keep_entry:
					bseq.write(record.format('fasta').encode())

			aseq.seek(0)
			bseq.seek(0)

			# Generate the command and run needleall
			command = ['needleall',	'-asequence', aseq.name, '-bsequence', bseq.name,
				'-gapopen', f'{self.gap_open_penalty}', '-gapextend',f'{self.gap_extend_penalty}',
				'-outfile', needleout.name, '-aformat3', 'pair']

			process = _sp.Popen(command, stdout=_sp.PIPE, stderr=_sp.PIPE)
			stdout, stderr = process.communicate()
			# Parse the output file
			identities = []
			with open(needleout.name, 'r') as f:
				id1, id2, identity = None, None, None
				for line in f:
					if line.strip().startswith('# 1:'):
						id1 = line.strip().split()[2]

					if line.strip().startswith('# 2:'):
						id2 = line.strip().split()[2]

					if line.strip().startswith('# Identity'):
						num, den = line.strip().split()[2].split('/')
						num, den = int(num), int(den)
						identity = num / den
						identities.append((id1, id2, identity,))

						# Reset variables so that any future iterations don't use these.
						num, den, identity, id1, id2 = None, None, None, None, None


		with lock:
			with open(self.outfile, 'a') as f:
				for id1, id2, identity in identities:
					if not identity >= self.threshold:
						continue
					f.write(f"{self.record_id_map[id1]} {self.record_id_map[id2]} {identity}{_NEWLINE}")

	def run(self, seqfile):
		jobs = []

		with _tf.NamedTemporaryFile() as f:
			counter = 0
			for record in _sqio.parse(seqfile, 'fasta'):
				new_id = f'R{counter}'
				self.record_id_map[new_id] = record.id
				record.id = new_id
				f.write(record.format('fasta').encode())
				f.seek(0,2)
				jobs.append( (record.id, f.name) )
				counter += 1


			lock = _mp.Lock()
			with _mp.Pool(_mp.cpu_count(), initializer=set_global_lock, initargs=(lock,)) as pool:
				pool.starmap(self.run_record, jobs, chunksize=1)


A = NeedleAll("identities.txt", threshold=${params.threshold})
A.run("${fasta_file.name}")
