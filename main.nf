#!/usr/bin/env nextflow

params.infile = null
params.outdir = null
params.threshold = -1

/*
Check that the relevant parameters are present to carry out the assembly
*/

// Checking whether the user has indicated an infile and outfile
if (params.infile == null){
	error "--infile is a required parameter (the FASTA file containing sequences for all vs all identity calculations)"
} else {
	infile = file( params.infile )
}


// Create the outdir
if (params.outdir == null){
	error "--outdir is a required parameter (the name of the directory to store results)"
} else {
	outdir = file( params.outdir )
	outdir.mkdirs()
}


/*
Run the Nextflow workflow
*/

// This process exposes the forward and reverse reads to the rest of the workflow.
process exposeData {
	output:
	file "in.fasta" into calculate_identity, build_graph
	
	script:
	"""
	ln -s $infile in.fasta
	"""
}

process runNeedleall {

	input:
	file fasta_file from calculate_identity

	output:
	file "identities.txt" into identities

	script:
	template "needleall.py"
}


process buildGraph {
        publishDir "${outdir}", mode: "copy"

        input:
        file fasta_file from build_graph
	file identities

        output:
        file "identities.txt" into identities_out
	file "identities.gml" into gml_out

        script:
        template "make_ssn.py"

}
