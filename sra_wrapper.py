import json
import os
import sys


def map_fq_record(obj):
    """ Convert CWL input to BBX """
    # TODO: Currently input is array of single-end FQs. Should be array of records.
    return {
        'value': obj['path'],  # obj['value']['path'],
        'id': 'se',  # obj['id'],
        'type': 'single',  # obj['type'],
    }


def load_job():
    """ Load the CWL inputs """
    # TODO: Read inputs fro serialized Job. Currently reading single-end FQs from arguments.
    # with open('cwl.inputs.json') as fp:
    #     return json.load(fp)
    return {
      'task': sys.argv[2],
      'fastq': sys.argv[3:]
    }


def write_inputs(job, indir='/bbx/input'):
    """ Serialize BBX input YAML """
    bbx_input = {
        'version': '0.9.3',
        'arguments': [
            {
                'fastq': [map_fq_record(fq) for fq in job['fastq']]
            }
        ]
    }
    target = os.path.join(indir, 'biobox.yaml')
    with open(target, 'w') as fp:
        json.dump(bbx_input, fp)


def write_output(output_fasta):
    """ Serialize CWL output JSON file """
    with open('cwl.output.json', 'w') as fp:
        json.dump({'fasta': {'class': 'File', 'path': output_fasta}}, fp)


def main():
    indir, outdir = '/bbx/input', '/bbx/output'

    # Symlink output directory since we're CWL requires outputs to be in CWD
    if not os.path.exists(outdir):
        os.symlink(os.path.abspath('.'), outdir)

    # Load CWL inputs and serialize as BBX inputs
    job = load_job()
    if not os.path.exists(indir):
        os.makedirs(indir)
    write_inputs(job, indir=indir)

    # Run assembler
    entrypoint = sys.argv[1]
    task = job['task']
    exit_code = os.system(' '.join([entrypoint, task]))
    if exit_code:
        raise Exception('Process exit code: %s' % exit_code)

    # TODO: Read output fasta path from BBX YAML
    fasta = 'result.fa'
    with open(fasta, 'w') as fp:
        fp.write('Mock result file.')

    # Write CWL output
    write_output(fasta)


if __name__ == '__main__':
    main()
