# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Templates for URLs and paths to specific relase, species, and file type on the
Ensembl ftp server.

For example, the human chromosomal DNA sequences for release 78 are in:

    https://ftp.ensembl.org/pub/release-78/fasta/homo_sapiens/dna/

For plant, fungi and metazoa species, the url is as follow:

    https://ftp.ensemblgenomes.ebi.ac.uk/pub/release-57/plants/fasta/glycine_max/cdna/
"""

from .ensembl_release_versions import check_release_number
from .species import Species, find_species_by_name

ENSEMBL_FTP_SERVER = "https://ftp.ensembl.org"
ENSEMBLGENOME_FTP_SERVER = "https://ftp.ensemblgenomes.ebi.ac.uk"

# Example directories
# FASTA files: /pub/release-78/fasta/homo_sapiens/
# GTF annotation files: /pub/release-78/gtf/homo_sapiens/
FASTA_SUBDIR_TEMPLATE = "/pub/release-%(release)d/fasta/%(species)s/%(type)s/"
GTF_SUBDIR_TEMPLATE = "/pub/release-%(release)d/gtf/%(species)s/"

DATABASE_FASTA_SUBDIR_TEMPLATE = (
    "/pub/release-%(release)d/%(database)s/fasta/%(species)s/%(type)s/"
)
DATABASE_GTF_SUBDIR_TEMPLATE = (
    "/pub/release-%(release)d/%(database)s/gtf/%(species)s/"
)

# GTF annotation file example: Homo_sapiens.GTCh38.gtf.gz
GTF_FILENAME_TEMPLATE = "%(Species)s.%(reference)s.%(release)d.gtf.gz"

# cDNA & protein FASTA file for releases before (and including) Ensembl 75
# example: Homo_sapiens.NCBI36.54.cdna.all.fa.gz
OLD_FASTA_FILENAME_TEMPLATE = (
    "%(Species)s.%(reference)s.%(release)d.%(sequence_type)s.all.fa.gz"
)

# ncRNA FASTA file for releases before (and including) Ensembl 75
# example: Homo_sapiens.NCBI36.54.ncrna.fa.gz

OLD_FASTA_FILENAME_TEMPLATE_NCRNA = (
    "%(Species)s.%(reference)s.%(release)d.ncrna.fa.gz"
)

# cDNA & protein FASTA file for releases after Ensembl 75
# example: Homo_sapiens.GRCh37.cdna.all.fa.gz
NEW_FASTA_FILENAME_TEMPLATE = (
    "%(Species)s.%(reference)s.%(sequence_type)s.all.fa.gz"
)

# ncRNA FASTA file for releases after Ensembl 75
# example: Homo_sapiens.GRCh37.ncrna.fa.gz
NEW_FASTA_FILENAME_TEMPLATE_NCRNA = "%(Species)s.%(reference)s.ncrna.fa.gz"


def normalize_release_properties(ensembl_release, species):
    """
    Make sure a given release is valid, normalize it to be an integer,
    normalize the species name, and get its associated reference.
    """
    if not isinstance(species, Species):
        species = find_species_by_name(species)
    ensembl_release = check_release_number(
        ensembl_release, database=species.database
    )
    reference_name = species.which_reference(ensembl_release)
    return ensembl_release, species.latin_name, reference_name


def make_gtf_filename(ensembl_release, species):
    """
    Return GTF filename expect on Ensembl FTP server for a specific
    species/release combination.
    """
    ensembl_release, species, reference_name = normalize_release_properties(
        ensembl_release, species
    )
    return GTF_FILENAME_TEMPLATE % {
        "Species": species.capitalize(),
        "reference": reference_name,
        "release": ensembl_release,
    }


def make_gtf_url(ensembl_release, species, server=None, database=None):
    """
    Returns a URL and a filename, which can be joined together.
    """
    if server is None:
        if database is None:
            server = ENSEMBL_FTP_SERVER
        else:
            server = ENSEMBLGENOME_FTP_SERVER
    ensembl_release, species, _ = normalize_release_properties(
        ensembl_release, species
    )
    if database is None:
        subdir = GTF_SUBDIR_TEMPLATE % {
            "release": ensembl_release,
            "species": species,
        }
    else:
        subdir = DATABASE_GTF_SUBDIR_TEMPLATE % {
            "release": ensembl_release,
            "database": database,
            "species": species,
        }
    filename = make_gtf_filename(
        ensembl_release=ensembl_release, species=species
    )
    return server + subdir + filename


def make_fasta_filename(ensembl_release, species, database, sequence_type):
    ensembl_release, species, reference_name = normalize_release_properties(
        ensembl_release, species
    )
    # for plant database, start from release 32 (inlcude 32) , the fasta file use the "old name"
    # for releses before 31, the fasta file use the "new name"
    # version 31 use both old and new name
    if (ensembl_release <= 75 and database is None) or (
        ensembl_release <= 31 and database is not None
    ):
        if sequence_type == "ncrna":
            return OLD_FASTA_FILENAME_TEMPLATE_NCRNA % {
                "Species": species.capitalize(),
                "reference": reference_name,
                "release": ensembl_release,
            }
        else:
            return OLD_FASTA_FILENAME_TEMPLATE % {
                "Species": species.capitalize(),
                "reference": reference_name,
                "release": ensembl_release,
                "sequence_type": sequence_type,
            }
    else:
        if sequence_type == "ncrna":
            return NEW_FASTA_FILENAME_TEMPLATE_NCRNA % {
                "Species": species.capitalize(),
                "reference": reference_name,
            }
        else:
            return NEW_FASTA_FILENAME_TEMPLATE % {
                "Species": species.capitalize(),
                "reference": reference_name,
                "sequence_type": sequence_type,
            }


def make_fasta_url(
    ensembl_release,
    species,
    sequence_type,
    server=None,
    database=None,
):
    """
    Construct URL to FASTA file with cDNA transcript or protein sequences.

    Parameter examples:
        ensembl_release = 75
        species = "Homo_sapiens"
        sequence_type = "cdna" (other option: "pep")
    """
    if server is None:
        if database is None:
            server = ENSEMBL_FTP_SERVER
        else:
            server = ENSEMBLGENOME_FTP_SERVER
    ensembl_release, species, _ = normalize_release_properties(
        ensembl_release, species
    )
    if database is None:
        subdir = FASTA_SUBDIR_TEMPLATE % {
            "release": ensembl_release,
            "species": species,
            "type": sequence_type,
        }
    else:
        subdir = DATABASE_FASTA_SUBDIR_TEMPLATE % {
            "release": ensembl_release,
            "database": database,
            "species": species,
            "type": sequence_type,
        }

    filename = make_fasta_filename(
        ensembl_release=ensembl_release,
        species=species,
        database=database,
        sequence_type=sequence_type,
    )
    return server + subdir + filename
