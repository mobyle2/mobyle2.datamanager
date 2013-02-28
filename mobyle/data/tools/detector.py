from ctypes import *
import os
import logging

squizz = True
try:
    libc = cdll.LoadLibrary("libc.so.6")
    # For squizz
    libbioseq = CDLL("libbioseq.so.0", mode=RTLD_GLOBAL)
    libbioali = CDLL("libbioali.so.0", mode=RTLD_GLOBAL)
except Exception:
    logging.warn("Squizz libraries could not be loaded, skipping squizz")
    squizz = False

SEQFMT_UNKWN = "unknown"
SEQFMT_SPROT = "sprot"
SEQFMT_EMBL = "embl"
SEQFMT_GENBANK = "genbank"
SEQFMT_PIR = "pir"
SEQFMT_NBRF = "nbrf"
SEQFMT_GDE = "gde"
SEQFMT_IG = "ig"
SEQFMT_FASTA = "fasta"
SEQFMT_GCG = "gcg"
SEQFMT_RAW = "raw"
SEQFMT_NONE = "none"

ALIFMT_UNKWN = SEQFMT_UNKWN
ALIFMT_CLUSTAL = "clustal"
ALIFMT_PHYLIPI = "PHYLIPI"
ALIFMT_PHYLIPS = "PHYLIPS"
ALIFMT_FASTA = "FASTA"
ALIFMT_MEGA = "MEGA"
ALIFMT_MSF = "MSF"
ALIFMT_NEXUSI = "NEXUSI"
ALIFMT_STOCK = "STOCKHOLM"
ALIFMT_NONE = SEQFMT_NONE

class SquizzDetector (object):
    '''Detector using Squizz'''

    def __init__( self ):
        SquizzDetector.seqformats = [ SEQFMT_UNKWN, SEQFMT_SPROT, SEQFMT_EMBL, SEQFMT_GENBANK, SEQFMT_PIR,
                                      SEQFMT_NBRF, SEQFMT_GDE, SEQFMT_IG, SEQFMT_FASTA, SEQFMT_GCG, SEQFMT_RAW,
                                      SEQFMT_NONE ]

        SquizzDetector.alignformats = [ ALIFMT_UNKWN, ALIFMT_CLUSTAL, ALIFMT_PHYLIPI, ALIFMT_PHYLIPS,
                                        ALIFMT_FASTA, ALIFMT_MEGA, ALIFMT_MSF, ALIFMT_NEXUSI, ALIFMT_STOCK,
                                        ALIFMT_NONE ]

    def detect(self,filename):
        '''Detect method'''
        f = libc.fopen(filename, "r")
        format = libbioseq.sequence_format(f)
        if format == SEQFMT_NONE:
            format = libbioali.align_format(f)
            libc.fclose(f) 
            if format == ALIFMT_NONE:
                return None
            return SquizzDetector.alignformats[format]
        else:
            libc.fclose(f)
            return SquizzDetector.seqformats[format]

class BioFormat (object):
    '''Generic detector for an input sequence. Call all registered detectors until one answers'''

    detectors = []

    def __init__( self ):

        if BioFormat.detectors is None:
            BioFormat.detectors = []

        self.datatypes_by_extension = {
                'ab1'         : 'ab1',
                'axt'         : 'axt',
                'bam'         : 'bam',
                'bed'         : 'bed',
                'coverage'    : 'coverage',
                'customtrack' : 'customtrack',
                'csfasta'     : 'csFasta()',
                'fasta'       : 'fasta',
                'fa'          : 'fasta',
                'fsa'         : 'fasta',
                'eland'       : 'eland',
                'fastq'       : 'fastq()',
                'fastqsanger' : 'fastqsanger()',
                'gbk'         : 'genbank',
                'gtf'         : 'gtf',
                'gff'         : 'gff',
                'gff3'        : 'gff3',
                'genetrack'   : 'genetrack',
                'interval'    : 'interval',
                'laj'         : 'laj',
                'lav'         : 'lav',
                'maf'         : 'maf',
                'pileup'      : 'pileup',
                'qualsolid'   : 'qualsolid',
                'qualsolexa'  : 'qualsolexa',
                'qual454'     : 'qual454',
                'sam'         : 'sam',
                'scf'         : 'scf',
                'sff'         : 'sff',
                'tabular'     : 'tabular',
                'taxonomy'    : 'taxonomy',
                'txt'         : 'txt',
                'wig'         : 'wig',
                'xml'         : 'xml',
            }

        self.mimetypes = {
                'ab1'         : 'application/octet-stream',
                'axt'         : 'text/plain',
                'bam'         : 'application/octet-stream',
                'bed'         : 'text/plain',
                'customtrack' : 'text/plain',
                'csfasta'     : 'text/plain',
                'eland'       : 'application/octet-stream',
                'fasta'       : 'text/plain',
                'fastq'       : 'text/plain',
                'fastqsanger' : 'text/plain',
                'gtf'         : 'text/plain',
                'gff'         : 'text/plain',
                'gff3'        : 'text/plain',
                'interval'    : 'text/plain',
                'laj'         : 'text/plain',
                'lav'         : 'text/plain',
                'maf'         : 'text/plain',
                'memexml'     : 'application/xml',
                'pileup'      : 'text/plain',
                'qualsolid'   : 'text/plain',
                'qualsolexa'  : 'text/plain',
                'qual454'     : 'text/plain',
                'sam'         : 'text/plain',
                'scf'         : 'application/octet-stream',
                'sff'         : 'application/octet-stream',
                'tabular'     : 'text/plain',
                'taxonomy'    : 'text/plain',
                'txt'         : 'text/plain',
                'wig'         : 'text/plain',
                'xml'         : 'application/xml',
            }

    @staticmethod
    def register(detector):
        '''
        Register a format detector
        :param detector: detector class
        :type detector: Class
        :return: format of the file
        '''
        BioFormat.detectors.append(detector)

    def detect_by_extension(self,filename):
        '''
        Try to detect the format of the input file based on extension
        :params filename: file to detect
        :type filename: str
        :return: format
        '''
        name, fileExtension = os.path.splitext(filename)
        fileExtension = fileExtension.replace('.','')
        if fileExtension in self.datatypes_by_extension:
            return self.datatypes_by_extension[fileExtension]
        return None


    def detect(self,filename):
        '''
        Try to detect the format of the input file
        :params filename: file to detect
        :type filename: str
        :return: tuple (format,mimetype)
        '''
        format = self.detect_by_extension(filename)
        if format:
            return (format,self.mimetypes[format])

        for detector in BioFormat.detectors:
            logging.debug("Try detector "+detector.__name__)
            curdetector = detector()
            format = curdetector.detect(filename)
            if format is not None:
                mime = 'application/octet-stream'
                if format in self.mimetypes:
                    mime = self.mimetypes[format]
                return (format,mime)

        return (None,None)




if __name__ == "__main__":
    if squizz:
        BioFormat.register(SquizzDetector)
    detector = BioFormat()
    (format,mime) = detector.detect("test.fasta")
    print("test.fasta: "+str(format)+" : "+str(mime))
    (format,mime) = detector.detect("test.myfasta")
    print("test.myfasta: "+str(format)+" : "+str(mime))

